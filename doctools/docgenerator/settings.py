from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'z*i6mb-i!jjgcmiopy@1=)j=)svgo-08jd6b$1($=2gycmstrn'
DEBUG = True

ALLOWED_HOSTS = ['*']

# The directory holding mnx-metaspec.json, mnx-examples.json and content/.
METASPEC_DIR = BASE_DIR

# The directory holding the example documents and images.
MEDIA_DIR = BASE_DIR / 'media'

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'spectools',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'docgenerator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'spectools.context_processors.docs_global_variables',
            ],
            'builtins': ['spectools.tags'],
        },
    },
]

WSGI_APPLICATION = 'docgenerator.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = f'/static/'
STATICFILES_DIRS = [BASE_DIR / 'media']
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
