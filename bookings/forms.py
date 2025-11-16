from django import forms
from .models import Booking, ParkingSpot, UserCar

class BookingForm(forms.ModelForm):
    user_car = forms.ModelChoiceField(
        queryset=UserCar.objects.none(),  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        }),
        label='🚗 Choose Your Car',
        help_text='Select from your saved cars or enter new car details below.'
    )
    
    class Meta:
        model = Booking
        fields = [
            'user_car', 'car_license', 'car_model', 
            'phone_number', 'booking_date', 
            'start_time', 'end_time', 'note'
        ]
        
        widgets = {
            'car_license': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., ABC 1234 Bangkok'
            }),
            'car_model': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., Toyota Camry'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., 081-234-5678'
            }),
            'booking_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'time'
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Additional notes (optional)',
                'rows': 3
            }),
        }

        labels = {
            'car_license': '🚗 License Plate',
            'car_model': '🏎️ Car Brand/Model',
            'phone_number': '📱 Phone Number',
            'booking_date': '📅 Booking Date',
            'start_time': '⏰ Start Time',
            'end_time': '⏰ End Time',
            'note': '📝 Notes',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        
        if user:
            # Show only cars belonging to this user
            self.fields['user_car'].queryset = UserCar.objects.filter(user=user)
            
            # Auto-select default car if user has one
            default_car = UserCar.objects.filter(user=user, is_default=True).first()
            if default_car and not self.instance.pk:
                self.fields['user_car'].initial = default_car
                self.fields['car_license'].initial = default_car.car_license
                self.fields['car_model'].initial = default_car.car_model
    
    def clean(self):
        cleaned_data = super().clean()
        user_car = cleaned_data.get('user_car')
        car_license = cleaned_data.get('car_license')
        car_model = cleaned_data.get('car_model')
        
        # If selected a saved car, auto-fill license and model
        if user_car:
            cleaned_data['car_license'] = user_car.car_license
            cleaned_data['car_model'] = user_car.car_model
        else:
            # If not selecting a car, user must provide car details manually
            if not car_license:
                self.add_error('car_license', 'Please enter your car license plate.')
            if not car_model:
                self.add_error('car_model', 'Please enter your car brand/model.')
        
        return cleaned_data
