from decimal import Decimal, InvalidOperation

from .dto import ProductImportRowDTO


TRUE_VALUES = {"1", "true", "yes", "y", "on"}


def _to_bool(value):
    return str(value or "").strip().lower() in TRUE_VALUES


def serialize_product_csv_row(row):
    try:
        price = Decimal(str(row.get("price", "0")).strip() or "0")
    except (InvalidOperation, ValueError):
        return None, "Invalid price"

    name = str(row.get("name", "")).strip()
    sku = str(row.get("sku", "")).strip()
    if not name or not sku:
        return None, "Missing required name or sku"

    category_name = str(row.get("category", "")).strip() or "Uncategorized"
    category_type = str(row.get("category_type", "")).strip() or "accessories"
    if category_type not in {"coffee", "tea", "accessories", "drinkware", "gift_sets"}:
        category_type = "accessories"

    dto = ProductImportRowDTO(
        category_name=category_name,
        category_type=category_type,
        name=name,
        sku=sku,
        price=price,
        description=str(row.get("description", "")).strip() or "Imported product",
        is_active=_to_bool(row.get("is_active", "true")),
        is_featured=_to_bool(row.get("is_featured", "false")),
    )
    return dto, None
