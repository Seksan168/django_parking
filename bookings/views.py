from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from .models import Booking, ParkingSpot, Ticket, UserCar
from .forms import BookingForm
from .register_forms import UserRegisterForm
from .car_forms import UserCarForm

import qrcode
import base64
from io import BytesIO

def home(request):
    """หน้าแรก - แสดงสถานะที่จอด"""
    spots = ParkingSpot.objects.all()
    total_spots = spots.count()
    available_spots = spots.filter(is_available=True).count()
    
    context = {
        'spots': spots,
        'total_spots': total_spots,
        'available_spots': available_spots,
        'occupied_spots': total_spots - available_spots,
    }
    return render(request, 'bookings/home.html', context)


@login_required
def create_booking(request):
    """สร้างการจองใหม่"""
    # เช็คว่ามีรถหรือยัง
    has_cars = UserCar.objects.filter(user=request.user).exists()
    
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = 'WAITING'
            
            # ถ้าเลือกรถจาก dropdown ให้บันทึก user_car
            if form.cleaned_data.get('user_car'):
                booking.user_car = form.cleaned_data['user_car']
            
            booking.save()
            
            messages.success(request, f'✅ จองสำเร็จ! รหัสจอง: {booking.booking_id} - รอการอนุมัติ')
            return redirect('my_bookings')
    else:
        form = BookingForm(user=request.user)
    
    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'has_cars': has_cars
    })


@login_required
def my_bookings(request):
    """รายการจองของฉัน"""
    bookings = Booking.objects.filter(user=request.user)

    total = bookings.count()
    pending = bookings.filter(status='WAITING').count()
    approved = bookings.filter(status='APPROVED').count()
    rejected = bookings.filter(status='REJECTED').count()

    context = {
        'bookings': bookings,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    }
    return render(request, 'bookings/my_bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """รายละเอียดการจอง"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    ticket = None
    
    # ถ้าอนุมัติแล้ว ดูว่ามีตั๋วหรือยัง
    if booking.status == 'APPROVED':
        try:
            ticket = Ticket.objects.get(booking=booking)
        except Ticket.DoesNotExist:
            ticket = None
    
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'ticket': ticket
    })


def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_dashboard(request):
    """แดชบอร์ดสำหรับ Admin"""
    waiting_bookings = Booking.objects.filter(status='WAITING')
    approved_bookings = Booking.objects.filter(status='APPROVED')
    all_bookings = Booking.objects.all()[:10]
    
    context = {
        'waiting_bookings': waiting_bookings,
        'approved_bookings': approved_bookings,
        'all_bookings': all_bookings,
        'waiting_count': waiting_bookings.count(),
    }
    return render(request, 'bookings/admin_dashboard.html', context)


@user_passes_test(is_staff)
def approve_booking(request, booking_id):
    """อนุมัติการจอง"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.status == 'WAITING':
        # หาที่จอดว่าง
        available_spot = ParkingSpot.objects.filter(is_available=True).first()
        
        if available_spot:
            booking.status = 'APPROVED'
            booking.approved_by = request.user
            booking.approved_at = timezone.now()
            booking.parking_spot = available_spot
            booking.save()
            
            # ทำให้ที่จอดไม่ว่าง
            available_spot.is_available = False
            available_spot.save()
            
            # สร้างตั๋ว
            ticket = Ticket.objects.create(
                booking=booking,
                qr_code=f"QR-{booking.booking_id}"
            )
            
            messages.success(request, f'✅ อนุมัติการจอง {booking.booking_id} สำเร็จ! ออกตั๋ว {ticket.ticket_number}')
        else:
            messages.error(request, '❌ ไม่มีที่จอดว่าง!')
    
    return redirect('admin_dashboard')


@user_passes_test(is_staff)
def reject_booking(request, booking_id):
    """ปฏิเสธการจอง"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.status == 'WAITING':
        booking.status = 'REJECTED'
        booking.save()
        messages.warning(request, f'⚠️ ปฏิเสธการจอง {booking.booking_id} แล้ว')
    
    return redirect('admin_dashboard')


@login_required
def view_ticket(request, booking_id):
    """ดูตั๋วจอดรถ"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if booking.status != 'APPROVED':
        messages.error(request, '❌ การจองนี้ยังไม่ได้รับอนุมัติ')
        return redirect('my_bookings')
    
    try:
        ticket = Ticket.objects.get(booking=booking)
    except Ticket.DoesNotExist:
        messages.error(request, '❌ ยังไม่มีตั๋ว')
        return redirect('my_bookings')
    
    # 🔹 Data to encode in QR
    qr_data = ticket.qr_code or f"TICKET:{ticket.ticket_number}|BOOKING:{booking.booking_id}"
    
    # 🔹 Generate QR image
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 🔹 Convert to Base64 for <img src="">
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'bookings/ticket.html', {
        'ticket': ticket,
        'booking': booking,
        'qr_image': qr_base64,   # 👉 send to template
    })



def register(request):
    """หน้าลงทะเบียนผู้ใช้ใหม่"""
    if request.user.is_authenticated:
        messages.info(request, 'คุณเข้าสู่ระบบอยู่แล้ว')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # เข้าสู่ระบบอัตโนมัติหลังลงทะเบียน
            login(request, user)
            
            messages.success(request, f'✅ ยินดีต้อนรับ {username}! ลงทะเบียนสำเร็จ')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'bookings/register.html', {'form': form})


def user_login(request):
    """หน้าเข้าสู่ระบบ"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ ยินดีต้อนรับกลับ {username}!')
            
            # Redirect ไปหน้าที่ต้องการก่อนหน้า (ถ้ามี)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    
    return render(request, 'bookings/login.html')


def user_logout(request):
    """ออกจากระบบ"""
    username = request.user.username if request.user.is_authenticated else ''
    logout(request)
    
    if username:
        messages.info(request, f'👋 {username} ออกจากระบบเรียบร้อย')
    
    return redirect('home')


@login_required
def my_cars(request):
    """รายการรถของฉัน"""
    cars = UserCar.objects.filter(user=request.user)
    return render(request, 'bookings/my_cars.html', {'cars': cars})


@login_required
def add_car(request):
    """เพิ่มรถใหม่"""
    if request.method == 'POST':
        form = UserCarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            
            # เช็คว่าทะเบียนซ้ำกับของตัวเองหรือไม่
            if UserCar.objects.filter(user=request.user, car_license=car.car_license).exists():
                messages.error(request, '❌ คุณเพิ่มรถทะเบียนนี้ไว้แล้ว')
                return render(request, 'bookings/add_car.html', {'form': form})
            
            car.save()
            messages.success(request, f'✅ เพิ่มรถ {car.car_license} สำเร็จ!')
            return redirect('my_cars')
    else:
        form = UserCarForm()
    
    return render(request, 'bookings/add_car.html', {'form': form})


@login_required
def edit_car(request, car_id):
    """แก้ไขข้อมูลรถ"""
    car = get_object_or_404(UserCar, id=car_id, user=request.user)
    
    if request.method == 'POST':
        form = UserCarForm(request.POST, instance=car)
        if form.is_valid():
            # เช็คว่าทะเบียนซ้ำกับรถคันอื่นของตัวเองหรือไม่
            new_license = form.cleaned_data['car_license']
            if UserCar.objects.filter(user=request.user, car_license=new_license).exclude(id=car.id).exists():
                messages.error(request, '❌ คุณมีรถทะเบียนนี้อยู่แล้ว')
                return render(request, 'bookings/edit_car.html', {'form': form, 'car': car})
            
            form.save()
            messages.success(request, f'✅ แก้ไขข้อมูลรถ {car.car_license} สำเร็จ!')
            return redirect('my_cars')
    else:
        form = UserCarForm(instance=car)
    
    return render(request, 'bookings/edit_car.html', {'form': form, 'car': car})


@login_required
def delete_car(request, car_id):
    """ลบรถ"""
    car = get_object_or_404(UserCar, id=car_id, user=request.user)
    
    # เช็คว่ามีการจองที่ใช้รถคันนี้อยู่หรือไม่
    active_bookings = Booking.objects.filter(
        user_car=car, 
        status__in=['WAITING', 'APPROVED']
    ).count()
    
    if active_bookings > 0:
        messages.error(request, f'❌ ไม่สามารถลบรถคันนี้ได้ เนื่องจากมีการจองที่ใช้รถคันนี้อยู่ ({active_bookings} รายการ)')
        return redirect('my_cars')
    
    car_license = car.car_license
    car.delete()
    messages.success(request, f'✅ ลบรถ {car_license} สำเร็จ')
    return redirect('my_cars')


@login_required
def set_default_car(request, car_id):
    """ตั้งเป็นรถหลัก"""
    car = get_object_or_404(UserCar, id=car_id, user=request.user)
    
    # ยกเลิกรถหลักเดิม
    UserCar.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # ตั้งรถนี้เป็นรถหลัก
    car.is_default = True
    car.save()
    
    messages.success(request, f'✅ ตั้ง {car.car_license} เป็นรถหลักแล้ว')
    return redirect('my_cars')
