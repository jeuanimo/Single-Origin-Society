from django.core.management.base import BaseCommand

from products.models import Category


CATEGORY_SEED_DATA = {
    "coffee": [
        "Coffee",
        "Bali",
        "Brazil",
        "Colombia",
        "Costa Rica",
        "Ethiopia (Natural)",
        "Guatemala",
        "Honduras",
        "Robusta",
        "Kenya",
        "Mexico",
        "Nicaragua",
        "Papua New Guinea",
        "Peru",
        "Sumatra",
        "Tanzania",
        "Uganda",
    ],
    "tea": [
        "Tea",
        "Jasmine",
        "English Breakfast",
        "Masala Chai",
        "Earl Grey",
        "Peach Paradise",
        "Mango Treat",
        "Moroccan Mint",
        "Apple Cider Rooibos",
        "Hibiscus Berry",
        "Hojicha",
        "Matcha",
    ],
    "accessories": [
        "Accessories",
        "Grinders",
        "Kettles",
        "Drippers",
        "Filters",
        "Scales",
        "Canisters",
        "Infusers",
        "Matcha tools",
        "Cleaning tools",
    ],
    "drinkware": [
        "Drinkware",
        "Matte mugs",
        "Double-walled glass mugs",
        "Tumblers",
        "Tasting glasses",
    ],
    "gift_sets": [
        "Gift Sets",
        "Morning Ritual Box",
        "Coffee Lover's Set",
        "Tea Ritual Set",
        "Fundraiser Gift Box",
    ],
}

TYPE_SORT_BASE = {
    "coffee": 100,
    "tea": 200,
    "accessories": 300,
    "drinkware": 400,
    "gift_sets": 500,
}


class Command(BaseCommand):
    help = "Seed product catalog categories for storefront browsing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Deactivate existing categories that are not in the seed list.",
        )

    def _upsert_category(self, category_type, name, sort_order):
        category, created = Category.objects.get_or_create(
            name=name,
            category_type=category_type,
            defaults={
                "sort_order": sort_order,
                "is_active": True,
            },
        )

        changed = False
        if category.sort_order != sort_order:
            category.sort_order = sort_order
            changed = True
        if not category.is_active:
            category.is_active = True
            changed = True

        if changed:
            category.save(update_fields=["sort_order", "is_active"])

        return category.slug, created, changed

    def _deactivate_missing_categories(self, kept_slugs):
        return (
            Category.objects.exclude(slug__in=kept_slugs)
            .exclude(is_active=False)
            .update(is_active=False)
        )

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        kept_slugs = []

        for category_type, names in CATEGORY_SEED_DATA.items():
            base = TYPE_SORT_BASE[category_type]
            for index, name in enumerate(names, start=1):
                target_sort = base + index
                slug, created, changed = self._upsert_category(category_type, name, target_sort)

                if created:
                    created_count += 1
                elif changed:
                    updated_count += 1

                kept_slugs.append(slug)

        deactivated_count = 0
        if options["deactivate_missing"]:
            deactivated_count = self._deactivate_missing_categories(kept_slugs)

        self.stdout.write(self.style.SUCCESS("Catalog categories seeded successfully."))
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        if options["deactivate_missing"]:
            self.stdout.write(f"Deactivated: {deactivated_count}")
