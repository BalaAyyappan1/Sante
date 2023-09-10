from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import login_view



urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    # path('register/step2/', views.step2, name='step2'),
    # path('register/step3/', views.step3, name='step3'),
    path('login/', views.login_view, name='login'),
    path('success/', views.success, name='success'),
    path('add_food_intake/', views.add_food_intake, name='add_food_intake'),
    path('logout/', views.logout, name='logout'),
    # path('food_intake_list/', views.food_intake_list, name='food_intake_list'),
    path('delete_food_intake/<int:food_intake_id>/', views.delete_food_intake, name='delete_food_intake'),

     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
