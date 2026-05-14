from rest_framework import serializers

from .models import Employee
from core import validators, constants


class EmployeeSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(
        min_length=constants.MIN_LEN_NAME,
        max_length=constants.MAX_LEN_NAME,
        validators=[validators.validate_empty_field])
    position = serializers.CharField(
        min_length=constants.MIN_LEN_POSITION,
        max_length=constants.MAX_LEN_POSITION,
        validators=[validators.validate_empty_field])

    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'position', 'hired_at', 'created_at'
        )
        fields_read_only = ('created_at')
