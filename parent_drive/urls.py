# parent_drive/urls.py

from django.contrib import admin
from django.urls import path, include
from scheduler import views as scheduler_views # Імпортуємо views з додатку

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Явно вказуємо шлях до вашої кастомної сторінки реєстрації
    path('accounts/signup/', scheduler_views.signup_view, name='signup'),

    # 2. Підключаємо всі стандартні шляхи Django (вхід, вихід і т.д.)
    path('accounts/', include('django.contrib.auth.urls')),

    # 3. Підключаємо всі інші шляхи з вашого додатку (календар, кабінет і т.д.)
    path('', include('scheduler.urls')),
]