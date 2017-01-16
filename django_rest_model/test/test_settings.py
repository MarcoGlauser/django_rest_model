SECRET_KEY = 'fake-key'
DEBUG_PROPAGATE_EXCEPTIONS=True,
INSTALLED_APPS = [
    "test"
]

DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
}