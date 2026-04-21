from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductImportRowDTO:
    category_name: str
    category_type: str
    name: str
    sku: str
    price: Decimal
    description: str
    is_active: bool
    is_featured: bool
