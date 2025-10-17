import socket
from .base import *
from decouple import config
import os

SECRET_KEY = config(
    'SECRET_KEY', ''
)

DEBUG = False

ALLOWED_HOSTS = ["*"]


STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


APPEND_SLASH = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

d_name = config('POSTGRES_DB', default='cms')
d_user = config('POSTGRES_USER', default='cms')
d_password = config('POSTGRES_PASSWORD', default='cms')
d_host = config('POSTGRES_HOST', default='cms_db')
d_port = config('POSTGRES_PORT', default='5432')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': d_name,
        'USER': d_user,
        'PASSWORD': d_password,
        'HOST': d_host,
        'PORT': d_port
    }
}


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
