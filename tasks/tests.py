from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class RateLimitedAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = '/rate-limited/'  # URL for your rate-limited endpoint

    def test_rate_limit_enforced(self):
        # Make 5 successful requests (within the limit)
        for _ in range(5):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], "This is a rate-limited endpoint.")

        # 6th request should be blocked
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['detail'], "Rate limit exceeded. Try again later.")

    def test_rate_limit_resets_after_timeout(self):
        # Hit the rate limit first
        for _ in range(5):
            self.client.get(self.url)

        # Wait for 60 seconds (mock time delay for testing)
        from django.core.cache import cache
        cache.clear()  # Clear the cache to simulate timeout reset

        # Now the request should be accepted again
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "This is a rate-limited endpoint.")
