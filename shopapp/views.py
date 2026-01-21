from django.shortcuts import render, redirect
from shopapp.forms import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json


# home
def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, "shop/index.html", {'products': products})

# logout page
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')

# login page
def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':  
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully')
                return redirect('/')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('/login')  
    return render(request, "shop/login.html")

# Register
def register(request):
    form = CustomUserForm()
    if request.method == 'POST':  
        form = CustomUserForm(request.POST)  
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can login now.")
            return redirect("/login")
    return render(request, "shop/register.html", {'form': form})

# collection page
def collection(request):
    catagory = Catagory.objects.filter(status=0)
    return render(request, "shop/collection.html", {'catagory': catagory})

# collectionsview
def collectionview(request, name):
    catagory = Catagory.objects.filter(name=name, status=0)
    if catagory:
        products = Product.objects.filter(category__name=name, status=0)
        return render(request, "shop/products/index.html", {'products': products, "category_name": name})
    else:
        messages.warning(request, "No such category found")
        return redirect('collection')

def product_details(request, cname, pname):
    catagory = Catagory.objects.filter(name=cname, status=0)
    if catagory:
        product = Product.objects.filter(name=pname, status=0).first()
        if product:
            return render(request, 'shop/products/product_details.html', {'product': product})
        else:
            messages.error(request, "No such product found")
            return redirect('collection')
    else:
        messages.error(request, "No such category found")
        return redirect('collection')


def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
                data = json.loads(request.body)
                product_qty = data['product_qty']
                product_id = data['pid']
                product_status = Product.objects.filter(id=product_id).first()

                if product_status:
                    if Cart.objects.filter(user=request.user, product_id=product_id):
                        return JsonResponse({'status': 'product already in cart'}, status=200)
                    else:
                        if product_status.quantity>=product_qty:
                            Cart.objects.create(
                                user=request.user,
                                product_id=product_id,
                                product_qty=product_qty
                            )
                            return JsonResponse({'status': 'product added to cart'}, status=200)
                        else:
                            return JsonResponse({'status': 'product stock not available'}, status=200)
                else:
                    return JsonResponse({'status': 'No such product found'}, status=404)
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'shop/cart.html', {'cart': cart})
    else:
        return redirect('/')

def remove_cart(request, cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')

#fav_page
def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            product_id = data['pid']
            product_status = Product.objects.filter(id=product_id).first()

            if product_status:
                fav_exists = Favourite.objects.filter(user=request.user, product_id=product_id).exists()
                if fav_exists:
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
            else:
                return JsonResponse({'status': 'No such product found'}, status=404)
        else:
            return JsonResponse({'status': 'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=400)

#favviewpage
def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, 'shop/fav.html', {'fav': fav})
    else:
        return redirect('/')
#removefavourite
def remove_fav(request,fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect('/favviewpage')