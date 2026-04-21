import csv
from dataclasses import dataclass, field
from io import TextIOWrapper

from products.models import Category, Product
from .serializers import serialize_product_csv_row


@dataclass
class ProductImportResult:
    created: int = 0
    updated: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


def import_products_csv(uploaded_file):
    result = ProductImportResult()
    wrapped = TextIOWrapper(uploaded_file.file, encoding="utf-8")
    reader = csv.DictReader(wrapped)

    for index, row in enumerate(reader, start=2):
        dto, error = serialize_product_csv_row(row)
        if error:
            result.failed += 1
            result.errors.append(f"Line {index}: {error}")
            continue

        category, _ = Category.objects.get_or_create(
            name=dto.category_name,
            category_type=dto.category_type,
            defaults={"is_active": True},
        )

        product, created = Product.objects.get_or_create(
            sku=dto.sku,
            defaults={
                "name": dto.name,
                "category": category,
                "price": dto.price,
                "description": dto.description,
                "is_active": dto.is_active,
                "is_featured": dto.is_featured,
            },
        )

        if created:
            result.created += 1
            continue

        product.name = dto.name
        product.category = category
        product.price = dto.price
        product.description = dto.description
        product.is_active = dto.is_active
        product.is_featured = dto.is_featured
        product.save(update_fields=["name", "category", "price", "description", "is_active", "is_featured"])
        result.updated += 1

    return result
