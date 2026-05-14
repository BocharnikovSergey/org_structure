import pytest

from rest_framework import status

from employees.models import Employee


pytestmark = pytest.mark.django_db


def test_create_employee(
    api_client,
    root_department,
):
    """Проверяет создание сотрудника."""

    response = api_client.post(
        f'/api/departments/{root_department.id}/employees/',
        data={
            'full_name': 'Иван Иванов',
            'position': 'Backend Developer',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Employee.objects.count() == 1


def test_delete_department_reassign(
    api_client,
    root_department,
    child_department,
):
    """Проверяет перенос сотрудниковпри удалении отдела."""
    employee = Employee.objects.create(
        department=root_department,
        full_name='Иван Иванов',
        position='Backend Developer',
    )
    response = api_client.delete(
        f'/api/departments/{root_department.id}/'
        f'?mode=reassign'
        f'&reassign_to_department_id={child_department.id}'
    )
    employee.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert employee.department == child_department