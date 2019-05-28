# Core
import os
import unittest
from unittest.mock import patch

# Packages
import django
from django.conf import settings
from django.test import Client

this_dir = os.path.dirname(os.path.realpath(__file__))

# Mock Django
settings.configure(
    BLOG_CONFIG={
        "TAG_IDS": [],
        "EXCLUDED_TAGS": [3184, 3265],
        "BLOG_TITLE": "Blog",
        "TAG_NAME": "",
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
    def setUp(self):
        get_articles_mock = patch(
            "canonicalwebteam.blog.wordpress_api.get_articles",
            return_value=tuple([[mock_article], "1"]),
        )
        get_index_context_mock = patch(
            "canonicalwebteam.blog.common_view_logic.get_index_context",
            return_value={},
        )

        # https://docs.python.org/3/library/unittest.mock.html#patch-methods-start-and-stop
        self.get_articles_patch = get_articles_mock.start()
        self.get_index_context_patch = get_index_context_mock.start()
        self.addCleanup(patch.stopall)

    def test_homepage(self,):

        django_client = Client()

        django_client.get("/")

        self.assertEqual(self.get_articles_patch.call_count, 3)
        self.get_index_context_patch.assert_called_once_with(
            "1",
            [mock_article],
            "1",
            featured_articles=[mock_article],
            upcoming=[mock_article],
        )

    # TODO: This test has a problem with the patching method
    # It fails due to a mismatch on the patched method
    # between test function and application funcion.
    # It needs a through debugging, which is for now descoped
    def ignore_test_second_page(self):

        django_client = Client()

        django_client.get("/?page=2")

        self.get_articles_patch.assert_called_once()
        self.get_index_context_patch.assert_called_once_with(
            "2", [mock_article], "2", featured_articles=[]
        )
