"""
Base settings to build other settings data upon.
"""

# flake8: noqa

import os

import environ
from crispy_forms_govuk.settings import *
from dateutil import parser

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (transit_odp/config/settings/base.py - 3 = transit_odp/)
APPS_DIR = ROOT_DIR.path("transit_odp")

env = environ.Env()

with open(os.path.join(ROOT_DIR, "version.txt")) as v_file:
    APP_VERSION_NUMBER = v_file.read()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    ENV_FILE = env("DJANGO_ENV_FILE", default=".env")
    env_file = str(ROOT_DIR.path(ENV_FILE))
    env.read_env(env_file)

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/London"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
# SITE_ID = 1  # GB removing to ensure get_current_site uses request thus resolving Site for the django-host
ROOT_SITE_ID = (
    1  # GB - adding this as some migrations specifically update the root site
)
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls.www"
DATA_URLCONF = "transit_odp.browse.urls.root"
PUBLISH_URLCONF = "config.urls.publish"
ADMIN_URLCONF = "config.urls.admin"

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# https://django-hosts.readthedocs.io/en/latest/index.html#settings
ROOT_HOSTCONF = "config.hosts"
DEFAULT_HOST = "www"
PARENT_HOST: str = env("DJANGO_PARENT_HOST")
HOST_PORT = env("DJANGO_HOST_PORT", default="")
HOST_SCHEME = env("DJANGO_HOST_SCHEME", default=None)

# some environments require a proxy
HTTPS_PROXY = env("HTTPS_PROXY", default=None)

# subdomains used in hosts.py and to create Site records (see data migration transit_odp/contrib/sites/migrations/0004)
ROOT_SUBDOMAIN = env("DJANGO_ROOT_SUBDOMAIN", default="www")
DATA_SUBDOMAIN = env("DJANGO_DATA_SUBDOMAIN", default="data")
PUBLISH_SUBDOMAIN = env("DJANGO_PUBLISH_SUBDOMAIN", default="publish")
ADMIN_SUBDOMAIN = env("DJANGO_ADMIN_SUBDOMAIN", default="admin")

# ALLOWED_HOSTS are generated for each subdomain.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
ALLOWED_HOSTS += [
    f"{ROOT_SUBDOMAIN}.{PARENT_HOST}",
    f"{DATA_SUBDOMAIN}.{PARENT_HOST}",
    f"{PUBLISH_SUBDOMAIN}.{PARENT_HOST}",
    f"{ADMIN_SUBDOMAIN}.{PARENT_HOST}",
]

# https://github.com/ottoyiu/django-cors-headers#cors_origin_whitelist
CORS_ORIGIN_REGEX_WHITELIST = (
    rf"^(https?://)?([\w-]+\.)?{PARENT_HOST}(:{HOST_PORT})?$",
)
# CORS_URLS_REGEX = rf'^(https?://)?{ROOT_SUBDOMAIN}.{PARENT_HOST}(:{HOST_PORT})?/api/.*$'
CORS_URLS_REGEX = rf"^(https?://)?.*/api/.*$"

# Share django session across all subdomains of PARENT_HOST. This allows 'single sign on' across the different services
# Note there are security risks in doing this (see https://docs.djangoproject.com/en/2.2/topics/http/sessions/#session-security):
# we must have control over all subdomains of PARENT_HOST.
SESSION_COOKIE_DOMAIN = "." + PARENT_HOST

# Django will use browser-length cookies - cookies that expire as soon as the user closes their browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Age of session cookies, in seconds
SESSION_COOKIE_AGE = 72000  # set to 20 hours

# Whether to save the session data on every request
SESSION_SAVE_EVERY_REQUEST = True

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.contrib.postgres",
    "django.contrib.gis",
]
THIRD_PARTY_APPS = [
    "django_hosts",
    "crispy_forms",
    "crispy_forms_govuk",
    "allauth",
    "allauth.account",
    "invitations",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_gis",
    "rest_framework_swagger",
    "django_filters",
    "django_tables2",
    "formtools",
    "django_celery_beat",
    "django_celery_results",
    "frontend",  # technically 'third party'
]
LOCAL_APPS = [
    "transit_odp.api.apps.ApiConfig",
    "transit_odp.avl.apps.AvlConfig",
    "transit_odp.fares.apps.FaresConfig",
    "transit_odp.users.apps.UsersAppConfig",
    "transit_odp.organisation.apps.OrganisationConfig",
    "transit_odp.publish.apps.PublishConfig",
    "transit_odp.site_admin.apps.SiteAdminConfig",
    "transit_odp.common.apps.CommonConfig",
    "transit_odp.browse.apps.BrowseConfig",
    "transit_odp.guidance.apps.GuidanceConfig",
    "transit_odp.naptan.apps.NaptanConfig",
    "transit_odp.transmodel.apps.TransmodelConfig",
    "transit_odp.pipelines.apps.PipelinesConfig",
    "transit_odp.xmltoolkit.apps.XmlToolkitConfig",
    "transit_odp.data_quality.apps.DataQualityConfig",
    "transit_odp.notifications.apps.NotifyConfig",
    "transit_odp.restrict_sessions.apps.RestrictedSessions",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "transit_odp.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"

# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_LOGOUT_REDIRECT_URL = "account_logout_success"

# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# Login url's for Publish when AVL feature flag is turned on/off
PUBLISH_SELECT_DATA_URL = "select-data"
PUBLISH_FEED_LIST_URL = "feed-list"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django_hosts.middleware.HostsRequestMiddleware",
    "transit_odp.common.middleware.DefaultHostMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_hosts.middleware.HostsResponseMiddleware",
    "transit_odp.restrict_sessions.middleware.OneSessionPerUserMiddleware",
    "transit_odp.common.middleware.APILoggerMiddleware",  # leave this to last
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = (
    "/assets/"  # TODO - fix issue with Gov.UK footer logo then put back to /static/
)
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        # 'APP_DIRS': True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "builtins": [
                # overrides url template tag with django_hosts impl
                "django_hosts.templatetags.hosts_override"
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # custom context processors
                "transit_odp.common.context_processors.site",
                "transit_odp.common.context_processors.host",
                "transit_odp.common.context_processors.js_bundle_init",
                "transit_odp.common.context_processors.global_settings",
            ],
        },
    }
]

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL", default="Bus Open Data Service <noreply@bods.com>"
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[BODS] ")

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Gregory Brown""", "greg.brown@itoworld.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# Celery
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["transit_odp.taskapp.celery.CeleryAppConfig"]
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    # celery should use db timezone to avoid problems, e.g. expired data sets task runs at
    # 00:00 4th Nov BST but UTC is still 23:00 3rd Nov. Data sets expiring 00:00 4th Nov (UTC) therefore aren't
    # expired until the task runs again in 24 hours
    CELERY_TIMEZONE = "UTC"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-transport-options
# Increasing visibility_timeout due to issues with duplicate Celery tasks,
# see https://github.com/celery/django-celery/issues/215#issuecomment-154824966
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 18000}

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_SOFT_TIME_LIMIT = 60

# USER ACCOUNTS
# ------------------------------------------------------------------------------

# django-allauth
# ------------------------------------------------------------------------------
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
ACCOUNT_EMAIL_SUBJECT_PREFIX = env.bool(
    "DJANGO_ACCOUNT_EMAIL_SUBJECT_PREFIX", EMAIL_SUBJECT_PREFIX
)
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_ADAPTER = "transit_odp.common.adapters.AccountAdapter"

# Do not require username
ACCOUNT_USERNAME_REQUIRED = False

# This removes the 'remember' field from the LoginForm
ACCOUNT_SESSION_REMEMBER = False

# https://itoworld.atlassian.net/browse/BODP-734 - confirm account on GET to avoid issues with 're-using' the link
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

"""
BODP-519 account validation and password reset emails should expire after 24 hours

Note - the crypo algorithm in allauth only has precision of 1 day. Therefore, if the user generates an email
 5 minutes before midnight, the link will expire 5 minutes later as this counts as a day.

Note - account_email is checked with >= whereas password_reset is just >. Therefore, password reset times out after
 0 days.
"""
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

PASSWORD_RESET_TIMEOUT_DAYS = 0

# BODP-519 verification emails should become invalid when superseded by an new email
#  by storing emails in EmailConfirmation model - we can delete the 'superseded' emails
#  see transit_odp.users.receivers.delete_previous_email_confirmations
ACCOUNT_EMAIL_CONFIRMATION_HMAC = False

ACCOUNT_FORMS = {
    # Override AllAuth forms
    "login": "transit_odp.users.forms.auth.LoginForm",
    "developer_signup": "transit_odp.users.forms.auth.DeveloperSignupForm",
    "operator_signup": "transit_odp.users.forms.auth.OperatorSignupForm",
    "agent_signup": "transit_odp.users.forms.auth.AgentSignupForm",
    "change_password": "transit_odp.users.forms.auth.ChangePasswordForm",
    "reset_password": "transit_odp.users.forms.auth.ResetPasswordForm",
    "reset_password_from_key": "transit_odp.users.forms.auth.ResetPasswordKeyForm",
    # Not used
    "add_email": "allauth.account.forms.AddEmailForm",
    "set_password": "allauth.account.forms.SetPasswordForm",
}

# django-invitations
# ------------------------------------------------------------------------------
# https://github.com/bee-keeper/django-invitations#additional-configuration
INVITATIONS_ADAPTER = (
    ACCOUNT_ADAPTER  # django-invitations isn't consistent with allauth...
)
INVITATIONS_EMAIL_SUBJECT_PREFIX = env.bool(
    "DJANGO_INVITATIONS_EMAIL_SUBJECT_PREFIX", EMAIL_SUBJECT_PREFIX
)
INVITATION_MODEL = "users.Invitation"
INVITATIONS_INVITATION_MODEL = (
    INVITATION_MODEL  # invitations settings are not used self-consistently
)
INVITATIONS_ADMIN_ADD_FORM = "transit_odp.users.forms.admin.InvitationAdminAddForm"
INVITATIONS_INVITE_FORM = "transit_odp.organisation.forms.management.InvitationForm"
# If we need to provide different invitation forms for different views,  we could override SendInvite view in urls.py
# rather than this static setting
INVITATIONS_ACCEPT_INVITE_AFTER_SIGNUP = True

# API
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "transit_odp.api.authentication.TokenAuthSupportQueryString",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
    "MAX_PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# GOV.NOTIFY API KEY
# ------------------------------------------------------------------------------
GOV_NOTIFY_API_KEY = env("GOV_NOTIFY_API_KEY")


# Data Quality Service
# ------------------------------------------------------------------------------
DQS_URL = env("DQS_URL")
DQS_WAIT_TIMEOUT = 30  # minutes


# ClamAV
# -----------------------------------------------------------------------------
CLAMAV_HOST = env("CLAMAV_HOST", default="clamav")
CLAMAV_PORT = env.int("CLAMAV_PORT", default=3310)


# Internal settings
# ------------------------------------------------------------------------------

DISABLE_NAPTAN_SCHEMA_VALIDATION = True
FEED_MONITOR_MAX_RETRY_ATTEMPTS = env(
    "DJANGO_FEED_MONITOR_MAX_RETRY_ATTEMPTS", default=6
)

# NAPTAN import URL
NAPTAN_IMPORT_URL = env(
    "NAPTAN_IMPORT_URL", default="http://naptan.app.dft.gov.uk/Datarequest/naptan.ashx"
)

# NPTG import URL
NPTG_IMPORT_URL = env(
    "NPTG_IMPORT_URL", default="http://naptan.app.dft.gov.uk/datarequest/nptg.ashx"
)

# Google Analytics Key
GOOGLE_ANALYTICS_KEY = env("GOOGLE_ANALYTICS_KEY", default="")

# Central AVL Service
# ------------------------------------------------------------------------------
IS_AVL_FEATURE_FLAG_ENABLED = env("IS_AVL_FEATURE_FLAG_ENABLED", default=False)
CAVL_URL = env("CAVL_URL")
CAVL_SERVICE = "transit_odp.bods.adapters.gateways.cavl.CAVLService"
CAVL_CONSUMER_URL = env("CAVL_CONSUMER_URL")

# Fares Service
# ------------------------------------------------------------------------------
IS_FARES_FEATURE_FLAG_ENABLED = env("IS_FARES_FEATURE_FLAG_ENABLED", default=False)

# ITO GTFS Files
# ------------------------------------------------------------------------------

ITO_GTFS_AWS_ACCESS_KEY_ID = env("DJANGO_ITO_GTFS_AWS_ACCESS_KEY_ID", default=None)
ITO_GTFS_AWS_SECRET_ACCESS_KEY = env(
    "DJANGO_ITO_GTFS_AWS_SECRET_ACCESS_KEY", default=None
)
ITO_GTFS_AWS_STORAGE_BUCKET_NAME = env(
    "DJANGO_ITO_GTFS_AWS_STORAGE_BUCKET_NAME", default=None
)
ITO_GTFS_AWS_REGION = env("DJANGO_ITO_GTFS_AWS_REGION", default="eu-west-2")

# PTI
# ------------------------------------------------------------------------------
# Date when PTI feature was released
PTI_START_DATE = parser.parse(env("PTI_START_DATE", default="2021-04-01"))
# Date after which operators will not be able to publish non compliant datasets
PTI_ENFORCED_DATE = parser.parse(env("PTI_ENFORCED_DATE", default="2021-08-02"))


PTI_PDF_URL = env(
    "PTI_PDF_URL",
    default="https://pti.org.uk/system/files/files/TransXChange_UK_PTI_Profile_v1.1.A.pdf",
)
