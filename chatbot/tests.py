from django.test import TestCase, Client
from django.urls import reverse

from .models import Intent


class ChatbotReplyTests(TestCase):
    def setUp(self):
        Intent.objects.create(
            name="Opening hours",
            trigger_phrases="opening hours\nwhat time",
            response="We're online 24/7 — our Nairobi studio is open Mon-Fri, 9am-5pm EAT.",
            is_active=True,
        )
        self.client = Client()

    def test_matches_intent(self):
        response = self.client.post(
            reverse("chatbot:message"),
            data='{"message": "what are your opening hours?"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["matched"])

    def test_falls_back_when_no_match(self):
        response = self.client.post(
            reverse("chatbot:message"),
            data='{"message": "asdkjaslkdj random text"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["matched"])

    def test_rejects_empty_message(self):
        response = self.client.post(
            reverse("chatbot:message"),
            data='{"message": ""}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
