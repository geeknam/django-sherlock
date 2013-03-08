import os.path

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'djcelery',

    'sherlock',
    'polls',
]


ROOT_URLCONF = "urls"

DEBUG = True

ROOTDIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOTDIR + '/templates',
)
STATIC_URL = '/static/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'database.db'),
    }
}

REDIS_HOST = "127.0.0.1"
BROKER_URL = "redis://%s/2" % REDIS_HOST

REDIS_SETTINGS = {'host': REDIS_HOST}
