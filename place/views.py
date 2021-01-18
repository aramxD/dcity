from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import PlaceForm, ProductForm, CuponForm
from django.http import HttpResponseRedirect
from membership.models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
import stripe
# Create your views here.

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(user_membership = get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None


def homepage(request): #FREE ACCESS
    if request.user.is_authenticated: 
        current_membership = get_user_membership(request)
        user_membership = current_membership.membership
        user_subscription = get_user_subscription(request)
        select_membership = request.POST.get('membership_type')
        print(user_membership)
        print(user_subscription)
        print(select_membership)
    else: 
        user_membership = None
        user_subscription = None
        
    places = Place.objects.all()
    maps_qs = PlaceMap.objects.all()
    
    context = {
        'places': places,  
        'maps_qs' : maps_qs,
        'user_membership': user_membership, 
        'user_subscription': user_subscription,
    }
    return render(request, 'homepage.html', context)

def discounts_places(request): #FREE ACCESS
    places = Place.objects.all()
    maps_qs = PlaceMap.objects.all()
    maps_key = settings.MAPS_API_KEY 
    print(maps_key)
    context = {
        'places': places,  
        'maps_qs' : maps_qs,
        'maps_key': maps_key, 
    }
    return render(request, 'discounts_places.html', context)


def add_place(request): #ADD PLACE ADMIN ONLY
    if request.method == 'GET':
        context = {'form': PlaceForm() }
        return render(request, 'place/add_place.html', context)
    else:
        try:
            form = PlaceForm(request.POST, request.FILES)
            newplace = form.save(commit=False)
            newplace.save()
            return redirect('list_place')
        except ValueError:
            context = {'form': form, 'error':'La informacion esta mal' }
            return render(request, 'place/add_place.html', context)


def list_place(request): #LIST PLACE ADMIN ONLY
    places = Place.objects.all()
    context = {
        'places': places
    }
    return render (request, 'place/list_place.html', context)


def delete_place(request, place_pk): #DELETE PLACE ADMIN ONLY
    place = get_object_or_404(Place, pk=place_pk)
    if request.method == 'POST':
        place.delete()
        return redirect('list_place')


def view_place(request, place_pk): #CRUD PLACES ADMIN ONLY
    place = get_object_or_404(Place, pk=place_pk)
    if request.method == 'GET':
        form = PlaceForm(instance=place)
        
        context = {'place': place, 'form': form}
        return render(request, 'place/view_place.html', context)
    else:
        try:
            form = PlaceForm(request.POST, request.FILES, instance=place)
            
            form.save()
            return redirect('list_place')
        except ValueError:
            context = {'place': place, 'form': form, 'error':'La informacion esta mal' }
            return render(request, 'place/view_place.html', context)


def place_detail(request, state, slug): #FREE ACCESS
    place = get_object_or_404(Place, slug=slug)# Trae la informacion del restaurante
    queryset = ServiceMenu.objects.all() # Trae la informacion del menu
    lugar = place.id
    
    fs_list = queryset.filter(place =lugar)
    fs_category = queryset.filter(place =lugar).values_list('product_category', flat=True).order_by('product_orden').distinct()
    fs_category_detail = queryset.filter(place =lugar).distinct('product_category_detail')
    
    
    if request.user.is_authenticated:
        qs_descuentos = CuponBlock.objects.filter(user=request.user)
        cupon_descuento = qs_descuentos.filter(cupon__restaurant=lugar)
        context = { 
        'place': place, 
        'food_services': fs_list,
        'cat_menu': fs_category,
        'cat_menu_detail': fs_category_detail,
        'cupones': cupon_descuento,
        }
        return render(request, 'place/place.html', context)
    else:
        print('usuario no registrado')
        context = { 
            'place': place, 
            'food_services': fs_list,
            'cat_menu': fs_category,
            
            }
        return render(request, 'place/place.html', context)


def add_product(request, state, slug, ):
    place = get_object_or_404(Place, slug=slug) # Trae la informacion del restaurante
    queryset = ServiceMenu.objects.all() # Trae la informacion del menu
    lugar = place.id
    fs_list = queryset.filter(place =lugar).order_by('product_category')
    fs_category = queryset.filter(place =lugar).values_list('product_category', flat=True).distinct()    
    if request.method == 'GET':
        context = {
            'place': place, 
            'form': ProductForm(),
            'obj_list': fs_list,
            'obj_category': fs_category,}
        return render(request, 'place/add_product.html', context)
    else:
        try:
            form = ProductForm(request.POST, request.FILES)
            newproduct = form.save(commit=False)
            newproduct.save()
            context = {'place': place, 
                    'form': ProductForm(),
                    'obj_list': fs_list,
                    'obj_category': fs_category,}
            return render(request, 'place/add_product.html', context)
        except ValueError:
            context = {'form': form, 'error':'La informacion esta mal' }
            return render(request, 'place/add_place.html', context)


def add_cupon(request, state, slug,):
    place = get_object_or_404(Place, slug=slug) # Trae la informacion del restaurante
    if request.method == 'GET':
        context = {'form' : CuponForm()}
        return render(request, 'place/add_cupon.html', context )
    else:
        form = CuponForm(request.POST)
        newcupon = form.save(commit=False)
        newcupon.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_product(request,  product_pk):
    product = get_object_or_404(ServiceMenu, pk=product_pk)
    if request.method == 'POST':
        
        product.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_discount(request,  cupon_pk):
    cupon_descuento = get_object_or_404(CuponBlock, pk=cupon_pk)
    if request.method == 'POST':
        if cupon_descuento.used == 0:
            cupon_descuento.used = cupon_descuento.used + 1
            cupon_descuento.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_discount(request, state, slug,):
    place = get_object_or_404(Place, slug=slug) # Trae la informacion del restaurante
    if request.method == 'GET':
        context = {'form' : CuponForm()}
        return render(request, 'place/add_discount.html', context )
    else:
        form = CuponForm(request.POST)
        newcupon = form.save(commit=False)
        newcupon.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def maps(request):
    maps_qs = PlaceMap.objects.all()
    maps_key = settings.MAPS_API_KEY 
    
    context = {
        'maps_key': maps_key,
        'maps_qs' : maps_qs,
        }
    return render(request, 'place/maps.html', context )



def payment_stripe(request):
    current_membership = get_user_membership(request)
    id_membership = current_membership.stripe_customer_id
    id_product = current_membership.membership.stripe_plan_id
    user_membership = current_membership.membership
    username_membership = current_membership.user
    price_membership = current_membership.membership.price
    user_subscription = get_user_subscription(request)
    select_membership = request.POST.get('membership_type')


    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    
    if request.method == "POST":
        try:
            token = request.POST['stripeToken']
            stripe.Subscription.create(
                customer="id_membership",
                items=[
                    {"price": "id_product"},
                    ],
                    source=token
                    )
            print('Your payment was completed!') 

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught

            print('Status is: %s' % e.http_status)
            print('Code is: %s' % e.code)
            # param is '' in this case
            print('Param is: %s' % e.param)
            print('Message is: %s' % e.user_message)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            pass
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            pass
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            pass
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            pass
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            pass
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            pass
            
        
    context = {
        'id_product':id_product,
        'id_membership':id_membership,
        'user_membership': user_membership, 
        'username_membership': username_membership,
        'price_membership': price_membership,
        'user_subscription':user_subscription,
        'publishKey': publishKey,
    }
    return render(request, 'place/payment_stripe.html', context)
