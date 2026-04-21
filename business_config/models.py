from django.db import models


class BusinessSettings(models.Model):
    """Singleton model for site-wide business settings."""

    store_name = models.CharField(max_length=200, default="Single Origin Society")
    tagline = models.CharField(max_length=300, blank=True, default="Quiet luxury for the intentional palate")
    email = models.EmailField(default="hello@singleoriginsociety.com")
    phone = models.CharField(max_length=30, blank=True, default="")
    address_line1 = models.CharField(max_length=200, blank=True, default="")
    address_line2 = models.CharField(max_length=200, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=50, blank=True, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, default="US")
    currency = models.CharField(max_length=3, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    free_shipping_threshold = models.DecimalField(max_digits=8, decimal_places=2, default=75)
    instagram_url = models.URLField(blank=True, default="")
    facebook_url = models.URLField(blank=True, default="")
    twitter_url = models.URLField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Business Settings"
        verbose_name_plural = "Business Settings"

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
