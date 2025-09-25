from django.contrib import admin
from .models import ParentProfile, Child, DrivingSlot, Unavailability, Holiday

admin.site.register(ParentProfile)
admin.site.register(Child)
admin.site.register(DrivingSlot)
admin.site.register(Unavailability)
admin.site.register(Holiday)