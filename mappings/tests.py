from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient

User = get_user_model()


class MappingAPITests(APITestCase):
    """
    Test suite for Patient-Doctor Mappings, ownership authorization,
    duplicate prevention, and endpoint conflict resolution.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='physician1@clinic.com',
            name='Dr. User One',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='physician2@clinic.com',
            name='Dr. User Two',
            password='Password123!'
        )

        self.patient1 = Patient.objects.create(
            created_by=self.user1,
            name='Patient One',
            age=45,
            gender='Male',
            phone='+15551112222',
            address='100 Main St'
        )
        self.patient2 = Patient.objects.create(
            created_by=self.user2,
            name='Patient Two',
            age=30,
            gender='Female',
            phone='+15553334444',
            address='200 Oak St'
        )

        self.doctor1 = Doctor.objects.create(
            created_by=self.user1,
            name='Dr. Strange',
            specialization='Neurochirurgery',
            phone='+15557778888',
            email='strange@clinic.com'
        )
        self.doctor2 = Doctor.objects.create(
            created_by=self.user1,
            name='Dr. Watson',
            specialization='General Practice',
            phone='+15558889999',
            email='watson@clinic.com'
        )

        self.client.force_authenticate(user=self.user1)
        self.list_create_url = reverse('mapping-list-create')

    def test_create_mapping_success(self):
        """User can assign a doctor to a patient they own."""
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id,
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient'], self.patient1.id)
        self.assertEqual(response.data['doctor'], self.doctor1.id)
        self.assertTrue(
            PatientDoctorMapping.objects.filter(patient=self.patient1, doctor=self.doctor1).exists()
        )

    def test_prevent_duplicate_mapping(self):
        """Re-assigning the same doctor to the same patient must be rejected."""
        PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id,
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_prevent_assigning_doctor_to_another_users_patient(self):
        """Security: User 1 cannot assign a doctor to User 2's patient."""
        payload = {
            'patient': self.patient2.id,  # Owned by User 2
            'doctor': self.doctor1.id,
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data)

    def test_list_mappings_returns_only_owned_patients_mappings(self):
        """Listing mappings must only return mappings for patients created by the authenticated user."""
        mapping1 = PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        # Mapping for User 2's patient
        PatientDoctorMapping.objects.create(patient=self.patient2, doctor=self.doctor2)

        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], mapping1.id)

    def test_get_doctors_for_patient_endpoint(self):
        """GET /api/mappings/<patient_id>/ returns all doctors assigned to that patient."""
        PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor2)

        # Testing assessment compatible endpoint /api/mappings/<patient_id>/
        resolver_url = reverse('mapping-detail-resolver', kwargs={'pk': self.patient1.id})
        response = self.client.get(resolver_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        doctor_names = [item['doctor_name'] for item in response.data]
        self.assertIn('Dr. Strange', doctor_names)
        self.assertIn('Dr. Watson', doctor_names)

        # Testing Option A endpoint /api/mappings/patient/<patient_id>/
        option_a_url = reverse('patient-doctors-clean', kwargs={'patient_id': self.patient1.id})
        response_a = self.client.get(option_a_url)
        self.assertEqual(response_a.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_a.data), 2)

    def test_get_doctors_for_another_users_patient_forbidden(self):
        """User cannot retrieve doctors for a patient owned by someone else."""
        PatientDoctorMapping.objects.create(patient=self.patient2, doctor=self.doctor1)

        resolver_url = reverse('mapping-detail-resolver', kwargs={'pk': self.patient2.id})
        response = self.client.get(resolver_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_mapping_by_id(self):
        """DELETE /api/mappings/<mapping_id>/ deletes the mapping if user owns the patient."""
        mapping = PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        delete_url = reverse('mapping-detail-resolver', kwargs={'pk': mapping.id})

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

    def test_delete_mapping_belonging_to_another_users_patient_forbidden(self):
        """User cannot delete a mapping for another user's patient."""
        mapping2 = PatientDoctorMapping.objects.create(patient=self.patient2, doctor=self.doctor1)
        delete_url = reverse('mapping-detail-resolver', kwargs={'pk': mapping2.id})

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(id=mapping2.id).exists())
