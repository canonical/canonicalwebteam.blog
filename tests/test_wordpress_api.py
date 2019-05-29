import unittest
import vcr

from datetime import timedelta, datetime
from unittest.mock import patch
from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.http import CachedSession

# make sure that timeouts do not hinder tests
api.api_session = CachedSession(fallback_cache_duration=3600, timeout=(1, 100))


class FailingMockResponse:
    ok = False

    def raise_for_status(*args):
        raise Exception()

    headers = {"X-WP-TotalPages": 12}


class TestWordPressApi(unittest.TestCase):
    @vcr.use_cassette("fixtures/vcr_cassettes/articles_with_metadata.yaml")
    def test_get_articles_with_metadata(self):
        articles, metadata = api.get_articles_with_metadata()
        self.assertIsNotNone(metadata["total_pages"])
        self.assertIsNotNone(metadata["total_posts"])
        self.assertEqual(len(articles), 12)

        # all other functionality is test via get_articles

    @vcr.use_cassette("fixtures/vcr_cassettes/articles.yaml")
    def test_get_articles(self):
        articles, total_pages = api.get_articles()
        self.assertIsInstance(total_pages, str)
        self.assertEqual(len(articles), 12)

        first_page_articles, _ = api.get_articles(page=1, per_page=6)
        second_page_articles, _ = api.get_articles(page=2, per_page=6)
        first_and_second, _ = api.get_articles(per_page=12)
        self.assertEqual(len(first_page_articles), 6)
        self.assertEqual(len(second_page_articles), 6)
        self.assertEqual(len(first_and_second), 12)
        for article in first_page_articles:
            self.assertTrue(article in first_and_second)
        for article in second_page_articles:
            self.assertTrue(article in first_and_second)
        for article in second_page_articles:
            self.assertTrue(article not in first_page_articles)

        articles_without_tags, _ = api.get_articles(tags_exclude=[3278])

        for article in articles_without_tags:
            self.assertTrue(3278 not in article["tags"])

        articles_all_have_one_tag, _ = api.get_articles(tags=[3278])

        for article in articles_all_have_one_tag:
            self.assertTrue(3278 in article["tags"])

        # TODO: this is not yet implemented
        # articles_with_all_tags, _ = api.get_articles(tags=[3278, 1419])

        # for article in articles_with_all_tags:
        #    self.assertTrue(
        #        3278 in article["tags"] and 1419 in article["tags"]
        #    )

        articles_with_either_tags, _ = api.get_articles(tags=[3278, 1419])
        for article in articles_with_either_tags:
            self.assertTrue(3278 in article["tags"] or 1419 in article["tags"])

        articles_for_one_tag_excluding_another_tag, _ = api.get_articles(
            tags=[3278], tags_exclude=[1419]
        )

        self.assertTrue(
            articles_for_one_tag_excluding_another_tag
            is not articles_all_have_one_tag
        )

        articles_for_category, _ = api.get_articles(categories=[1453])
        for article in articles_for_category:
            self.assertTrue(1453 in article["categories"])

        featured_articles, _ = api.get_articles(sticky=True)
        for article in featured_articles:
            self.assertTrue(article["sticky"] is True)

        before = datetime(
            year=2018, month=12, day=30, hour=12, minute=00, second=00
        )
        after = before - timedelta(days=365)
        articles_in_2018, _ = api.get_articles(after=after, before=before)
        for article in articles_in_2018:
            self.assertTrue("2018" in article["date"])

        articles_from_author, _ = api.get_articles(author=217)
        for article in articles_from_author:
            self.assertTrue(article["author"] == 217)

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
            api.get_articles()
