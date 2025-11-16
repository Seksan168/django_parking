from django import forms
from .models import UserCar

class UserCarForm(forms.ModelForm):
    """Form for adding/editing a user's car"""
    
    class Meta:
        model = UserCar
        fields = ['car_license', 'car_model', 'car_color', 'is_default']
        
        widgets = {
            'car_license': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., ABC 1234 Bangkok'
            }),
            'car_model': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Toyota Camry'
            }),
            'car_color': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Black, White, Silver'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'rounded text-indigo-600 focus:ring-indigo-500'
            }),
        }
        
        labels = {
            'car_license': '🚗 License Plate',
            'car_model': '🏎️ Brand/Model',
            'car_color': '🎨 Car Color',
            'is_default': '⭐ Set as Default Car',
        }
        
        help_texts = {
            'car_license': 'Provide the complete license plate number.',
            'car_model': 'e.g., Honda Civic, Toyota Camry.',
            'car_color': 'Car color (optional).',
            'is_default': 'The default car will be pre-selected when making a booking.',
        }
