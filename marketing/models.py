from django.db import models


class Campaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    ]
    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("social", "Social Media"),
        ("sms", "SMS"),
        ("print", "Print"),
        ("event", "Event"),
    ]
    name = models.CharField(max_length=200)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    target_audience = models.CharField(max_length=300, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def roi(self):
        if self.spend > 0:
            return ((self.revenue or 0) - self.spend) / self.spend * 100
        return 0


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=10, choices=[("percent", "Percent"), ("fixed", "Fixed Amount")])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField(null=True, blank=True)
    times_used = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class EmailSubscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=100, blank=True)
    referral_code = models.CharField(max_length=80, blank=True)
    utm_source = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)
    landing_path = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class CampaignLandingPage(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name="landing_pages")
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=260, blank=True)
    body = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="campaign_landing/", blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=320, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class HomepagePromoBlock(models.Model):
    TONE_CHOICES = [
        ("cream", "Cream"),
        ("dark", "Dark"),
    ]

    key = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=260, blank=True)
    body = models.TextField(blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="homepage_promos/", blank=True)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default="cream")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title


class PromoCode(Coupon):
    class Meta:
        proxy = True
        verbose_name = "promo code"
        verbose_name_plural = "promo codes"
