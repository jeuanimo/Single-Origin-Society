from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    CATEGORY_TYPES = [
        ("coffee", "Coffee"),
        ("tea", "Tea"),
        ("accessories", "Accessories"),
        ("drinkware", "Drinkware"),
        ("gift_sets", "Gift Sets"),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    image_alt = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    blend_info = models.CharField(max_length=300, blank=True)
    roast_level = models.CharField(max_length=50, blank=True)
    flavor_notes = models.CharField(max_length=300, blank=True)
    aroma_profile = models.CharField(max_length=200, blank=True)
    body_profile = models.CharField(max_length=100, blank=True)
    acidity_profile = models.CharField(max_length=100, blank=True)
    finish_profile = models.CharField(max_length=100, blank=True)
    steeping_notes = models.TextField(blank=True)
    ritual_description = models.TextField(blank=True)
    available_sizes = models.CharField(max_length=200, blank=True)
    grind_options = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=250, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=320, blank=True)
    is_subscription_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("storefront:product_detail", kwargs={"slug": self.slug})

    @property
    def margin(self):
        if self.cost:
            return self.price - self.cost
        return None

    @property
    def stock_available(self):
        if hasattr(self, "stock"):
            return self.stock.available
        return None

    @property
    def in_stock(self):
        available = self.stock_available
        return available is None or available > 0

    @property
    def is_low_stock(self):
        if not hasattr(self, "stock"):
            return False
        return self.stock.needs_reorder and self.stock.available > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]


class ProductVariant(models.Model):
    """Sellable variant options for a product (size, grind, packaging, etc)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=60, blank=True)
    size = models.CharField(max_length=60, blank=True)
    grind = models.CharField(max_length=60, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.product.name} — {self.name}"


class TastingNote(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="tasting_notes")
    title = models.CharField(max_length=100)
    body = models.TextField()
    aroma = models.CharField(max_length=200, blank=True)
    flavor = models.CharField(max_length=200, blank=True)
    finish = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    pairings = models.CharField(max_length=200, blank=True)
    style_notes = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=250, blank=True)
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.title}"


class BrewingGuide(models.Model):
    GUIDE_TYPE_CHOICES = [
        ("pour_over", "Pour-Over"),
        ("french_press", "French Press"),
        ("espresso_basics", "Espresso Basics"),
        ("tea_steeping", "Tea Steeping"),
        ("matcha_preparation", "Matcha Preparation"),
        ("other", "Other"),
    ]
    AUDIENCE_LEVEL_CHOICES = [
        ("beginner", "Beginner-Friendly"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="brewing_guides")
    guide_type = models.CharField(max_length=30, choices=GUIDE_TYPE_CHOICES, default="other")
    audience_level = models.CharField(max_length=20, choices=AUDIENCE_LEVEL_CHOICES, default="beginner")
    tags = models.CharField(max_length=200, blank=True)
    is_premium_featured = models.BooleanField(default=False)
    method = models.CharField(max_length=100)
    description = models.TextField()
    instructions = models.TextField()
    water_temp = models.CharField(max_length=50, blank=True)
    brew_time = models.CharField(max_length=50, blank=True)
    grind_size = models.CharField(max_length=50, blank=True)
    ratio = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to="guides/", blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "product category"
        verbose_name_plural = "product categories"


class BrewGuide(BrewingGuide):
    class Meta:
        proxy = True
        verbose_name = "brew guide"
        verbose_name_plural = "brew guides"
