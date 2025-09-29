from django.contrib import admin
from .models import ParentProfile, Child, DrivingSlot, Unavailability, Holiday

# Цей клас робить адмін-панель для профілів більш інформативною
@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_driver', 'color')
    list_editable = ('color',) # Дозволяє редагувати колір прямо зі списку
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

# Реєстрація інших моделей (якщо потрібно)
admin.site.register(Child)
admin.site.register(DrivingSlot)
admin.site.register(Unavailability)
admin.site.register(Holiday)