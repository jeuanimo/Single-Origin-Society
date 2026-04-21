from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, TastingNote, BrewingGuide


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class TastingNoteInline(admin.TabularInline):
    model = TastingNote
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category_type", "is_active", "sort_order"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "price", "is_active", "is_featured"]
    list_filter = ["category", "is_active", "is_featured"]
    search_fields = ["name", "sku", "origin", "blend_info", "tags"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline, TastingNoteInline]
    fieldsets = (
        ("Core", {
            "fields": (
                "category", "name", "slug", "sku", "short_description", "description", "price", "compare_price", "cost"
            )
        }),
        ("Editorial Product Details", {
            "fields": (
                "origin", "blend_info", "aroma_profile", "body_profile", "acidity_profile", "finish_profile",
                "steeping_notes", "ritual_description", "available_sizes", "grind_options", "roast_level",
                "flavor_notes", "tags", "weight", "is_subscription_available"
            )
        }),
        ("SEO Metadata", {
            "fields": (
                "meta_title", "meta_description", "og_title", "og_description"
            )
        }),
        ("Media", {"fields": ("image", "image_alt")}),
        ("Visibility", {"fields": ("is_active", "is_featured")}),
    )


@admin.register(BrewingGuide)
class BrewingGuideAdmin(admin.ModelAdmin):
    list_display = ["title", "guide_type", "audience_level", "method", "is_published", "is_premium_featured"]
    list_filter = ["guide_type", "audience_level", "is_published", "is_premium_featured"]
    search_fields = ["title", "method", "description", "tags"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["name", "product", "sku", "size", "grind", "price", "is_active"]
    list_filter = ["is_active", "product"]
    search_fields = ["name", "sku", "product__name"]
