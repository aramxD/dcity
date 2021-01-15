from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from place.models import *

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

"""membership types"""
MEMBERSHIP_CHOICES = (
    ('Member', 'member'),
    ('Free', 'free'),
    ('admin', 'admin'),)

# Create your models here.
class Membership(models.Model):
    slug = models.SlugField()
    membership_type = models.CharField(
        choices=MEMBERSHIP_CHOICES, 
        default='Member', 
        max_length=30)
    price = models.DecimalField(max_digits=3, decimal_places=2, default=1.99)
    stripe_plan_id = models.CharField(max_length=40)

    def __str__(self):
        return self.membership_type


class UserMembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=40)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null= True)

    def __str__(self):
        return self.user.username

def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
    c = Membership.objects.filter( membership_type='Member')
    select_membership = c.first()
    if created:
        UserMembership.objects.get_or_create(user=instance)

    user_membership, created = UserMembership.objects.get_or_create(user=instance)

    if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
        new_customer_id = stripe.Customer.create(email=instance.email)
        user_membership.stripe_customer_id = new_customer_id['id']
        user_membership.membership = select_membership
        user_membership.save()
post_save.connect(post_save_usermembership_create, sender=settings.AUTH_USER_MODEL)


class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=40)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_membership.user.username


class CuponBlock(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    cupon = models.ForeignKey(Cupon, null=True, on_delete=models.CASCADE)
    used = models.IntegerField(default=0, verbose_name='Usado?')




def cuponblock_create_user(sender, instance, created, *args, **kwargs):
    
    c = Cupon.objects.all()
    #print(c)
    
    if created:
        for i in c:    
            print(i)
            new, created = CuponBlock.objects.get_or_create(user=instance, cupon=i)
post_save.connect(cuponblock_create_user, sender=settings.AUTH_USER_MODEL)

def cuponblock_create_cupon(sender, instance, created, *args, **kwargs):
    
    c = Cupon.objects.all()
    new = CuponBlock.objects.all()
    u = User.objects.all()
    if created:
        for i in u:    
            
            new, created = CuponBlock.objects.get_or_create(user=i, cupon=instance)

post_save.connect(cuponblock_create_cupon, sender=Cupon)


