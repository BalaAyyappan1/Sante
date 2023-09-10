from django.db import models
from decimal import Decimal
# Create your models here.
from django.db import models


class UserProfile(models.Model):
    GOAL_CHOICES = (
         ('L', 'Lose'),
        ('G', 'Gain'),
        ('M', 'Maintain'),
    )
    

    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=255)
    age = models.IntegerField()
    height = models.FloatField()
    current_weight = models.FloatField()
    goal = models.CharField(max_length=15, choices=GOAL_CHOICES, default='M')
    goal_weight = models.FloatField()
    activity = models.DecimalField(max_digits=4, decimal_places=2)
    gender = models.CharField(max_length=10)
    bmi = models.FloatField(null=True, blank=True)
    bmr = models.FloatField(null=True, blank=True)
    
    
    def __str__(self):
        return self.username

    def calculate_bmi(self):
        height_in_m = self.height / 100
        self.bmi = round(self.current_weight / (height_in_m ** 2), 2)

    def calculate_bmr(self):
        # print(f"current_weight={self.current_weight}")
        # print(f"height={self.height}")
        # print(f"age={self.age}")
        # print(f"gender={self.gender}")
        # print(f"activity={self.activity}")
        # print(f"goal={self.goal}")
        
        if self.gender == 'M':
            bmr = 10 * self.current_weight + 6.25 * self.height - 5 * self.age + 5
        elif self.gender == 'F':
            bmr = 10 * self.current_weight + 6.25 * self.height - 5 * self.age - 161
        else:
            bmr = 0
        bmr *= float(self.activity)
        
        # adjust BMR based on goal
        if self.goal == 'L':
            bmr -= float(Decimal('1000'))
        elif self.goal == 'G':
            bmr += float(Decimal('500'))
            
        self.bmr=bmr-100
        print(f"bmr after goal adjustment={bmr}")     
        return round(bmr)


class FoodIntake(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=255)
    serving_size = models.FloatField(default=0.0)
    calories = models.FloatField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()
    fat = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.food_name