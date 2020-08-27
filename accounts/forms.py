from django.forms import ModelForm
from .models import CustomUser


class UserForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'address', 'is_seller', 'introduction']
