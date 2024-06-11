from kivy.uix.screenmanager import Screen, FadeTransition, ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDRoundFlatIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder

Builder.load_file('libs/screens_kivy/new_user.kv')


class ScreenNewUser(Screen):
    pass


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

    def update_sex(self, widget):
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
        self.sex = None
        self.first_name = None
        self.sec_name = None

    def validate_fields(self):
        return self.first_name and self.sec_name and self.sex

    def update_name(self, widget):
        self.first_name = widget.text

    def update_sec_name(self, widget):
        self.sec_name = widget.text

    def update_sex(self, sex):
        self.sex = sex

    def process_data(self):
        if self.validate_fields():
            app = MDApp.get_running_app()
            app.user_data = {
                'name': self.first_name,
                'sec_name': self.sec_name,
                'sex': self.sex
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

