from django.test import TestCase, override_settings
from django.urls import reverse

from orders.models import Order
from products.models import Category, Product


class CheckoutFlowTests(TestCase):
	@override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLIC_KEY="")
	def test_checkout_post_confirms_order_without_stripe(self):
		category = Category.objects.create(name="Coffee", category_type="coffee")
		product = Product.objects.create(
			category=category,
			name="Test Roast",
			sku="TR-001",
			description="Test",
			price="12.50",
		)

		session = self.client.session
		session["cart"] = {str(product.pk): 2}
		session.save()

		response = self.client.post(reverse("checkout:checkout"), {
			"email": "buyer@example.com",
			"first_name": "Ada",
			"last_name": "Buyer",
			"phone": "123456789",
			"shipping_line1": "123 Main",
			"shipping_city": "City",
			"shipping_state": "ST",
			"shipping_postal": "12345",
		})

		self.assertEqual(response.status_code, 302)
		order = Order.objects.latest("id")
		self.assertEqual(order.status, "confirmed")
		self.assertEqual(order.items.count(), 1)

	def test_checkout_get_redirects_when_cart_empty(self):
		response = self.client.get(reverse("checkout:checkout"))
		self.assertEqual(response.status_code, 302)
