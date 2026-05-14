import logging

from rest_framework import serializers


logger = logging.getLogger(__name__)


def validate_empty_field(value: str) -> str:
    """Проверяет, что строка не пустая."""
    logger.info('Проверка, что строка не пустая')
    value = value.strip()
    if not value:
        message = 'Поле не может быть пустым.'
        logger.error(message)
        raise serializers.ValidationError(message)
    return value
