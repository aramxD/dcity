from django.forms import ModelForm
from .models import *


class  PlaceForm(ModelForm): 
    class Meta:
        model = Place
        fields = '__all__'
        exclude = ('timestamp',)

class  ProductForm(ModelForm): 
    class Meta:
        model = ServiceMenu
        fields = '__all__'

class  CuponForm(ModelForm): 
    class Meta:
        model = Cupon
        fields = '__all__'

