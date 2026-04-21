from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Customer product review with star rating."""

    STATUS_CHOICES = [
        ("pending", "Pending Moderation"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.rating}★ — {self.product.name} by {self.user.email}"


class ReviewResponse(models.Model):
    """Staff response to a customer review."""

    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name="response")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="review_responses"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to review on {self.review.product.name}"
