from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import * 
from membership import views

from django.contrib.auth import views as auth_views



urlpatterns = [
    
    #Auth
    
    path('signup/', views.signupuser, name="signupuser"),
    path('logout/', views.logoutuser, name="logoutuser"),
    path('login/', views.loginuser, name="loginuser"),
    path('checkout/', views.checkout, name="checkout"),
    #path('payment_stripe/', views.payment_stripe, name="payment_stripe"),
    path('settings', views.settings, name='settings'),
    
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="users/reset_password.html"), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="users/reset_password_sent.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/reset_password_form.html"), name='password_reset_confirm'),
    path('reset_password_complete_=D/', auth_views.PasswordResetCompleteView.as_view(template_name="users/reset_password_done.html"), name='password_reset_complete'),
]

