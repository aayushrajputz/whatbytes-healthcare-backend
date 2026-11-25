from rest_framework import viewsets

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    queryset = Doctor.objects.all()
