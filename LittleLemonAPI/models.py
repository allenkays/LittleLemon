from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "categories"


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True, default=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.title} ({self.category.title})"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menuitem.title} for {self.user.username}"

    def save(self, *args, **kwargs):
        # Ensure price is consistent with unit_price * quantity
        self.unit_price = self.menuitem.price
        self.price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'menuitem'], name='unique_cart_item'),
            models.CheckConstraint(check=models.Q(quantity__gte=1), name='quantity_gte_1'),
        ]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="delivery_crew_orders",
        null=True,
        blank=True
    )
    status = models.BooleanField(db_index=True, default=0)  # 0 = out for delivery, 1 = delivered
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True, auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} on {self.date}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menuitem.title} in Order {self.order.id}"

    def save(self, *args, **kwargs):
        # Ensure price is consistent with unit_price * quantity
        self.unit_price = self.menuitem.price
        self.price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'menuitem'], name='unique_order_item'),
            models.CheckConstraint(check=models.Q(quantity__gte=1), name='quantity_gte_1'),
        ]