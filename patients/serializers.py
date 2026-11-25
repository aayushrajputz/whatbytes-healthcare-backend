from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            'id',
            'name',
            'age',
            'gender',
            'contact_number',
            'address',
            'created_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_age(self, value):
        if value < 0 or value > 130:
            raise serializers.ValidationError('Age must be between 0 and 130.')
        return value

    def validate_contact_number(self, value):
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in '+-() ')
        if cleaned != value or len(''.join(ch for ch in value if ch.isdigit())) < 7:
            raise serializers.ValidationError('Enter a valid contact number.')
        return value
