from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

# List all products
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})

# Product Details
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/detail.html', {'product': product})

# Add to Cart Logic
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('cart_view')

# View Cart
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total = product.price * quantity
        total_price += total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': total
        })

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items, 
        'total_price': total_price
    })