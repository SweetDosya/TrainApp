import json

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

from libs.other.info_more import IMT_INFO, BRM_INFO
from db.user_db import CONFIG_FILE_USER

Builder.load_file('libs/screens_kivy/info.kv')


class InfoScreen(Screen):
    def on_pre_enter(self, *args):
        with open(CONFIG_FILE_USER, 'r') as file:
            user_config = json.load(file)
        user_id = user_config.get('user_id')
        if user_id:
            app = MDApp.get_running_app()
            user_data = app.user_db.get_user_data()
            if user_data:
                self.calculate_imt(user_data)
                self.calculate_brm(user_data)

    def calculate_imt(self, user_data):
        weight = user_data.get('weight', 0)
        height_cm = user_data.get('height', 0)
        height_m = height_cm / 100
        imt = weight / (height_m ** 2)
        self.ids.imt_value.text = f"{imt:.1f}"
        self.update_imt_category(imt)

    def update_imt_category(self, imt):
        if imt < 18.5:
            category = "Недостатня вага"
            color = (1, 1, 0, 1)  # Yellow
        elif 18.5 <= imt < 25:
            category = "Норма"
            color = (0, 1, 0, 1)  # Green
        elif 25 <= imt < 30:
            category = "Надмірна вага"
            color = (1, 0.65, 0, 1)  # Orange
        elif 30 <= imt < 34.9:
            category = "Ожиріння I ступеню"
            color = (1, 0, 0, 1)  # Red
        elif 35 <= imt < 39.9:
            category = "Ожиріння II ступеню"
            color = (1, 0, 0.5, 1)  # Dark Red
        else:
            category = "Ожиріння III ступеню"
            color = (0.5, 0, 0, 1)  # Darker Red
        self.ids.imt_category.text = category
        self.ids.imt_value.color = color
        self.ids.imt_category.color = color

    def calculate_brm(self, user_data):
        weight = user_data.get('weight')
        height_cm = user_data.get('height')
        age = user_data.get('age')
        sex = user_data.get('sex')

        if sex == 'Чоловік':
            brm = 88.362 + (13.397 * weight) + (4.799 * height_cm) - (5.677 * age)
        else:
            brm = 447.593 + (9.247 * weight) + (3.098 * height_cm) - (4.330 * age)

        self.ids.brm_value.text = f"{brm:.0f} ккал"

    def show_imt_info(self):
        self.dialog = MDDialog(
            title="ІМТ",
            text=IMT_INFO,
            buttons=[
                MDRaisedButton(
                    text="ЗАКРИТИ",
                    on_release=self.close_dialog
                ),
            ],
        )
        self.dialog.open()

    def show_brm_info(self):
        self.dialog = MDDialog(
            title="БРМ",
            text=BRM_INFO,
            buttons=[
                MDRaisedButton(
                    text="ЗАКРИТИ",
                    on_release=self.close_dialog
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()
