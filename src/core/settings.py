"""
Django settings for MEDIGEST Health Platform.
"""

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-ws2!t#hxufg3=82^j+kcx#abbwl#hi&hloi!gmai)v+@cznx9)'
)
# DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')
DEBUG = True
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Automatic support for Render's hostname
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Webhook signing secret (from Shopify Integration PDF)
WEBHOOK_SIGNING_SECRET = os.environ.get(
    'WEBHOOK_SIGNING_SECRET',
    '8828edf31bf2349bde1141cc3e0d841b1560bebadd5bdab0adeb0bf214fc6094'
)

# ─────────────────────────────────────────────
# Application Definition
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    # Unfold admin (must be before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_ckeditor_5',

    # Project apps
    'accounts',
    'books',
    'questions',
    'flashcards',
    'learning',
    'certificates',
    'webhooks',
    'support',
]

# Allow iframes for Unfold
X_FRAME_OPTIONS = 'SAMEORIGIN'
SILENCED_SYSTEM_CHECKS = ['security.W019']

# ─────────────────────────────────────────────
# Unfold Admin Configuration
# ─────────────────────────────────────────────
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "MEDIGEST Health",
    "SITE_HEADER": "MEDIGEST Health",
    "SITE_SUBHEADER": "Content Management System",
    "SITE_URL": "/",
    "SITE_SYMBOL": "local_hospital",
    # Logo — shown in the sidebar header (optimise images for ~32px height)
    "SITE_LOGO": {
        "light": lambda request: static("img/logo-light.png"),  # light mode
        "dark": lambda request: static("img/logo-dark.png"),    # dark mode
    },
    # Small icon — used for favicon area / collapsed sidebar
    "SITE_ICON": {
        "light": lambda request: static("img/logo-light.png"),
        "dark": lambda request: static("img/logo-dark.png"),
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("img/logo-light.png"),
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "BORDER_RADIUS": "10px",
    "STYLES": [
        lambda request: static("css/admin-custom.css"),
    ],
    # ── Figma-matched color palette ──────────────────────────────
    # Base: dark navy from sidebar (#0F2042 → mapped to oklch scale)
    # Primary: teal/green accent (#2BB5A0 → mapped to oklch scale)
    "COLORS": {
        "base": {
            # Dark-navy sidebar scale extracted from Figma (#0F2042)
            "50":  "oklch(97.8% .004 250)",
            "100": "oklch(94.5% .009 250)",
            "200": "oklch(88.0% .016 250)",
            "300": "oklch(78.0% .028 250)",
            "400": "oklch(62.0% .04  250)",
            "500": "oklch(46.0% .05  250)",
            "600": "oklch(36.0% .055 248)",
            "700": "oklch(28.5% .055 245)",
            "800": "oklch(22.0% .05  242)",
            "900": "oklch(17.0% .045 240)",
            "950": "oklch(12.5% .04  238)",
        },
        "primary": {
            # Teal/green accent scale extracted from Figma (#2BB5A0)
            "50":  "oklch(96.5% .022 170)",
            "100": "oklch(92.0% .048 170)",
            "200": "oklch(85.0% .09  170)",
            "300": "oklch(77.0% .12  170)",
            "400": "oklch(70.0% .135 172)",
            "500": "oklch(62.5% .125 174)",
            "600": "oklch(53.0% .11  175)",
            "700": "oklch(45.0% .09  176)",
            "800": "oklch(38.0% .075 177)",
            "900": "oklch(32.0% .06  178)",
            "950": "oklch(24.0% .04  180)",
        },
        "font": {
            "subtle-light":    "var(--color-base-500)",
            "subtle-dark":     "var(--color-base-400)",
            "default-light":   "var(--color-base-600)",
            "default-dark":    "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark":  "var(--color-base-100)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Main"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                ],
            },
            {
                "title": _("Content"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Books"),
                        "icon": "menu_book",
                        "link": reverse_lazy("admin:books_book_changelist"),
                    },
                    {
                        "title": _("Specialties"),
                        "icon": "biotech",
                        "link": reverse_lazy("admin:books_specialty_changelist"),
                    },
                    {
                        "title": _("Topics"),
                        "icon": "article",
                        "link": reverse_lazy("admin:books_topic_changelist"),
                    },
                    {
                        "title": _("User Book Access"),
                        "icon": "key",
                        "link": reverse_lazy("admin:books_userbookaccess_changelist"),
                    },
                ],
            },
            {
                "title": _("Assessments"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Questions"),
                        "icon": "quiz",
                        "link": reverse_lazy("admin:questions_question_changelist"),
                    },
                    {
                        "title": _("Question Attempts"),
                        "icon": "fact_check",
                        "link": reverse_lazy("admin:questions_userquestionattempt_changelist"),
                    },
                    {
                        "title": _("Quiz Sessions"),
                        "icon": "assignment",
                        "link": reverse_lazy("admin:questions_quizsession_changelist"),
                    },
                    {
                        "title": _("Flashcards"),
                        "icon": "style",
                        "link": reverse_lazy("admin:flashcards_flashcard_changelist"),
                    },
                    {
                        "title": _("Flashcard Progress"),
                        "icon": "trending_up",
                        "link": reverse_lazy("admin:flashcards_userflashcardprogress_changelist"),
                    },
                ],
            },
            {
                "title": _("Learning & Progress"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Topic Progress"),
                        "icon": "school",
                        "link": reverse_lazy("admin:learning_usertopicprogress_changelist"),
                    },
                    {
                        "title": _("Highlights"),
                        "icon": "highlight",
                        "link": reverse_lazy("admin:learning_userhighlight_changelist"),
                    },
                    {
                        "title": _("Notes"),
                        "icon": "sticky_note_2",
                        "link": reverse_lazy("admin:learning_usernote_changelist"),
                    },
                    {
                        "title": _("Recent Activity"),
                        "icon": "history",
                        "link": reverse_lazy("admin:learning_recentactivity_changelist"),
                    },
                ],
            },
            {
                "title": _("Certifications"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("CME Activities"),
                        "icon": "workspace_premium",
                        "link": reverse_lazy("admin:certificates_cmeactivity_changelist"),
                    },
                    {
                        "title": _("CME Credits"),
                        "icon": "military_tech",
                        "link": reverse_lazy("admin:certificates_usercmecredit_changelist"),
                    },
                    {
                        "title": _("Certificates"),
                        "icon": "card_membership",
                        "link": reverse_lazy("admin:certificates_certificate_changelist"),
                    },
                ],
            },
            {
                "title": _("Support"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("FAQ Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:support_faqcategory_changelist"),
                    },
                    {
                        "title": _("FAQs"),
                        "icon": "live_help",
                        "link": reverse_lazy("admin:support_faq_changelist"),
                    },
                    {
                        "title": _("Contact Methods"),
                        "icon": "contact_support",
                        "link": reverse_lazy("admin:support_contactmethod_changelist"),
                    },
                ],
            },
            {
                "title": _("System"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Webhook Logs"),
                        "icon": "webhook",
                        "link": reverse_lazy("admin:webhooks_webhooklog_changelist"),
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "books.book",
                "books.specialty",
                "books.topic",
                "books.userbookaccess",
            ],
            "items": [
                {
                    "title": _("Books"),
                    "link": reverse_lazy("admin:books_book_changelist"),
                },
                {
                    "title": _("Specialties"),
                    "link": reverse_lazy("admin:books_specialty_changelist"),
                },
                {
                    "title": _("Topics"),
                    "link": reverse_lazy("admin:books_topic_changelist"),
                },
                {
                    "title": _("Access"),
                    "link": reverse_lazy("admin:books_userbookaccess_changelist"),
                },
            ],
        },
        {
            "models": [
                "questions.question",
                "questions.userquestionattempt",
                "questions.quizsession",
            ],
            "items": [
                {
                    "title": _("Questions"),
                    "link": reverse_lazy("admin:questions_question_changelist"),
                },
                {
                    "title": _("Attempts"),
                    "link": reverse_lazy("admin:questions_userquestionattempt_changelist"),
                },
                {
                    "title": _("Sessions"),
                    "link": reverse_lazy("admin:questions_quizsession_changelist"),
                },
            ],
        },
        {
            "models": [
                "flashcards.flashcard",
                "flashcards.userflashcardprogress",
                "flashcards.usercustomflashcard",
            ],
            "items": [
                {
                    "title": _("Flashcards"),
                    "link": reverse_lazy("admin:flashcards_flashcard_changelist"),
                },
                {
                    "title": _("Progress"),
                    "link": reverse_lazy("admin:flashcards_userflashcardprogress_changelist"),
                },
                {
                    "title": _("Custom Cards"),
                    "link": reverse_lazy("admin:flashcards_usercustomflashcard_changelist"),
                },
            ],
        },
        {
            "models": [
                "certificates.cmeactivity",
                "certificates.usercmecredit",
                "certificates.certificate",
            ],
            "items": [
                {
                    "title": _("Activities"),
                    "link": reverse_lazy("admin:certificates_cmeactivity_changelist"),
                },
                {
                    "title": _("Credits"),
                    "link": reverse_lazy("admin:certificates_usercmecredit_changelist"),
                },
                {
                    "title": _("Certificates"),
                    "link": reverse_lazy("admin:certificates_certificate_changelist"),
                },
            ],
        },
    ],
    "DASHBOARD_CALLBACK": "core.dashboard.dashboard_callback",
}

# ─────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ─────────────────────────────────────────────
# Database — SQLite for dev, PostgreSQL for production
# ─────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ─────────────────────────────────────────────
# Custom User Model
# ─────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

# ─────────────────────────────────────────────
# Password Validation
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────
# Internationalization
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# Static & Media Files
# ─────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────────
# Default Primary Key
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# Django REST Framework
# ─────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ─────────────────────────────────────────────
# Simple JWT
# ─────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF trusted origins for production
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# Allow all origins in development (when CORS_ALLOW_ALL is set)
if os.environ.get('CORS_ALLOW_ALL', 'False').lower() in ('true', '1'):
    CORS_ALLOW_ALL_ORIGINS = True

# ─────────────────────────────────────────────
# CKEditor 5
# ─────────────────────────────────────────────
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'link', 'insertImage', 'insertTable', 'mediaEmbed', '|',
            'outdent', 'indent', '|',
            'code', 'codeBlock', '|',
            'undo', 'redo',
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:full', 'imageStyle:side',
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight',
            ],
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableCellProperties', 'tableProperties',
            ],
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
            ],
        },
        'height': '400px',
        'width': '100%',
    },
    'minimal': {
        'toolbar': ['bold', 'italic', 'link', 'bulletedList', 'numberedList'],
        'height': '150px',
        'width': '100%',
    },
}

CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'svg']

# ─────────────────────────────────────────────
# Email Configuration (Gmail SMTP)
# ─────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'platraincloud@gmail.com'
EMAIL_HOST_PASSWORD = 'meczfpooichwkudl'
DEFAULT_FROM_EMAIL = 'MEDIGEST Health <platraincloud@gmail.com>'

# Frontend URL for password reset links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
