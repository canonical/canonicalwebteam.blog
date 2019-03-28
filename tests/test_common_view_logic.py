import unittest

from unittest.mock import patch
from canonicalwebteam.blog.common_view_logic import (
    get_index_context,
    get_article_context,
)


class TestCommonViewLogic(unittest.TestCase):
    @patch("canonicalwebteam.blog.wordpress_api.get_group_by_id")
    @patch("canonicalwebteam.blog.wordpress_api.get_category_by_id")
    @patch("canonicalwebteam.blog.wordpress_api.get_user")
    @patch("canonicalwebteam.blog.wordpress_api.get_media")
    def test_building_index_context(
        self, get_media, get_user, get_category_by_id, get_group_by_id
    ):
        get_media.return_value = "test_image"
        get_user.return_value = "test_author"
        get_category_by_id.return_value = "test_category"
        get_group_by_id.return_value = "test_group"
        articles = [
            {
                "featured_media": "test",
                "author": "test",
                "categories": [1, 2],
                "group": [1],
                "tags": ["test"],
            },
            {
                "featured_media": "test2",
                "author": "test2",
                "categories": [2, 3],
                "group": [1],
                "tags": ["test2"],
            },
        ]
        context = get_index_context(1, articles, 2)
        expected_context = {
            "current_page": 1,
            "total_pages": 2,
            "articles": [
                {
                    "author": "test_author",
                    "categories": [1, 2],
                    "display_category": "test_category",
                    "featured_media": "test",
                    "group": "test_group",
                    "image": "test_image",
                    "tags": ["test"],
                },
                {
                    "author": "test_author",
                    "categories": [2, 3],
                    "display_category": "test_category",
                    "featured_media": "test2",
                    "group": "test_group",
                    "image": "test_image",
                    "tags": ["test2"],
                },
            ],
            "groups": {1: "test_group"},
            "used_categories": {
                1: "test_category",
                2: "test_category",
                3: "test_category",
            },
        }
        self.assertEqual(context, expected_context)

    @patch("canonicalwebteam.blog.wordpress_api.get_group_by_id")
    @patch("canonicalwebteam.blog.wordpress_api.get_category_by_id")
    @patch("canonicalwebteam.blog.wordpress_api.get_user")
    @patch("canonicalwebteam.blog.wordpress_api.get_media")
    def test_building_index_context_with_params_as_strings(
        self, get_media, get_user, get_category_by_id, get_group_by_id
    ):
        get_media.return_value = "test_image"
        get_user.return_value = "test_author"
        get_category_by_id.return_value = "test_category"
        get_group_by_id.return_value = "test_group"
        articles = [
            {
                "featured_media": "test",
                "author": "test",
                "categories": [1, 2],
                "group": [1],
                "tags": ["test"],
            },
            {
                "featured_media": "test2",
                "author": "test2",
                "categories": [2, 3],
                "group": [1],
                "tags": ["test2"],
            },
        ]
        context = get_index_context("1", articles, "2")
        expected_context = {
            "current_page": 1,
            "total_pages": 2,
            "articles": [
                {
                    "author": "test_author",
                    "categories": [1, 2],
                    "display_category": "test_category",
                    "featured_media": "test",
                    "group": "test_group",
                    "image": "test_image",
                    "tags": ["test"],
                },
                {
                    "author": "test_author",
                    "categories": [2, 3],
                    "display_category": "test_category",
                    "featured_media": "test2",
                    "group": "test_group",
                    "image": "test_image",
                    "tags": ["test2"],
                },
            ],
            "groups": {1: "test_group"},
            "used_categories": {
                1: "test_category",
                2: "test_category",
                3: "test_category",
            },
        }
        self.assertEqual(context, expected_context)

    @patch("canonicalwebteam.blog.wordpress_api.get_tags_by_ids")
    @patch("canonicalwebteam.blog.wordpress_api.get_articles")
    @patch("canonicalwebteam.blog.wordpress_api.get_user")
    @patch("canonicalwebteam.blog.wordpress_api.get_media")
    @patch("canonicalwebteam.blog.wordpress_api.get_group_by_id")
    def test_building_article_context(
        self,
        get_group_by_id,
        get_media,
        get_user,
        get_articles,
        get_tags_by_id,
    ):
        get_media.return_value = "test_image"
        get_group_by_id.return_value = "test_group"
        get_articles.return_value = (
            [
                {
                    "id": 2,
                    "featured_media": "test_related_article_image",
                    "author": "test_related_article_author",
                    "categories": [4, 5],
                    "group": [4],
                    "tags": ["test_related_article"],
                }
            ],
            2,
        )
        get_user.return_value = "test_author"
        get_tags_by_id.return_value = [
            {"id": 1, "name": "test_tag_1"},
            {"id": 2, "name": "test_tag_2"},
        ]
        article = {
            "id": 1,
            "featured_media": "test",
            "author": "test",
            "categories": [1, 2],
            "group": [1],
            "tags": ["test"],
        }

        context = get_article_context(article)
        expected_context = {
            "article": {
                "id": 1,
                "author": "test_author",
                "categories": [1, 2],
                "featured_media": "test",
                "group": "test_group",
                "image": None,
                "tags": ["test"],
            },
            "is_in_series": False,
            "related_articles": [
                {
                    "id": 2,
                    "featured_media": "test_related_article_image",
                    "author": None,
                    "categories": [4, 5],
                    "group": [4],
                    "image": None,
                    "tags": ["test_related_article"],
                }
            ],
            "tags": [
                {"id": 1, "name": "test_tag_1"},
                {"id": 2, "name": "test_tag_2"},
            ],
        }

        self.maxDiff = None
        self.assertEqual(context, expected_context)
