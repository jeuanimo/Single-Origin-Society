import csv
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q

from content.models import (
    AmbassadorInquiry,
    AmbassadorInquiryNote,
    WholesaleInquiry,
    WholesaleInquiryNote,
)


def filter_wholesale_inquiries(filter_dto):
    inquiries = WholesaleInquiry.objects.select_related("assigned_to", "reviewed_by").all()
    if filter_dto.q:
        inquiries = inquiries.filter(
            Q(name__icontains=filter_dto.q)
            | Q(email__icontains=filter_dto.q)
            | Q(company_name__icontains=filter_dto.q)
            | Q(location__icontains=filter_dto.q)
            | Q(monthly_volume__icontains=filter_dto.q)
        )
    if filter_dto.from_date:
        inquiries = inquiries.filter(created_at__date__gte=filter_dto.from_date)
    if filter_dto.to_date:
        inquiries = inquiries.filter(created_at__date__lte=filter_dto.to_date)
    return inquiries


def filter_ambassador_inquiries(filter_dto):
    inquiries = AmbassadorInquiry.objects.select_related("assigned_to", "reviewed_by").all()
    if filter_dto.q:
        inquiries = inquiries.filter(
            Q(name__icontains=filter_dto.q)
            | Q(email__icontains=filter_dto.q)
            | Q(social_handle__icontains=filter_dto.q)
            | Q(city__icontains=filter_dto.q)
            | Q(audience_size__icontains=filter_dto.q)
        )
    if filter_dto.platform:
        inquiries = inquiries.filter(primary_platform__icontains=filter_dto.platform)
    if filter_dto.from_date:
        inquiries = inquiries.filter(created_at__date__gte=filter_dto.from_date)
    if filter_dto.to_date:
        inquiries = inquiries.filter(created_at__date__lte=filter_dto.to_date)
    return inquiries


def mark_wholesale_reviewed(inquiry, user):
    inquiry.reviewed_by = user
    inquiry.reviewed_at = timezone.now()
    inquiry.save(update_fields=["reviewed_by", "reviewed_at"])


def mark_ambassador_reviewed(inquiry, user):
    inquiry.reviewed_by = user
    inquiry.reviewed_at = timezone.now()
    inquiry.save(update_fields=["reviewed_by", "reviewed_at"])


def assign_wholesale(inquiry, assigned_to_id):
    inquiry.assigned_to_id = assigned_to_id
    inquiry.save(update_fields=["assigned_to"])


def assign_ambassador(inquiry, assigned_to_id):
    inquiry.assigned_to_id = assigned_to_id
    inquiry.save(update_fields=["assigned_to"])


def add_wholesale_note(inquiry, user, body):
    return WholesaleInquiryNote.objects.create(inquiry=inquiry, author=user, body=body)


def add_ambassador_note(inquiry, user, body):
    return AmbassadorInquiryNote.objects.create(inquiry=inquiry, author=user, body=body)


def export_wholesale_csv(queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="wholesale_inquiries.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Submitted",
        "Company",
        "Name",
        "Email",
        "Phone",
        "Location",
        "Monthly Volume",
        "Assigned To",
        "Reviewed At",
        "Reviewed By",
    ])
    for inquiry in queryset:
        writer.writerow([
            inquiry.created_at.isoformat(),
            inquiry.company_name,
            inquiry.name,
            inquiry.email,
            inquiry.phone,
            inquiry.location,
            inquiry.monthly_volume,
            inquiry.assigned_to.get_full_name() if inquiry.assigned_to else "",
            inquiry.reviewed_at.isoformat() if inquiry.reviewed_at else "",
            inquiry.reviewed_by.get_full_name() if inquiry.reviewed_by else "",
        ])
    return response


def export_ambassador_csv(queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="ambassador_inquiries.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Submitted",
        "Name",
        "Email",
        "Social Handle",
        "Platform",
        "Audience",
        "City",
        "Assigned To",
        "Reviewed At",
        "Reviewed By",
    ])
    for inquiry in queryset:
        writer.writerow([
            inquiry.created_at.isoformat(),
            inquiry.name,
            inquiry.email,
            inquiry.social_handle,
            inquiry.primary_platform,
            inquiry.audience_size,
            inquiry.city,
            inquiry.assigned_to.get_full_name() if inquiry.assigned_to else "",
            inquiry.reviewed_at.isoformat() if inquiry.reviewed_at else "",
            inquiry.reviewed_by.get_full_name() if inquiry.reviewed_by else "",
        ])
    return response
