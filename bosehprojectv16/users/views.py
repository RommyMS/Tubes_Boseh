from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from .models import Akun, Customer, Admin, Sepeda, Pemeliharaan, Stasiun, Pembayaran, Peminjaman
from .forms import CustomerRegisterForm, CustomerLoginForm, SepedaForm, PemeliharaanForm, StasiunForm , PeminjamanForm

def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = make_password(form.cleaned_data['password'])

            # Buat akun baru
            akun = Akun.objects.create(username=username, password=password, role='customer')

            # Buat data customer
            customer = form.save(commit=False)
            customer.id_akun = akun
            customer.save()

            return redirect('login')
    else:
        form = CustomerRegisterForm()
    return render(request, 'users/register_customer.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            akun = Akun.objects.get(username=username)
            if check_password(password, akun.password):
                # Set session berdasarkan role
                request.session['akun_id'] = akun.id
                if akun.role == 'customer':
                    return redirect('home_customer')
                elif akun.role == 'admin':
                    return redirect('admin_dashboard')
            else:
                return render(request, 'users/login.html', {'error': 'Password salah.'})
        except Akun.DoesNotExist:
            return render(request, 'users/login.html', {'error': 'Akun tidak ditemukan.'})

    return render(request, 'users/login.html')

def home_customer(request):
    akun_id = request.session.get('akun_id')
    if akun_id:
        try:
            customer = Customer.objects.get(id_akun_id=akun_id)
            
            if request.method == 'POST':
                form = PeminjamanForm(request.POST)
                if form.is_valid():
                    peminjaman = form.save(commit=False)
                    peminjaman.id_customer = customer
                    peminjaman.save()

                    sepeda = peminjaman.id_sepeda
                    sepeda.status_sepeda = 'dipinjam'
                    sepeda.save()

                    messages.success(request, "Peminjaman sepeda berhasil!")
                    return redirect('home_customer')
                else:
                    messages.error(request, "Ada kesalahan dalam pengisian form.")

            else:
                form = PeminjamanForm()

            # Menampilkan sepeda yang tersedia beserta informasi stasiunnya
            sepeda_tersedia = Sepeda.objects.filter(status_sepeda='tersedia').select_related('stasiun')

            return render(request, 'users/home_customer.html', {
                'customer': customer,
                'form': form,
                'sepeda_tersedia': sepeda_tersedia
            })
        except Customer.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')



def pilih_sepeda(request, id_sepeda):
    akun_id = request.session.get('akun_id')
    if not akun_id:
        return redirect('login')

    sepeda = get_object_or_404(Sepeda, id_sepeda=id_sepeda)
    form = PeminjamanForm(initial={'id_sepeda': sepeda})

    return render(request, 'users/pilih_sepeda.html', {
        'sepeda': sepeda,
        'form': form
    })


def admin_dashboard(request):
    # Pastikan admin sudah login
    akun_id = request.session.get('akun_id')
    if not akun_id:
        return redirect('login')

    try:
        admin = Admin.objects.get(id_akun_id=akun_id)
    except Admin.DoesNotExist:
        return redirect('login')

    # Fetch semua data
    sepeda_list = Sepeda.objects.all()
    pemeliharaan_list = Pemeliharaan.objects.all()
    stasiun_list = Stasiun.objects.all()

    # Forms (inisial kosong)
    sepeda_form = SepedaForm()
    stasiun_form = StasiunForm()

    # Handle GET requests untuk edit
    if request.method == "GET":
        edit_stasiun_id = request.GET.get('edit_stasiun')
        edit_sepeda_id = request.GET.get('edit_sepeda')

        if edit_stasiun_id:
            stasiun = get_object_or_404(Stasiun, id_stasiun=edit_stasiun_id)
            stasiun_form = StasiunForm(instance=stasiun)  # Isi form dengan data stasiun
        if edit_sepeda_id:
            sepeda = get_object_or_404(Sepeda, id_sepeda=edit_sepeda_id)
            sepeda_form = SepedaForm(instance=sepeda)  # Isi form dengan data sepeda

    # Handle POST requests untuk operasi CRUD
    if request.method == "POST":
        # Tambah atau Perbarui Stasiun
        if 'stasiun_submit' in request.POST:
            stasiun_id = request.POST.get('stasiun_id')
            if stasiun_id:  # Update Stasiun
                stasiun = get_object_or_404(Stasiun, id_stasiun=stasiun_id)
                stasiun_form = StasiunForm(request.POST, instance=stasiun)
            else:  # Tambah Stasiun Baru
                stasiun_form = StasiunForm(request.POST)
            if stasiun_form.is_valid():
                stasiun_form.save()
                messages.success(request, "Stasiun berhasil disimpan!")
            else:
                messages.error(request, "Gagal menyimpan stasiun. Periksa input Anda.")
            return redirect('admin_dashboard')

        # Tambah atau Perbarui Sepeda
        elif 'sepeda_submit' in request.POST:
            sepeda_id = request.POST.get('sepeda_id')
            if sepeda_id:  # Update Sepeda
                sepeda = get_object_or_404(Sepeda, id_sepeda=sepeda_id)
                sepeda_form = SepedaForm(request.POST, instance=sepeda)
            else:  # Tambah Sepeda Baru
                sepeda_form = SepedaForm(request.POST)
            if sepeda_form.is_valid():
                sepeda_form.save()
                messages.success(request, "Sepeda berhasil disimpan!")
            else:
                messages.error(request, "Gagal menyimpan sepeda. Periksa input Anda.")
            return redirect('admin_dashboard')

        # Assign Sepeda ke Stasiun
        elif 'assign_sepeda' in request.POST:
            stasiun_id = request.POST.get('stasiun_id')
            sepeda_id = request.POST.get('sepeda_id')

            try:
                stasiun = Stasiun.objects.get(id_stasiun=stasiun_id)
                sepeda = Sepeda.objects.get(id_sepeda=sepeda_id)

                if sepeda.status_sepeda != 'tersedia':
                    messages.error(request, f"Sepeda {sepeda.id_sepeda} tidak dapat diassign karena statusnya bukan 'tersedia'.")
                elif sepeda.stasiun and sepeda.stasiun != stasiun:
                    messages.error(request, f"Sepeda {sepeda.id_sepeda} sudah diassign ke stasiun {sepeda.stasiun.nama_stasiun}.")
                else:
                    sepeda.stasiun = stasiun  # Assign sepeda ke stasiun
                    sepeda.status_sepeda = 'terkait'  # Update status sepeda agar tidak bisa dipilih lagi
                    sepeda.save()

                    messages.success(request, f"Sepeda {sepeda.id_sepeda} berhasil diassign ke {stasiun.nama_stasiun}.")
            except Stasiun.DoesNotExist:
                messages.error(request, "Stasiun tidak ditemukan.")
            except Sepeda.DoesNotExist:
                messages.error(request, "Sepeda tidak ditemukan.")

            return redirect('admin_dashboard')

    # Handle GET requests untuk operasi hapus
    delete_stasiun_id = request.GET.get('delete_stasiun')
    delete_sepeda_id = request.GET.get('delete_sepeda')
    delete_pemeliharaan_id = request.GET.get('delete_pemeliharaan')

    if delete_stasiun_id:
        stasiun = get_object_or_404(Stasiun, id_stasiun=delete_stasiun_id)
        stasiun.delete()
        messages.success(request, "Stasiun berhasil dihapus!")
        return redirect('admin_dashboard')

    if delete_sepeda_id:
        sepeda = get_object_or_404(Sepeda, id_sepeda=delete_sepeda_id)
        sepeda.delete()
        messages.success(request, "Sepeda berhasil dihapus!")
        return redirect('admin_dashboard')

    if delete_pemeliharaan_id:
        pemeliharaan = get_object_or_404(Pemeliharaan, id=delete_pemeliharaan_id)
        pemeliharaan.delete()
        messages.success(request, "Data pemeliharaan berhasil dihapus!")
        return redirect('admin_dashboard')

    return render(request, 'users/admin_dashboard.html', {
        'admin': admin,
        'sepeda_list': sepeda_list,
        'sepeda_form': sepeda_form,
        'pemeliharaan_list': pemeliharaan_list,
        'pemeliharaan_form': PemeliharaanForm,
        'stasiun_list': stasiun_list,
        'stasiun_form': stasiun_form,
    })

def pilih_sepeda(request, id_sepeda):
    akun_id = request.session.get('akun_id')
    if not akun_id:
        return redirect('login')

    try:
        customer = Customer.objects.get(id_akun_id=akun_id)
    except Customer.DoesNotExist:
        return redirect('login')

    sepeda = get_object_or_404(Sepeda, id_sepeda=id_sepeda)

    if sepeda.status_sepeda != 'tersedia':
        messages.error(request, "Sepeda tidak tersedia untuk dipinjam.")
        return redirect('home_customer')

    if request.method == 'POST':
        form = PeminjamanForm(request.POST)
        if form.is_valid():
            peminjaman = form.save(commit=False)
            peminjaman.id_customer = customer
            peminjaman.id_sepeda = sepeda

            # Konversi lama_peminjaman ke timedelta
            lama_peminjaman = form.cleaned_data['lama_peminjaman']
            if isinstance(lama_peminjaman, str):
                try:
                    hours, minutes, seconds = map(int, lama_peminjaman.split(':'))
                    lama_peminjaman = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except ValueError:
                    messages.error(request, "Format lama peminjaman salah. Gunakan HH:MM:SS.")
                    return redirect('pilih_sepeda', id_sepeda=id_sepeda)

            # Hitung total biaya menggunakan Decimal
            total_jam = Decimal(lama_peminjaman.total_seconds()) / Decimal(3600)
            peminjaman.total_biaya = total_jam * sepeda.harga_sewa
            peminjaman.lama_peminjaman = lama_peminjaman
            peminjaman.status_peminjaman = 'menunggu pembayaran'
            peminjaman.save()

            # Update status sepeda
            sepeda.status_sepeda = 'dipinjam'
            sepeda.save()

            messages.success(request, "Peminjaman berhasil dibuat! Silakan lanjutkan ke proses pembayaran.")
            return redirect('proses_pembayaran', id_peminjaman=peminjaman.id_peminjaman)
        else:
            messages.error(request, "Ada kesalahan pada form peminjaman.")
    else:
        form = PeminjamanForm()

    return render(request, 'users/form_peminjaman.html', {
        'customer': customer,
        'sepeda': sepeda,
        'form': form
    })

def proses_pembayaran(request, id_peminjaman):
    peminjaman = get_object_or_404(Peminjaman, id_peminjaman=id_peminjaman)

    # Pastikan Pembayaran sudah ada atau buat yang baru
    pembayaran, created = Pembayaran.objects.get_or_create(
        id_peminjaman=peminjaman,
        defaults={
            'jumlah_pembayaran': peminjaman.total_biaya,
            'status_pembayaran': 'belum',
        },
    )

    if request.method == 'POST':
        metode_pembayaran = request.POST.get('metode_pembayaran')
        bukti_pembayaran = request.FILES.get('bukti_pembayaran')

        if not metode_pembayaran:
            messages.error(request, "Metode pembayaran harus diisi.")
            return redirect('proses_pembayaran', id_peminjaman=id_peminjaman)

        # Update detail pembayaran
        pembayaran.metode_pembayaran = metode_pembayaran
        pembayaran.bukti_pembayaran = bukti_pembayaran
        pembayaran.status_pembayaran = 'lunas'
        pembayaran.save()  # Status sepeda dan peminjaman akan diperbarui di sini

        messages.success(request, "Pembayaran berhasil! Peminjaman Anda aktif.")
        return redirect('home_customer')

    return render(request, 'users/proses_pembayaran.html', {
        'peminjaman': peminjaman,
        'pembayaran': pembayaran
    })


def logout(request):
    request.session.flush()  # Hapus semua data sesi
    messages.success(request, "Anda telah keluar.")
    return redirect('login')
