"""
Конфигурация ASGI для проекта config.

Предоставляет ASGI callable как переменную уровня модуля с именем ``application``.

Для получения дополнительной информации об этом файле см.
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
