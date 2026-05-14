import logging

from django.db import transaction
from rest_framework import mixins, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from departments.models import Department
from departments.serializers import (
    DepartmentSerializer, DepartmentTreeSerializer,
    DepartmentRetrieveQuerySerializer,
)
from departments.services import (
    update_department, delete_department, create_employee,
)
from employees.serializers import EmployeeSerializer


logger = logging.getLogger(__name__)


class DepartmentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet для управления отделами."""

    queryset = (
        Department.objects.select_related('parent').prefetch_related(
            'children',
            'employees',
        )
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self) -> serializers.ModelSerializer:
        """Возвращает serializer в зависимости от action."""
        if self.action == 'retrieve':
            return DepartmentTreeSerializer
        elif self.action == 'create_employee':
            return EmployeeSerializer
        return DepartmentSerializer

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Возвращает дерево отделов с ограничением глубины вложенности."""
        department = self.get_object()
        logger.info(f'Запрос на получение отдела id={department.id}')
        query_serializer = (DepartmentRetrieveQuerySerializer(
                data=request.query_params
        ))
        query_serializer.is_valid(raise_exception=True)
        logger.info(
            f'Глубина дерева={query_serializer.validated_data.get("depth")}, '
            f'include_employees={
                query_serializer.validated_data.get("include_employees")
            }'
        )
        serializer = self.get_serializer(
            department,
            context=query_serializer.validated_data,
        )
        return Response(serializer.data)

    @transaction.atomic
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """Частично обновляет отдел."""
        department = self.get_object()
        logger.info(
            f'PATCH запрос на обновление отдела id={department.id}'
        )
        serializer = DepartmentSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        department = update_department(
            department=department,
            data=serializer.validated_data,
        )

        return Response(
            DepartmentSerializer(department).data
        )

    @transaction.atomic
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Удаляет отдел:

        - cascade
        - reassign
        """
        department = self.get_object()

        mode = request.query_params.get('mode')
        logger.info(
            f'DELETE запрос отдела id={department.id}, mode={mode}'
        )
        reassign_id = request.query_params.get(
            'reassign_to_department_id'
        )
        reassign_to = (
            Department.objects.filter(id=reassign_id).first()
            if reassign_id else None
        )

        delete_department(
            department=department,
            mode=mode,
            reassign_to=reassign_to,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=['post'], detail=True, url_path='employees')
    @transaction.atomic
    def create_employee(
        self, request: Request, pk: int | None = None
    ) -> Response:
        """Создаёт сотрудника в отделе."""
        department = self.get_object()
        logger.info(
            f'Создание сотрудника в отделе id={department.id}'
        )

        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = create_employee(
            department=department,
            data=serializer.validated_data,
        )
        return Response(
            EmployeeSerializer(employee).data,
            status=status.HTTP_201_CREATED,
        )
