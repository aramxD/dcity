from django.contrib import admin
from .models import *
# Register your models here.


class InLineMenu(admin.TabularInline):
    pass

class PlaceTypeAdmin(admin.ModelAdmin):
    pass


class PlaceAdmin(admin.ModelAdmin):
    
    readonly_fields = ('timestamp', )
    list_display = ('title', 'state') #visualizar columnas
    ordering = ('-timestamp', ) #ordenar listas
    search_fields = ('title',)  #buscador

class ServiceMenuAdmin(admin.ModelAdmin):
    list_display = ('place', 'product_category', 'product_name') #visualizar columnas
    ordering = ('place', ) #ordenar listas
    search_fields = ('place', 'product_category', 'product_name',)  #buscador

class CuponAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'number', 'title', 'description',  ) #visualizar columnas
    list_editable = ('number', 'title', 'description',)
    ordering = ('restaurant','number', )


    

admin.site.register(PlaceType, PlaceTypeAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(ServiceMenu, ServiceMenuAdmin)
admin.site.register(Cupon, CuponAdmin)
