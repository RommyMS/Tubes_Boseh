from django.contrib import admin
from .models import Akun, Customer, Admin

@admin.register(Akun)
class AkunAdmin(admin.ModelAdmin):
    list_display = ('username', 'role')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id_akun', 'nama_customer', 'telepon_customer', 'alamat_customer')

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('id_akun', 'nama_admin', 'telepon_admin')
