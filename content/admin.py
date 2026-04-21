from django.contrib import admin
from .models import (
    AmbassadorInquiry,
    AmbassadorInquiryNote,
    BlogPost,
    Page,
    RitualJournalEntry,
    WholesaleInquiry,
    WholesaleInquiryNote,
)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_published"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "entry_type", "status", "author", "is_published", "published_at"]
    list_filter = ["entry_type", "status", "is_published"]
    search_fields = ["title", "excerpt", "body", "tags"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(RitualJournalEntry)
class RitualJournalEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at"]


@admin.register(WholesaleInquiry)
class WholesaleInquiryAdmin(admin.ModelAdmin):
    list_display = ["company_name", "name", "email", "assigned_to", "reviewed_at", "created_at"]
    list_filter = ["reviewed_at", "assigned_to"]
    search_fields = ["company_name", "name", "email", "location"]


@admin.register(AmbassadorInquiry)
class AmbassadorInquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "primary_platform", "assigned_to", "reviewed_at", "created_at"]
    list_filter = ["reviewed_at", "assigned_to", "primary_platform"]
    search_fields = ["name", "email", "social_handle", "primary_platform", "city"]


@admin.register(WholesaleInquiryNote)
class WholesaleInquiryNoteAdmin(admin.ModelAdmin):
    list_display = ["inquiry", "author", "created_at"]
    search_fields = ["inquiry__company_name", "body"]


@admin.register(AmbassadorInquiryNote)
class AmbassadorInquiryNoteAdmin(admin.ModelAdmin):
    list_display = ["inquiry", "author", "created_at"]
    search_fields = ["inquiry__name", "body"]
