import unittest

from unittest.mock import patch
from canonicalwebteam.blog import wordpress_api as api


class MockResponse:
    ok = True

    def json(self):
        return ["hello_test"]

    def raise_for_status(*args):
        pass

    headers = {"X-WP-TotalPages": 12}


class TestWordPressApi(unittest.TestCase):
    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting(self, get):

        get.return_value = MockResponse()

        article = api.get_article(slug="test")
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/"
            + "posts?slug=test&tags=&tags_exclude="
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_excluding_article(self, get):

        get.return_value = MockResponse()

        article = api.get_article(slug="test", tags_exclude=[1234, 5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?slug=test&tags=&tags_exclude=1234,5678"
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_including_article(self, get):

        get.return_value = MockResponse()

        article = api.get_article(slug="test", tags=[1234, 5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?slug=test&tags=1234,5678"
            + "&tags_exclude="
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_including_and_excluding_article(self, get):

        get.return_value = MockResponse()

        article = api.get_article(
            slug="test", tags=[1234, 5678], tags_exclude=[9876]
        )
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?slug=test&tags=1234,5678&tags_exclude=9876"
        )
        self.assertEqual(article, "hello_test")

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting_24_articles_from_page_3(self, get):

        get.return_value = MockResponse()

        article = api.get_articles(page=3, per_page=24)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=24"
            + "&tags="
            + "&page=3"
            + "&tags_exclude="
            + "&categories="
            + "&exclude="
        )
        self.assertEqual(article, (["hello_test"], 12))

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting_all_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_articles()
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags="
            + "&page=1"
            + "&tags_exclude="
            + "&categories="
            + "&exclude="
        )
        self.assertEqual(article, (["hello_test"], 12))

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_excluding_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_articles(tags_exclude=[1234, 5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags="
            + "&page=1"
            + "&tags_exclude=1234,5678"
            + "&categories="
            + "&exclude="
        )
        self.assertEqual(article, (["hello_test"], 12))

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_including_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_articles(tags=[1234, 5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags=1234,5678"
            + "&page=1"
            + "&tags_exclude="
            + "&categories="
            + "&exclude="
        )
        self.assertEqual(article, (["hello_test"], 12))

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_including_and_excluding_articles(self, get):

        get.return_value = MockResponse()

        article = api.get_articles(tags=[1234, 5678], tags_exclude=[9876])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags=1234,5678"
            + "&page=1"
            + "&tags_exclude=9876"
            + "&categories="
            + "&exclude="
        )
        self.assertEqual(article, (["hello_test"], 12))

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_get_articles_for_category(self, get):

        get.return_value = MockResponse()

        article = api.get_articles(categories=[5678])
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags="
            + "&page=1"
            + "&tags_exclude="
            + "&categories=5678"
            + "&exclude="
        )
        self.assertEqual(article, (["hello_test"], 12))

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting_sticky_only(self, get):

        get.return_value = MockResponse()

        article = api.get_articles(sticky=True)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags="
            + "&page=1"
            + "&tags_exclude="
            + "&categories="
            + "&exclude="
            + "&sticky=True"
        )
        self.assertEqual(article, (["hello_test"], 12))
