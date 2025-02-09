from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from auth_app.models import User, Organisation

class AuthEndToEndTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        User.objects.all().delete()
        Organisation.objects.all().delete()

    def test_register_user_successfully(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "securepassword",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Registration successful')
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])
        
        # Validate the user and organisation in the database
        user = User.objects.get(email='john@example.com')
        org = Organisation.objects.get(name="John's Organisation")
        self.assertIn(user, org.users.all())

    def test_register_user_missing_fields(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "email": "john@example.com",
            "password": "securepassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        
        # Assert errors
        self.assertIn('errors', response.data)
        self.assertIn('lastName', response.data['errors'])
        self.assertEqual(response.data['errors']['lastName'][0].code, 'required')

    def test_register_user_duplicate_email(self):
        # First registration
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "securepassword",
            "phone": "1234567890"
        }
        self.client.post(url, data, format='json')

        # Second registration with the same email
        data['firstName'] = "Jane"
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        
        # Assert errors
        self.assertIn('errors', response.data)
        self.assertIn('email', response.data['errors'])
        self.assertEqual(response.data['errors']['email'][0].code, 'unique')

    def test_login_user_successfully(self):
        # Register a user first
        self.test_register_user_successfully()

        # Login
        url = reverse('login')
        data = {
            "email": "john@example.com",
            "password": "securepassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])

    def test_login_user_invalid_credentials(self):
        url = reverse('login')
        data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Authentication failed')
