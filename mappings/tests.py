from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from doctors.models import Doctor
from patients.models import Patient

User = get_user_model()


class MappingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user@example.com', email='user@example.com', password='pass1234'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='pass1234',
        )
        self.patient = Patient.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            contact_number='+15551234567',
            created_by=self.user,
        )
        self.other_patient = Patient.objects.create(
            name='Jane Roe',
            age=30,
            gender='Female',
            contact_number='+15557654321',
            created_by=self.other_user,
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Alice',
            specialization='Cardiology',
            email='alice@hospital.com',
            phone_number='+15559990000',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_mapping(self):
        response = self.client.post(
            '/api/mappings/',
            {'patient_id': str(self.patient.id), 'doctor_id': str(self.doctor.id)},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(response.data['patient_id']), str(self.patient.id))
        self.assertEqual(str(response.data['doctor_id']), str(self.doctor.id))

    def test_duplicate_mapping_returns_400(self):
        payload = {
            'patient_id': str(self.patient.id),
            'doctor_id': str(self.doctor.id),
        }
        self.client.post('/api/mappings/', payload, format='json')
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_cannot_map_other_users_patient(self):
        response = self.client.post(
            '/api/mappings/',
            {
                'patient_id': str(self.other_patient.id),
                'doctor_id': str(self.doctor.id),
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_cannot_delete_other_users_mapping(self):
        self.client.post(
            '/api/mappings/',
            {'patient_id': str(self.patient.id), 'doctor_id': str(self.doctor.id)},
            format='json',
        )
        mapping_id = self.patient.doctor_mappings.first().id

        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f'/api/mappings/{mapping_id}/')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(self.patient.doctor_mappings.exists())
