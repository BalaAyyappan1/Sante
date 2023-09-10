from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import AuthenticationForm
import re
from .models import UserProfile


# Form for login username, password 
class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.users_collection = kwargs.pop("users_collection", None)
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "Username"})
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})
    # Validation 
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = self.users_collection.find_one(
            {"username": username, "password": password}
        )
        if not user:
            raise forms.ValidationError("Invalid username or password")


# Register PersonalInfo fullname, username, password1, password2 
class PersonalInfoForm(forms.Form):
    full_name = forms.CharField(label="What’s your first name?", max_length=100)
    username = forms.CharField(label="Username")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update({"placeholder": "Full Name"})
        self.fields["username"].widget.attrs.update({"placeholder": "username"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm Password"}
        )
    #validation 
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        if len(password1) < 4:
            raise forms.ValidationError("Password must be at least 4")
        if not re.search(r"\d", password1):
            raise forms.ValidationError("Password must contain at least one number")

        # password_validation.validate_password(password1)
        return cleaned_data


class BodyInfoForm(forms.Form):
    age = forms.IntegerField(
        label="Age", validators=[MaxValueValidator(150), MinValueValidator(1)]
    )
    height = forms.IntegerField(
        label="Height (cm)", validators=[MaxValueValidator(300), MinValueValidator(1)]
    )
    current_weight = forms.FloatField(
        label="Current Weight (kg)",
        validators=[MaxValueValidator(1000), MinValueValidator(1)],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["age"].widget.attrs.update({"placeholder": "Age"})
        self.fields["height"].widget.attrs.update({"placeholder": "Height"})
        self.fields["current_weight"].widget.attrs.update(
            {"placeholder": "Current Weight"}
        )


class ActivityChoices:
    SEDENTARY = 1.2
    LIGHTLY_ACTIVE = 1.375
    ACTIVE = 1.725
    VERY_ACTIVE = 1.9

    CHOICES = [
        (SEDENTARY, "Not Very Active"),
        (LIGHTLY_ACTIVE, "Lightly Active"),
        (ACTIVE, "Active"),
        (VERY_ACTIVE, "Very Active"),
    ]


class GoalInfoForm(forms.Form):
    goal_weight = forms.FloatField(
        label="Goal Weight (kg)",
        validators=[MaxValueValidator(1000), MinValueValidator(1)],
    )
    activity = forms.ChoiceField(
        choices=ActivityChoices.CHOICES, label="Activity Level"
    )
    gender = forms.ChoiceField(
        choices=[
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other"),
        ],
        label="Gender",
        widget=forms.RadioSelect(attrs={"class": "gender-radio"}),
    )
    goal = forms.ChoiceField(choices=UserProfile.GOAL_CHOICES, label="Goal")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["goal_weight"].widget.attrs.update({"placeholder": "Goal Weight"})

    def clean(self):
        cleaned_data = super().clean()
        goal = cleaned_data.get("goal", "M")
        cleaned_data["goal"] = {
            "L": "weight loss",
            "G": "weight gain",
            "M": "maintain weight",
        }[goal]
        return cleaned_data


class FoodIntakeForm(forms.Form):
    food_name = forms.CharField(max_length=255)
    serving_size = forms.FloatField(label="Serving Size")
