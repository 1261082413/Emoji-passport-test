from django import forms
import re


EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001F1E0-\U0001F1FF"
    "]"
)


def count_emojis(text):
    return len(EMOJI_RE.findall(text or ""))


def char_count(text):
    return len(list(text or ""))


class TextRegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter text password"})
    )

    def clean_password(self):
        pw = self.cleaned_data.get("password", "").strip()
        if not pw:
            raise forms.ValidationError("Password cannot be empty.")
        if char_count(pw) > 8:
            raise forms.ValidationError("Password must be 8 characters or fewer.")
        return pw


class EmojiRegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Choose at least 3 emojis"})
    )

    def clean_password(self):
        pw = self.cleaned_data.get("password", "").strip()
        if not pw:
            raise forms.ValidationError("Password cannot be empty.")
        if char_count(pw) > 8:
            raise forms.ValidationError("Password must be 8 characters or fewer.")

        emoji_count = count_emojis(pw)
        if emoji_count < 3:
            raise forms.ValidationError("Emoji password must contain at least 3 emojis.")
        return pw


class MixRegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Use text + at least 3 emojis"})
    )

    def clean_password(self):
        pw = self.cleaned_data.get("password", "").strip()
        if not pw:
            raise forms.ValidationError("Password cannot be empty.")
        if char_count(pw) > 8:
            raise forms.ValidationError("Password must be 8 characters or fewer.")

        emoji_count = count_emojis(pw)
        if emoji_count < 3:
            raise forms.ValidationError("Mix password must contain at least 3 emojis.")

        non_emoji_text = EMOJI_RE.sub("", pw).strip()
        if not non_emoji_text:
            raise forms.ValidationError("Mix password must also include text or numbers.")
        return pw


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password_type = forms.ChoiceField(
        choices=[
            ("text", "Text password"),
            ("emoji", "Emoji password"),
            ("mix", "Mix password"),
        ],
        widget=forms.RadioSelect,
        initial="text",
    )
    password = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter password"})
    )

    def clean_password(self):
        pw = self.cleaned_data.get("password", "")
        if char_count(pw) > 8:
            raise forms.ValidationError("Password must be 8 characters or fewer.")
        return pw


class SurveyForm(forms.Form):
    CHOICES = [
        ("text", "Text password"),
        ("emoji", "Emoji password"),
        ("mix", "Mix password"),
        ("all", "All"),
    ]

    used_password_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    easier_to_remember = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    faster_to_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    real_life_choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Any other comments?"}),
    )