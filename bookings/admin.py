from django.contrib import admin
from .models import ParkingSpot, Booking, Ticket, UserCar


@admin.register(UserCar)
class UserCarAdmin(admin.ModelAdmin):
    list_display = ['car_license', 'car_model', 'car_color', 'user', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['car_license', 'car_model', 'user__username']
    list_editable = ['is_default']


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ['spot_number', 'zone', 'is_available']
    list_filter = ['zone', 'is_available']
    search_fields = ['spot_number']
    list_editable = ['is_available']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'car_license', 'booking_date', 'status', 'parking_spot', 'created_at']
    list_filter = ['status', 'booking_date', 'created_at']
    search_fields = ['booking_id', 'car_license', 'user__username']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('ข้อมูลการจอง', {
            'fields': ('booking_id', 'user', 'parking_spot', 'status')
        }),
        ('ข้อมูลรถยนต์', {
            'fields': ('car_license', 'car_model', 'phone_number')
        }),
        ('วันเวลา', {
            'fields': ('booking_date', 'start_time', 'end_time')
        }),
        ('การอนุมัติ', {
            'fields': ('approved_by', 'approved_at', 'note')
        }),
        ('ระบบ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'booking', 'issued_at']
    search_fields = ['ticket_number', 'booking__booking_id']
    readonly_fields = ['ticket_number', 'issued_at']
