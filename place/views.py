from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import PlaceForm, ProductForm, CuponForm
from django.http import HttpResponseRedirect
from membership.models import *
# Create your views here.


def homepage(request): #FREE ACCESS
    places = Place.objects.all()
    context = {
        'places': places,   
    }
    return render(request, 'index.html', context)


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
    fs_category = queryset.filter(place =lugar).values_list('product_category', flat=True).distinct()
    qs_descuentos = CuponBlock.objects.filter(user=request.user)
    cupon_descuento = qs_descuentos.filter(cupon__restaurant=lugar)
    

    context = { 
        'place': place, 
        'food_services': fs_list,
        'cat_menu': fs_category,
        'cupones': cupon_descuento,
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