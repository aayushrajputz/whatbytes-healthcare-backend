from django.db.models import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Doctor
from .permissions import IsAdminOrReadOnly
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    queryset = Doctor.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            raise ValidationError(
                {'detail': 'Cannot delete a doctor with existing patient mappings.'}
            )
