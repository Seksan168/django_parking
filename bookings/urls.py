from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Car Management
    path('my-cars/', views.my_cars, name='my_cars'),
    path('add-car/', views.add_car, name='add_car'),
    path('edit-car/<int:car_id>/', views.edit_car, name='edit_car'),
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'),
    path('set-default-car/<int:car_id>/', views.set_default_car, name='set_default_car'),
    
    # Booking
    path('create/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<str:booking_id>/', views.booking_detail, name='booking_detail'),
    path('ticket/<str:booking_id>/', views.view_ticket, name='view_ticket'),
    
    # Admin routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
]
