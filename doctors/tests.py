from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Doctor

User = get_user_model()

DOCTOR_PAYLOAD = {
    'name': 'Dr. Alice',
    'specialization': 'Cardiology',
    'email': 'alice@hospital.com',
    'phone_number': '+15559990000',
}


class DoctorPermissionTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='pass1234',
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username='user@example.com', email='user@example.com', password='pass1234'
        )
        self.doctor = Doctor.objects.create(**DOCTOR_PAYLOAD)

    def test_authenticated_user_can_list_doctors(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_non_staff_cannot_create_doctor(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/doctors/', DOCTOR_PAYLOAD, format='json')
        self.assertEqual(response.status_code, 403)

    def test_non_staff_cannot_delete_doctor(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/doctors/{self.doctor.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Doctor.objects.filter(pk=self.doctor.id).exists())

    def test_staff_can_create_and_delete_doctor(self):
        self.client.force_authenticate(user=self.staff)
        new_doctor = {**DOCTOR_PAYLOAD, 'email': 'bob@hospital.com'}
        response = self.client.post('/api/doctors/', new_doctor, format='json')
        self.assertEqual(response.status_code, 201)

        response = self.client.delete(f'/api/doctors/{self.doctor.id}/')
        self.assertEqual(response.status_code, 204)

    def test_staff_cannot_delete_doctor_with_mappings(self):
        from patients.models import Patient
        from mappings.models import PatientDoctorMapping

        patient = Patient.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            contact_number='+15551234567',
            created_by=self.user,
        )
        PatientDoctorMapping.objects.create(patient=patient, doctor=self.doctor)

        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(f'/api/doctors/{self.doctor.id}/')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Doctor.objects.filter(pk=self.doctor.id).exists())
