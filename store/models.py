from django.db import models
from accounts.models import CustomUser


"""class UserStore(models.Model):
    user = models.OneToOneField(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
    name = models.CharField(max_length=120, null=True)
    last_name = models.CharField(max_length=120, null=True)
    address = models.CharField(max_length=225, null=True)
    is_seller = models.BooleanField(default=False)
    introduction = models.TextField(blank=True)
    start_date = models.DateTimeField(auto_now_add=True)"""


class Product(models.Model):
    seller = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=225, null=True)
    price = models.IntegerField()
    numbers = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    date_of_share = models.DateTimeField(auto_now_add=True)
    special = models.BooleanField(default=False)
    number_of_sell = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    views = models.IntegerField(default=0)
    digital = models.BooleanField(default=False, null=True, blank=False)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Order(models.Model):
    owner = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=120, null=True)
    status = models.BooleanField(default=False)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True

        return shipping


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Messages(models.Model):
    receiver = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=120, null=True)
    state = models.CharField(max_length=120, null=True)
    postal_code = models.CharField(max_length=120, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address