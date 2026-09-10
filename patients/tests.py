from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from patients.models import Patient

User = get_user_model()


class PatientAPITests(APITestCase):
    """
    Test suite for Patient CRUD and ownership/authorization isolation.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='doctor1@hospital.com',
            name='Dr. User One',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='doctor2@hospital.com',
            name='Dr. User Two',
            password='Password123!'
        )

        self.client.force_authenticate(user=self.user1)

        self.patient_payload = {
            'name': 'Jane Doe',
            'age': 34,
            'gender': 'Female',
            'phone': '+15551234567',
            'address': '123 Main Street, Springfield',
            'medical_history': 'No known drug allergies.',
        }
        self.list_url = reverse('patient-list')

    def test_unauthenticated_access_rejected(self):
        """Unauthenticated requests must be rejected with 401 Unauthorized."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_patient_creation(self):
        """Authenticated user can create a patient record, with ownership set automatically."""
        response = self.client.post(self.list_url, self.patient_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Jane Doe')
        self.assertEqual(response.data['created_by'], self.user1.email)

        # Verify in database
        patient = Patient.objects.get(id=response.data['id'])
        self.assertEqual(patient.created_by, self.user1)

    def test_client_cannot_override_patient_owner(self):
        """Attempts to pass a different created_by in the payload must be ignored."""
        payload = self.patient_payload.copy()
        payload['created_by'] = self.user2.id
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.user1.email)

    def test_user_can_only_see_own_patients(self):
        """User A must see only their own patients; User B's patients must not be visible."""
        Patient.objects.create(created_by=self.user1, **self.patient_payload)
        Patient.objects.create(
            created_by=self.user2,
            name='User 2 Patient',
            age=50,
            gender='Male',
            phone='+15559876543',
            address='456 Elm St'
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Jane Doe')

    def test_user_cannot_retrieve_another_users_patient_by_id(self):
        """IDOR Prevention: Accessing another user's patient ID must return 404 Not Found."""
        patient2 = Patient.objects.create(
            created_by=self.user2,
            name='User 2 Patient',
            age=40,
            gender='Male',
            phone='+15559876543',
            address='456 Elm St'
        )
        detail_url = reverse('patient-detail', kwargs={'pk': patient2.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_update_by_owner(self):
        """Patient owner can update record details."""
        patient = Patient.objects.create(created_by=self.user1, **self.patient_payload)
        detail_url = reverse('patient-detail', kwargs={'pk': patient.id})
        update_data = self.patient_payload.copy()
        update_data['name'] = 'Jane Doe Updated'
        update_data['age'] = 35

        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Jane Doe Updated')
        self.assertEqual(response.data['age'], 35)

    def test_patient_delete_by_owner(self):
        """Patient owner can delete their record."""
        patient = Patient.objects.create(created_by=self.user1, **self.patient_payload)
        detail_url = reverse('patient-detail', kwargs={'pk': patient.id})

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())

    def test_patient_invalid_age(self):
        """Age validation rejects negative values and unrealistic human lifespans (>120)."""
        payload = self.patient_payload.copy()
        payload['age'] = -5
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)

        payload['age'] = 150
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)

    def test_patient_invalid_phone(self):
        """Invalid phone formats must be rejected."""
        payload = self.patient_payload.copy()
        payload['phone'] = 'invalid-phone-number'
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
