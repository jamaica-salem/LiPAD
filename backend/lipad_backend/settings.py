import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# --- Base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment from .env (create it next)
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'CHANGE_ME')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = ['*']  # lock this down in prod

# --- Installed Apps ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',
    'corsheaders',

    # local
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # keep CSRF for session-auth flows
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lipad_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # not needed for API-only
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lipad_backend.wsgi.application'

# --- Database (MySQL) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DB'),         
        'USER': 'root',
        'PASSWORD': '',
        'HOST': os.getenv('MYSQL_HOST'),
        'PORT': os.getenv('MYSQL_PORT'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}

# --- Media (for ImageField) ---
MEDIA_URL = os.getenv('MEDIA_URL')
MEDIA_ROOT = os.path.join(BASE_DIR, os.getenv('MEDIA_ROOT'))

# --- DRF defaults (pagination + sane JSON errors) ---
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',  # for file uploads
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# === CORS & CSRF (development) ===
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5174',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]
CORS_ALLOW_ALL_ORIGINS = True  # (lock down in prod)

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5176",
    "http://127.0.0.1:5176",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
] 

# === Cookie security (development / production notes) ===
SESSION_COOKIE_HTTPONLY = True     # prevents JavaScript access to session cookie
SESSION_COOKIE_SECURE = False      # set to True in production (requires HTTPS)
SESSION_COOKIE_SAMESITE = "Lax"    # "Lax" for most cases; use "None" + Secure in cross-site over HTTPS
CSRF_COOKIE_SECURE = False         # set to True in production
CSRF_COOKIE_HTTPONLY = False       # must be readable by JS to attach X-CSRFToken from document.
SESSION_COOKIE_AGE = 1800  

# If True, session will end when browser is closed, regardless of age
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Refresh the expiry time on every request (rolling session)
SESSION_SAVE_EVERY_REQUEST = True  

# --- Timezone/Locale ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
