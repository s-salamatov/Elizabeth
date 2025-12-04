import os

import django
import pytest


@pytest.fixture(scope="session", autouse=True)
def django_setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.elizabeth.settings.dev")
    django.setup()
