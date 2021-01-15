from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from .forms import CreateUserForm
from .models import *
from django.http import HttpResponseRedirect






def signupuser(request):
	if request.user.is_authenticated:
		return redirect('discounts_places')
	else:
		if request.method == 'GET':
			return render(request, 'signupuser.html', {'form': CreateUserForm()})
		else:
			if request.POST['password1'] == request.POST['password2']:
				try:
					user = User.objects.create_user(request.POST['username'], first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'] , password=request.POST['password1'])
					#uso serializer (cliente-servidor)creacion de usuario con cupones existentes
					user.save()
					login(request, user)
					return redirect('discounts_places')
				except IntegrityError:
					return render(request, 'signupuser.html', {'form': CreateUserForm() ,'error': 'User has been taken'})
			else:
				return render(request, 'signupuser.html', {'form': CreateUserForm() ,'error': 'Password did not match'})

def logoutuser(request):
	if request.method == 'POST':
		logout(request)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def loginuser(request):
	if request.method == 'GET':
		return render(request, 'loginuser.html',  {'form': AuthenticationForm()})
	else:
		user = authenticate(request, username=request.POST['username'], password=request.POST['Password'])
		if user is None:
			return render(request, 'loginuser.html', {'form': AuthenticationForm() , 'error': 'User or password did not match'})
		else:
			login(request, user)
			return redirect('discounts_places')


