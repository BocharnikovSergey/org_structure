from django.db import models
from django.core.validators import MinLengthValidator

from core.models import TimeStampedModel
from core import constants

class Employee(TimeStampedModel):
    """Модель сотрудника"""
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='employees'
    )
    full_name = models.CharField(
        max_length=constants.MAX_LEN_NAME,
        validators=[
            MinLengthValidator(constants.MIN_LEN_NAME),
        ]
    )
    position = models.CharField(
        max_length=constants.MAX_LEN_POSITION,
        validators=[
            MinLengthValidator(constants.MIN_LEN_POSITION),
        ]
    )
    hired_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return self.full_name
    
    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, name={self.full_name}, position={self.position},'
            f'department={self.department.name}, hired_at={self.hired_at})'
        )