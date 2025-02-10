from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('store_owner', 'Store Owner'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_permissions",
        related_query_name="customuser",
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'auth_user'  # This ensures the model uses the auth_user table


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    residential_address = models.CharField(max_length=100)
    location = models.CharField(max_length=10, choices=(('ogoja', 'Ogoja'), ('okuku', 'Okuku')))

    def __str__(self):
        return f"{self.user.username} - {self.location}"

class StoreOwner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store_owner')
    business_name = models.CharField(max_length=100)
    business_location = models.CharField(max_length=10, choices=(('ogoja', 'Ogoja'), ('okuku', 'Okuku')))
    cac_bvn_number = models.CharField(max_length=20, blank=True, null=True)
    business_address = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.business_name} - {self.business_location}"

class Restaurant(models.Model):
    owner = models.ForeignKey(StoreOwner, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=10, choices=(('ogoja', 'Ogoja'), ('okuku', 'Okuku')))

    def __str__(self):
        return f"{self.name} - {self.location}"
    
class Food(models.Model):
    CATEGORY_CHOICES = (
        ('fast', 'Fast'),
        ('drinks', 'Drinks'),
        ('swallow', 'Swallow'),
        ('desserts', 'Desserts'),
    )
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='foods')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='fast')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    weight = models.IntegerField(help_text='Weight in grams', default=0)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=(('online', 'Online'), ('on_delivery', 'On Delivery')))
    address = models.TextField(null=True, blank=True)  # Make address nullable

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username} - {self.address}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.food.name} x{self.quantity} - Order {self.order.id}"


