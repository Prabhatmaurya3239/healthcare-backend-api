from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor

User = get_user_model()


class DoctorAPITests(APITestCase):
    """
    Test suite for Doctor CRUD endpoints and permissions.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='admin1@hospital.com',
            name='Hospital Admin 1',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='admin2@hospital.com',
            name='Hospital Admin 2',
            password='Password123!'
        )

        self.client.force_authenticate(user=self.user1)

        self.doctor_payload = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'phone': '+15559998888',
            'email': 'house@hospital.com',
        }
        self.list_url = reverse('doctor-list')

    def test_unauthenticated_doctor_access_rejected(self):
        """Unauthenticated requests must be rejected."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor(self):
        """Authenticated user can register a doctor."""
        response = self.client.post(self.list_url, self.doctor_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gregory House')
        self.assertEqual(response.data['created_by'], self.user1.email)

    def test_list_doctors(self):
        """Authenticated users can browse doctors."""
        Doctor.objects.create(created_by=self.user1, **self.doctor_payload)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_doctor(self):
        """Can retrieve individual doctor details."""
        doctor = Doctor.objects.create(created_by=self.user1, **self.doctor_payload)
        detail_url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Diagnostic Medicine')

    def test_update_doctor_by_creator(self):
        """The user who registered the doctor can update details."""
        doctor = Doctor.objects.create(created_by=self.user1, **self.doctor_payload)
        detail_url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        update_data = self.doctor_payload.copy()
        update_data['specialization'] = 'Infectious Disease'

        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Infectious Disease')

    def test_update_doctor_by_non_creator_forbidden(self):
        """Another user cannot update a doctor they did not register."""
        doctor = Doctor.objects.create(created_by=self.user1, **self.doctor_payload)
        self.client.force_authenticate(user=self.user2)
        detail_url = reverse('doctor-detail', kwargs={'pk': doctor.id})
        update_data = self.doctor_payload.copy()
        update_data['name'] = 'Tampered Name'

        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_doctor_by_creator(self):
        """Creator can delete their doctor record."""
        doctor = Doctor.objects.create(created_by=self.user1, **self.doctor_payload)
        detail_url = reverse('doctor-detail', kwargs={'pk': doctor.id})

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())

    def test_delete_doctor_by_non_creator_forbidden(self):
        """Non-creator cannot delete doctor."""
        doctor = Doctor.objects.create(created_by=self.user1, **self.doctor_payload)
        self.client.force_authenticate(user=self.user2)
        detail_url = reverse('doctor-detail', kwargs={'pk': doctor.id})

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Doctor.objects.filter(id=doctor.id).exists())
