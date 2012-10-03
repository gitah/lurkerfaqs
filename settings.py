import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Django settings for lurkerfaqs project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'lurkerfaqs',                   # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'qwerty',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'America/Vancouver'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "lurkerfaqs/static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9#m4_@rlb)d11)ecc24+k2j=ao__c+p2sg4qk-4d6&amp;qgl%!lyo'

#-- Template Stuff --#
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.static',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "lurkerfaqs/templates"),
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lurkerfaqs.urls'

WSGI_APPLICATION = 'lurkerfaqs.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'gfaqs',
    'lurkerfaqs',
)

#-- LurkerFAQs General vars ---#
LURKERFAQS_LOG_DIR = "/var/log/lurkerfaqs"
LURKERFAQS_RUN_DIR = "/var/run/lurkerfaqs"

LURKERFAQS_TOPICS_PER_PAGE = 30
LURKERFAQS_POSTS_PER_PAGE = 3
LURKERFAQS_PAGES_TO_DISPLAY = 10

#-- GFAQs Archiver Settings --#
# path of PID file for gfaqs-archiver daemon
GFAQS_ARCHIVER_PID_FILE = "%s/gfaqs-archiver.pid" % LURKERFAQS_RUN_DIR

# base url for gamefaqs
GFAQS_URL = "http://www.gamefaqs.com"
GFAQS_BOARD_URL = "%s/boards" % GFAQS_URL
GFAQS_LOGIN_URL = "%s/user/login.html" % GFAQS_URL

# List of boards to scrape
# Each board is represented as a 2-tuple:
# (<board_path>,<board_name>, <refresh_time_in_minutes>) 
GFAQS_BOARDS = [
    ("2000121-anime-and-manga-other-titles", "Anime and Manga - Other Titles", 5),
    ("8-gamefaqs-contests", "GameFAQs Contests", 5)
]

GFAQS_LOGIN_AS_USER=False
GFAQS_LOGIN_EMAIL=""
GFAQS_LOGIN_PASSWORD=""


#-- Logging Settings --#
GFAQS_ERROR_LOGGER = 'gfaqs.errors'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    },
    'handlers': {
        'file': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': '%s/gfaqs_archiver_error.log' % LURKERFAQS_LOG_DIR
        }
    },
    'loggers': {
        GFAQS_ERROR_LOGGER: {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
