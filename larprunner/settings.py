# Django settings for larprunner project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Petr Muller', 'afri@afri.cz'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'larprunner'             # Or path to database file if using sqlite3.
DATABASE_USER = 'afri'             # Not used with sqlite3.
DATABASE_PASSWORD = 'fo0m4nchU'        # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Prague'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'EN-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h__rkjo*hm!1u_zl9uojr%!e+_%mydoy(&ysqi^mx2=3=lud57'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'larprunner.urls'

TEMPLATE_DIRS = (
    '/home/afri/projects/larp-runner/larprunner/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.admin',
    'django.contrib.sites',
    'larprunner.admin',
    'larprunner.events',
    'larprunner.users',
    'larprunner.questions'
)

SESSION_EXPIRE_AT_BROWSER_CLOSE=True
AUTH_PROFILE_MODULE="users.Person"
ACCOUNT_ACTIVATION_DAYS=7
EMAIL_HOST="mesias.brnonet.cz"
EMAIL_HOST_USER="afri"
EMAIL_HOST_PASSWORD="MEror7popax"
DEFAULT_FROM_EMAIL='afri@afri.cz'
