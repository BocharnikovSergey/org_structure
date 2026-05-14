import pytest

from rest_framework import status


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'payload, expected_status',
    [
        (
            {'name': 'Backend'},
            status.HTTP_201_CREATED,
        ),
        (
            {'name': ''},
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            {'name': '   '},
            status.HTTP_400_BAD_REQUEST,
        ),
    ]
)
def test_create_department(
    api_client,
    payload,
    expected_status,
):
    """Проверяет создание отдела."""

    response = api_client.post(
        '/api/departments/',
        data=payload,
        format='json',
    )

    assert response.status_code == expected_status


def test_department_cycle_validation(
    api_client,
    root_department,
    child_department,
):
    """Проверяет запрет циклов."""

    response = api_client.patch(
        f'/api/departments/{root_department.id}/',
        data={
            'parent': child_department.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    'depth, expected_status',
    [
        (1, status.HTTP_200_OK),
        (3, status.HTTP_200_OK),
        (10, status.HTTP_400_BAD_REQUEST),
    ]
)
def test_depth_validation(
    api_client,
    root_department,
    depth,
    expected_status,
):
    """Проверяет ограничение depth."""

    response = api_client.get(
        f'/api/departments/{root_department.id}/?depth={depth}'
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'mode, expected_status',
    [
        ('cascade', status.HTTP_204_NO_CONTENT),
        ('invalid', status.HTTP_400_BAD_REQUEST),
    ]
)
def test_delete_department_modes(
    api_client,
    root_department,
    mode,
    expected_status,
):
    """Проверяет режимы удаления."""

    response = api_client.delete(
        f'/api/departments/{root_department.id}/?mode={mode}'
    )
    assert response.status_code == expected_status
