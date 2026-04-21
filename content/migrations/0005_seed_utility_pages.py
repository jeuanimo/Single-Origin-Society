from django.db import migrations


UTILITY_PAGES = [
    {
        "slug": "shipping",
        "title": "Shipping Policy",
        "meta_description": "Shipping timelines, delivery methods, and processing details for Single Origin Society orders.",
        "body": "<p>Orders are processed within 1-2 business days. Once fulfilled, you will receive a tracking link by email.</p><p>Standard and expedited shipping options are available at checkout. Shipping windows vary by destination and carrier conditions.</p><p>International shipping availability depends on destination regulations.</p>",
    },
    {
        "slug": "refunds",
        "title": "Refund Policy",
        "meta_description": "Return and refund guidelines for orders placed with Single Origin Society.",
        "body": "<p>If your order arrives damaged or incorrect, contact us within 14 days of delivery and include your order number.</p><p>Eligible products may be refunded, replaced, or issued store credit depending on product condition and category.</p><p>Refunds are returned to the original payment method after review.</p>",
    },
    {
        "slug": "privacy",
        "title": "Privacy Policy",
        "meta_description": "How Single Origin Society collects, uses, and protects personal data.",
        "body": "<p>We collect personal information needed to fulfill orders, provide support, and improve your experience.</p><p>We never sell customer data. Information is shared only with trusted service providers required to operate our business.</p><p>You may contact us anytime to request account or data updates.</p>",
    },
    {
        "slug": "terms",
        "title": "Terms of Service",
        "meta_description": "Terms and conditions governing use of the Single Origin Society website.",
        "body": "<p>By using this website, you agree to these terms and applicable laws.</p><p>Product pricing and availability may change without notice. We reserve the right to update policies and terms as needed.</p><p>Questions about these terms can be sent through our contact page.</p>",
    },
    {
        "slug": "faq",
        "title": "Frequently Asked Questions",
        "meta_description": "Answers to common questions about orders, shipping, freshness, and support.",
        "body": "<h2>How quickly do orders ship?</h2><p>Most orders ship in 1-2 business days.</p><h2>How fresh is your coffee?</h2><p>We roast in small batches and label roast dates whenever possible.</p><h2>Can I get help choosing products?</h2><p>Yes. Use our contact page and we will recommend options based on your taste and brew method.</p>",
    },
    {
        "slug": "wholesale",
        "title": "Wholesale",
        "meta_description": "Partnership inquiries for cafes, hotels, offices, and retail programs.",
        "body": "<p>We partner with hospitality and retail teams looking for exceptional coffee and tea experiences.</p><p>Tell us about your business using the inquiry form below and our team will follow up with next steps.</p>",
    },
    {
        "slug": "ambassador-program",
        "title": "Ambassador Program",
        "meta_description": "Creator and community partnership inquiries for the Single Origin Society ambassador program.",
        "body": "<p>Our ambassador program supports creators and community leaders who share thoughtful ritual and hospitality.</p><p>Complete the application form below and we will review your profile for fit.</p>",
    },
]


def seed_utility_pages(apps, schema_editor):
    page_model = apps.get_model("content", "Page")
    for item in UTILITY_PAGES:
        page_model.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "title": item["title"],
                "body": item["body"],
                "meta_description": item["meta_description"],
                "is_published": True,
            },
        )


def unseed_utility_pages(apps, schema_editor):
    page_model = apps.get_model("content", "Page")
    page_model.objects.filter(slug__in=[item["slug"] for item in UTILITY_PAGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0004_ambassadorinquiry_wholesaleinquiry"),
    ]

    operations = [
        migrations.RunPython(seed_utility_pages, unseed_utility_pages),
    ]
