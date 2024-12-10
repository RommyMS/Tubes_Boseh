from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Menghubungkan aplikasi 'users'
    path('', lambda request: redirect('login')),  # Redirect root URL ke halaman login
]
