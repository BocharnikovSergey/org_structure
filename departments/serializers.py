from rest_framework import serializers

from .models import Department
from core import constants, validators
from employees.serializers import EmployeeSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    """Сериализатор для отдела"""

    name = serializers.CharField(
        min_length=constants.MIN_LEN_NAME,
        max_length=constants.MAX_LEN_NAME,
        validators=[validators.validate_empty_field])

    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'created_at')


class DepartmentRetrieveQuerySerializer(
    serializers.Serializer
):
    depth = serializers.IntegerField(
        default=constants.DEFAULT_DEPTH,
        min_value=constants.MIN_DEPTH,
        max_value=constants.MAX_DEPTH,
    )
    include_employees = serializers.BooleanField(default=True)


class DepartmentTreeSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'created_at', 'employees', 'children')

    def get_employees(self, obj):
        return (
            EmployeeSerializer(
                obj.employees.all().order_by('full_name'), many=True
            ).data
            if self.context.get('include_employees', True)
            else []
        )

    def get_children(self, obj):
        depth = self.context.get('depth', constants.DEFAULT_DEPTH)
        return (
            DepartmentTreeSerializer(
                obj.children.all(), many=True, context={
                    **self.context,
                    'depth': depth - 1,
                }
            )
        ).data if depth > 0 else []
