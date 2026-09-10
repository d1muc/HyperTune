import os
import re
import json
import tempfile
import subprocess
import sys
from pathlib import Path

SHADER_PATH = Path(os.path.expanduser("~/.config/hypr/shaders/contrast.glsl"))
CONFIG_PATH = Path(os.path.expanduser("~/.config/hyprtune/config.json"))

DEFAULT_SETTINGS = {
    "brightness": 0.00, "contrast": 0.00, "exposure": 0.00, "gamma": 0.00,
    "shadows": 0.00, "midtones": 0.00, "highlights": 0.00,
    "saturation": 0.00, "vibrance": 0.00, "hue": 0.00,
    "temperature": 0.00, "tint": 0.00,
    "redGain": 0.00, "greenGain": 0.00, "blueGain": 0.00
}

DEFAULT_CONFIG = {
    "theme": "Просто темная",
    "preset": "По умолчанию",
    "autostart": False,
    "hotkey": "SUPER, X",
    "res_hotkey": "SUPER, F12",
    "language": "Русский",
    "monitor": "Auto",
    "resolution": "Native",
    "refresh_rate": "Auto",
    "stretch_4_3": True
}

GLSL_TEMPLATE = """precision mediump float;
varying vec2 v_texcoord;
uniform sampler2D tex;

// PRISMIX_SETTINGS_START
const float brightness = {brightness:.2f};
const float contrast = {contrast:.2f};
const float exposure = {exposure:.2f};
const float gamma = {gamma:.2f};
const float shadows = {shadows:.2f};
const float midtones = {midtones:.2f};
const float highlights = {highlights:.2f};
const float saturation = {saturation:.2f};
const float vibrance = {vibrance:.2f};
const float hue = {hue:.2f};
const float temperature = {temperature:.2f};
const float tint = {tint:.2f};
const float redGain = {redGain:.2f};
const float greenGain = {greenGain:.2f};
const float blueGain = {blueGain:.2f};
// PRISMIX_SETTINGS_END

vec3 hueRotate(vec3 col, float hueShift) {{
    vec3 k = vec3(0.57735, 0.57735, 0.57735);
    float cosAngle = cos(hueShift);
    return col * cosAngle + cross(k, col) * sin(hueShift) + k * dot(k, col) * (1.0 - cosAngle);
}}

void main() {{
    vec4 texColor = texture2D(tex, v_texcoord);
    vec3 color = texColor.rgb;

    color *= pow(2.0, exposure);
    color += brightness;
    color = (color - 0.5) * (contrast + 1.0) + 0.5;
    color = max(color, vec3(0.0));
    color = pow(color, vec3(1.0 / (gamma + 1.0)));

    float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float shadowMask = smoothstep(0.4, 0.0, luma);
    float highlightMask = smoothstep(0.6, 1.0, luma);
    float midtoneMask = max(0.0, 1.0 - shadowMask - highlightMask);

    color += color * (shadows * shadowMask * 0.4);
    color += color * (midtones * midtoneMask * 0.4);
    color += color * (highlights * highlightMask * 0.4);

    color.r *= (1.0 + redGain) + (temperature * 0.05);
    color.g *= (1.0 + greenGain) + (tint * 0.05);
    color.b *= (1.0 + blueGain) - (temperature * 0.05);

    if (abs(hue) > 0.001) {{
        color = hueRotate(color, hue * 3.14159265);
    }}

    float maxChan = max(color.r, max(color.g, color.b));
    float minChan = min(color.r, min(color.g, color.b));
    float vibMask = 1.0 - (maxChan - minChan);
    color = mix(vec3(luma), color, 1.0 + saturation + (vibrance * vibMask * 0.5));

    gl_FragColor = vec4(color, texColor.a);
}}
"""

def load_shader_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    if not SHADER_PATH.exists():
        save_shader_settings(settings)
        return settings
    try:
        content = SHADER_PATH.read_text()
        match = re.search(r"// PRISMIX_SETTINGS_START(.*)// PRISMIX_SETTINGS_END", content, re.DOTALL)
        if match:
            for line in match.group(1).strip().split("\n"):
                kv = re.search(r"const float (\w+)\s*=\s*([\d\.-]+);", line)
                if kv:
                    settings[kv.group(1)] = float(kv.group(2))
    except Exception:
        pass
    return settings

def save_shader_settings(settings: dict):
    try:
        SHADER_PATH.parent.mkdir(parents=True, exist_ok=True)
        glsl_code = GLSL_TEMPLATE.format(**settings)
        fd, temp_path = tempfile.mkstemp(dir=str(SHADER_PATH.parent), suffix=".tmp")
        with os.fdopen(fd, 'w') as f:
            f.write(glsl_code)
        os.replace(temp_path, str(SHADER_PATH))
    except Exception as e:
        print(f"Ошибка записи шейдера: {e}")

def load_app_config() -> dict:
    if not CONFIG_PATH.exists():
        save_app_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        data = json.loads(CONFIG_PATH.read_text())
        for k, v in DEFAULT_CONFIG.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return DEFAULT_CONFIG

def save_app_config(config: dict):
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(config, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка конфига: {e}")

def update_hyprland_shortcut(hotkey_shader: str, hotkey_res: str):
    hypr_conf = Path(os.path.expanduser("~/.config/hypr/hyprland.conf"))
    if not hypr_conf.exists():
        return
    try:
        content = hypr_conf.read_text()
        lines = content.splitlines()
        
        lines = [line for line in lines if "# hyprtune-bind" not in line and "# hyprtune-res-bind" not in line]
        
        if hotkey_shader.strip():
            toggle_cmd = f'hyprctl keyword decoration:screen_shader "$(hyprctl getoption decoration:screen_shader | grep -q "EMPTY" && echo "{SHADER_PATH}" || echo "[[EMPTY]]")"'
            lines.append(f"bind = {hotkey_shader}, exec, {toggle_cmd} # hyprtune-bind")
            
        if hotkey_res.strip():
            script_path = os.path.abspath(sys.argv[0])
            lines.append(f"bind = {hotkey_res}, exec, python3 {script_path} --toggle-res # hyprtune-res-bind")
            
        hypr_conf.write_text("\n".join(lines) + "\n")
    except Exception as e:
        print(f"Не удалось обновить горячие клавиши в hyprland.conf: {e}")

def load_monitors() -> list:
    try:
        res = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True)
        if res.returncode == 0:
            return json.loads(res.stdout)
    except Exception:
        pass
    return []

def apply_display_settings(monitor_name: str, resolution: str, hz: str, stretch: bool):
    try:
        monitors = load_monitors()
        target_mon = None
        for m in monitors:
            if m.get("name") == monitor_name:
                target_mon = m
                break
        
        pos_str = "0x0"
        scale_str = "1"
        if target_mon:
            pos_str = f"{target_mon.get('x', 0)}x{target_mon.get('y', 0)}"
            scale_str = str(target_mon.get("scale", 1))

        resolution = resolution.strip()
        hz = hz.strip()

        if resolution.lower() == "native" or not resolution:
            res_rule = "preferred"
        else:
            if hz.lower() == "auto" or not hz:
                res_rule = resolution
            else:
                res_rule = f"{resolution}@{hz}"
        
        cmd = f"{monitor_name},{res_rule},{pos_str},{scale_str}"
        subprocess.run(["hyprctl", "keyword", "monitor", cmd], capture_output=True)
    except Exception as e:
        print(f"Ошибка применения дисплея: {e}")

def toggle_resolution():
    config = load_app_config()
    monitor_name = config.get("monitor", "Auto")
    target_res = config.get("resolution", "Native")
    target_hz = config.get("refresh_rate", "Auto")
    stretch = config.get("stretch_4_3", True)
    
    if target_res.lower() == "native":
        return 
        
    monitors = load_monitors()
    if not monitors: return
    
    target_mon = None
    if monitor_name == "Auto":
        target_mon = monitors[0]
        monitor_name = target_mon.get("name")
    else:
        target_mon = next((m for m in monitors if m.get("name") == monitor_name), None)
        
    if not target_mon: return
        
    current_width = target_mon.get("width", 0)
    current_height = target_mon.get("height", 0)
    
    is_custom = False
    if "x" in target_res.lower():
        try:
            tw, th = map(int, target_res.lower().split("x"))
            if current_width == tw and current_height == th:
                is_custom = True
        except: pass
        
    if is_custom:
        apply_display_settings(monitor_name, "Native", "Auto", stretch)
    else:
        apply_display_settings(monitor_name, target_res, target_hz, stretch)