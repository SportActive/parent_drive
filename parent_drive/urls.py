from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', scheduler_views.signup_view, name='signup'),    
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('scheduler.urls')),
]