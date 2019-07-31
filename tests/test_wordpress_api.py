import unittest
from unittest.mock import patch

from canonicalwebteam.blog import wordpress_api as api


class FailingMockResponse:
    ok = False

    def raise_for_status(*args):
        raise Exception()

    headers = {"X-WP-TotalPages": 12}


class SuccessMockResponse:
    ok = True
    status = 200
    headers = {"X-WP-TotalPages": "12", "X-WP-Total": "52"}

    def raise_for_status(*args):
        pass

    def json(self):
        return {}


class TestWordPressApi(unittest.TestCase):
    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_articles_with_metadata(self, get):
        get.return_value = SuccessMockResponse()

        articles, metadata = api.get_articles()
        self.assertIsNotNone(metadata["total_pages"])
        self.assertIsNotNone(metadata["total_posts"])

        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            "wp-json/wp/v2/posts?per_page=12&page=1"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_articles(self, get):
        get.return_value = SuccessMockResponse()

        _, metadata = api.get_articles()
        self.assertEqual(metadata["total_pages"], "12")
        self.assertEqual(metadata["total_posts"], "52")
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            "wp-json/wp/v2/posts?"
            "per_page=12&page=1"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_article(self, get):
        slug = "test"
        _ = api.get_article(slug=slug)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/posts?"
            "slug=test&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_user(self, get):
        user_id = 217
        _ = api.get_user(user_id)

        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/users/217?"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_user_by_username(self, get):
        username = "canonical"
        _ = api.get_user_by_username(username)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            "wp-json/wp/v2/users?slug=canonical"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_media(self, get):
        id = 89203
        _ = api.get_media(id)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/media/89203?"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_tag_by_slug(self, get):
        slug = "snappy"
        _ = api.get_tag_by_slug(slug)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/tags?slug=snappy"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_category_by_id(self, get):
        id = 1453
        _ = api.get_category_by_id(id)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/categories/1453?"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_category_by_slug(self, get):
        slug = "articles"
        _ = api.get_category_by_slug(slug)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            "wp-json/wp/v2/categories?slug=articles"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_categories(self, get):
        _ = api.get_categories()
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            "wp-json/wp/v2/categories?per_page=100"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_group_by_id(self, get):
        id = 3367
        _ = api.get_group_by_id(id)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/group/3367?"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_group_by_slug(self, get):
        slug = "ai"
        _ = api.get_group_by_slug(slug)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/group?slug=ai"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_tags_by_ids(self, get):
        ids = [2080, 2655]
        _ = api.get_tags_by_ids(ids)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/"
            "wp-json/wp/v2/tags?include=2080%2C2655"
            "&_embed"
        )

    @patch("canonicalwebteam.blog.wordpress_api.api_session.get")
    def test_get_tag_by_name(self, get):
        name = "10.04"
        _ = api.get_tag_by_name(name)
        get.assert_called_once_with(
            "https://admin.insights.ubuntu.com/wp-json/wp/v2/tags?search=10.04"
            "&_embed"
        )
