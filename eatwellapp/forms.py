from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Customer, StoreOwner

User = get_user_model()

class CustomUserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
    }))

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    residential_address = forms.CharField(max_length=100, required=True)
    location = forms.ChoiceField(choices=(('ogoja', 'Ogoja'), ('okuku', 'Okuku')), required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                residential_address=self.cleaned_data['residential_address'],
                location=self.cleaned_data['location']
            )
        return user

class StoreOwnerRegistrationForm(UserCreationForm):
    business_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    business_location = forms.ChoiceField(choices=(('ogoja', 'Ogoja'), ('okuku', 'Okuku')), required=True)
    cac_bvn_number = forms.CharField(max_length=20, required=False)
    business_address = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'store_owner'
        if commit:
            user.save()
            StoreOwner.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name'],
                business_location=self.cleaned_data['business_location'],
                cac_bvn_number=self.cleaned_data['cac_bvn_number'],
                business_address=self.cleaned_data['business_address']
            )
        return user

