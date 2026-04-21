from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Address


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in fields}


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["label", "line1", "line2", "city", "state", "postal_code", "country"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in fields}
