from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, F, Avg
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Product

from .models import Member, Product, Category, Review,wishlist
from .forms import RegisterForm, ReviewForm
from django.contrib.auth.decorators import login_required

# Bosh sahifa
def index(request):
    products = Product.objects.filter(is_active=True)
    query = request.GET.get("q")

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, "index.html", {
        "products": products,
        "query": query
    })


# About
def about(request):
    return render(request, "about.html")


# Contact
def contact(request):
    return render(request, "contact.html")


# Card
def card(request):
    return render(request, "card.html")


# Mahsulotlar
def products(request):
    mahsulotlar = Product.objects.filter(is_active=True)
    query = request.GET.get("q")

    if query:
        mahsulotlar = mahsulotlar.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, "index.html", {
        "products": mahsulotlar,
        "mahsulot": mahsulotlar,
        "query": query
    })


# Ro'yxatdan o'tish
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )

            messages.success(
                request,
                "Muvaffaqiyatli ro'yxatdan o'tdingiz!"
            )
            return redirect("index")

        messages.error(request, "Formani tekshirib qayta kiriting!")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# Tizimga kirish
def login_form(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Tizimga muvaffaqiyatli kirdingiz!")
            return redirect("index")

        messages.error(request, "Login yoki parol xato!")
        return redirect("login")

    return render(request, "login.html")


# Tizimdan chiqish
def logout_view(request):
    logout(request)
    messages.success(request, "Tizimdan chiqdingiz!")
    return redirect("index")


# Mahsulot sahifasi va izohlar
def product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by("-created_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Izoh qoldirish uchun tizimga kiring!")
            return redirect("login")

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.Product = product
            review.User = request.user
            review.save()

            messages.success(request, "Izohingiz muvaffaqiyatli saqlandi!")
            return redirect("product-view", slug=product.slug)

    else:
        form = ReviewForm()

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    if average_rating is None:
        average_rating = 0
    else:
        average_rating = round(average_rating, 1)

    # Bir sessiyada mahsulotni bir marta sanash
    korilgan = request.session.get("korilgan", [])

    if product.id not in korilgan:
        Product.objects.filter(id=product.id).update(
            views=F("views") + 1
        )

        korilgan.append(product.id)
        request.session["korilgan"] = korilgan

    product.refresh_from_db()

    liked = False

    if request.user.is_authenticated:
        liked = product.likes.filter(
            id=request.user.id
        ).exists()

    context = {
        "product": product,
        "liked": liked,
        "reviews": reviews,
        "form": form,
        "average_rating": average_rating
    }

    return render(request, "product.html", context)


# Like bosish
@require_POST
def like_view(request, slug):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, slug=slug)

    if product.likes.filter(id=request.user.id).exists():
        product.likes.remove(request.user)
    else:
        product.likes.add(request.user)

    return redirect("product-view", slug=product.slug)
def wishlist_list(request):
    wishlist_items = wishlist.objects.filter(User=request.user).select_related('product')
    context = {
        'wishlist_items' : wishlist_items
    }
    return render(request, 'wishlist.html',context)


@login_required
def toggle_wishlist(request,products_id):
    product = get_object_or_404(Product,id=products_id)
    wishlist_item , created = wishlist.objects.get_or_create(User=request.user,product=product)

    if not created:
        wishlist_list.delete()
        added = False
    else:
        added = True
    return redirect(request.META.get('HTTP_REFERER','wishlist_list'))

def cart_qism(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')

        if cart_id:
            cart = Cart.objects.filter(id=cart_id, user=None).first()

            if not cart:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

    return cart


def add_to_cart(request, slug):
    mahsulot = get_object_or_404(Product, slug=slug)
    cart = cart_qism(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        mahsulot=mahsulot
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Savatcha qo'shildi")
    return redirect(request.META.get("HTTP_REFERER", "index"))


def cart_detail(request):
    cart = cart_qism(request)

    context = {
        'cart': cart
    }

    return render(request, "cart.html", context)


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()

    messages.success(request, "Mahsulot savatdan olib tashlandi.")
    return redirect('cart_detail')


def cart_qism(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')

        if cart_id:
            cart = Cart.objects.filter(id=cart_id, user=None).first()

            if not cart:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

    return cart


def add_to_cart(request, slug):
    mahsulot = get_object_or_404(Product, slug=slug)
    cart = cart_qism(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        mahsulot=mahsulot
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Savatcha qo'shildi")
    return redirect(request.META.get("HTTP_REFERER", "index"))


def cart_detail(request):
    cart = cart_qism(request)

    context = {
        'cart': cart
    }

    return render(request, "cart.html", context)


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()

    messages.success(request, "Mahsulot savatdan olib tashlandi.")
    return redirect('cart_detail')


