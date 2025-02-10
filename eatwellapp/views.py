from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomerRegistrationForm, StoreOwnerRegistrationForm, CustomUserLoginForm
from .models import Restaurant, Food, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def home(request):
    return render(request, 'eatwellapp/home.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {username}!')
                try:
                    user_type = user.userprofile.user_type
                    if user_type == 'customer':
                        return redirect('customer_dashboard')
                    elif user_type == 'store_owner':
                        return redirect('store_owner_dashboard')
                except:
                    messages.error(request, 'User profile not found.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomUserLoginForm()
    return render(request, 'eatwellapp/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')
    else:
        return redirect('home')  # Or some other page if you prefer

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'eatwellapp/customer_register.html', {'form': form})

def store_owner_register(request):
    if request.method == 'POST':
        form = StoreOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('store_owner_dashboard')
    else:
        form = StoreOwnerRegistrationForm()
    return render(request, 'eatwellapp/store_owner_register.html', {'form': form})

@login_required
def customer_dashboard(request):
    if request.user.user_type != 'customer':
        messages.error(request, 'You do not have access to this page.')
        return redirect('home')
    
    query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    restaurants = Restaurant.objects.all()
    
    foods = Food.objects.all()
    if query:
        foods = foods.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(restaurant__name__icontains=query)
        )
    if category:
        foods = foods.filter(category=category)
    
    cart = request.session.get('cart', {})
    cart_count = sum(int(item.get('quantity', 0)) for item in cart.values())
    
    context = {
        'user': request.user,
        'foods': foods,
        'restaurants': restaurants,
        'category_name': category.title() if category else 'All Categories',
        'cart_count': cart_count,
    }
    return render(request, 'eatwellapp/customer_dashboard.html', context)

@login_required
def store_owner_dashboard(request):
    if request.user.user_type != 'store_owner':
        messages.error(request, 'You do not have access to this page.')
        return redirect('home')
    context = {
        'user': request.user,
    }
    return render(request, 'eatwellapp/store_owner_dashboard.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user.customer).order_by('-created_at')
    return render(request, 'eatwellapp/order_history.html', {'orders': orders})

@login_required
def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    category = request.GET.get('category', '')
    
    # Get all restaurants for sidebar
    restaurants = Restaurant.objects.all()
    
    # Get foods for this restaurant
    foods = Food.objects.filter(restaurant=restaurant)
    if category:
        foods = foods.filter(category=category)
    
    # Get cart count
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    
    context = {
        'restaurant': restaurant,
        'foods': foods,
        'restaurants': restaurants,
        'categories': Food.CATEGORY_CHOICES,
        'category': category,
        'cart_count': cart_count,
    }
    return render(request, 'eatwellapp/restaurant_menu.html', context)

@login_required
def add_to_cart(request, food_id):
    food = Food.objects.get(id=food_id)
    restaurant_id = Food.restaurant.id
    cart = request.session.get('cart', {})
    cart[food_id] = cart.get(food_id, 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for food_id, details in cart.items():
        food = Food.objects.get(id=food_id)
        # Extract the quantity value if `details` is a dictionary
        quantity = details if isinstance(details, int) else details.get('quantity', 1)
        subtotal = food.price * quantity
        total += subtotal
        items.append({'food': food, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'eatwellapp/cart.html', {'items': items, 'total': total})

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        # Redirect to the cart page if it's empty
        if not cart:
            return redirect('cart')
        
        # Retrieve the restaurant ID
        restaurant_id = next(iter(cart.keys()), None) 
        if not restaurant_id:
            return redirect('cart')  # Safety check in case of invalid cart structure
        
        # Fetch the restaurant object
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        # Calculate total amount safely
        total_amount = 0
        for food_id, details in cart.items():
            food = get_object_or_404(Food, id=food_id)
            # Handle case where details might be a dictionary or an integer
            quantity = details if isinstance(details, int) else details.get('quantity', 1)
            total_amount += food.price * quantity
        
        # Create the order
        order = Order.objects.create(
            customer=request.user.customer,
            restaurant=restaurant,
            total_amount=total_amount,
            payment_method=request.POST.get('payment_method', 'unknown')  # Default to 'unknown' if not provided
        )
        
        # Create order items
        for food_id, details in cart.items():
            food = get_object_or_404(Food, id=food_id)
            quantity = details if isinstance(details, int) else details.get('quantity', 1)
            OrderItem.objects.create(
                order=order,
                food=food,
                quantity=quantity,
                price=food.price
            )
        
        # Clear the cart after successful checkout
        request.session['cart'] = {}
        
        # Redirect to order confirmation page
        return redirect('order_confirmation', order_id=order.id)
    
    # Render the checkout page for GET requests
    return render(request, 'eatwellapp/checkout.html')

@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'eatwellapp/order_confirmation.html', {'order': order})

@login_required
def food_categories(request):
    categories = Food.objects.values('category').distinct()
    return render(request, 'eatwellapp/food_categories.html', {'categories': categories})

@login_required
def add_to_cart(request, food_id):
    if request.method == 'POST':
        food = get_object_or_404(Food, id=food_id)
        cart = request.session.get('cart', {})
        cart_id = str(food_id)
        
        if cart_id in cart:
            cart[cart_id]['quantity'] += 1
        else:
            cart[cart_id] = {
                'quantity': 1,
                'price': str(food.price)
            }
        
        request.session['cart'] = cart
        messages.success(request, f'{food.name} added to cart.')
        
        return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))
    
    return redirect('customer_dashboard')

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user.customer).order_by('-created_at')
    return render(request, 'eatwellapp/order_history.html', {'orders': orders})

@login_required
def order_now(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    
    # Create order with single item
    order = Order.objects.create(
        customer=request.user.customer,
        restaurant=food.restaurant,
        total_amount=food.price,
        payment_method='online'  # Default to online payment
    )
    
    # Create order item
    OrderItem.objects.create(
        order=order,
        food=food,
        quantity=1,
        price=food.price
    )
    
    return redirect('order_confirmation', order_id=order.id)

@login_required
def remove_from_cart(request, food_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart_id = str(food_id)
        
        if cart_id in cart:
            del cart[cart_id]
            request.session['cart'] = cart
            messages.success(request, 'Item removed from cart.')
        
    return redirect('cart')


