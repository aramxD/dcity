

#birthday = models.DateField(null=False, blank=False,)
#phone_number = models.CharField(max_length=11, null=False, blank=False, unique=True)


class Cupon(models.Model):
    number = models.IntegerField(verbose_name="#", default=1)
    titulo = models.CharField(max_length=30, verbose_name="titulo cupon")
    descripcion = models.CharField(max_length=80, verbose_name="descripcion cupon", blank=True)
    restaurant = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name="restaurante")

    def __str__(self):
        return self.titulo

class Descuentos(models.Model):
    cupon = models.ForeignKey(Cupon, on_delete=models.CASCADE, verbose_name="Cupon")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    cupon_used = models.IntegerField(default=0, verbose_name="se uso?")
    
    
    def __str__(self):
        return self.cupon.titulo

    def descuento_lugar(self):
        return self.cupon.restaurant.title




class Place(models.Model):
#    def get_absolute_url(self):
#        return reverse('places:place-detail', kwargs={
#            'state':self.state,
#            'slug':self.slug
#        } ) 


#    def get_absolute_crud(self):
#        return reverse('places:place-crud', kwargs={
#            'state':self.state,
#            'slug':self.slug
#        } ) 