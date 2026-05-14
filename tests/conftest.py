import pytest
from rest_framework.test import APIClient

from departments.models import Department


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def root_department():
    return Department.objects.create(
        name='Backend'
    )


@pytest.fixture
def child_department(root_department):
    return Department.objects.create(
        name='API',
        parent=root_department,
    )
