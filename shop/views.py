from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product
from .forms import ProductForm

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



def staff_required(view_func):
    """Same pattern as core.views.staff_required — kept local to this
    app so shop/views.py doesn't need to import from core."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


@staff_required
def admin_products(request):
    queryset = Product.objects.all().order_by('-created_at')

    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category=category)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_count': queryset.count(),
        'category_filter': category,
        'category_choices': Product.CATEGORY_CHOICES,
        'segment': 'admin_products',
    }
    return render(request, 'users/admin_products.html', context)


@staff_required
def admin_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added.')
            return redirect('admin_products')
    else:
        form = ProductForm()

    return render(request, 'users/admin_product_form.html', {
        'form': form,
        'is_edit': False,
        'segment': 'admin_products',
    })


@staff_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated.')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'users/admin_product_form.html', {
        'form': form,
        'is_edit': True,
        'product': product,
        'segment': 'admin_products',
    })


@staff_required
@require_POST
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('admin_products')