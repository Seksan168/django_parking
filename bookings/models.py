from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class UserCar(models.Model):
    """User's registered car"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cars', verbose_name='Owner'
    )
    car_license = models.CharField(max_length=20, verbose_name='License Plate')
    car_model = models.CharField(max_length=100, verbose_name='Brand/Model')
    car_color = models.CharField(max_length=50, blank=True, verbose_name='Car Color')
    is_default = models.BooleanField(default=False, verbose_name='Default Car')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'User Car'
        verbose_name_plural = 'User Cars'
        unique_together = ['user', 'car_license']  # Prevent duplicate plates for the same user
    
    def __str__(self):
        return f"{self.car_license} - {self.car_model}"
    
    def save(self, *args, **kwargs):
        # If this is the user's first car, make it default automatically
        if not self.pk and not UserCar.objects.filter(user=self.user).exists():
            self.is_default = True
        
        # Ensure only one default car per user
        if self.is_default:
            UserCar.objects.filter(user=self.user, is_default=True).update(is_default=False)
        
        super().save(*args, **kwargs)


class ParkingSpot(models.Model):
    """Parking spot zone"""
    ZONE_CHOICES = [
        ('A', 'Zone A - Near Entrance'),
        ('B', 'Zone B - Middle Area'),
        ('C', 'Zone C - Back Area'),
    ]
    
    spot_number = models.CharField(max_length=10, unique=True, verbose_name='Spot Number')
    zone = models.CharField(max_length=1, choices=ZONE_CHOICES, verbose_name='Zone')
    is_available = models.BooleanField(default=True, verbose_name='Available')
    
    class Meta:
        ordering = ['zone', 'spot_number']
        verbose_name = 'Parking Spot'
        verbose_name_plural = 'Parking Spots'
    
    def __str__(self):
        return f"{self.get_zone_display()} - {self.spot_number}"


class Booking(models.Model):
    """Parking booking request"""
    STATUS_CHOICES = [
        ('WAITING', 'Waiting for Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Booking information
    booking_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Booking ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Booked By')
    user_car = models.ForeignKey(
        'UserCar', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Selected Car'
    )
    parking_spot = models.ForeignKey(
        ParkingSpot, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Parking Spot'
    )
    
    # Car details
    car_license = models.CharField(max_length=20, verbose_name='License Plate')
    car_model = models.CharField(max_length=100, verbose_name='Brand/Model')
    phone_number = models.CharField(max_length=15, verbose_name='Phone Number')
    
    # Date and time
    booking_date = models.DateField(verbose_name='Booking Date')
    start_time = models.TimeField(verbose_name='Start Time')
    end_time = models.TimeField(verbose_name='End Time')
    
    # Status
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES,
        default='WAITING', verbose_name='Status'
    )
    note = models.TextField(blank=True, verbose_name='Notes')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_bookings', verbose_name='Approved By'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Approved At')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Parking Booking'
        verbose_name_plural = 'Parking Bookings'
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Generate booking ID (date + shortened UUID)
            self.booking_id = f"PK{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.booking_id} - {self.user.username}"
    
    def get_status_color(self):
        """Return color code for status badges"""
        colors = {
            'WAITING': 'yellow',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'CANCELLED': 'gray',
        }
        return colors.get(self.status, 'gray')


class Ticket(models.Model):
    """Parking ticket (created after approval)"""
    ticket_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Ticket Number')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, verbose_name='Booking')
    qr_code = models.CharField(max_length=200, blank=True, verbose_name='QR Code')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Issued At')
    
    class Meta:
        ordering = ['-issued_at']
        verbose_name = 'Parking Ticket'
        verbose_name_plural = 'Parking Tickets'
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TK{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.ticket_number
