from django.contrib import admin
from .models import ParentProfile, Child, DrivingSlot, Unavailability, Holiday

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_driver')
    list_editable = ('is_driver',)

admin.site.register(Child)
admin.site.register(DrivingSlot)
admin.site.register(Unavailability)
admin.site.register(Holiday)