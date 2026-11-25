from django.urls import path

from .views import MappingDeleteView, MappingListCreateView, PatientMappingsView

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    # UUID patient_id route must precede the integer mapping-id route
    path('<uuid:patient_id>/', PatientMappingsView.as_view(), name='patient-mappings'),
    path('<int:pk>/', MappingDeleteView.as_view(), name='mapping-delete'),
]
