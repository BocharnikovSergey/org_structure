import logging

from django.db import transaction
from rest_framework import exceptions

from .models import Department
from employees.models import Employee


logger = logging.getLogger(__name__)


def validate_no_cycles(department: Department, new_parent: Department) -> None:
    """Проверяет отсутствие циклов в дереве отделов."""
    logger.info(f'Проверка отстутствия циклов в {department.name}')
    current = new_parent
    while current:
        if current.id == department.id:
            logger.error(f'Обнаружен цикл в {department.name}')
            raise exceptions.ValidationError('Обнаружен цикл')
        current = current.parent


@transaction.atomic
def update_department(department: Department, data: dict) -> Department:
    """Обновляет отдел и проверяет корректность дерева."""
    logger.info(f'Обновление отдела id={department.id}')

    name = data.get('name')
    parent_id = data.get('parent_id')

    if name:
        logger.info('Обновлено название отдела')
        department.name = name.strip()

    if 'parent_id' in data:
        logger.info(f'Изменение родителя отдела id={department.id}')
        if parent_id == department.id:
            logger.error(f'{department.name} не может быть сам себе родителем')
            raise exceptions.ValidationError(
                'Не может быть сам себе родителем'
            )
        department.parent = (
            None
            if parent_id is None
            else Department.objects.get(id=parent_id)
        )
        if department.parent:
            validate_no_cycles(
                department=department,
                new_parent=department.parent,
            )
        
    department.full_clean()
    department.save()
    return department


@transaction.atomic
def delete_department(
    department: Department,
    mode: str,
    reassign_to: Department | None = None,
) -> None:
    """Удаляет отдел с обработкой дерева и сотрудников."""
    logger.info(
        f'Удаление отдела id={department.id}, mode={mode}'
    )

    if mode not in ('cascade', 'reassign'):
        logger.error(f'Неверный режим удаления: {mode}')
        raise exceptions.ValidationError(
            'Режим должен быть cascade или reassign.'
        )

    if mode == 'reassign':
        if reassign_to is None:
            logger.error(
                f'reassign_to не указан для отдела id={department.id}'
            )
            raise exceptions.ValidationError(
                'reassign_to обязателен для режима reassign'
            )
        elif reassign_to.id == department.id:
            logger.error(
                f'Попытка перенести сотрудников в тот же отдел id={
                    department.id
                }'
            )
            raise exceptions.ValidationError(
                'Нельзя перенести сотрудников в тот же отдел.'
            )
        Employee.objects.filter(department=department).update(
            department=reassign_to
        )

    if mode == 'cascade':
        for child in department.children.all():
            delete_department(
                department=child,
                mode='cascade',
            )
    else:
        department.children.update(parent=None)
    department.delete()


@transaction.atomic
def create_employee(department: Department, data: dict):
    """Создаёт сотрудника в отделе."""
    logger.info(f'Создание сотрудника в отделе {department.name}')
    return Employee.objects.create(
        department=department,
        **data
    )