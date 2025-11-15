import random
import uuid
import string

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)    

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.first_name + " " + self.last_name

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        db_table = "category"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    sub_category_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        unique_together = ("category", "name")
        db_table = "sub_category"

    def __str__(self):
        return self.name

class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    external_id = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)
    description = models.TextField(null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return self.name
        
    class Meta:
	    db_table = 'item'
        
class Order(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    date_created = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=6, unique=True, editable=False, db_index=True)

    class Meta:
        db_table = "order"

    def __str__(self):
        return f"{self.external_id} - {self.user} - {self.date_created}"

    def generate_external_id(self):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))

    def save(self, *args, **kwargs):
  
        if not self.external_id:
            external_id = self.generate_external_id()
            while Order.objects.filter(external_id=external_id).exists():
                external_id = self.generate_external_id()
            self.external_id = external_id

        super().save(*args, **kwargs)

class OrderStatus(models.Model):
    order_status_id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "order_status"

    def __str__(self):
        return self.status

class OrderStatusHistory(models.Model):
    order_status_history_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="statuses")
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, related_name="order_history")
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_status_history"
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.order} - {self.status} @ {self.date_created}"

class OrderItem(models.Model):
    order_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} (Order #{self.order.id})"
    
    class Meta:
	    db_table = 'order_item'

class Cart(models.Model):
    cart_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)
    
    class Meta:
	    db_table = 'cart'


class CartItem(models.Model):
    cart_item_id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
	    db_table = 'cart_item'
	    
class OrderFulfillment(models.Model):
    FULFILLMENT_TYPES = (
        ("pickup", "Pickup"),
        ("delivery", "Delivery"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="fulfillment")
    type = models.CharField(max_length=20, choices=FULFILLMENT_TYPES)

    class Meta:
        db_table = "order_fulfillment"

    def __str__(self):
        return f"Fulfillment ({self.get_type_display()}) for Order {self.order.external_id}"

class DeliveryWindow(models.Model):
    WINDOW_TYPES = (
        ("lax", "Lax – 5 hour window, prior-day delivery"),
        ("strict", "Strict – 2 hour window, prior-day delivery"),
        ("same_day", "Same-Day – 2 hour window"),
        ("exact", "Exact-Time"),
    )

    type = models.CharField(max_length=20, choices=WINDOW_TYPES, unique=True)
    window_hours = models.PositiveIntegerField(default=0)
    prior_day_delivery = models.BooleanField(default=False)
    same_day_delivery = models.BooleanField(default=False)
    exact_time_required = models.BooleanField(default=False)
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        db_table = "delivery_window"

    def __str__(self):
        return f"{self.get_type_display()} (x{self.price_multiplier})"

class DeliveryFulfillment(models.Model):
    fulfillment = models.OneToOneField(OrderFulfillment, on_delete=models.CASCADE, related_name="delivery_details")
    delivery_date = models.DateField()
    pickup_date = models.DateField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    window = models.ForeignKey(DeliveryWindow, on_delete=models.PROTECT)

    class Meta:
        db_table = "delivery_fulfillment"

    def __str__(self):
        return f"Delivery for Order {self.fulfillment.order.external_id}"

    @property
    def price_adjustment(self):
        return self.window.price_multiplier

class PickupFulfillment(models.Model):
    fulfillment = models.OneToOneField(OrderFulfillment, on_delete=models.CASCADE, related_name="pickup_details")
    pickup_location = models.CharField(max_length=255)
    pickup_time = models.DateTimeField()

    class Meta:
        db_table = "pickup_fulfillment"

    def __str__(self):
        return f"Pickup for Order {self.fulfillment.order.external_id}"