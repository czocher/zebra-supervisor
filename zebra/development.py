# -*- coding: utf-8 -*-
"""
Django settings for zebra project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib.messages import constants as messages

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def p(*x):
    return os.path.join(BASE_DIR, *x)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/


# Generate a unique SECRET_KEY on first run.
try:
    from .secretkey import SECRET_KEY
except ImportError:
    from django.utils.crypto import get_random_string

    with open(p('zebra/secretkey.py'), 'w') as secretkey:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        secretkey.write('SECRET_KEY = \'{}\'\n'.format(
            get_random_string(50, chars)))

    from .secretkey import SECRET_KEY as SECRET
    SECRET_KEY = SECRET

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            p('templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request'
            ],
        },
    },
]

ALLOWED_HOSTS = []

if DEBUG:
    SENDFILE_BACKEND = 'sendfile.backends.development'
else:
    SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'guardian',
    'bootstrap3',
    'judge',
    'rest',
    'questions',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'zebra.middleware.RequireLoginMiddleware',
)

ROOT_URLCONF = 'zebra.urls'

WSGI_APPLICATION = 'zebra.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': p('db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Security

# Set to true if SSL is enabled
SECURE_HSTS_SECONDS = 0

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

SECURE_SSL_REDIRECT = False

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

CSRF_COOKIE_HTTPONLY = True

X_FRAME_OPTIONS = 'DENY'

# Absolute filesystem path to the directory that will hold user-uploaded files.

MEDIA_ROOT = p('media-files')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.

MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.

STATIC_ROOT = p('static-files')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Additional locations of static files

STATICFILES_DIRS = (
    p('static/'),
)

# Avalible page translations
LANGUAGES = (
    ('pl', u"Polish"),
    ('en', u"English"),
)

# Paths to locale folders
LOCALE_PATHS = (
    p('judge/locale'),
    p('questions/locale'),
    p('rest/locale'),
    p('locale'),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest.tokenpermission.TokenPermission'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
    ]
}

ANONYMOUS_USER_ID = -1

LOGIN_REDIRECT_URL = '/judge/'
LOGIN_URL = '/login/'
LOGIN_REQUIRED_URLS = (
    r'/judge/(.*)$',
)

# Available programming languages
PROGRAMMING_LANGUAGES = (
    ('c', 'C'),
    ('cpp', 'C++'),
    ('pas', 'Pascal'),
    ('py', 'Python'),
    ('java', 'Java'),
)

# Show print buttons for users
PRINTING_AVAILABLE = True

BOOTSTRAP3 = {
    'success_css_class': '',
}

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ("[%(asctime)s] %(levelname)s "
                       "[%(name)s:%(lineno)s] %(message)s"),
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': p('zebra.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'zebra': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'rest': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
