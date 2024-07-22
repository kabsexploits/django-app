from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.forms import UserCreationForm


#db = firebase.FirebaseApplication(firebaseConfig['databaseURL'], None)


import pyrebase

#For Firebase JS SDK v7.20.0 and later, measurementId is optional
firebaseConfig = {
  'apiKey': "AIzaSyBvyFbHO1sePKePy_PDcqx-BiX9BoBNQfg",
  'authDomain': "django-2c82f.firebaseapp.com",
  'databaseURL': "https://django-2c82f-default-rtdb.firebaseio.com",
  'projectId': "django-2c82f",
  'storageBucket': "django-2c82f.appspot.com",
  'messagingSenderId': "507362072315",
  'appId': "1:507362072315:web:481c072b190b65ffc1c25e",
  'measurementId': "G-M6V1C1DF4Y"
}

firebase = pyrebase.initialize_app(firebaseConfig)

database = firebase.database()
storage = firebase.storage()


auth = firebase.auth()


from django.conf import settings

loginchecks=''

currentUser = []


def createitem(request) :
	if request.method == 'POST' and request.FILES['image']:
		image = request.FILES['image']
		print(image)
		storage_path = image.name
		storage.child(storage_path).put(image)
		print(image)
		return HttpResponse(f'Image uploaded successfully: <a href="{image}">{image}</a>')
	print("success")
	return render(request, 'store/index.html')
	
	


def index(request):
	data = {'data':{"name": "joseph", "age": "38", "hight": "5.3"}}
	
	
	return render(request, 'store/index.html', {'data':data['data'].values()})

       
    

def signup_view(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password1']
		print(email,password)


		try:
			user = auth.create_user_with_email_and_password(
            email,
                password
            )
			return redirect('login')
		except Exception as e:
			return str(e)
	return render(request, 'store/register.html')

def login_view(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']
		try:
			user = auth.sign_in_with_email_and_password(email,password)
			sign_user = auth.refresh(user['refreshToken'])
			currentUser.append(sign_user)
			print(sign_user['userId'])
			print("sign In Successfull")
			return redirect('/')
		except Exception as e:
			return 
	return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')




def store(request):

	print(currentUser)
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()


	
	
	context = {'products':products, 'cartItems':cartItems,loginchecks:loginchecks}

	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
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
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)