from django import forms
from .models import Customer, Akun, Sepeda, Pemeliharaan, Stasiun, Peminjaman
from django.utils import timezone

class CustomerRegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['nama_customer', 'telepon_customer', 'alamat_customer']

    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class SepedaForm(forms.ModelForm):
    class Meta:
        model = Sepeda
        fields = ['id_sepeda', 'tipe_sepeda', 'merk_sepeda', 'harga_sewa', 'status_sepeda']
        widgets = {
            'id_sepeda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Sepeda'}),
            'tipe_sepeda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipe Sepeda'}),
            'merk_sepeda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Merk Sepeda'}),
            'harga_sewa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Harga Sewa'}),
            'status_sepeda': forms.Select(attrs={'class': 'form-control'}),
        }

class PemeliharaanForm(forms.ModelForm):
    class Meta:
        model = Pemeliharaan
        fields = ['sepeda', 'admin', 'status_pemeliharaan', 'tanggal_pemeliharaan']
        widgets = {
            'sepeda': forms.Select(attrs={'class': 'form-control'}),
            'admin': forms.Select(attrs={'class': 'form-control'}),
            'status_pemeliharaan': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_pemeliharaan': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class StasiunForm(forms.ModelForm):
    class Meta:
        model = Stasiun
        fields = ['id_stasiun', 'nama_stasiun', 'alamat_stasiun']

class PeminjamanForm(forms.ModelForm):
    class Meta:
        model = Peminjaman
        fields = ['tanggal_peminjaman', 'lama_peminjaman']
        widgets = {
            'tanggal_peminjaman': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'lama_peminjaman': forms.TextInput(attrs={
                'placeholder': 'Masukkan durasi (HH:MM:SS)',
                'class': 'form-control'
            }),
        }
