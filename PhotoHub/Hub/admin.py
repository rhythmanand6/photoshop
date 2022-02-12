from django.contrib import admin
from .models import Customer, Photographer, Appointment

# Register your models here.
admin.site.register(Customer)
admin.site.register(Photographer)
admin.site.register(Appointment)

