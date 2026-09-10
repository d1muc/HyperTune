#!/usr/bin/env python3
import sys
import os
import subprocess

if len(sys.argv) > 1 and sys.argv[1] == "--toggle-res":
    import shader_utils
    shader_utils.toggle_resolution()
    sys.exit(0)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QPushButton, QFrame, QComboBox, QGraphicsOpacityEffect, QScrollArea, QCheckBox, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap

import shader_utils
import themes
import presets

SLIDER_RANGES = {
    "brightness": (-1.0, 1.0), "contrast": (-1.0, 1.0), "exposure": (-2.0, 2.0), "gamma": (-0.8, 2.0),
    "shadows": (-1.0, 1.0), "midtones": (-1.0, 1.0), "highlights": (-1.0, 1.0),
    "saturation": (-1.0, 1.0), "vibrance": (-1.0, 1.0), "hue": (-1.0, 1.0),
    "temperature": (-1.0, 1.0), "tint": (-1.0, 1.0),
    "redGain": (-1.0, 1.0), "greenGain": (-1.0, 1.0), "blueGain": (-1.0, 1.0)
}

UI_TEXTS = {
    "English": {
        "side_title": "Program Settings", "theme": "UI Color Scheme:", "preset": "Image Profile:",
        "lang": "Language:", "autostart": "Load shader on startup", 
        "hotkey": "Shader Hotkey:", "hotkey_res": "Resolution Hotkey:",
        "btn_en": "Enable", "btn_dis": "Disable", "btn_res": "Reset",
        "lum": "Luminance", "chrom": "Chromance",
        "tone": "Tone", "band": "3-Band", "color": "Color", "gain": "Per-channel Gain",
        "disp_title": "Display Settings", "lbl_mon": "Monitor:", "lbl_res": "Resolution:", 
        "lbl_hz": "Refresh Rate:", "chk_stretch": "Stretch 4:3 Aspect Ratio", "btn_apply_disp": "Apply Display Changes",
        "preset_list": ["Default", "Warm Comfort", "Cold Ice", "Contrast World", "Night Dream"],
        "theme_names": {
            "Просто темная": "Just Dark",
            "Просто светлая": "Just Light",
            "Пурпурный Закат": "Purple Sunset",
            "Солнечный Янтарь": "Sunny Amber"
        },
        "params": {
            "brightness": "Brightness", "contrast": "Contrast", "exposure": "Exposure", "gamma": "Gamma",
            "shadows": "Shadows", "midtones": "Midtones", "highlights": "Highlights",
            "saturation": "Saturation", "vibrance": "Vibrance", "hue": "Hue Shift", "temperature": "Temperature", "tint": "Tint",
            "redGain": "Red Gain", "greenGain": "Green Gain", "blueGain": "Blue Gain"
        }
    },
    "Русский": {
        "side_title": "Настройки программы", "theme": "Цветовая схема UI:", "preset": "Профиль изображения:",
        "lang": "Язык (Language):", "autostart": "Загружать шейдер при старте", 
        "hotkey": "Хоткей шейдера:", "hotkey_res": "Хоткей разрешения:",
        "btn_en": "Включить", "btn_dis": "Отключить", "btn_res": "Сбросить",
        "lum": "Освещенность", "chrom": "Цветопередача",
        "tone": "Тон", "band": "3-Полосный", "color": "Цвет", "gain": "Усиление каналов",
        "disp_title": "Настройки дисплея", "lbl_mon": "Монитор:", "lbl_res": "Разрешение:", 
        "lbl_hz": "Герцовка:", "chk_stretch": "Растягивать изображение (4:3 на весь экран)", "btn_apply_disp": "Применить настройки экрана",
        "preset_list": ["По умолчанию", "Теплый Уют", "Холодный Лед", "Контрастный Мир", "Ночная Мечта"],
        "theme_names": {
            "Просто темная": "Просто темная",
            "Просто светлая": "Просто светлая",
            "Пурпурный Закат": "Пурпурный Закат",
            "Солнечный Янтарь": "Солнечный Янтарь"
        },
        "params": {
            "brightness": "Яркость", "contrast": "Контраст", "exposure": "Экспозиция", "gamma": "Гамма",
            "shadows": "Тени", "midtones": "Ср. тона", "highlights": "Света",
            "saturation": "Насыщенность", "vibrance": "Сочность", "hue": "Оттенок", "temperature": "Температура", "tint": "Тон",
            "redGain": "Красный", "greenGain": "Зеленый", "blueGain": "Синий"
        }
    },
    "Español": {
        "side_title": "Configuración", "theme": "Esquema de colores:", "preset": "Perfil de imagen:",
        "lang": "Idioma:", "autostart": "Cargar shader al inicio", 
        "hotkey": "Atajo de Shader:", "hotkey_res": "Atajo de Resolución:",
        "btn_en": "Activar", "btn_dis": "Desactivar", "btn_res": "Restablecer",
        "lum": "Luminancia", "chrom": "Crominancia",
        "tone": "Tono", "band": "3-Bandas", "color": "Color", "gain": "Ganancia por canal",
        "disp_title": "Ajustes de Pantalla", "lbl_mon": "Monitor:", "lbl_res": "Resolución:", 
        "lbl_hz": "Refresco (Hz):", "chk_stretch": "Estirar relación de aspecto 4:3", "btn_apply_disp": "Aplicar cambios de pantalla",
        "preset_list": ["Por defecto", "Confort Cálido", "Hielo Frío", "Mundo de Contraste", "Sueño Nocturno"],
        "theme_names": {
            "Просто темная": "Simplemente Oscuro",
            "Просто светлая": "Simplemente Claro",
            "Пурпурный Закат": "Ocaso Púrpura",
            "Солнечный Янтарь": "Ámbar Soleado"
        },
        "params": {
            "brightness": "Brillo", "contrast": "Contraste", "exposure": "Exposición", "gamma": "Gamma",
            "shadows": "Sombras", "midtones": "Medios tonos", "highlights": "Luces",
            "saturation": "Saturación", "vibrance": "Intensidad", "hue": "Matiz", "temperature": "Temperatura", "tint": "Tinte",
            "redGain": "Rojo", "greenGain": "Verde", "blueGain": "Azul"
        }
    }
}

class ModernSlider(QWidget):
    def __init__(self, param_name, current_val, callback):
        super().__init__()
        self.param_name = param_name
        self.min_val, self.max_val = SLIDER_RANGES[param_name]
        self.callback = callback

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)

        self.label = QLabel("")
        self.label.setMinimumWidth(100)
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 200)
        self.slider.valueChanged.connect(self._value_changed)
        layout.addWidget(self.slider)

        self.val_label = QLabel(f"{current_val:.2f}")
        self.val_label.setMinimumWidth(40)
        self.val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.val_label)

        self.set_ui_value(current_val)
        self.setLayout(layout)

    def _value_changed(self, raw_val):
        float_val = self.min_val + (raw_val / 200.0) * (self.max_val - self.min_val)
        self.val_label.setText(f"{float_val:.2f}")
        self.callback(self.param_name, float_val)

    def set_ui_value(self, float_val):
        self.slider.blockSignals(True)
        pos = int(((float_val - self.min_val) / (self.max_val - self.min_val)) * 200)
        self.slider.setValue(pos)
        self.val_label.setText(f"{float_val:.2f}")
        self.slider.blockSignals(False)

    def update_text(self, text):
        self.label.setText(text)


class HyprTuneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HyprTune - Screen Calibration")
        self.setMinimumSize(980, 720)
        
        self.current_settings = shader_utils.load_shader_settings()
        self.app_config = shader_utils.load_app_config()
        self.sliders = {}
        self.splash_active = True
        self.block_preset_signal = False
        self.block_theme_signal = False
        
        self.setup_main_ui()
        self.apply_theme(self.app_config.get("theme", "Просто темная"))
        self.apply_language(self.app_config.get("language", "English"))
        self.setup_splash_screen()

    def setup_splash_screen(self):
        self.splash = QWidget(self)
        self.splash.setGeometry(self.rect())
        self.splash.setStyleSheet("background-color: #0f172a;")
        
        layout = QVBoxLayout(self.splash)
        logo_label = QLabel()
        pixmap = QPixmap("source/logo_hyprTune.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        self.splash.show()
        
        QTimer.singleShot(1000, self.fade_out_splash)

    def fade_out_splash(self):
        self.opacity_effect = QGraphicsOpacityEffect(self.splash)
        self.splash.setGraphicsEffect(self.opacity_effect)

        self.anim_splash = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_splash.setDuration(800)
        self.anim_splash.setStartValue(1.0)
        self.anim_splash.setEndValue(0.0)
        self.anim_splash.finished.connect(self._cleanup_splash)
        self.anim_splash.start()

    def _cleanup_splash(self):
        if hasattr(self, 'splash') and self.splash:
            self.splash.deleteLater()
            self.splash = None
        self.splash_active = False
        if self.app_config.get("autostart", False):
            self.dispatch_shader()

    def setup_main_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setMaximumWidth(0)
        
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(15, 20, 15, 20)
        side_layout.setSpacing(12)

        self.lbl_side_title = QLabel()
        self.lbl_side_title.setObjectName("SectionHeader")
        side_layout.addWidget(self.lbl_side_title)

        self.lbl_lang = QLabel()
        side_layout.addWidget(self.lbl_lang)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["English", "Русский", "Español"])
        self.combo_lang.setCurrentText(self.app_config.get("language", "English"))
        self.combo_lang.currentTextChanged.connect(self.change_language)
        side_layout.addWidget(self.combo_lang)

        self.lbl_theme = QLabel()
        side_layout.addWidget(self.lbl_theme)
        self.combo_themes = QComboBox()
        self.combo_themes.currentIndexChanged.connect(self.change_theme_by_index)
        side_layout.addWidget(self.combo_themes)

        self.lbl_preset = QLabel()
        side_layout.addWidget(self.lbl_preset)
        self.combo_presets = QComboBox()
        self.combo_presets.currentIndexChanged.connect(self.apply_preset_by_index)
        side_layout.addWidget(self.combo_presets)

        side_layout.addWidget(QFrame())

        self.chk_autostart = QCheckBox()
        self.chk_autostart.setChecked(self.app_config.get("autostart", False))
        self.chk_autostart.toggled.connect(self.save_configs)
        side_layout.addWidget(self.chk_autostart)

        self.lbl_hotkey = QLabel()
        side_layout.addWidget(self.lbl_hotkey)
        self.txt_hotkey = QLineEdit()
        self.txt_hotkey.setText(self.app_config.get("hotkey", "SUPER, X"))
        self.txt_hotkey.textChanged.connect(self.save_configs)
        side_layout.addWidget(self.txt_hotkey)

        self.lbl_res_hotkey = QLabel()
        side_layout.addWidget(self.lbl_res_hotkey)
        self.txt_res_hotkey = QLineEdit()
        self.txt_res_hotkey.setText(self.app_config.get("res_hotkey", "SUPER, F12"))
        self.txt_res_hotkey.textChanged.connect(self.save_configs)
        side_layout.addWidget(self.txt_res_hotkey)

        side_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        content_pane = QWidget()
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)

        top_bar = QHBoxLayout()
        self.btn_burger = QPushButton("☰")
        self.btn_burger.setObjectName("BurgerBtn")
        self.btn_burger.setFixedSize(36, 36)
        self.btn_burger.clicked.connect(self.toggle_sidebar)
        top_bar.addWidget(self.btn_burger)

        lbl_title = QLabel("HyprTune")
        lbl_title.setObjectName("Title")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch()

        self.btn_en = QPushButton()
        self.btn_en.clicked.connect(self.dispatch_shader)
        top_bar.addWidget(self.btn_en)

        self.btn_dis = QPushButton()
        self.btn_dis.clicked.connect(self.disable_shader)
        top_bar.addWidget(self.btn_dis)

        self.btn_res = QPushButton()
        self.btn_res.clicked.connect(self.reset_parameters)
        top_bar.addWidget(self.btn_res)
        content_layout.addLayout(top_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)

        self.lbl_display_title = QLabel()
        self.lbl_display_title.setObjectName("SectionHeader")
        scroll_layout.addWidget(self.lbl_display_title)

        display_card = QFrame()
        display_card.setObjectName("Card")
        display_inner = QVBoxLayout(display_card)
        display_inner.setSpacing(10)

        disp_selectors = QHBoxLayout()
        
        vbox_mon = QVBoxLayout()
        self.lbl_mon = QLabel()
        self.combo_monitors = QComboBox()
        vbox_mon.addWidget(self.lbl_mon)
        vbox_mon.addWidget(self.combo_monitors)
        disp_selectors.addLayout(vbox_mon)

        vbox_res = QVBoxLayout()
        self.lbl_res = QLabel()
        self.combo_resolutions = QComboBox()
        self.combo_resolutions.setEditable(True) 
        self.combo_resolutions.addItems([
            "Native", "3440x1440", "2560x1440", "1920x1080", "1440x1080", "1280x1024", 
            "1280x960", "1280x720", "1440x1440", "1024x768", "1080x1080", "800x600"
        ])
        vbox_res.addWidget(self.lbl_res)
        vbox_res.addWidget(self.combo_resolutions)
        disp_selectors.addLayout(vbox_res)

        vbox_hz = QVBoxLayout()
        self.lbl_hz = QLabel()
        self.combo_hz = QComboBox()
        self.combo_hz.setEditable(True) 
        self.combo_hz.addItems(["Auto", "60", "75", "120", "144", "165", "240", "360"])
        vbox_hz.addWidget(self.lbl_hz)
        vbox_hz.addWidget(self.combo_hz)
        disp_selectors.addLayout(vbox_hz)

        display_inner.addLayout(disp_selectors)

        disp_bottom = QHBoxLayout()
        self.chk_stretch = QCheckBox()
        self.chk_stretch.setChecked(self.app_config.get("stretch_4_3", True))
        disp_bottom.addWidget(self.chk_stretch)
        disp_bottom.addStretch()
        
        self.btn_apply_display = QPushButton()
        self.btn_apply_display.clicked.connect(self.commit_display_changes)
        disp_bottom.addWidget(self.btn_apply_display)
        display_inner.addLayout(disp_bottom)
        
        scroll_layout.addWidget(display_card)

        self.refresh_monitor_list()

        self.lbl_lum_title = QLabel()
        self.lbl_lum_title.setObjectName("SectionHeader")
        scroll_layout.addWidget(self.lbl_lum_title)

        lum_container = QHBoxLayout()
        
        tone_card = QFrame()
        tone_card.setObjectName("Card")
        tone_layout = QVBoxLayout(tone_card)
        self.lbl_tone = QLabel()
        tone_layout.addWidget(self.lbl_tone)
        for name in ["brightness", "contrast", "exposure", "gamma"]:
            sl = ModernSlider(name, self.current_settings[name], self.update_parameter)
            self.sliders[name] = sl
            tone_layout.addWidget(sl)
        lum_container.addWidget(tone_card)

        band_card = QFrame()
        band_card.setObjectName("Card")
        band_layout = QVBoxLayout(band_card)
        self.lbl_3band = QLabel()
        band_layout.addWidget(self.lbl_3band)
        for name in ["shadows", "midtones", "highlights"]:
            sl = ModernSlider(name, self.current_settings[name], self.update_parameter)
            self.sliders[name] = sl
            band_layout.addWidget(sl)
        lum_container.addWidget(band_card)
        scroll_layout.addLayout(lum_container)

        self.lbl_chrom_title = QLabel()
        self.lbl_chrom_title.setObjectName("SectionHeader")
        scroll_layout.addWidget(self.lbl_chrom_title)

        chrom_container = QHBoxLayout()

        color_card = QFrame()
        color_card.setObjectName("Card")
        color_layout = QVBoxLayout(color_card)
        self.lbl_color = QLabel()
        color_layout.addWidget(self.lbl_color)
        for name in ["saturation", "vibrance", "hue", "temperature", "tint"]:
            sl = ModernSlider(name, self.current_settings[name], self.update_parameter)
            self.sliders[name] = sl
            color_layout.addWidget(sl)
        chrom_container.addWidget(color_card)

        gain_card = QFrame()
        gain_card.setObjectName("Card")
        gain_layout = QVBoxLayout(gain_card)
        self.lbl_gain = QLabel()
        gain_layout.addWidget(self.lbl_gain)
        for name in ["redGain", "greenGain", "blueGain"]:
            sl = ModernSlider(name, self.current_settings[name], self.update_parameter)
            self.sliders[name] = sl
            gain_layout.addWidget(sl)
        chrom_container.addWidget(gain_card)
        scroll_layout.addLayout(chrom_container)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        content_layout.addWidget(scroll_area)
        main_layout.addWidget(content_pane, stretch=1)

    def refresh_monitor_list(self):
        self.combo_monitors.clear()
        monitors = shader_utils.load_monitors()
        if monitors:
            for m in monitors:
                name = m.get("name", "Unknown")
                self.combo_monitors.addItem(name, name)
            saved_mon = self.app_config.get("monitor", "")
            idx = self.combo_monitors.findData(saved_mon)
            if idx >= 0:
                self.combo_monitors.setCurrentIndex(idx)
        else:
            self.combo_monitors.addItem("Auto", "Auto")

        res_idx = self.combo_resolutions.findText(self.app_config.get("resolution", "Native"))
        if res_idx >= 0: self.combo_resolutions.setCurrentIndex(res_idx)
        else: self.combo_resolutions.setCurrentText(self.app_config.get("resolution", "Native"))
        
        hz_idx = self.combo_hz.findText(self.app_config.get("refresh_rate", "Auto"))
        if hz_idx >= 0: self.combo_hz.setCurrentIndex(hz_idx)
        else: self.combo_hz.setCurrentText(self.app_config.get("refresh_rate", "Auto"))

    def commit_display_changes(self):
        mon = self.combo_monitors.currentData() or "Auto"
        res = self.combo_resolutions.currentText()
        hz = self.combo_hz.currentText()
        stretch = self.chk_stretch.isChecked()

        self.app_config["monitor"] = mon
        self.app_config["resolution"] = res
        self.app_config["refresh_rate"] = hz
        self.app_config["stretch_4_3"] = stretch
        shader_utils.save_app_config(self.app_config)

        if mon != "Auto":
            shader_utils.apply_display_settings(mon, res, hz, stretch)

    def toggle_sidebar(self):
        width = self.sidebar.width()
        target = 290 if width == 0 else 0
        
        self.anim_side = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim_side.setDuration(350)
        self.anim_side.setStartValue(width)
        self.anim_side.setEndValue(target)
        self.anim_side.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_side.start()

    def change_language(self, lang_name):
        self.app_config["language"] = lang_name
        self.save_configs()
        self.apply_language(lang_name)

    def apply_language(self, lang_name):
        t = UI_TEXTS.get(lang_name, UI_TEXTS["English"])
        
        self.lbl_side_title.setText(t["side_title"])
        self.lbl_theme.setText(t["theme"])
        self.lbl_preset.setText(t["preset"])
        self.lbl_lang.setText(t["lang"])
        self.chk_autostart.setText(t["autostart"])
        self.lbl_hotkey.setText(t.get("hotkey", "Shader Hotkey:"))
        self.lbl_res_hotkey.setText(t.get("hotkey_res", "Resolution Hotkey:"))
        
        self.btn_en.setText(t["btn_en"])
        self.btn_dis.setText(t["btn_dis"])
        self.btn_res.setText(t["btn_res"])
        
        self.lbl_lum_title.setText(t["lum"])
        self.lbl_chrom_title.setText(t["chrom"])
        self.lbl_tone.setText(t["tone"])
        self.lbl_3band.setText(t["band"])
        self.lbl_color.setText(t["color"])
        self.lbl_gain.setText(t["gain"])

        self.lbl_display_title.setText(t["disp_title"])
        self.lbl_mon.setText(t["lbl_mon"])
        self.lbl_res.setText(t["lbl_res"])
        self.lbl_hz.setText(t["lbl_hz"])
        self.chk_stretch.setText(t["chk_stretch"])
        self.btn_apply_display.setText(t["btn_apply_disp"])
        
        for name, slider in self.sliders.items():
            slider.update_text(t["params"][name])

        self.block_preset_signal = True
        saved_preset_key = self.app_config.get("preset", "По умолчанию")
        self.combo_presets.clear()
        
        preset_keys = list(presets.PRESETS.keys())
        preset_displays = t.get("preset_list", preset_keys)
        
        for i, key in enumerate(preset_keys):
            display_text = preset_displays[i] if i < len(preset_displays) else key
            self.combo_presets.addItem(display_text, key)
            
        index = self.combo_presets.findData(saved_preset_key)
        self.combo_presets.setCurrentIndex(max(0, index))
        self.block_preset_signal = False

        self.block_theme_signal = True
        saved_theme_key = self.app_config.get("theme", "Просто темная")
        self.combo_themes.clear()
        
        theme_keys = list(themes.THEMES.keys())
        theme_dict = t.get("theme_names", {})
        
        for key in theme_keys:
            display_text = theme_dict.get(key, key)
            self.combo_themes.addItem(display_text, key)
            
        idx = self.combo_themes.findData(saved_theme_key)
        self.combo_themes.setCurrentIndex(max(0, idx))
        self.block_theme_signal = False

    def update_parameter(self, name, value):
        self.current_settings[name] = value
        shader_utils.save_shader_settings(self.current_settings)
        self.dispatch_shader()

    def reset_parameters(self):
        for name, default_val in shader_utils.DEFAULT_SETTINGS.items():
            self.current_settings[name] = default_val
            if name in self.sliders:
                self.sliders[name].set_ui_value(default_val)
        shader_utils.save_shader_settings(self.current_settings)
        self.dispatch_shader()

    def apply_preset_by_index(self, index):
        if getattr(self, 'block_preset_signal', False) or index < 0:
            return
        
        preset_key = self.combo_presets.itemData(index)
        
        self.app_config["preset"] = preset_key
        shader_utils.save_app_config(self.app_config)
        
        preset_values = presets.PRESETS.get(preset_key, {})
        for name, val in preset_values.items():
            self.current_settings[name] = val
            if name in self.sliders:
                self.sliders[name].set_ui_value(val)
        shader_utils.save_shader_settings(self.current_settings)
        self.dispatch_shader()

    def change_theme_by_index(self, index):
        if getattr(self, 'block_theme_signal', False) or index < 0:
            return
            
        theme_key = self.combo_themes.itemData(index)
        self.app_config["theme"] = theme_key
        self.save_configs()
        self.apply_theme(theme_key)

    def apply_theme(self, theme_name):
        if theme_name in themes.THEMES:
            qss = themes.BASE_STYLE + themes.THEMES[theme_name]
            self.setStyleSheet(qss)

    def save_configs(self):
        self.app_config["autostart"] = self.chk_autostart.isChecked()
        hotkey_shader = self.txt_hotkey.text()
        hotkey_res = self.txt_res_hotkey.text()
        self.app_config["hotkey"] = hotkey_shader
        self.app_config["res_hotkey"] = hotkey_res
        shader_utils.save_app_config(self.app_config)
        shader_utils.update_hyprland_shortcut(hotkey_shader, hotkey_res)

    def dispatch_shader(self):
        if shader_utils.SHADER_PATH.exists():
            subprocess.run(["hyprctl", "keyword", "decoration:screen_shader", str(shader_utils.SHADER_PATH)], capture_output=True)

    def disable_shader(self):
        subprocess.run(["hyprctl", "keyword", "decoration:screen_shader", "[[EMPTY]]"], capture_output=True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if getattr(self, 'splash_active', False) and hasattr(self, 'splash') and self.splash:
            try:
                self.splash.setGeometry(self.rect())
            except RuntimeError:
                self.splash = None

if __name__ == "__main__":
    os.environ["QT_QPA_PLATFORM"] = "wayland"
    app = QApplication(sys.argv)
    win = HyprTuneApp()
    win.show()
    sys.exit(app.exec())