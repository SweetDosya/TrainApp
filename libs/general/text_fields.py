import re

from kivymd.uix.textfield import MDTextField


class MDTextFieldPattern(MDTextField):
    pat = None

    def insert_filter(self, substring, from_undo=False):
        if len(self.text) >= self.max_text_length:
            return
        s = re.sub(self.pat, '', substring)
        return s


class MDTextFieldOnlyLetters(MDTextFieldPattern):
    pat = re.compile('[^a-zA-Zа-яА-ЯіІїЇєЄґҐ]')


class MDTextFieldLettersNumsSpacing(MDTextFieldPattern):
    pat = re.compile('[^a-zA-Zа-яА-ЯіІїЇєЄґҐ0-9 ]')
