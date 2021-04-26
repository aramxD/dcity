from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from .forms import CreateUserForm
from django.conf import settings
from .models import *
from django.http import HttpResponseRedirect
from datetime import datetime


#def get_user_membership(request):
#    user_membership_qs = UserMembership.objects.filter(user=request.user)
#    if user_membership_qs.exists():
#        return user_membership_qs.first()
#    return None
#
#def get_user_subscription(request):
#    user_subscription_qs = Subscription.objects.filter(user_membership = get_user_membership(request))
#    if user_subscription_qs.:
#        user_subscription = user_subscription_qs.first()
#        return user_subscription
#    return None
#
#def create_subscription(request, subscription_id):
#    current_membership = get_user_membership(request)
#    sub, created = Subscription.objects.get_or_create(user_membership=current_membership)
#    sub.stripe_subscription_id = subscription_id
#    sub.active = True
#    sub.save()


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
					return redirect('checkout')
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

@login_required
def checkout(request):
    try:
        if request.user.customer.membership:
            return redirect('settings')
    except Customer.DoesNotExist:
        pass
    
    coupons = { 'aramxd':35, 'israel':45, 'elsa':10, 'admin':100 }
    


    if request.method == 'POST':
        stripe_customer = stripe.Customer.create(
            email = request.user.email,
            source=request.POST['stripeToken'])
        plan = 'price_1HsZziKozHJOGShQIxUenrNF'
        
        if request.POST['coupon'] in coupons:
            percentage = coupons[request.POST['coupon'].lower()]
            try:
                coupon = stripe.Coupon.create(duration='once', id=request.POST['coupon'].lower(),
                percent_off=percentage)
            except:
                pass
            subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[{'plan':plan }],
                coupon=request.POST['coupon'].lower()
                )
        else:
            subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[{'plan':plan},
                
                ])

        customer = Customer()
        customer.user = request.user
        customer.stripeid = stripe_customer.id
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = subscription.id
        customer.save()


        return redirect('discounts_places')
    else:
        plan = 'monthly'
        coupon = 'none'
        price = 199
        og_dollar = 1.99
        coupon_dollar = 0
        final_dollar = 1.99
        if request.method == 'GET' and 'plan' in request.GET:
            if request.GET['plan'] == 'yearly':
                plan = 'yearly'
                coupon = 'none'
                price = 1000
                og_dollar = 10
                final_dollar = 10



        if request.method == 'GET' and 'coupon' in request.GET:
            if request.GET['coupon'].lower() in coupons:
                coupon = request.GET['coupon'].lower()
                percentage = coupons[coupon]
                coupon_price = int((percentage/100) * price)
                price = price - coupon_price
                coupon_dollar = str(coupon_price)[:-2] + '.' + str(coupon_price)[-2:] 
                final_dollar = str(price)[:-2] + '.' + str(price)[-2:] 

        context={
        'plan':plan,
        'coupon':coupon,
        'price':price,
        'og_dollar':og_dollar,
        'coupon_dollar':coupon_dollar,
        'final_dollar':final_dollar,
        
    }
        return render(request, 'users/checkout.html', context)

@login_required
def settings(request):
    membership = False
    cancel_at_period_end = False

    fecha_inscripcion = None
    fecha_renovacion= None

    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True
        subscription.save()
        request.user.customer.save()
    else:
        try:
            renovation_date = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id).current_period_end
            subscription_date = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id).current_period_start
            fecha_inscripcion = datetime.fromtimestamp(subscription_date)
            fecha_renovacion= datetime.fromtimestamp(renovation_date)
            
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        
        except Customer.DoesNotExist:
            membership = False

    context={
            'membership':membership,

            'cancel_at_period_end':cancel_at_period_end,
            'fecha_renovacion':fecha_renovacion,
            'fecha_inscripcion':fecha_inscripcion
        }

    return render(request, 'users/settings.html', context)

#4242424242424242
#def payment_stripe(request):
#    current_membership = get_user_membership(request)
#    id_membership = current_membership.stripe_customer_id #ID MEMBRECIA 
#    id_product = current_membership.membership.stripe_plan_id #ID PRODUCTO
#    user_membership = current_membership.membership  #Nombre de la membrecia
#    username_membership = current_membership.user   #usuario 
#    price_membership = current_membership.membership.price #Precio de la membrecia

#    publishKey = settings.STRIPE_PUBLISHABLE_KEY
#    stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY
#    if request.method == "POST":
#        try:
#            stripeToken = request.POST['stripeToken']
#            stripe.Subscription.create(
#            customer=id_membership,
#            items=[{"price": id_product,},],
#            default_source=stripeToken,
#            )
            
#            print('Your payment was completed!') 
#            return redirect('discounts_places')

#        except stripe.error.CardError as e:
# Since it's a decline, stripe.error.CardError will be caught

#            print('Status is: %s' % e.http_status)
#            print('Code is: %s' % e.code)
#            # param is '' in this case
#            print('Param is: %s' % e.param)
#            print('Message is: %s' % e.user_message)
#        except stripe.error.RateLimitError as e:
##            # Too many requests made to the API too quickly
#           pass
#        except stripe.error.InvalidRequestError as e:
#            # Invalid parameters were supplied to Stripe's API
#            pass
#        except stripe.error.AuthenticationError as e:
#            # Authentication with Stripe's API failed
#            # (maybe you changed API keys recently)
#            pass
#        except stripe.error.APIConnectionError as e:
#            # Network communication with Stripe failed
#            pass
#        except stripe.error.StripeError as e:
#            # Display a very generic error to the user, and maybe send
#            # yourself an email
#            pass
#        except Exception as e:
#            # Something else happened, completely unrelated to Stripe
#            pass       
#    context = {
#        'id_product':id_product,
#        'id_membership':id_membership,
#        'user_membership': user_membership, 
#        'username_membership': username_membership,
#        'price_membership': price_membership,
#        'publishKey': publishKey,
#    }
#    return render(request, 'users/payment_stripe.html', context)