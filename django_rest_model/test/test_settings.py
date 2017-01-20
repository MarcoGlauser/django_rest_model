SECRET_KEY = 'fake-key'
DEBUG_PROPAGATE_EXCEPTIONS=True,
INSTALLED_APPS = [
    "django_rest_model.db",
    "django_rest_model.test",
]

DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}