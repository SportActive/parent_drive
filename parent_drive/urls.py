from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This handles built-in auth URLs like /accounts/login/, /accounts/logout/
    path('accounts/', include('django.contrib.auth.urls')),
    
    # This includes all of our app's URLs, including signup
    path('', include('scheduler.urls')),
]