# forms.py
from django import forms
from .models import Customer, Account
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User  # Assuming you have a User model
        # fields = ['username', 'email', 'password']  # Adjust fields as necessary
        fields = ['email', 'password']

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account  # Assuming you have an Account model
        fields = ['address', 'private_key']  # Adjust fields as necessary

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'gender', 'is_owner', 'phone', 'address', 'display_image']  # Exclude user and account