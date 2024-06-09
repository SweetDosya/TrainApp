from db import db
import os
import json

CONFIG_FILE_USER = "user_id.json"

USER_DEFAULT_DATA = {
    'name': "Daniel",
    'sec_name': "Yeromenko",
    'sex': "male",
    'age': 23,
    'height': 166,
    'weight': 72
}


class UserDB:
    def __init__(self):
        self.user_id = self.__get_user_id()
        self.db = db

    def __get_user_id(self):
        # Check if user ID file exists
        if os.path.exists(CONFIG_FILE_USER):
            with open(CONFIG_FILE_USER, 'r') as file:
                user_id = json.load(file).get('user_id', False)
                if user_id:
                    doc_ref = db.collection("users").document(user_id)
                    if doc_ref.get().exists:
                        return user_id
                return user_id

    def get_exist_user(self):
        if self.user_id:
            # Check if the user document exists in the database
            doc_ref = db.collection("users").document(self.user_id)
            if doc_ref.get().exists:
                return doc_ref
        return False

    @staticmethod
    def _create_user(data):
        doc_ref = db.collection("users").document()
        doc_ref.set(data)
        print(doc_ref.id)
        # Save the new user ID to the file
        with open(CONFIG_FILE_USER, 'w') as file:
            json.dump({'user_id': doc_ref.id}, file)
        print(doc_ref.id)
        return doc_ref

    def get_user_data(self):
        doc_ref = db.collection("users").document(self.user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print("No such document!")
            return None

    def create_custom_user(self, data):
        self._create_user(data)

    def create_default_user(self):
        self._create_user(USER_DEFAULT_DATA)

    def get_workout_calendar(self, day):
        user_ref = self.get_exist_user()
        return user_ref.collection('workout_calendar').document(day).get()

    def get_workout_programs(self):
        user_ref = self.get_exist_user()
        return user_ref.collection('workout_programs').get()

    def create_workout_program(self, program_data):
        user_ref = self.get_exist_user()
        program_ref = user_ref.collection('workout_programs').document()
        program_ref.set(program_data)
        return program_ref

    def update_workout_calendar(self, day, program_refs):
        user_ref = self.get_exist_user()
        calendar_ref = user_ref.collection('workout_calendar').document(day)
        calendar_ref.set({'programs': program_refs})
