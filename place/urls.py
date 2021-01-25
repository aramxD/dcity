from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from place import views




urlpatterns = [
    
    #Auth
    path('', views.homepage, name="homepage"),
    path('discounts-places', views.discounts_places, name="discounts_places"),
    path('add-place/', views.add_place, name="add_place"),
    path('list-place/', views.list_place, name="list_place"),
    path('view_place/<int:place_pk>/', views.view_place, name="view_place"),
    path('delete_place/<int:place_pk>/delete', views.delete_place, name="delete_place"),
    path('<str:state>/<str:slug>/', views.place_detail, name='place_detail'),
    path('<str:state>/<str:slug>/add-product', views.add_product, name='add_product'),
    path('<str:state>/<str:slug>/<str:product_pk>/edit-product', views.edit_product, name='edit_product'),
    path('product/<int:product_pk>/delete', views.delete_product, name="delete_product"),
    path('get_discount/<int:cupon_pk>/discount', views.get_discount, name="get_discount"),
    path('<str:state>/<str:slug>/add-cupon', views.add_cupon, name='add_cupon'),
    path('<str:state>/<str:slug>/add-discount', views.add_discount, name='add_discount'),
    path('maps/', views.maps, name="maps"),
    path('contact/', views.contact, name="contact"),
    path('payment_stripe/', views.payment_stripe, name="payment_stripe"),

]