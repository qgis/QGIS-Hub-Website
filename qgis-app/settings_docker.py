from settings import *
import ast
import os

from settings import *

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
from datetime import timedelta
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

DEBUG = ast.literal_eval(os.environ.get("DEBUG", "True"))
THUMBNAIL_DEBUG = DEBUG
ALLOWED_HOSTS = ["*"]

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "/home/web/media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
# MEDIA_URL = '/media/'
# setting full MEDIA_URL to be able to use it for the feeds
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.environ.get("STATIC_ROOT", "/home/web/static/")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Manage static files storage ensuring that their 
# filenames contain a hash of their content for cache busting
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    # Uncomment the next line to enable the admin:
    "django.contrib.admin",
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    "django.contrib.staticfiles",
    "django.contrib.flatpages",
    # full text search postgres
    "django.contrib.postgres",
    "django.contrib.humanize",
    "django.contrib.syndication",
    "bootstrap_pagination",
    "sortable_listview",
    "lib",  # Container for small tags and functions
    "sorl.thumbnail",
    "djangoratings",
    "taggit",
    "taggit_autosuggest",
    "taggit_templatetags",
    "haystack",
    "simplemenu",
    "tinymce",
    "rpc4django",
    "preferences",
    "rest_framework",
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    "sorl_thumbnail_serializer",  # serialize image
    "drf_multiple_model",
    "drf_yasg",
    "api",
    "map_gallery",
    "screenshots",
    # styles:
    "styles",
    # geopackages
    "geopackages",
    # QGIS Layer Definition File (.qlr)
    "layerdefinitions",
    # models (sharing .model3 file feature)
    "models",
    # 3D models
    "wavefronts",
    # Processing algorithms
    "processing_scripts",
    "matomo",
    # Webpack
    "webpack_loader"
]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ["DATABASE_NAME"],
        "USER": os.environ["DATABASE_USERNAME"],
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": os.environ["DATABASE_HOST"],
        "PORT": 5432,
        "TEST": {
            "NAME": "unittests",
        },
    }
}

PAGINATION_DEFAULT_PAGINATION = 20
PAGINATION_DEFAULT_PAGINATION_HUB = 30
LOGIN_REDIRECT_URL = "/"
SERVE_STATIC_MEDIA = DEBUG
DEFAULT_HUB_SITE = os.environ.get("DEFAULT_HUB_SITE", "https://hub.qgis.org/")

# See fig.yml file for postfix container definition
#
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
# Host for sending e-mail.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp")
# Port for sending e-mail.
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
# SMTP authentication information for EMAIL_HOST.
# See fig.yml for where these are defined
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "automation")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "docker")
EMAIL_USE_TLS = ast.literal_eval(os.environ.get("EMAIL_USE_TLS", "False"))
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[QGIS Hub]")

# django uploaded file permission
FILE_UPLOAD_PERMISSIONS = 0o644

REST_FRAMEWORK = {
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

GEOIP_PATH='/var/opt/maxmind/'
METABASE_DOWNLOAD_STATS_URL = os.environ.get(
    "METABASE_DOWNLOAD_STATS_URL", 
    "/metabase"
)

# Set plugin token access and refresh validity to a very long duration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365*1000),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365*1000)
}

MATOMO_SITE_ID="1"
MATOMO_URL="//matomo.qgis.org/"

# Default primary key type
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Sentry
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_RATE = os.environ.get("SENTRY_RATE", 1.0)

if SENTRY_DSN and SENTRY_DSN != "":
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=SENTRY_RATE,
    )
# Webpack
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles',
        'STATS_FILE': os.path.join(SITE_ROOT, 'webpack-stats.json'),
    }
}


HUB_SUBMENU = [
    {
        'name': 'Styles',
        'url': '/styles/?sort=upload_date&order=desc',
        'icon': 'fa-paint-brush',
        'order': 1,
        'description': 'QGIS styles are a set of properties that can be applied to vector layers. They are used to render the layer in the map canvas.'
    },
    {
        'name': 'Projects',
        'url': '/geopackages/?sort=upload_date&order=desc',
        'icon': 'fa-folder-open',
        'order': 2,
        'description': 'Geopackage files that contain a QGIS project file and all the data layers used in the project.'
    },
    {
        'name': 'Models',
        'url': '/models/?sort=upload_date&order=desc',
        'icon': 'fa-cogs',
        'order': 3,
        'description': 'QGIS models are a set of processing algorithms that can be run in a sequence to automate a task.'
    },
    {
        'name': '3D Models',
        'url': '/wavefronts/?sort=upload_date&order=desc',
        'icon': 'fa-cube',
        'order': 4,
        'description': 'QGIS 3D models can be used in any 3D software to visualize and analyze spatial data in three dimensions.'
    },
    {
        'name': 'QLR',
        'url': '/layerdefinitions/?sort=upload_date&order=desc',
        'icon': 'fa-layer-group',
        'order': 5,
        'description': 'The QGIS Layer Definition (QLR) format makes it possible to share “complete” QGIS layers with other QGIS users. QLR files contain links to the data sources and all the QGIS style information necessary to style the layer.'
    },
    {
        'name': 'Map Gallery',
        'url': '/map-gallery/?sort=upload_date&order=desc',
        'icon': 'fa-map',
        'order': 6,
        'description': 'QGIS Map Gallery is a collection of maps created with QGIS. They are a great way to learn how to use QGIS and to get inspiration for your own maps.'
    },
    {
        'name': 'Screenshots',
        'url': '/screenshots/?sort=upload_date&order=desc',
        'icon': 'fa-image',
        'order': 7,
        'description': 'Showcase screenshots of QGIS in action.'
    },
    {
        'name': 'Processing Scripts',
        'url': '/scripts/?sort=upload_date&order=desc',
        'icon': 'fa-cogs',
        'order': 8,
        'description': 'QGIS Processing Scripts are a set of processing algorithms that can be run in a sequence to automate a task.'
    },
]

API_SUBMENU = [
    {
        'name': 'Tokens',
        'url': '/api/v1/tokens/',
        'icon': 'fa-key',
        'order': 0,
    },
    {
        'name': 'Swagger',
        'url': '/swagger/',
        'icon': 'fa-book',
        'order': 1,
    },
    {
        'name': 'Resources RAW',
        'url': '/api/v1/resources/',
        'icon': 'fa-database',
        'order': 2,
    },
]

# Set the navigation menu
NAVIGATION_MENU = [
    {
        'name': 'QGIS Hub Home',
        'url': '/',
        'icon': 'fa-house',
        'order': 0,
    },
    {
        'name': 'Hub',
        'url': '#',
        'icon': 'fa-cubes',
        'order': 1,
        'submenu': HUB_SUBMENU
    },
    {
        'name': 'API',
        'url': '/api/v1/tokens/',
        'icon': 'fa-code',
        'order': 2,
        'submenu': API_SUBMENU
    },
    {
        'name': 'Metrics',
        'url': METABASE_DOWNLOAD_STATS_URL,
        'icon': 'fa-chart-bar',
        'order': 4,
    }
]

# Set the default timezone
USE_TZ = False
TIME_ZONE = 'UTC'
