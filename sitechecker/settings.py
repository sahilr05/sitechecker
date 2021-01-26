import os
from distutils.util import strtobool

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.getenv(name)
        try:
            return bool(strtobool(value))
        except ValueError as e:
            error_msg = "{} is an invalid value for {}".format(value, name)
            raise ImproperlyConfigured(error_msg) from e
    return default_value


def get_env_variable_or_default(name, default_value):
    if name in os.environ:
        return os.getenv(name)
    else:
        if type(default_value) == "int":
            return int(default_value)
        else:
            return default_value


def get_env_variable(var_name):
    try:
        return os.getenv(var_name)
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


DEBUG = get_bool_from_env("DEBUG", True)

if DEBUG:
    with open("secretkey.txt") as f:
        SECRET_KEY = f.read().strip()
else:
    SECRET_KEY = get_env_variable("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "sitechecker"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Custom
    "accounts",
    "checkerapp",
    # Third-party
    "celery",
    "widget_tweaks",
    "django_extensions",
    "storages",
    "boto3",
    # Plugins
    "bot",
    "django_telegrambot",
    "sc_generic_plugin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sitechecker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": get_env_variable_or_default(
            "SQL_ENGINE", "django.db.backends.postgresql"
        ),
        "NAME": get_env_variable_or_default("SQL_DATABASE", "sitechecker"),
        "USER": get_env_variable_or_default("SQL_USER", "postgres"),
        "PASSWORD": get_env_variable_or_default("SQL_PASSWORD", 8149547570),
        "HOST": get_env_variable_or_default("SQL_HOST", "localhost"),
        "PORT": get_env_variable_or_default("SQL_PORT", 5432),
    }
}

WSGI_APPLICATION = "sitechecker.wsgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGOUT_REDIRECT_URL = "checkerapp:home"
LOGIN_REDIRECT_URL = "accounts:login"
LOGIN_URL = "/accounts/login"

if DEBUG:
    STATIC_URL = "/static/"
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
else:
    AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME")
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    # s3 static settings
    AWS_LOCATION = "static"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"


# Celery
BROKER_URL = get_env_variable_or_default("REDIS_HOST", "redis://127.0.0.1:6379/0")
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0

# CELERY_RESULT_BACKEND = 'django-db'
# CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_TASK_SERIALIZER = "pickle"
CELERY_ROUTES = {
    "checkerapp.tasks.check_interval": {"queue": "check_queue"},
    "checkerapp.tasks.send_alert": {"queue": "alert_queue"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {"": {"handlers": ["console"], "level": "INFO", "propagate": True}},
}
DJANGO_TELEGRAMBOT = {
    "MODE": "POLLING",
    "BOTS": [
        {"TOKEN": get_env_variable_or_default("TG_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")}
    ],
}
