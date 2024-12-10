from django.urls import path
from . import views

urlpatterns = [
    # Customer Routes
    path('register/', views.register_customer, name='register_customer'),  # Halaman register untuk pelanggan
    path('login/', views.login, name='login'),  # Halaman login pelanggan/admin
    path('home-customer/', views.home_customer, name='home_customer'),
    path('pilih-sepeda/<str:id_sepeda>/', views.pilih_sepeda, name='pilih_sepeda'),
    path('proses-pembayaran/<int:id_peminjaman>/', views.proses_pembayaran, name='proses_pembayaran'),
    # Admin Routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Halaman dashboard admin

    # Logout Route
    path('logout/', views.logout, name='logout'),  # Logout (umum)
]
