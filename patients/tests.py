from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Patient

User = get_user_model()


class PatientScopingTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            username='a@example.com', email='a@example.com', password='pass1234'
        )
        self.user_b = User.objects.create_user(
            username='b@example.com', email='b@example.com', password='pass1234'
        )
        self.patient = Patient.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            contact_number='+15551234567',
            created_by=self.user_a,
        )

    def test_list_returns_only_own_patients(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], str(self.patient.id))

        self.client.force_authenticate(user=self.user_b)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_cannot_retrieve_other_users_patient(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(f'/api/patients/{self.patient.id}/')
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_patient(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.delete(f'/api/patients/{self.patient.id}/')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Patient.objects.filter(pk=self.patient.id).exists())

    def test_create_sets_created_by_request_user(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.post(
            '/api/patients/',
            {
                'name': 'Jane Roe',
                'age': 30,
                'gender': 'Female',
                'contact_number': '+15557654321',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['created_by'], self.user_b.id)
