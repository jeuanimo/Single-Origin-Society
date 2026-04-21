from django.contrib import admin
from .models import Campaign, Coupon, EmailSubscriber, CampaignLandingPage, HomepagePromoBlock


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "status", "budget", "spend"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "is_active"]


@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "source", "utm_source", "utm_campaign", "is_active", "subscribed_at"]
    search_fields = ["email", "first_name", "source", "referral_code", "utm_source", "utm_campaign"]


@admin.register(CampaignLandingPage)
class CampaignLandingPageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "campaign", "is_active", "updated_at"]
    list_filter = ["is_active", "campaign"]
    search_fields = ["title", "slug", "meta_title", "meta_description", "og_title"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(HomepagePromoBlock)
class HomepagePromoBlockAdmin(admin.ModelAdmin):
    list_display = ["title", "key", "tone", "sort_order", "is_active"]
    list_filter = ["tone", "is_active"]
    search_fields = ["title", "key", "subtitle", "meta_title", "meta_description"]
