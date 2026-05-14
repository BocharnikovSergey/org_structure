from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

from core import constants
from core.models import TimeStampedModel


class Department(TimeStampedModel):
    """Модель для отделов"""
    name = models.CharField(
        max_length=constants.MAX_LEN_NAME,
        validators=[
            MinLengthValidator(constants.MIN_LEN_NAME)
        ]
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent',],
                name='unique_name_parent'
            )
        ]
        ordering = ['created_at']

    def clean(self) -> None:
        """Проверяет корректность дерева отделов."""
        self.name = self.name.strip()
        if self.parent == self:
            raise ValidationError(
                'Отдел не может быть родительским по отношению к самому себе'
            )
        if self.pk and self._has_cycle():
            raise ValidationError('Невозможно создать цикл в дереве отделов')

    def _has_cycle(self) -> bool:
        """Проверяет наличие цикла в дереве."""
        parent = self.parent
        while parent:
            if parent.pk == self.pk:
                return True
            parent = parent.parent
        return False

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, name={self.name}, parent={self.parent})'
        )