from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, FadeTransition, NoTransition
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDRoundFlatIconButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.list import OneLineListItem, MDList, TwoLineIconListItem, IconRightWidget, TwoLineRightIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from user_db import UserDB, CONFIG_FILE_USER
from info_more import IMT_INFO, BRM_INFO
from datetime import datetime, timedelta
import locale
import re
import os
import json

Builder.load_file("main.kv")
Window.size = (500, 600)
CONFIG_FILE = "theme_config.json"
locale.setlocale(locale.LC_TIME, "uk_UA")


class ScreenNewUser(Screen):
    pass


class NavigationScreenManager(ScreenManager):
    screen_stack = []

    def push(self, screen_name):
        if screen_name not in self.screen_stack:
            self.screen_stack.append(self.current)
            self.current = screen_name

    def pop(self):
        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.current = screen_name


class NavigationExerciseManager(NavigationScreenManager):
    date_obj = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transition = FadeTransition(duration=0.1)

    def start_workout(self):
        day_of_week = str(self.date_obj.weekday())
        user_db = MDApp.get_running_app().user_db
        workout_calendar = user_db.get_workout_calendar(day_of_week)
        if workout_calendar.exists:
            program_refs = workout_calendar.to_dict().get('programs', [])
            if program_refs:
                self.show_workout_programs(program_refs)
                return
        self.show_no_programs()

    def show_workout_programs(self, program_refs):
        self.current = 'workout_programs'
        programs_screen = self.get_screen('workout_programs')
        programs_screen.ids.programs_list.clear_widgets()

        for ref in program_refs:
            program_data = ref.get().to_dict()
            programs_screen.ids.programs_list.add_widget(
                OneLineListItem(text=program_data['name'])
            )

    def show_no_programs(self):
        self.current = 'program_not_found'

    def create_program(self):
        self.current = 'create_program'


class MainExerciseScreen(Screen):
    current_date = StringProperty("")

    def on_pre_enter(self, *args):
        self.manager.date_obj = datetime.now()
        self.update_date()

    def update_date(self):
        self.current_date = self.manager.date_obj.strftime("%a, %d %b")

    def next_day(self):
        self.manager.date_obj += timedelta(days=1)
        self.update_date()

    def prev_day(self):
        self.manager.date_obj -= timedelta(days=1)
        self.update_date()



class CreateProgramScreen(Screen):
    group_muscles_images = (
        'd_abs.png', 'd_arms.png',
        'd_back.png', 'd_chest.png',
        'd_legs.png', 'd_shoulders.png'
    )

    def on_pre_enter(self):
        Clock.schedule_once(self.load_muscle_groups, 0.1)

    def load_muscle_groups(self, *args):
        self.ids.muscle_groups_list.clear_widgets()
        db = MDApp.get_running_app().user_db.db
        muscle_groups = db.collection('exercises').stream()
        for img_num, group in enumerate(muscle_groups):
            group_data = group.to_dict()
            exercises_list = self.load_exercises_for_group(group.id)
            group_item = MDExpansionPanel(
                icon=f'source/images/{self.group_muscles_images[img_num]}',
                content=exercises_list,
                panel_cls=MDExpansionPanelOneLine(text=group_data['name'])
            )
            self.ids.muscle_groups_list.add_widget(group_item)

    def load_exercises_for_group(self, group_id):
        exercises_list = MDList()
        db = MDApp.get_running_app().user_db.db
        exercises = db.collection('exercises').document(group_id).collection('exercises').stream()
        for exercise in exercises:
            exercise_data = exercise.to_dict()
            exercise_item = TwoLineRightIconListItem(
                text=exercise_data['name'],
                secondary_text=f"Рівень складності - {exercise_data['difficulty']}"
            )
            exercise_item.selected = False  # Додаємо прапор вибору
            exercise_item.bind(on_release=lambda item=exercise_item: self.toggle_selection(item))
            icon = IconRightWidget(icon="information-outline")
            icon.on_release = lambda x=exercise_data: self.show_exercise_description(x)
            exercise_item.add_widget(icon)
            exercises_list.add_widget(exercise_item)
        return exercises_list

    def toggle_selection(self, exercise_item):
        app = MDApp.get_running_app()
        if exercise_item.selected:
            exercise_item.bg_color = app.theme_cls.bg_normal
        else:
            primary_color = app.theme_cls.primary_color
            exercise_item.bg_color = (primary_color[0], primary_color[1], primary_color[2], 0.1)
        exercise_item.selected = not exercise_item.selected

    def show_exercise_description(self, exercise_data):
        # Логіка для показу опису вправи
        pass

    def save_program(self):
        program_name = self.ids.program_name.text
        if not program_name:
            return  # Handle the error, maybe show a message to the user
        user_db = MDApp.get_running_app().user_db.db

        # Створюємо програму тренувань
        program_data = {
            'name': program_name,
            'exercises': []
        }
        for item in self.ids.muscle_groups_list.children:
            if isinstance(item, OneLineListItem):
                checkbox = item.ids.checkbox
                if checkbox.active:
                    program_data['exercises'].append(item.text)

        # Зберігаємо програму в колекцію програм тренувань
        program_ref = user_db.create_workout_program(program_data)

        # Оновлюємо календар тренувань
        day_of_week = str(self.manager.date_obj.weekday())
        workout_calendar = user_db.get_workout_calendar(day_of_week)
        if workout_calendar.exists:
            program_refs = workout_calendar.to_dict().get('programs', [])
        else:
            program_refs = []
        program_refs.append(program_ref)
        user_db.update_workout_calendar(day_of_week, program_refs)

        # Перемикаємося назад на головний екран тренувань
        self.manager.current = 'main_exercise'


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
        sex = user_data.get('gender')

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


class MainAppPage(Screen):
    bar_name = StringProperty("Головна")

    def change_tab_screen(self, widget, name):
        self.change_main_screen_app_bar(name)
        self.bar_name = widget.text
        self.ids.main_nav_bar_manager.current = name

    def change_main_screen_app_bar(self, screen):
        top_bar = self.ids.top_bar
        if screen == "main_exercise":
            top_bar.left_action_items = []
        else:
            top_bar.left_action_items = [["arrow-left", lambda x: self.to_main_screen()]]

    def to_main_screen(self):
        self.ids.bottom_nav.switch_tab('main_tab')
        self.bar_name = "Головна"
        self.change_main_screen_app_bar("main_exercise")
        self.ids.main_nav_bar_manager.current = "main_exercise"


class MainAppNavigationBarManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transition = FadeTransition(duration=0.1)


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
                self.sex_field = user_data.get('gender', '')
                self.age_field = str(user_data.get('age', ''))
                self.height_field = str(user_data.get('height', ''))
                self.weight_field = str(user_data.get('weight', ''))


class MDTextFieldLetters(MDTextField):
    pat = re.compile('[^a-zA-Zа-яА-ЯіІїЇєЄґҐ]')

    def insert_filter(self, substring, from_undo=False):
        if len(self.text) >= self.max_text_length:
            return
        s = re.sub(self.pat, '', substring)
        return s


class CustomUser(Screen):
    pass


class PhysicalUserData(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = None
        self.age = None
        self.user_height = None
        self.user_weight = None

    def validate_fields(self):
        return self.age and self.user_height and self.user_weight

    def update_name(self, widget):
        self.age = widget.text

    def update_sec_name(self, widget):
        self.user_height = widget.text

    def update_gender(self, widget):
        self.user_weight = widget.text

    def open_menu(self, widget, rng):
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_widget_value(widget, x),
            } for i in range(*rng)]
        self.menu = MDDropdownMenu(
            caller=widget,
            items=menu_items,
            position="bottom",
        )
        self.menu.open()

    def set_widget_value(self, widget, value):
        widget.text = value
        self.menu.dismiss()

    def process_data(self):
        if self.validate_fields():
            app = MDApp.get_running_app()
            app.user_data.update({
                'age': int(self.age),
                'height': int(self.user_height),
                'weight': int(self.user_weight)
            })
            app.manager.transition = FadeTransition()
            app.manager.current = "main_app_menu"
            app.user_db.create_custom_user(app.user_data)
        else:
            print("pass")


class GeneralUserData(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gender = None
        self.first_name = None
        self.sec_name = None

    def validate_fields(self):
        return self.first_name and self.sec_name and self.gender

    def update_name(self, widget):
        self.first_name = widget.text

    def update_sec_name(self, widget):
        self.sec_name = widget.text

    def update_gender(self, gender):
        self.gender = gender

    def process_data(self):
        if self.validate_fields():
            app = MDApp.get_running_app()
            app.user_data = {
                'name': self.first_name,
                'sec_name': self.sec_name,
                'gender': self.gender
            }
            self.manager.next_page()
        else:
            pass


class SexUserToggleButton(MDRoundFlatIconButton, MDToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = self.theme_cls.primary_color


class NewUserScreenManager(ScreenManager):

    def next_page(self):
        self.current = "physic_data"
        self.transition = SlideTransition(direction="left")


class MainAppScreenManager(ScreenManager):
    pass


class TrainApp(MDApp):
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_db = UserDB()

    def build(self) -> ObjectProperty:
        self.load_theme()
        self.manager = MainAppScreenManager()
        user_doc = self.user_db.get_exist_user()
        if user_doc:
            self.manager.current = "main_app_menu"
        return self.manager

    def switch_theme(self) -> None:
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.primary_palette = "Orange"
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Green"
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

    def on_start(self):
        pass
