import unittest

from unittest.mock import patch
from canonicalwebteam.blog import wordpress_api as api


class MockResponse:
    ok = True

    def json(self):
        return "hello_test"


class TestWordPressApi(unittest.TestCase):
    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting_all_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_article(slug="test")
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/"
            + "posts?slug=test&tags=&tags_exclude="
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_excluding_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_article(slug="test", tags_exclude=[1234, 5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?slug=test&tags=&tags_exclude=1234,5678"
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_including_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_article(slug="test", tags=[1234, 5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?slug=test&tags=1234,5678"
            + "&tags_exclude="
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_including_and_excluding_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_article(
            slug="test", tags=[1234, 5678], tags_exclude=[9876]
        )
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?slug=test&tags=1234,5678&tags_exclude=9876"
        )
        self.assertEqual(article, "hello_test")
