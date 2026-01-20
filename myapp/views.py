from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import razorpay
from django.conf import settings

# Create your views here.

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validation
        if not all([name, email, password, confirm_password]):
            messages.error(request, 'All fields are required!')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')
        
        if Register.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'register.html')
        
        Register.objects.create(name=name, email=email, password=password)
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Email and password are required!')
            return render(request, 'login.html')
        
        try:
            user = Register.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            messages.success(request, f'Welcome {user.name}!')
            return redirect('home')
        except Register.DoesNotExist:
            messages.error(request, 'Invalid email or password!')
            return render(request, 'login.html')
    return render(request, 'login.html')

def home(request):
    products=Product.objects.all()
    return render(request,'home.html',{'products':products})

def products(request):
    products=Product.objects.all()
    return render(request,'products.html',{'products':products})

def add_to_cart(request, product_id):
    if 'user_id' not in request.session:
        messages.warning(request, 'Please login first!')
        return redirect('login')
    
    try:
        user = Register.objects.get(id=request.session['user_id'])
        product = Product.objects.get(id=product_id)
        
        cart, created = Cart.objects.get_or_create(user=user, product=product)
        if not created:
            cart.quantity += 1
            cart.save()
        messages.success(request, f'{product.name} added to cart!')
    except Register.DoesNotExist:
        messages.error(request, 'User not found!')
        return redirect('login')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!')
    
    return redirect('cart')

def increase_qty(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
        cart.quantity += 1
        cart.save()
    except Cart.DoesNotExist:
        messages.error(request, 'Cart item not found!')
    return redirect('cart')

def decrease_qty(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.save()
        else:
            cart.delete()
    except Cart.DoesNotExist:
        messages.error(request, 'Cart item not found!')
    return redirect('cart')

def remove_item(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
        cart.delete()
        messages.success(request, 'Item removed from cart!')
    except Cart.DoesNotExist:
        messages.error(request, 'Cart item not found!')
    return redirect('cart')

def cart(request):
    if 'user_id' not in request.session:
        messages.warning(request, 'Please login first!')
        return redirect('login')
    
    try:
        user = Register.objects.get(id=request.session['user_id'])
        cart_items = Cart.objects.filter(user=user)
        total_amount = sum(item.total_price for item in cart_items) if cart_items else 0
        return render(request, 'cart.html', {'cart_items': cart_items, 'total': total_amount})
    except Register.DoesNotExist:
        messages.error(request, 'User not found!')
        return redirect('login')

def checkout(request):
    if 'user_id' not in request.session:
        messages.warning(request, 'Please login first!')
        return redirect('login')
    
    try:
        user = Register.objects.get(id=request.session['user_id'])
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items:
            messages.warning(request, 'Your cart is empty!')
            return redirect('cart')
        
        total_amount = sum(item.total_price for item in cart_items)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'COD')
            
            # Create order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                payment_method=payment_method,
                status="Pending"
            )
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Clear cart
            cart_items.delete()
            
            # Handle payment method
            if payment_method == 'COD':
                order.status = "Order Placed"
                order.save()
                messages.success(request, 'Order placed successfully!')
                return redirect('order_success')
            else:
                # Razorpay Online Payment
                try:
                    client = razorpay.Client(
                        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                    )
                    razorpay_order = client.order.create({
                        'amount': int(total_amount * 100),  # Amount in paise
                        'currency': 'INR',
                        'payment_capture': '1'
                    })
                    
                    return render(request, 'checkout.html', {
                        'total_amount': total_amount,
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'razorpay_order_id': razorpay_order['id'],
                        'order_id': order.id
                    })
                except Exception as e:
                    messages.error(request, f'Payment gateway error: {str(e)}')
                    return redirect('checkout')
        
        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_amount': total_amount
        })
    
    except Register.DoesNotExist:
        messages.error(request, 'User not found!')
        return redirect('login')


def order_success(request):
    return render(request, 'order_success.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if not all([name, email, subject, message]):
            messages.error(request, 'All fields are required!')
            return render(request, 'contact.html')
        
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Thank you! We will contact you soon.')
        return redirect('contact')
    
    return render(request, 'contact.html')

def logout(request):
    request.session.flush()  # Clear session data
    messages.success(request, 'You have been logged out!')
    return redirect('login')

def about(request):
    return render(request, 'about.html')