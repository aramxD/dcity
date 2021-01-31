from django.contrib import admin
from .models import *
# Register your models here.

class MembershipAdmin(admin.ModelAdmin):
    pass


class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'membership',  'stripe_customer_id', ) #visualizar columnas


class SubscriptionAdmin(admin.ModelAdmin):
    pass

class CuponBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cupon', 'used',  ) #visualizar columnas




admin.site.register(Membership, MembershipAdmin)
admin.site.register(UserMembership, UserMembershipAdmin)
admin.site.register(Subscription, SubscriptionAdmin) 
admin.site.register(CuponBlock, CuponBlockAdmin)

