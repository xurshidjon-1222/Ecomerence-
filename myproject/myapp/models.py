from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Member(models.Model):
    ism = models.CharField("Ism", max_length=20)
    familiya = models.CharField("Familiya", max_length=25)
    yosh = models.IntegerField(null=True)
    email = models.EmailField("Email")

    def __str__(self):
        return self.ism + " " + self.familiya


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Mahsulot nomi", max_length=200)
    image = models.ImageField(upload_to="media")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    views = models.PositiveIntegerField(default=0)

    likes = models.ManyToManyField(
        User,
        related_name="likes_products",
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True
    )

    def like_soni(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
    Product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    User = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(
        choices=[(i, f"{i} Yulduz") for i in range(1, 6)],
        default=5,
        verbose_name="Reyting"
    )

    comment = models.TextField(verbose_name="Izoh")

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sana"
    )

    def __str__(self):
        return f"{self.User.username} - {self.Product.name} ({self.rating})"

class wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name = 'wishlist')
    products = models.ForeignKey(User,on_delete=models.CASCADE,related_name = 'wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'products')

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Savat #{self.id} - {self.user.username if self.user else 'Mehmon'}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    mahsulot = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.mahsulot.nomi}"

    @property
    def total_price(self):
        return self.mahsulot.narxi * self.quantity
