from django.forms import ModelForm
from .models import Product
from accounts.models import CustomUser
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['image', 'name', 'price', 'numbers', 'description', 'special']
