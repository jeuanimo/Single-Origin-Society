from django.test import TestCase
from django.urls import reverse

from accounts.models import ROLE_CONTENT_EDITOR, ROLE_OPERATIONS_MANAGER, User
from content.models import WholesaleInquiry


class InquiryWorkflowTests(TestCase):
	def setUp(self):
		self.editor = User.objects.create_user(username="editor", role=ROLE_CONTENT_EDITOR)
		self.owner = User.objects.create_user(username="owner", role=ROLE_OPERATIONS_MANAGER)
		self.inquiry = WholesaleInquiry.objects.create(
			name="Jamie",
			email="jamie@example.com",
			company_name="Cafe One",
		)
		self.client.force_login(self.editor)

	def test_wholesale_inquiry_detail_actions(self):
		detail_url = reverse("portal:content_wholesale_inquiry_detail", args=[self.inquiry.pk])

		review_response = self.client.post(detail_url, {"action": "mark_reviewed"})
		self.assertEqual(review_response.status_code, 302)

		assign_response = self.client.post(detail_url, {
			"action": "assign",
			"assign-assigned_to": self.owner.pk,
		})
		self.assertEqual(assign_response.status_code, 302)

		note_response = self.client.post(detail_url, {
			"action": "add_note",
			"note-note": "Follow up Wednesday.",
		})
		self.assertEqual(note_response.status_code, 302)

		self.inquiry.refresh_from_db()
		self.assertIsNotNone(self.inquiry.reviewed_at)
		self.assertEqual(self.inquiry.reviewed_by, self.editor)
		self.assertEqual(self.inquiry.assigned_to, self.owner)
		self.assertEqual(self.inquiry.internal_notes.count(), 1)

	def test_wholesale_export_csv(self):
		response = self.client.get(reverse("portal:content_wholesale_inquiries") + "?export=csv")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "text/csv")
