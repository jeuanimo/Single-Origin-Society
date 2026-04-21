from django.contrib import admin
from .models import FundraisingCampaign, Donation


@admin.register(FundraisingCampaign)
class FundraisingCampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "goal_amount", "raised_amount", "percent_raised"]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ["campaign", "donor_name", "amount", "created_at"]
