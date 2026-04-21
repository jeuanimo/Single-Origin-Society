from django.contrib import admin
from .models import Review, ReviewResponse


class ReviewResponseInline(admin.StackedInline):
    model = ReviewResponse
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "status", "is_verified_purchase", "helpful_count", "created_at")
    list_filter = ("status", "rating", "is_verified_purchase", "created_at")
    search_fields = ("product__name", "user__email", "title", "body")
    inlines = [ReviewResponseInline]
    actions = ["approve_reviews", "reject_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(status="approved")

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.update(status="rejected")
