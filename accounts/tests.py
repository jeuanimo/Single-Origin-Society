from django.test import TestCase
from django.urls import reverse

from .models import ROLE_CONTENT_EDITOR, ROLE_CUSTOMER, User


class PortalPermissionTests(TestCase):
	def test_customer_is_redirected_from_portal(self):
		customer = User.objects.create_user(username="cust", role=ROLE_CUSTOMER)
		self.client.force_login(customer)
		response = self.client.get(reverse("portal:dashboard"))
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse("storefront:home"))

	def test_content_editor_can_access_content_inquiries(self):
		editor = User.objects.create_user(username="editor", role=ROLE_CONTENT_EDITOR)
		self.client.force_login(editor)
		response = self.client.get(reverse("portal:content_wholesale_inquiries"))
		self.assertEqual(response.status_code, 200)
