from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("card/", views.card, name="card"),
    path("product/", views.products, name="products"),
    path("login/", views.login_form, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("product/<slug:slug>/", views.product_view, name="product-view"),
    path("likes/<slug:slug>/", views.like_view, name="like"),
   path('wishlist/', views.wishlist_list, name="wishlist_list"),
   path('wishlist/toggle/<int:product_id/', views.toggle_wishlist,name="toggle_wishlist"),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]
