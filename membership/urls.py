from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import * 
from membership import views




urlpatterns = [
    
    #Auth
    
    path('signup/', views.signupuser, name="signupuser"),
    path('logout/', views.logoutuser, name="logoutuser"),
    path('login/', views.loginuser, name="loginuser"),
]