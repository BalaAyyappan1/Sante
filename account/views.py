from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from django.contrib import messages
from .forms import LoginForm, PersonalInfoForm, GoalInfoForm, BodyInfoForm
from django.contrib.auth.decorators import login_required
from time import timezone
from pymongo import MongoClient
from .models import UserProfile
from .models import FoodIntake
import datetime
from json import JSONDecodeError
from django.utils import timezone
import requests
from .forms import FoodIntakeForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

client = MongoClient(
    "mongodb+srv://balaayyappan:wC9N7XS89z6IYU8X@cluster0.lgg50gu.mongodb.net/test"
)
db = client["Nutrition-Assistant"]
users_collection = db["users"]

# result = users_collection.find_one({})
# print(result)



# render home page
def home(request):
    return render(request, "home.html")


# render login 
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, users_collection=users_collection)
        if form.is_valid():
            # Log the user in and redirect to the success.html
            request.session["username"] = form.cleaned_data["username"]
            messages.success(request, "You have been logged in")
            return redirect("success")
    else:
        form = LoginForm(users_collection=users_collection)

    return render(request, "login.html", {"form": form})


# render register 
def register(request):
    if request.method == "POST":
        personal_form = PersonalInfoForm(request.POST)
        body_form = BodyInfoForm(request.POST)
        goal_form = GoalInfoForm(request.POST)

        if personal_form.is_valid() and body_form.is_valid() and goal_form.is_valid():
            # Check if username is already registered

            username = personal_form.cleaned_data["username"]

            if UserProfile.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")

                return redirect("register")

            # Save user information to UserProfile model
            user_profile = UserProfile(
                full_name=personal_form.cleaned_data["full_name"],
                username=username,
                password=personal_form.cleaned_data["password1"],
                age=body_form.cleaned_data["age"],
                height=body_form.cleaned_data["height"],
                current_weight=body_form.cleaned_data["current_weight"],
                goal_weight=goal_form.cleaned_data["goal_weight"],
                activity=goal_form.cleaned_data["activity"],
                gender=goal_form.cleaned_data["gender"],
                goal=goal_form.cleaned_data["goal"],
            )

            user_profile.save()
            user_profile.calculate_bmi()
            user_profile.calculate_bmr()

            # Save user information to MongoDB
            user_data = {
                "full_name": personal_form.cleaned_data["full_name"],
                "username": username,
                "password": personal_form.cleaned_data["password1"],
                "age": body_form.cleaned_data["age"],
                "height": body_form.cleaned_data["height"],
                "current_weight": body_form.cleaned_data["current_weight"],
                "goal_weight": goal_form.cleaned_data["goal_weight"],
                "activity": goal_form.cleaned_data["activity"],
                "gender": goal_form.cleaned_data["gender"],
                "goal": goal_form.cleaned_data["goal"],
            }
            # insert the data into mongodb 
            users_collection.insert_one(user_data)

            # Redirect to success page
            return redirect("login")

    else:
        personal_form = PersonalInfoForm()
        body_form = BodyInfoForm()
        goal_form = GoalInfoForm()

    return render(
        request,
        "register.html",
        {
            "personal_form": personal_form,
            "body_form": body_form,
            "goal_form": goal_form,
        },
    )


def success(request):
    # Get user's username, weight and height from the database
    username = request.session["username"]
    user_profile = UserProfile.objects.get(username=username)
    weight = user_profile.current_weight
    height = user_profile.height

    # Calculate BMI and show they are in which state
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        bmi_message = "underweight"
    elif bmi < 25:
        bmi_message = "normal"
    elif bmi < 30:
        bmi_message = "overweight"
    else:
        bmi_message = "obese"

    # Calculate BMR
    user_profile.calculate_bmr()
    bmr = user_profile.bmr
    #rounded_num = (bmr // 1000) * 1000

    # Get user's full name from the database
    full_name = user_profile.full_name

    context = {
        "bmi": round(bmi, 2),
        "bmr": round(bmr),
        "full_name": full_name,
        "bmi_message": bmi_message.capitalize(),
    }
    return render(request, "success.html", context)


def add_food_intake(request):
    if request.method == "POST":
        # Checking the user's is logged in
        username = request.session.get("username")
        if not username:
            messages.error(request, "User is not logged in")
            return redirect("login_view")
        try:
            user_profile = UserProfile.objects.get(username=username)

        except UserProfile.DoesNotExist:
            messages.error(request, "User profile does not exist")

            return redirect("add_food_intake")

        form = FoodIntakeForm(request.POST)
        if form.is_valid():
            # Create a new FoodIntake instance
            food_intake = FoodIntake(
                user_profile=user_profile,
                food_name=form.cleaned_data["food_name"],
                serving_size=form.cleaned_data["serving_size"],
                date=timezone.now().date(),
            )

            # Fetch nutritionix api data for the food from the API
            food_name = form.cleaned_data["food_name"]
            api_url = f"https://api.nutritionix.com/v1_1/search/{food_name}/?results=0:1&fields=item_name,brand_name,item_id,nf_calories,nf_protein,nf_total_carbohydrate,nf_total_fat&appId={settings.NUTRITIONIX_APP_ID}&appKey={settings.NUTRITIONIX_APP_KEY}"
            response = requests.get(api_url)

            data = response.json()["hits"][0]["fields"]
            response.raise_for_status()
    
            

            # Add nutrition data to the FoodIntake instance and save it to the database sqllite
            food_intake.calories = data["nf_calories"] * (
                form.cleaned_data["serving_size"] / data["nf_serving_size_qty"]
            )
            food_intake.protein = data["nf_protein"] * (
                form.cleaned_data["serving_size"] / data["nf_serving_size_qty"]
            )
            food_intake.carbohydrates = data["nf_total_carbohydrate"] * (
                form.cleaned_data["serving_size"] / data["nf_serving_size_qty"]
            )
            food_intake.fat = data["nf_total_fat"] * (
                form.cleaned_data["serving_size"] / data["nf_serving_size_qty"]
            )
            food_intake.save()

            # Redirect to the success page with the updated list of food intakes
            messages.success(
                request,
                f"{food_name} added to food intake (Calories: {food_intake.calories}, Protein: {food_intake.protein}, Carbohydrates: {food_intake.carbohydrates}, Fat: {food_intake.fat})",
            )
            return redirect("add_food_intake")

    else:
        form = FoodIntakeForm()
        # Checking the user's is logged in
        username = request.session.get("username")
        if not username:
            messages.error(request, "User is not logged in")
            return redirect("login_view")
        try:
            user_profile = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            messages.error(request, "User profile does not exist")
            return redirect("add_food_intake")

        user_profile.calculate_bmr()
        bmr = user_profile.bmr
        full_name = user_profile.full_name

        date_str = request.GET.get("date")
        if date_str:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format")
                return redirect("add_food_intake")
        else:
            # Set date_str to today's date if it is not already set
            date_obj = timezone.now().date()
            date_str = date_obj.strftime("%Y-%m-%d")

        food_intakes = FoodIntake.objects.filter(
            user_profile__username=request.session.get("username"), date=date_obj
        ).order_by("-date")

        total_calories = 0
        for food_intake in food_intakes:
            total_calories += food_intake.calories

        return render(
            request,
            "add_food_intake.html",
            {
                "form": form,
                "full_name": full_name,
                "food_intakes": food_intakes,
                "bmr": round(bmr),
                "total_calories": round(total_calories),
            },
        )


def delete_food_intake(request, food_intake_id):
    if request.method == "POST":
        try:
            food_intake = FoodIntake.objects.get(
                id=food_intake_id,
                user_profile__username=request.session.get("username"),
            )
            food_intake.delete()
            messages.success(request, "Food intake entry deleted successfully")
        except FoodIntake.DoesNotExist:
            messages.error(request, "Food intake entry does not exist")
    return redirect("add_food_intake")


# Render logout
def logout(request):
    auth_logout(request)
    return redirect("home")
