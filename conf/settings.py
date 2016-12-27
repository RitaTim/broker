# -*- coding: utf-8 -*-
# Django settings for bootstrap project.
import os
from django.core.exceptions import ImproperlyConfigured

PROJECT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '../'))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&_1f-rlk%j)s@=7n+w0ot27zxvp(@h!eyq27apf-9y4c*mc6s*'

WSGI_APPLICATION = 'wsgi.application'

MODULES = [
    'analize',
    'logger',
    'broker',
    'main'
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
] + MODULES

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders':[
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')


CELERY_RESULT_BACKEND = 'redis://'
CELERY_TASK_RESULT_EXPIRES = 1500  # 15 min

from kombu import Queue, Exchange, binding

topic = Exchange('main', type='topic')

CELERY_QUEUES = (
    Queue('default'),
    Queue('analize', [
        binding(exchange=topic, routing_key='task.*'),
        binding(exchange=topic, routing_key='*.analize'),
    ]),
    Queue('logger', [
        binding(exchange=topic, routing_key='task.*'),
        binding(exchange=topic, routing_key='*.logger'),
    ]),
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_SEND_TASK_ERROR_EMAILS = True

BROKER_URL = ""

from settings_local import *

if not BROKER_URL:
    raise ImproperlyConfigured(
        'BROKER_URL must be implemented'
    )

if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)
    DISABLE_PANELS = []
    DEBUG_TOOLBAR_PATCH_SETTINGS = True

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda x: True
    }

    # additional modules for development
    INSTALLED_APPS += (
        'debug_toolbar',
    )

    # Отключаем кеширование и добавляем toolbar при дебагинге
    MIDDLEWARE_CLASSES = (
        ('debug_toolbar.middleware.DebugToolbarMiddleware',) +
        MIDDLEWARE_CLASSES[1:-1]
    )

EMAIL_DEFAULT_FROM = "broker@km-union.ru"
SERVICE_EMAIL_DEFAULT_FROM = "broker@km-union.ru"
SERVICE_EMAIL_COPY = "broker@km-union.ru"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp1.km-union.ru'