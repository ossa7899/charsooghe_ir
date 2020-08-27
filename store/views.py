from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from .models import *
from accounts.models import CustomUser
from accounts.forms import UserForm
import json
import datetime
from django.http import JsonResponse
from .forms import ProductForm
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


def home(request, flag=False):
    context = {}
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(owner=request.user, complete=False)
        if flag:
            return order
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        context['cartItems'] = cartItems

    products = Product.objects.all()
    context['products'] = products

    return render(request, 'store/home.html', context)


def loginuser(request):
    if request.method == 'GET':
        return render(request, "store/loginuser.html", {'form': AuthenticationForm()})
    else:
        user = authenticate(request, phone=request.POST['phone'], password=request.POST['password'])
        if user is None:
            return render(request, "store/loginuser.html",
                          {'form': AuthenticationForm(), 'error': 'phone number and password did not match'})
        else:
            login(request, user)
            return redirect('home')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def signupuser(request):
    if request.method == 'GET':
        return render(request, "store/signupuser.html", {'form': UserForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = CustomUser.objects.create_user(request.POST['phone'],
                                                      password=request.POST['password1'])

                user.first_name = request.POST['first_name']
                user.last_name = request.POST['last_name']
                user.email = request.POST['email']
                user.address = request.POST['address']
                user.introduction = request.POST['introduction']
                try:
                    if request.POST['is_seller'] == 'on':
                        print("it is onnnnnnnnnnnnnn************************")
                        user.is_seller = True
                    else:
                        print("it is else else else else ************************")

                        user.is_seller = False
                except:
                    user.is_seller = False
                    print("it is try try try try ************************")

                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, "store/signupuser.html",
                              {'form': UserCreationForm(), 'error': 'This user name has already taken'})
        else:
            # Tell the user the password didn't match
            return render(request, "store/signupuser.html",
                          {'form': UserCreationForm(), 'error': 'password did not match'})


@login_required
def sell(request):
    if request.method == 'GET':
        return render(request, "store/sell.html", {'form': ProductForm()})
    else:
        try:
            form = ProductForm(request.POST, request.FILES)
            newProduct = form.save(commit=False)
            newProduct.seller = request.user
            newProduct.save()
            return redirect('sell')
        except ValueError:
            return render(request, "store/sell.html",
                          {'form': ProductForm(), 'error': 'bad data passed in, Try again.'})


@login_required
def userprofile(request):
    if request.method == 'GET':
        messages = Messages.objects.all()
        print(messages)
        products = Product.objects.all()
        return render(request, "store/userprofile.html",
                      {'form': UserForm(), 'messages': messages, 'products': products})
    else:
        try:
            request.user.first_name = request.POST['first_name']
            request.user.last_name = request.POST['last_name']
            request.user.email = request.POST['email']
            request.user.address = request.POST['address']
            request.user.introduction = request.POST['introduction']
            try:
                if request.POST['is_seller'] == 'on':
                    request.user.is_seller = True
                else:
                    request.user.is_seller = False
            except:
                request.user.is_seller = False

            request.user.save()
            return redirect('userprofile')
        except ValueError:
            return render(request, "store/userprofile.html",
                          {'form': ProductForm(), 'error': 'bad data passed in, Try again.'})


@login_required
def cart(request):
    order, created = Order.objects.get_or_create(owner=request.user, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {"items": items, "order": order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


@login_required
def checkout(request):
    customer = request.user
    order, created = Order.objects.get_or_create(owner=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {"items": items, "order": order, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/checkout.html', context)


@login_required
def updateItem(request, special=False):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print(productId, action)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(owner=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if special == True:
        return orderItem
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'delete':
        orderItem.quantity = 0

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@login_required
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(owner=customer, complete=False)

    total = int(data['form']['total'])
    order.transaction_id = transaction_id
    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            postal_code=data['shipping']['zipcode'],
        )
    message = Messages()
    message.receiver = request.user
    message.text = "سفارش شما انجام شد و بین 1 تا 2 روز دیگر تحویل شما داده خواهد شد. شماره سفارش :" + str(
        transaction_id)
    message.save()
    return JsonResponse('Payment Complete', safe=False)


@login_required
def delete(request):
    orderItem = updateItem(request, True)
    orderItem.quantity = 0
    orderItem.delete()
    return redirect('cart')


def product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product.html', {'product': product})
