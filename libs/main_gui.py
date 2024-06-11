from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window

from libs.general.app_theme import AppTheme
from db.user_db import UserDB
import locale

Builder.load_file("libs/main.kv")
Window.size = (500, 600)
locale.setlocale(locale.LC_TIME, "uk_UA")


class MainAppScreenManager(ScreenManager):

    def get_top_app_bar(self):
        return self.ids.main_menu.ids.top_bar


class TrainApp(MDApp, AppTheme):
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nav_bottom_bar_manager = None
        self.nav_exrcs_manager = None
        self.user_db = UserDB()

    def build(self) -> ObjectProperty:
        self.load_theme()
        self.manager = MainAppScreenManager()
        user_doc = self.user_db.get_exist_user()
        if user_doc:
            self.manager.current = "main_app_menu"
        return self.manager
