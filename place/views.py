from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.views.generic import (TemplateView)
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from membership.models import *
from .models import *
from .forms import PlaceForm, ProductForm, CuponForm
import stripe
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Create your views here.

class error_404(TemplateView):
    template_name = "error_404.html"

def homepage(request): #FREE ACCESS
    places_home = Place.objects.all().order_by('?')[:4]
    context = {
        'places_home': places_home,  
        
    }
    return render(request, 'homepage.html', context)

def discounts_places(request): #FREE ACCESS
    places = Place.objects.filter(featured=True).order_by('?')
    maps_qs = PlaceMap.objects.all()
    maps_key = settings.MAPS_API_KEY 
    places_sample = Place.objects.all().filter(featured=True).filter(sample__isnull=False).order_by('?')[:5] 
    context = {
        'places': places,  
        'maps_qs' : maps_qs,
        'maps_key': maps_key, 
        'places_sample': places_sample,
    }
    return render(request, 'discounts_places.html', context)


def contact(request):
    if request.method == 'POST':
        asunto = "Prospecto " + request.POST["txtName"] + " discounts.city (Formulario web)"
        mensaje = "La persona " + request.POST["txtName"] + ". Esta interesada, contactar al telefono: " + request.POST["txtPhoneNumber"] + " o Email: " + request.POST["txtEmail"] 
        email_from = settings.EMAIL_HOST_USER
        email_to = ["info.discount.citys@gmail.com"]
        sendgrid_apikey = settings.SENDGRID_API_KEY
        #send_mail(asunto, mensaje, email_from, email_to, fail_silently=False)

        message = Mail(email_from, email_to, asunto,
            html_content="<strong>La persona </strong>" + request.POST["txtName"] + ". Esta interesada, contactar al telefono: " + request.POST["txtPhoneNumber"] + " o Email: " + request.POST["txtEmail"] )
        try:
            sg = SendGridAPIClient(sendgrid_apikey)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

        
        return redirect('discounts_places') 
    return redirect('discounts_places')


@login_required
@staff_member_required
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


@login_required
@staff_member_required
def list_place(request): #LIST PLACE ADMIN ONLY
    places = Place.objects.all().order_by('id')
    context = {
        'places': places
    }
    return render (request, 'place/list_place.html', context)


@login_required
@staff_member_required
def delete_place(request, place_pk): #DELETE PLACE ADMIN ONLY
    place = get_object_or_404(Place, pk=place_pk)
    if request.method == 'POST':
        place.delete()
        return redirect('list_place')


@login_required
@staff_member_required
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
    
    
    if request.user.is_anonymous:
        print('usuario no registrado')
        context = { 
            'place': place, 
            'food_services': fs_list,
            'cat_menu': fs_category,
            }
        return render(request, 'place/place.html', context)

    try:
        if request.user.customer.membership:
            membership = request.user.customer.membership
            qs_descuentos = CuponBlock.objects.filter(user=request.user)
            cupon_descuento = qs_descuentos.filter(cupon__restaurant=lugar)
            context = { 
            'membership':membership,
            'place': place, 
            'food_services': fs_list,
            'cat_menu': fs_category,
            'cat_menu_detail': fs_category_detail,
            'cupones': cupon_descuento,
            }
            return render(request, 'place/place.html', context)
    except Customer.DoesNotExist:
            print('usuario no registrado')
            context = { 
            'place': place, 
            'food_services': fs_list,
            'cat_menu': fs_category,
            }
            return render(request, 'place/place.html', context)


@login_required
@staff_member_required
def add_product(request, state, slug, ):
    place = get_object_or_404(Place, slug=slug) # Trae la informacion del restaurante
    queryset = ServiceMenu.objects.all() # Trae la informacion del menu
    lugar = place.id
    fs_list = queryset.filter(place =lugar).order_by('product_orden')
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


@login_required
@staff_member_required
def edit_product(request, state, slug, product_pk):
    place = get_object_or_404(Place, slug=slug) # Trae la informacion del restaurante
    product = get_object_or_404(ServiceMenu, pk=product_pk)
    queryset = ServiceMenu.objects.all() # Trae la informacion del menu
    lugar = place.id
    fs_list = queryset.filter(place =lugar).order_by('product_orden')
    fs_category = queryset.filter(place =lugar).values_list('product_category', flat=True).distinct()    
    request.GET
    if request.method == 'GET':
        form = ProductForm(instance=product)
        context = {
            'place': place, 
            'form': form,
            'obj_list': fs_list,
            'obj_category': fs_category,}
        return render(request, 'place/add_product.html', context)
    else:
        try:
            form = ProductForm(request.POST, request.FILES, instance=product)
            
            form.save()
            context = {'place': place, 
                    'form': ProductForm(),
                    'obj_list': fs_list,
                    'obj_category': fs_category,}
            return render(request, 'place/add_product.html', context)
        except ValueError:
            context = {'form': form, 'error':'La informacion esta mal' }
            return render(request, 'place/add_place.html', context)


@login_required
@staff_member_required
def delete_product(request,  product_pk):
    product = get_object_or_404(ServiceMenu, pk=product_pk)
    if request.method == 'POST':
        
        product.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@staff_member_required
def add_cupon(request, state, slug,):
    place = get_object_or_404(Place, slug=slug) # Trae la informacion del restaurante
    coupon_queryset = Cupon.objects.all() # Trae la informacion del menu
    lugar = place.id
    coupon_list = coupon_queryset.filter(restaurant =lugar).order_by('id')
        

    if request.method == 'GET':
        context = {
            'form' : CuponForm(),
            'place': place, 
            'obj_list': coupon_list,
            }
        return render(request, 'place/add_cupon.html', context )
    else:
        form = CuponForm(request.POST)
        newcupon = form.save(commit=False)
        newcupon.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@staff_member_required
def delete_cupon(request,  cupon_pk):
    coupon = get_object_or_404(Cupon, pk=cupon_pk)
    if request.method == 'POST':
        
        coupon.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def get_discount(request,  cupon_pk):
    cupon_descuento = get_object_or_404(CuponBlock, pk=cupon_pk)
    if request.method == 'POST':
        if cupon_descuento.used == 0:
            cupon_descuento.used = cupon_descuento.used + 1
            cupon_descuento.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#Esta vista es para experimentar 
@login_required
@staff_member_required
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

@login_required
@staff_member_required
@xframe_options_exempt
def maps(request):
    maps_qs = PlaceMap.objects.all()
    maps_key = settings.MAPS_API_KEY 
    
    context = {
        'maps_key': maps_key,
        'maps_qs' : maps_qs,
        }
    return render(request, 'place/maps.html', context )


@login_required
@staff_member_required
def dashboard(request):
    places = Place.objects.all().order_by('id')
    maps_qs = PlaceMap.objects.all()
    maps_key = settings.MAPS_API_KEY 
    places_sample = Place.objects.all().filter(sample__isnull=False).order_by('?')[:5] 
    context = {
        'places': places,  
        'maps_qs' : maps_qs,
        'maps_key': maps_key, 
        'places_sample': places_sample,
        }
    return render(request, 'dashboard/dashboard.html', context )


@login_required
@staff_member_required
@xframe_options_exempt
def dash_place_list(request):
    places = Place.objects.all().order_by('-id')
    context = {
        'places': places,  
        }
    return render(request, 'dashboard/dash-place-list.html', context )


@login_required
@staff_member_required
@xframe_options_exempt
def dash_user_list(request):
    users = User.objects.all().order_by('-id')
    
    cupones = CuponBlock.objects.filter(used=1)
    #user_cupones = cupones.filter(user=User)
    print(cupones.first)
    #print(user_cupones)
    context = {
        'users': users,
        #'user_cupones':user_cupones,  
        }
    return render(request, 'dashboard/dash-user-list.html', context )

