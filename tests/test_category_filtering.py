# Standard library
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Packages
import requests

# Local
from canonicalwebteam.blog import Wordpress
from canonicalwebteam.blog.blog_api import BlogAPI


class TestWordpressGetArticleCategories(TestCase):
    def setUp(self):
        self.api = Wordpress(session=requests.Session())

    def test_get_article_forwards_categories_param(self):
        self.api.get_first_item = MagicMock(return_value={"slug": "x"})

        self.api.get_article(slug="x", categories=[5])

        params = self.api.get_first_item.call_args.args[1]
        self.assertEqual(params["categories"], [5])

    def test_get_article_categories_default_none(self):
        self.api.get_first_item = MagicMock(return_value={"slug": "x"})

        self.api.get_article(slug="x")

        params = self.api.get_first_item.call_args.args[1]
        self.assertIsNone(params["categories"])


class TestBlogAPIGetArticleCategories(TestCase):
    def test_get_article_forwards_categories_to_super(self):
        api = BlogAPI(session=requests.Session())

        with patch.object(
            Wordpress, "get_article", return_value={}
        ) as mock_super:
            api.get_article(slug="x", categories=[7])

        self.assertEqual(mock_super.call_args.kwargs["categories"], [7])


class TestBlogViewsCategoryThreading(TestCase):
    def _make_views(self, category_ids):
        from canonicalwebteam.blog import BlogViews

        api = MagicMock()
        api.get_articles.return_value = (
            [],
            {"total_pages": "1", "total_posts": "0"},
        )
        api.get_article.return_value = {}
        api.get_category_by_slug.return_value = {"id": 99}
        return BlogViews(api=api, category_ids=category_ids), api

    def test_get_index_threads_category_ids(self):
        # page=2 skips the featured/events branch, leaving one main call
        views, api = self._make_views([5])

        views.get_index(page=2)

        self.assertEqual(api.get_articles.call_args.kwargs["categories"], [5])

    def test_get_index_default_category_ids_is_empty(self):
        views, api = self._make_views([])

        views.get_index(page=2)

        self.assertEqual(api.get_articles.call_args.kwargs["categories"], [])

    def test_get_article_threads_category_ids(self):
        views, api = self._make_views([5])

        views.get_article("some-slug")

        self.assertEqual(api.get_article.call_args.kwargs["categories"], [5])

    def test_get_tag_threads_category_ids(self):
        views, api = self._make_views([5])
        api.get_tag_by_slug.return_value = {"id": 1, "name": "Design"}

        views.get_tag("design")

        self.assertEqual(api.get_articles.call_args.kwargs["categories"], [5])
