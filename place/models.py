from django.db import models

from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from membership.models import *



# Create your models here.

"""Place types"""
PLACE_TYPE = (
    ('Restaurant', 'restaurant'),
    ('Services', 'services'),
    ('Personal Care', 'personal care'),
    ('Markets', 'markets'),)

class PlaceType(models.Model):
    slug = models.CharField(max_length=30, verbose_name="slug para categorias")
    title = models.CharField(
        choices=PLACE_TYPE, 
        default='Restaurant', 
        max_length=30, 
        verbose_name='titulo')
    description = models.TextField(max_length=300, verbose_name="descripcion" )

    def __str__(self):
        return self.title


class Place(models.Model):
    slug = models.CharField(max_length=30, verbose_name="url del sitio")
    title = models.CharField(max_length=100, verbose_name="Nombre")
    logo = models.ImageField(verbose_name="logos", upload_to="logos", null=True, blank=True )
    sample = models.ImageField(verbose_name="Imagen Muestra", upload_to="samples", null=True, blank=True )
    horario = models.TextField(verbose_name="horario" , default="soy un horario", blank=True)
    location = models.TextField(verbose_name="Ubicacion de Lugar", default="soy un Mapa :D" , blank=True)
    phone_number = models.CharField(max_length=12, verbose_name="numero de telefono" , blank=True)
    city = models.CharField(max_length=30, verbose_name="Ciudad")
    state = models.CharField(max_length=30, verbose_name="Estado")
    place_type = models.ForeignKey(PlaceType, on_delete=models.CASCADE, verbose_name="Tipo de servicio")
    featured = models.BooleanField(default=True, verbose_name="Aparece en el landing>?")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('place_detail', kwargs={
        'state':self.state,
        'slug':self.slug
        } ) 


class PlaceMap(models.Model):
    place = models.ForeignKey(Place,  on_delete=models.CASCADE, verbose_name="Lugar")
    latitud = models.DecimalField(max_digits=15, decimal_places=9, verbose_name="Latitud" , blank=True)
    longitud = models.DecimalField(max_digits=15, decimal_places=9, verbose_name="Longitud" , blank=True)

    def __str__(self):
        return self.place.title

class Owner(models.Model):
    name_owner = models.CharField(max_length=30, verbose_name="nombre del responsable")
    phone_owner = models.IntegerField(verbose_name="telefono del responsable")
    email_owner = models.EmailField(max_length=30, verbose_name="email del responsable")
    place_owner = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name="Nombre del negocio")
    terms = models.BooleanField(default=False, verbose_name="Acepto terminos y condiciones")

    def __str__(self):
        return self.name_owner


#fs --> food / service
class ServiceMenu(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name="restaurante")
    product_category = models.CharField(max_length=30, verbose_name="Categoria food / service")
    product_category_detail = models.TextField(verbose_name="Detalles de categoria", null=True , blank=True)
    product_orden = models.IntegerField(default=1, verbose_name="Orden food / service")
    product_name = models.CharField(max_length=30, verbose_name="Nombre food / service")
    product_description = models.TextField(verbose_name="Descripcion food / service" , blank=True)
    product_image = models.ImageField(verbose_name="Imagen food / service", upload_to="place", null=True, blank=True )
    product_price = models.CharField(max_length=6, verbose_name="Precio food / service" , blank=True)

    def __str__(self):
        return self.product_name



class Cupon(models.Model):
    number = models.IntegerField(verbose_name="#", default=0)
    title = models.CharField(max_length=30, verbose_name="titulo cupon")
    description = models.CharField(max_length=80, verbose_name="descripcion cupon", blank=True)
    restaurant = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name="restaurante")

    def __str__(self):
        return self.title
















