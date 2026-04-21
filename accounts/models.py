from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_SUPER_ADMIN = "super_admin"
ROLE_OWNER = "owner"
ROLE_OPERATIONS_MANAGER = "operations_manager"
ROLE_INVENTORY_MANAGER = "inventory_manager"
ROLE_FULFILLMENT_STAFF = "fulfillment_staff"
ROLE_MARKETING_MANAGER = "marketing_manager"
ROLE_CONTENT_EDITOR = "content_editor"
ROLE_CUSTOMER_SUPPORT = "customer_support"
ROLE_FUNDRAISING_COORDINATOR = "fundraising_coordinator"
ROLE_CUSTOMER = "customer"

PERM_DASHBOARD_VIEW = "dashboard.view"
PERM_PRODUCTS_VIEW = "products.view"
PERM_PRODUCTS_MANAGE = "products.manage"
PERM_ORDERS_VIEW = "orders.view"
PERM_ORDERS_MANAGE = "orders.manage"
PERM_FULFILLMENT_MANAGE = "fulfillment.manage"
PERM_INVENTORY_VIEW = "inventory.view"
PERM_INVENTORY_MANAGE = "inventory.manage"
PERM_PURCHASING_VIEW = "purchasing.view"
PERM_PURCHASING_MANAGE = "purchasing.manage"
PERM_SHIPPING_VIEW = "shipping.view"
PERM_SHIPPING_MANAGE = "shipping.manage"
PERM_RETURNS_VIEW = "returns.view"
PERM_RETURNS_MANAGE = "returns.manage"
PERM_CRM_VIEW = "crm.view"
PERM_CRM_MANAGE = "crm.manage"
PERM_SUPPORT_VIEW = "support.view"
PERM_SUPPORT_MANAGE = "support.manage"
PERM_REVIEWS_VIEW = "reviews.view"
PERM_REVIEWS_MODERATE = "reviews.moderate"
PERM_MARKETING_VIEW = "marketing.view"
PERM_MARKETING_MANAGE = "marketing.manage"
PERM_CONTENT_VIEW = "content.view"
PERM_CONTENT_MANAGE = "content.manage"
PERM_FUNDRAISING_VIEW = "fundraising.view"
PERM_FUNDRAISING_MANAGE = "fundraising.manage"
PERM_FINANCE_VIEW = "finance.view"
PERM_FINANCE_MANAGE = "finance.manage"
PERM_REPORTS_VIEW = "reports.view"
PERM_REPORTS_EXPORT = "reports.export"
PERM_NOTES_VIEW = "notes.view"
PERM_NOTES_MANAGE = "notes.manage"
PERM_ACTIVITY_VIEW = "activity.view"
PERM_STAFF_MANAGE = "staff.manage"
PERM_SETTINGS_MANAGE = "settings.manage"


ROLE_PERMISSION_MATRIX = {
    ROLE_SUPER_ADMIN: {"*"},
    ROLE_OWNER: {
        PERM_DASHBOARD_VIEW,
        PERM_PRODUCTS_VIEW, PERM_PRODUCTS_MANAGE,
        PERM_ORDERS_VIEW, PERM_ORDERS_MANAGE,
        PERM_FULFILLMENT_MANAGE,
        PERM_INVENTORY_VIEW, PERM_INVENTORY_MANAGE,
        PERM_PURCHASING_VIEW, PERM_PURCHASING_MANAGE,
        PERM_SHIPPING_VIEW, PERM_SHIPPING_MANAGE,
        PERM_RETURNS_VIEW, PERM_RETURNS_MANAGE,
        PERM_CRM_VIEW, PERM_CRM_MANAGE,
        PERM_SUPPORT_VIEW, PERM_SUPPORT_MANAGE,
        PERM_REVIEWS_VIEW, PERM_REVIEWS_MODERATE,
        PERM_MARKETING_VIEW, PERM_MARKETING_MANAGE,
        PERM_CONTENT_VIEW, PERM_CONTENT_MANAGE,
        PERM_FUNDRAISING_VIEW, PERM_FUNDRAISING_MANAGE,
        PERM_FINANCE_VIEW, PERM_FINANCE_MANAGE,
        PERM_REPORTS_VIEW, PERM_REPORTS_EXPORT,
        PERM_NOTES_VIEW, PERM_NOTES_MANAGE,
        PERM_ACTIVITY_VIEW,
        PERM_STAFF_MANAGE,
        PERM_SETTINGS_MANAGE,
    },
    ROLE_OPERATIONS_MANAGER: {
        PERM_DASHBOARD_VIEW,
        PERM_PRODUCTS_VIEW, PERM_PRODUCTS_MANAGE,
        PERM_ORDERS_VIEW, PERM_ORDERS_MANAGE,
        PERM_FULFILLMENT_MANAGE,
        PERM_INVENTORY_VIEW, PERM_INVENTORY_MANAGE,
        PERM_PURCHASING_VIEW, PERM_PURCHASING_MANAGE,
        PERM_SHIPPING_VIEW, PERM_SHIPPING_MANAGE,
        PERM_RETURNS_VIEW, PERM_RETURNS_MANAGE,
        PERM_CRM_VIEW, PERM_CRM_MANAGE,
        PERM_SUPPORT_VIEW, PERM_SUPPORT_MANAGE,
        PERM_REVIEWS_VIEW, PERM_REVIEWS_MODERATE,
        PERM_REPORTS_VIEW, PERM_REPORTS_EXPORT,
        PERM_NOTES_VIEW, PERM_NOTES_MANAGE,
        PERM_ACTIVITY_VIEW,
    },
    ROLE_INVENTORY_MANAGER: {
        PERM_DASHBOARD_VIEW,
        PERM_PRODUCTS_VIEW,
        PERM_ORDERS_VIEW,
        PERM_FULFILLMENT_MANAGE,
        PERM_INVENTORY_VIEW, PERM_INVENTORY_MANAGE,
        PERM_PURCHASING_VIEW, PERM_PURCHASING_MANAGE,
        PERM_SHIPPING_VIEW,
        PERM_RETURNS_VIEW,
        PERM_REPORTS_VIEW,
    },
    ROLE_FULFILLMENT_STAFF: {
        PERM_DASHBOARD_VIEW,
        PERM_ORDERS_VIEW,
        PERM_FULFILLMENT_MANAGE,
        PERM_INVENTORY_VIEW,
        PERM_SHIPPING_VIEW, PERM_SHIPPING_MANAGE,
        PERM_RETURNS_VIEW, PERM_RETURNS_MANAGE,
    },
    ROLE_MARKETING_MANAGER: {
        PERM_DASHBOARD_VIEW,
        PERM_MARKETING_VIEW, PERM_MARKETING_MANAGE,
        PERM_CONTENT_VIEW,
        PERM_REPORTS_VIEW, PERM_REPORTS_EXPORT,
    },
    ROLE_CONTENT_EDITOR: {
        PERM_DASHBOARD_VIEW,
        PERM_CONTENT_VIEW, PERM_CONTENT_MANAGE,
        PERM_REVIEWS_VIEW, PERM_REVIEWS_MODERATE,
        PERM_REPORTS_VIEW,
    },
    ROLE_CUSTOMER_SUPPORT: {
        PERM_DASHBOARD_VIEW,
        PERM_ORDERS_VIEW,
        PERM_SHIPPING_VIEW,
        PERM_RETURNS_VIEW, PERM_RETURNS_MANAGE,
        PERM_CRM_VIEW, PERM_CRM_MANAGE,
        PERM_SUPPORT_VIEW, PERM_SUPPORT_MANAGE,
        PERM_NOTES_VIEW, PERM_NOTES_MANAGE,
        PERM_ACTIVITY_VIEW,
    },
    ROLE_FUNDRAISING_COORDINATOR: {
        PERM_DASHBOARD_VIEW,
        PERM_FUNDRAISING_VIEW, PERM_FUNDRAISING_MANAGE,
        PERM_CRM_VIEW,
        PERM_REPORTS_VIEW, PERM_REPORTS_EXPORT,
    },
    ROLE_CUSTOMER: set(),
}


LEGACY_ROLE_ALIASES = {
    "admin": ROLE_SUPER_ADMIN,
    "manager": ROLE_OWNER,
    "staff": ROLE_FULFILLMENT_STAFF,
}


class Permission(models.Model):
    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class Role(models.Model):
    code = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, "Super Admin"),
        (ROLE_OWNER, "Owner"),
        (ROLE_OPERATIONS_MANAGER, "Operations Manager"),
        (ROLE_INVENTORY_MANAGER, "Inventory Manager"),
        (ROLE_FULFILLMENT_STAFF, "Fulfillment Staff"),
        (ROLE_MARKETING_MANAGER, "Marketing Manager"),
        (ROLE_CONTENT_EDITOR, "Content Editor"),
        (ROLE_CUSTOMER_SUPPORT, "Customer Support"),
        (ROLE_FUNDRAISING_COORDINATOR, "Fundraising Coordinator"),
        (ROLE_CUSTOMER, "Customer"),
    ]
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    role_profile = models.ForeignKey("accounts.Role", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_portal_user(self):
        # Superusers always have portal access
        if self.is_superuser:
            return True
        return self.normalized_role != ROLE_CUSTOMER

    @property
    def is_manager_or_admin(self):
        return self.normalized_role in {ROLE_SUPER_ADMIN, ROLE_OWNER}

    @property
    def normalized_role(self):
        return LEGACY_ROLE_ALIASES.get(self.role, self.role)

    def has_portal_permission(self, permission_key):
        if not self.is_authenticated:
            return False
        if self.is_superuser:
            return True
        permissions = set(ROLE_PERMISSION_MATRIX.get(self.normalized_role, set()))
        if self.role_profile_id:
            profile_permissions = self.role_profile.permissions.filter(is_active=True).values_list("code", flat=True)
            permissions.update(profile_permissions)
        if "*" in permissions:
            return True
        return permission_key in permissions

    def can_access_module(self, module_name):
        return self.has_portal_permission(f"{module_name}.view") or self.has_portal_permission(f"{module_name}.manage")

    class Meta(AbstractUser.Meta):
        ordering = ["-date_joined"]


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50, default="Home")
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="US")
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.label}: {self.line1}, {self.city}"
