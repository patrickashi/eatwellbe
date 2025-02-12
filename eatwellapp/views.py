from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomerRegistrationForm, StoreOwnerRegistrationForm, CustomUserLoginForm
from .models import Restaurant, Food, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal

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
    total = Decimal('0.00')
    restaurants = set()

    for food_id, details in cart.items():
        food = get_object_or_404(Food, id=food_id)
        quantity = details if isinstance(details, int) else details.get('quantity', 1)
        subtotal = food.price * quantity
        total += subtotal
        restaurants.add(food.restaurant)
        items.append({
            'food': food,
            'quantity': quantity,
            'subtotal': subtotal
        })

    # Calculate delivery fee
    delivery_fee = Decimal('0.00')
    for restaurant in restaurants:
        if restaurant.location.lower() == 'ogoja':
            delivery_fee += Decimal('1000.00')
        elif restaurant.location.lower() == 'okuku':
            delivery_fee += Decimal('2000.00')
        # Add more locations as needed

    total_with_delivery = total + delivery_fee

    context = {
        'items': items,
        'total': total,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery,
        'restaurant_count': len(restaurants),
        'cart_count': sum(item['quantity'] for item in items)
    }

    return render(request, 'eatwellapp/cart.html', context)


@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            return redirect('cart')
        
        total_amount = Decimal('0.00')
        order_items = []
        restaurants = set()

        for food_id, details in cart.items():
            food = get_object_or_404(Food, id=food_id)
            quantity = details if isinstance(details, int) else details.get('quantity', 1)
            item_total = food.price * quantity
            total_amount += item_total
            
            restaurants.add(food.restaurant)
            
            order_items.append({
                'food': food,
                'quantity': quantity,
                'price': food.price,
                'restaurant': food.restaurant
            })

        # Calculate delivery fees
        delivery_fee = Decimal('0.00')
        for restaurant in restaurants:
            if restaurant.location.lower() == 'ogoja':
                delivery_fee += Decimal('1000.00')
            elif restaurant.location.lower() == 'okuku':
                delivery_fee += Decimal('2000.00')
            # Add more locations as needed

        total_amount += delivery_fee

        # Create separate orders for each restaurant
        orders = []
        for restaurant in restaurants:
            restaurant_items = [item for item in order_items if item['restaurant'] == restaurant]
            restaurant_total = sum(item['price'] * item['quantity'] for item in restaurant_items)
            
            order = Order.objects.create(
                customer=request.user.customer,
                restaurant=restaurant,
                total_amount=restaurant_total,
                delivery_fee=delivery_fee / len(restaurants),  # Split delivery fee equally among restaurants
                payment_method=request.POST.get('payment_method', 'unknown')
            )
            
            for item in restaurant_items:
                OrderItem.objects.create(
                    order=order,
                    food=item['food'],
                    quantity=item['quantity'],
                    price=item['price']
                )
            
            orders.append(order)

        # Store order IDs in session for order confirmation page
        request.session['recent_order_ids'] = [order.id for order in orders]

        # Clear the cart after successful checkout
        request.session['cart'] = {}
        
        # Redirect to order confirmation page
        return redirect('order_confirmation')
    
    # Render the checkout page for GET requests
    return render(request, 'eatwellapp/checkout.html', {'cart': request.session.get('cart', {})})


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
    
    # Store the order ID in the session
    request.session['recent_order_ids'] = [order.id]
    
    return redirect('order_confirmation')

@login_required
def order_confirmation(request):
    # Fetch the most recent orders for the current user
    recent_order_ids = request.session.get('recent_order_ids', [])
    
    if recent_order_ids:
        recent_orders = Order.objects.filter(id__in=recent_order_ids).order_by('-created_at')
    else:
        # If no recent order IDs in session, get the latest order
        recent_orders = Order.objects.filter(customer=request.user.customer).order_by('-created_at')[:1]
    
    total_amount = sum(order.total_amount for order in recent_orders)
    total_delivery_fee = sum(order.delivery_fee for order in recent_orders)

    context = {
        'orders': recent_orders,
        'total_amount': total_amount,
        'total_delivery_fee': total_delivery_fee,
        'grand_total': total_amount + total_delivery_fee
    }

    # Clear the recent order IDs from the session
    if 'recent_order_ids' in request.session:
        del request.session['recent_order_ids']

    return render(request, 'eatwellapp/order_confirmation.html', context)

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
    
    # Store the order ID in the session
    request.session['recent_order_ids'] = [order.id]
    
    return redirect('order_confirmation')

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


