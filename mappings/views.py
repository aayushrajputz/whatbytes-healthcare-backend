from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import MappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    """GET /api/mappings/ — list mappings for the current user's patients.
    POST /api/mappings/ — assign a doctor to a patient."""
    serializer_class = MappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related('patient', 'doctor')

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise ValidationError(
                {'detail': 'This doctor is already assigned to this patient.'}
            )


class PatientMappingsView(generics.ListAPIView):
    """GET /api/mappings/<patient_id>/ — all doctors assigned to a patient."""
    serializer_class = DoctorSerializer

    def get_queryset(self):
        patient = get_object_or_404(
            Patient, pk=self.kwargs['patient_id'], created_by=self.request.user
        )
        return Doctor.objects.filter(
            patient_mappings__patient=patient
        ).distinct()


class MappingDeleteView(APIView):
    """DELETE /api/mappings/<id>/ — remove a mapping by its ID."""

    def delete(self, request, pk):
        mapping = get_object_or_404(
            PatientDoctorMapping.objects.select_related('patient'),
            pk=pk,
            patient__created_by=request.user,
        )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
