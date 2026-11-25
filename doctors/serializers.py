from rest_framework import serializers

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'specialization',
            'email',
            'phone_number',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_phone_number(self, value):
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '+-() ')
        if cleaned != value or len(''.join(ch for ch in value if ch.isdigit())) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return value
