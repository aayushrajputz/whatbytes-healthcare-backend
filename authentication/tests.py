from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_returns_jwt_tokens(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'Str0ng!Passw0rd',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_login_returns_jwt_tokens(self):
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='Str0ng!Passw0rd',
        )
        response = self.client.post(
            '/api/auth/login/',
            {'identifier': 'test@example.com', 'password': 'Str0ng!Passw0rd'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_rejects_bad_password(self):
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='Str0ng!Passw0rd',
        )
        response = self.client.post(
            '/api/auth/login/',
            {'identifier': 'test@example.com', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
