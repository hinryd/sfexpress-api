from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class APIKey(models.Model):
    """
    API Key model for API authentication
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="A descriptive name for this API key")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a secure random API key"""
        return secrets.token_urlsafe(48)

    def __str__(self):
        return f"{self.name} - {self.key[:8]}..."


class CreditBalance(models.Model):
    """
    Credit system for tracking user API usage
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credit_balance')
    credits = models.IntegerField(default=0)
    total_earned = models.IntegerField(default=0)
    total_spent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_credits(self, amount):
        """Add credits to the user's balance"""
        self.credits += amount
        self.total_earned += amount
        self.save()

    def deduct_credits(self, amount):
        """Deduct credits from the user's balance"""
        if self.credits >= amount:
            self.credits -= amount
            self.total_spent += amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.username} - {self.credits} credits"


class CreditTransaction(models.Model):
    """
    Track credit transactions for auditing
    """
    TRANSACTION_TYPES = (
        ('PURCHASE', 'Purchase'),
        ('API_CALL', 'API Call'),
        ('REFUND', 'Refund'),
        ('ADMIN_ADJUSTMENT', 'Admin Adjustment'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()
    balance_after = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"


class Location(models.Model):
    """
    SF Express locker and shop locations
    """
    LOCATION_TYPES = (
        ('LOCKER', 'Locker'),
        ('SHOP', 'Shop'),
    )

    location_type = models.CharField(max_length=10, choices=LOCATION_TYPES)
    name = models.CharField(max_length=200)
    address = models.TextField()
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    opening_hours = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district', 'name']

    def __str__(self):
        return f"{self.get_location_type_display()} - {self.name}"
