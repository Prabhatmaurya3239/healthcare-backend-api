from django.contrib import admin
from mappings.models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_at')
    list_filter = ('assigned_at',)
    search_fields = ('patient__name', 'doctor__name', 'doctor__specialization')
    readonly_fields = ('assigned_at',)
    ordering = ('-assigned_at',)
