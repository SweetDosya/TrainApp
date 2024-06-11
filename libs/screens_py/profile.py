import json

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

from db.user_db import CONFIG_FILE_USER

Builder.load_file('libs/screens_kivy/profile.kv')


class ProfileScreen(Screen):
    name_field = StringProperty()
    sec_name_field = StringProperty()
    sex_field = StringProperty()
    age_field = StringProperty()
    height_field = StringProperty()
    weight_field = StringProperty()

    def on_pre_enter(self):
        with open(CONFIG_FILE_USER, 'r') as file:
            user_config = json.load(file)
        user_id = user_config.get('user_id')
        if user_id:
            app = MDApp.get_running_app()
            user_data = app.user_db.get_user_data()
            if user_data:
                self.name_field = user_data.get('name', '')
                self.sec_name_field = user_data.get('sec_name', '')
                self.sex_field = user_data.get('sex', '')
                self.age_field = str(user_data.get('age', ''))
                self.height_field = str(user_data.get('height', ''))
                self.weight_field = str(user_data.get('weight', ''))
