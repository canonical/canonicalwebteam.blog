import unittest
import vcr

from datetime import timedelta, date
from unittest.mock import patch
from canonicalwebteam.blog import wordpress_api as api


class FailingMockResponse:
    ok = False

    def raise_for_status(*args):
        raise Exception()

    headers = {"X-WP-TotalPages": 12}


class TestWordPressApi(unittest.TestCase):
    def test_build_get_articles_url(self,):

        base_url = (
            "https://admin.insights.ubuntu.com/"
            + "wp-json/wp/v2/posts?"
            + "per_page=12"
            + "&tags="
            + "&page=1"
            + "&group="
            + "&tags_exclude="
            + "&categories="
            + "&exclude="
            + "&author="
        )

        url = api.build_get_articles_url(page=3, per_page=24)
        self.assertEqual(
            base_url.replace("per_page=12", "per_page=24").replace(
                "page=1", "page=3"
            ),
            url,
        )

        url = api.build_get_articles_url(tags_exclude=[1234, 5678])
        self.assertEqual(
            base_url.replace("tags_exclude=", "tags_exclude=1234,5678"), url
        )

        url = api.build_get_articles_url(tags=[1234, 5678])
        self.assertEqual(base_url.replace("tags=", "tags=1234,5678"), url)

        url = api.build_get_articles_url(
            tags=[1234, 5678], tags_exclude=[9876]
        )
        self.assertEqual(
            base_url.replace("tags=", "tags=1234,5678").replace(
                "tags_exclude=", "tags_exclude=9876"
            ),
            url,
        )

        url = api.build_get_articles_url(categories=[5678])
        self.assertEqual(
            base_url.replace("categories=", "categories=5678"), url
        )

        url = api.build_get_articles_url(sticky=True)
        self.assertEqual(base_url + "&sticky=True", url)

        before = date(year=2007, month=12, day=5)
        after = before - timedelta(days=365)

        url = api.build_get_articles_url(after=after, before=before)
        self.assertEqual(
            base_url + "&before=2007-12-05" + "&after=2006-12-05", url
        )

        url = api.build_get_articles_url(author=1)
        self.assertEqual(base_url.replace("author=", "author=1"), url)

    @vcr.use_cassette("fixtures/vcr_cassettes/articles_with_metadata.yaml")
    def test_get_articles_with_metadata(self):
        articles, metadata = api.get_articles_with_metadata()
        self.assertIsNotNone(metadata["total_pages"])
        self.assertIsNotNone(metadata["total_posts"])
        self.assertEqual(len(articles), 12)

    @vcr.use_cassette("fixtures/vcr_cassettes/articles.yaml")
    def test_get_articles(self):
        articles, total_pages = api.get_articles()
        self.assertIsInstance(total_pages, str)
        self.assertEqual(len(articles), 12)

    @vcr.use_cassette("fixtures/vcr_cassettes/article.yaml")
    def test_get_article(self):
        slug = (
            "canonical-announces-support-"
            "for-ubuntu-on-windows-subsystem-for-linux-2"
        )
        article = api.get_article(slug=slug)
        self.assertEqual(article["slug"], slug)

    @vcr.use_cassette("fixtures/vcr_cassettes/user_by_id.yaml")
    def test_get_user(self):
        user_id = 217
        user = api.get_user(user_id)
        self.assertEqual(user["id"], user_id)

    @vcr.use_cassette("fixtures/vcr_cassettes/user_by_username.yaml")
    def test_get_user_by_username(self):
        username = "canonical"
        user = api.get_user_by_username(username)
        self.assertEqual(user["slug"], username)

        user = api.get_user_by_username("thisonedoesnotexist")
        self.assertIsNone(user)

    @vcr.use_cassette("fixtures/vcr_cassettes/media.yaml")
    def test_get_media(self):
        id = 89203
        media = api.get_media(id)
        self.assertEqual(media["id"], id)

        id = 0
        media = api.get_media(id)
        self.assertIsNone(media)

    @vcr.use_cassette("fixtures/vcr_cassettes/tag_by_slug.yaml")
    def test_get_tag_by_slug(self):
        slug = "snappy"
        tag = api.get_tag_by_slug(slug)
        self.assertEqual(tag["slug"], slug)

        slug = "doesnotexist"
        tag = api.get_tag_by_slug(slug)
        self.assertIsNone(tag)

    @vcr.use_cassette("fixtures/vcr_cassettes/category_by_id.yaml")
    def test_get_category_by_id(self):
        id = 1453
        category = api.get_category_by_id(id)
        self.assertEqual(category["id"], id)

    @vcr.use_cassette("fixtures/vcr_cassettes/category_by_slug.yaml")
    def test_get_category_by_slug(self):
        slug = "articles"
        category = api.get_category_by_slug(slug)
        self.assertEqual(category["slug"], slug)

        slug = "doesnotexist"
        category = api.get_category_by_slug(slug)
        self.assertIsNone(category)

    @vcr.use_cassette("fixtures/vcr_cassettes/categories.yaml")
    def test_get_categories(self):
        categories = api.get_categories()
        self.assertEqual(categories[0]["taxonomy"], "category")

    @vcr.use_cassette("fixtures/vcr_cassettes/group_by_id.yaml")
    def test_get_group_by_id(self):
        id = 3367
        group = api.get_group_by_id(id)
        self.assertEqual(group["id"], id)

    @vcr.use_cassette("fixtures/vcr_cassettes/group_by_slug.yaml")
    def test_get_group_by_slug(self):
        slug = "ai"
        group = api.get_group_by_slug(slug)
        self.assertEqual(group["slug"], slug)

        slug = "doesnotexist"
        category = api.get_category_by_slug(slug)
        self.assertIsNone(category)

    @vcr.use_cassette("fixtures/vcr_cassettes/tags_by_ids.yaml")
    def test_get_tags_by_ids(self):
        ids = [2080, 2655]
        tags = api.get_tags_by_ids(ids)
        for tag in tags:
            self.assertTrue(tag["id"] in ids)

    @vcr.use_cassette("fixtures/vcr_cassettes/tags_by_name.yaml")
    def test_get_tag_by_name(self):
        name = "10.04"
        tag = api.get_tag_by_name(name)
        self.assertEqual(tag["name"], name)

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting_articles_fail(self, get):
        get.return_value = FailingMockResponse()

        with self.assertRaises(Exception):
            api.get.articles()
