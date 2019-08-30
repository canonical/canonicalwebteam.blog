# Core
import os
import unittest

# Packages
import django
import vcr
from django.conf import settings
from django.test import Client

this_dir = os.path.dirname(os.path.realpath(__file__))

# Mock Django
settings.configure(
    BLOG_CONFIG={
        "TAG_IDS": [],
        "EXCLUDED_TAGS": [3184, 3265],
        "BLOG_TITLE": "Blog",
    },
    ROOT_URLCONF="canonicalwebteam.blog.django.urls",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [f"{this_dir}/test_templates"],
        }
    ],
)
django.setup()

mock_article = {"id": 1}


class TestDjangoViews(unittest.TestCase):
    @vcr.use_cassette("fixtures/vcr_cassettes/django_homepage.yaml")
    def test_homepage(self):
        django_client = Client()

        response = django_client.get("/")
        self.assertEqual(response.status_code, 200)
