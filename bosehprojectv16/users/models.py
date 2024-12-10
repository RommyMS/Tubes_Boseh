from django.db import models
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal

class Akun(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # Password terenkripsi
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Customer(models.Model):
    id_akun = models.OneToOneField(Akun, on_delete=models.CASCADE)
    nama_customer = models.CharField(max_length=100)
    telepon_customer = models.CharField(max_length=15)
    alamat_customer = models.TextField()

    def __str__(self):
        return self.nama_customer


class Admin(models.Model):
    id_akun = models.OneToOneField(Akun, on_delete=models.CASCADE)
    nama_admin = models.CharField(max_length=100)
    telepon_admin = models.CharField(max_length=15)

    def __str__(self):
        return self.nama_admin


from django.db import models

class Stasiun(models.Model):
    id_stasiun = models.CharField(max_length=20, primary_key=True)  # ID unik untuk stasiun
    nama_stasiun = models.CharField(max_length=100)  # Nama stasiun
    alamat_stasiun = models.TextField()  # Alamat stasiun
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu saat stasiun dibuat
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir pembaruan stasiun

    def __str__(self):
        return self.nama_stasiun

    class Meta:
        verbose_name = "Stasiun"
        verbose_name_plural = "Stasiun"
        ordering = ['nama_stasiun']  # Urutkan berdasarkan nama stasiun

class Sepeda(models.Model):
    STATUS_CHOICES = [
        ('tersedia', 'Tersedia'),
        ('dipinjam', 'Dipinjam'),
        ('pemeliharaan', 'Pemeliharaan'),
    ]

    id_sepeda = models.CharField(max_length=20, primary_key=True)  # ID unik untuk sepeda
    tipe_sepeda = models.CharField(max_length=50)  # Tipe sepeda, seperti 'MTB', 'Road Bike'
    merk_sepeda = models.CharField(max_length=50)  # Merk sepeda, seperti 'Polygon'
    harga_sewa = models.DecimalField(max_digits=10, decimal_places=2)  # Harga sewa per hari
    status_sepeda = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='tersedia'  # Default status sepeda
    )
    stasiun = models.ForeignKey(
        Stasiun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sepeda"  # Untuk mengakses sepeda yang terkait dengan stasiun
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu saat sepeda dibuat
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir pembaruan sepeda

    def __str__(self):
        return f"{self.tipe_sepeda} - {self.merk_sepeda} ({self.status_sepeda})"

    class Meta:
        verbose_name = "Sepeda"
        verbose_name_plural = "Sepeda"
        ordering = ['status_sepeda', 'tipe_sepeda']


class Pemeliharaan(models.Model):
    STATUS_PEMELIHARAAN_CHOICES = [
        ('dijadwalkan', 'Dijadwalkan'),
        ('sedang', 'Sedang Pemeliharaan'),
        ('selesai', 'Selesai'),
    ]

    sepeda = models.ForeignKey(Sepeda, on_delete=models.CASCADE, related_name="pemeliharaan")
    admin = models.ForeignKey('Admin', on_delete=models.SET_NULL, null=True, related_name="pemeliharaan")
    status_pemeliharaan = models.CharField(max_length=20, choices=STATUS_PEMELIHARAAN_CHOICES)
    tanggal_pemeliharaan = models.DateField()

    def __str__(self):
        return f"Pemeliharaan {self.sepeda.id_sepeda} ({self.status_pemeliharaan})"

class Peminjaman(models.Model):
    STATUS_PEMINJAMAN_CHOICES = [
        ('menunggu pembayaran', 'Menunggu Pembayaran'),
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('dibatalkan', 'Dibatalkan'),
    ]

    id_peminjaman = models.AutoField(primary_key=True)
    id_stasiun = models.ForeignKey(
        'Stasiun',
        on_delete=models.SET_NULL,
        null=True,
        related_name="peminjaman"
    )
    id_sepeda = models.ForeignKey(
        'Sepeda',
        on_delete=models.CASCADE,
        related_name="peminjaman"
    )
    id_customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name="peminjaman"
    )
    total_biaya = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tanggal_peminjaman = models.DateField()  # Tanggal saat peminjaman dibuat
    lama_peminjaman = models.DurationField()  # Lama peminjaman dalam bentuk timedelta
    status_peminjaman = models.CharField(
        max_length=20,
        choices=STATUS_PEMINJAMAN_CHOICES,
        default='menunggu pembayaran'
    )

    def __str__(self):
        return f"Peminjaman {self.id_peminjaman} - {self.id_customer.nama_customer}"

    def save(self, *args, **kwargs):
        # Validasi sepeda harus tersedia jika status peminjaman adalah 'menunggu pembayaran'
        if self.status_peminjaman == 'menunggu pembayaran' and self.id_sepeda.status_sepeda != 'tersedia':
            raise ValueError(f"Sepeda {self.id_sepeda.id_sepeda} tidak tersedia.")

        # Hitung total biaya berdasarkan lama peminjaman
        if self.lama_peminjaman and self.id_sepeda:
            total_jam = Decimal(self.lama_peminjaman.total_seconds()) / Decimal(3600)
            self.total_biaya = total_jam * self.id_sepeda.harga_sewa

        # Sepeda hanya diubah menjadi 'dipinjam' setelah pembayaran selesai
        if self.status_peminjaman == 'aktif' and self.id_sepeda.status_sepeda != 'dipinjam':
            self.id_sepeda.status_sepeda = 'dipinjam'
            self.id_sepeda.save()

        # Simpan perubahan ke database
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Peminjaman"
        verbose_name_plural = "Peminjaman"
        ordering = ['-tanggal_peminjaman']



class Pembayaran(models.Model):
    STATUS_PEMBAYARAN_CHOICES = [
        ('belum', 'Belum Dibayar'),
        ('lunas', 'Lunas'),
    ]

    id_pembayaran = models.AutoField(primary_key=True)
    id_peminjaman = models.ForeignKey(
        'Peminjaman',
        on_delete=models.CASCADE,
        related_name="pembayaran"
    )
    jumlah_pembayaran = models.DecimalField(max_digits=10, decimal_places=2)
    status_pembayaran = models.CharField(
        max_length=20,
        choices=STATUS_PEMBAYARAN_CHOICES,
        default='belum'
    )
    metode_pembayaran = models.CharField(max_length=50)
    bukti_pembayaran = models.ImageField(upload_to='bukti_pembayaran/', null=True, blank=True)
    tanggal_pembayaran = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Perbarui status peminjaman dan sepeda hanya jika pembayaran lunas
        if self.status_pembayaran == 'lunas':
            peminjaman = self.id_peminjaman
            peminjaman.status_peminjaman = 'aktif'
            peminjaman.id_sepeda.status_sepeda = 'dipinjam'
            peminjaman.id_sepeda.save()
            peminjaman.save()

    class Meta:
        verbose_name = 'Pembayaran'
        verbose_name_plural = 'Pembayaran'
