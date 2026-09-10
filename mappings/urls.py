from django.urls import path
from mappings.views import (
    MappingDetailOrPatientDoctorsView,
    MappingListCreateView,
    PatientDoctorsListView,
)

urlpatterns = [
    # List all mappings of current user's patients, or create a new mapping
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),

    # Option A Clean RESTful route for retrieving patient's doctors
    path('patient/<int:patient_id>/', PatientDoctorsListView.as_view(), name='patient-doctors-clean'),

    # Dual-compatible endpoint matching assessment requirement:
    # GET /api/mappings/<patient_id>/ -> returns patient's doctors
    # DELETE /api/mappings/<mapping_id>/ -> deletes mapping by ID
    path('<int:pk>/', MappingDetailOrPatientDoctorsView.as_view(), name='mapping-detail-resolver'),
]
