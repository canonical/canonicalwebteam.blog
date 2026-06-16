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
