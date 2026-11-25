from rest_framework import serializers

from doctors.models import Doctor
from patients.models import Patient

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor'
    )

    class Meta:
        model = PatientDoctorMapping
        fields = ('id', 'patient_id', 'doctor_id', 'assigned_at')
        read_only_fields = ('id', 'assigned_at')

    def validate(self, attrs):
        request = self.context.get('request')
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        if request and patient and patient.created_by_id != request.user.id:
            raise serializers.ValidationError(
                {'patient_id': 'You can only map doctors to patients you created.'}
            )

        if patient and doctor and PatientDoctorMapping.objects.filter(
            patient=patient, doctor=doctor
        ).exists():
            raise serializers.ValidationError(
                {'detail': 'This doctor is already assigned to this patient.'}
            )
        return attrs
