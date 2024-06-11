import json
import os

from kivy.uix.screenmanager import FadeTransition, NoTransition

CONFIG_FILE = "configs/theme_config.json"


class AppTheme:
    def switch_theme(self) -> None:
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.primary_palette = "Orange"
            self.theme_cls.theme_style = "Dark"
            self.nav_exrcs_manager.transition = FadeTransition(duration=0.1)
            self.nav_bottom_bar_manager.transition = FadeTransition(duration=0.1)
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Green"
            self.nav_exrcs_manager.transition = NoTransition()
            self.nav_bottom_bar_manager.transition = NoTransition()
        self.save_theme()

    def save_theme(self) -> None:
        theme_settings = {
            "theme_style": self.theme_cls.theme_style,
            "primary_palette": self.theme_cls.primary_palette,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(theme_settings, f)

    def load_theme(self) -> None:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                theme_settings = json.load(f)
                self.theme_cls.theme_style = theme_settings.get("theme_style", "Light")
                self.theme_cls.primary_palette = theme_settings.get("primary_palette", "Green")
        else:
            # Set default theme settings if config file does not exist
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Green"
