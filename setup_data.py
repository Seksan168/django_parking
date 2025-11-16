#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from bookings.models import ParkingSpot, Booking, UserCar
from datetime import date, time

# สร้าง Superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@parking.com', 'admin123')
    print('✅ สร้าง Admin: username=admin, password=admin123')
else:
    admin = User.objects.get(username='admin')
    print('ℹ️ Admin มีอยู่แล้ว')

# สร้าง User ทั่วไป
if not User.objects.filter(username='user1').exists():
    user1 = User.objects.create_user('user1', 'user1@test.com', 'pass1234')
    print('✅ สร้าง User: username=user1, password=pass1234')
else:
    user1 = User.objects.get(username='user1')
    print('ℹ️ User1 มีอยู่แล้ว')

# สร้างรถตัวอย่างสำหรับ user1
sample_cars = [
    {'car_license': 'กข 1234 กรุงเทพ', 'car_model': 'Toyota Camry', 'car_color': 'ดำ', 'is_default': True},
    {'car_license': 'คฆ 5678 นนทบุรี', 'car_model': 'Honda Civic', 'car_color': 'ขาว', 'is_default': False},
]

for car_data in sample_cars:
    if not UserCar.objects.filter(user=user1, car_license=car_data['car_license']).exists():
        UserCar.objects.create(user=user1, **car_data)
        print(f'✅ เพิ่มรถ: {car_data["car_license"]} - {car_data["car_model"]}')

# สร้างที่จอดรถ
zones = ['A', 'B', 'C']
spots_per_zone = 10

for zone in zones:
    for i in range(1, spots_per_zone + 1):
        spot_number = f"{zone}{i:02d}"
        if not ParkingSpot.objects.filter(spot_number=spot_number).exists():
            ParkingSpot.objects.create(
                spot_number=spot_number,
                zone=zone,
                is_available=True
            )
            print(f'✅ สร้างที่จอด: {spot_number}')

print(f'\n📊 สรุป:')
print(f'   ที่จอดทั้งหมด: {ParkingSpot.objects.count()} ช่อง')
print(f'   ผู้ใช้ทั้งหมด: {User.objects.count()} คน')
print(f'   รถทั้งหมด: {UserCar.objects.count()} คัน')
print('\n🎉 เสร็จสิ้น! พร้อมใช้งานแล้ว')
print('\n📝 ข้อมูลการเข้าสู่ระบบ:')
print('   Admin: username=admin, password=admin123')
print('   User:  username=user1, password=pass1234')
print('\n🚗 รถตัวอย่าง (user1):')
for car in UserCar.objects.filter(user=user1):
    print(f'   - {car.car_license} ({car.car_model}) {"⭐ รถหลัก" if car.is_default else ""}')
