import unittest
import vcr

from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog.common_view_logic import (
    get_complete_article,
    get_index_context,
    get_group_page_context,
    get_topic_page_context,
    get_article_context,
)
from canonicalwebteam.http import Session

api.api_session = Session()


class TestCommonViewLogic(unittest.TestCase):
    @vcr.use_cassette("fixtures/vcr_cassettes/get_complete_article.yaml")
    def test_get_complete_article(self):
        article = api.get_article(
            "canonical-announces-support-for"
            "-ubuntu-on-windows-subsystem-for-linux-2"
        )
        article["categories"] = [1453]

        complete_article = get_complete_article(article)
        self.assertEqual(complete_article["author"]["name"], "Canonical")
        self.assertEqual(
            complete_article["image"]["id"], article["featured_media"]
        )
        self.assertEqual(complete_article["date"], "6 May 2019")

        # The maximum allowed character count for the excerpt is 339
        # characters. If this limit is reached [...] is added
        # which is why we test for a max length of 339 + 5 = 344 here
        self.assertLessEqual(len(complete_article["excerpt"]["raw"]), 344)

        self.assertEqual(
            complete_article["display_category"]["name"], "Articles"
        )
        self.assertEqual(
            complete_article["group"]["name"], "Canonical announcements"
        )

    @vcr.use_cassette("fixtures/vcr_cassettes/get_index_context.yaml")
    def test_get_index_context(self):
        articles, total_pages = api.get_articles()
        all_categories = [
            category
            for article in articles
            for category in article["categories"]
        ]
        all_groups = [
            group for article in articles for group in article["group"]
        ]

        featured, _ = api.get_articles(sticky=True)

        index_context = get_index_context(1, articles, "2", featured)

        self.assertEqual(index_context["current_page"], 1)
        self.assertEqual(index_context["total_pages"], 2)

        for article in index_context["articles"]:
            self.assertIsNotNone(article["author"]["name"])
            self.assertIsNotNone(article["image"])
            self.assertIsNotNone(article["group"])

        for article in index_context["featured_articles"]:
            self.assertIsNotNone(article["author"]["name"])
            self.assertIsNotNone(article["image"])
            self.assertIsNotNone(article["group"])

        used_categories = list(index_context["used_categories"].keys())
        for category in all_categories:
            self.assertTrue(category in used_categories)

        used_groups = list(index_context["groups"].keys())
        for group in all_groups:
            self.assertTrue(group in used_groups)

    @vcr.use_cassette("fixtures/vcr_cassettes/get_group_context.yaml")
    def test_get_group_page_context(self):
        articles, total_pages = api.get_articles()
        all_categories = [
            category
            for article in articles
            for category in article["categories"]
        ]

        featured, _ = api.get_articles(sticky=True)

        # TODO: TDD refactor of function signature, to get
        # the groups based on a group id
        # https://github.com/canonical-web-and-design/canonicalwebteam.blog/issues/68
        group_context = get_group_page_context(
            1, articles, "2", "test", featured
        )

        self.assertEqual(group_context["current_page"], 1)
        self.assertEqual(group_context["total_pages"], 2)
        self.assertEqual(group_context["group"], "test")

        for article in group_context["articles"]:
            self.assertIsNotNone(article["author"]["name"])
            self.assertIsNotNone(article["image"])
            self.assertIsNotNone(article["group"])

        for article in group_context["featured_articles"]:
            self.assertIsNotNone(article["author"]["name"])
            self.assertIsNotNone(article["image"])
            self.assertIsNotNone(article["group"])

        used_categories = list(group_context["used_categories"].keys())
        for category in all_categories:
            self.assertTrue(category in used_categories)

    @vcr.use_cassette("fixtures/vcr_cassettes/get_topic_context.yaml")
    def test_get_topic_page_context(self):
        articles, total_pages = api.get_articles()
        all_categories = [
            category
            for article in articles
            for category in article["categories"]
        ]

        all_groups = [
            group for article in articles for group in article["group"]
        ]

        featured, _ = api.get_articles(sticky=True)

        # TODO: TDD refactor of function signature, to include
        # get the context by topic id
        # https://github.com/canonical-web-and-design/canonicalwebteam.blog/issues/69
        topic_context = get_topic_page_context(1, articles, "2")

        self.assertEqual(topic_context["current_page"], 1)
        self.assertEqual(topic_context["total_pages"], 2)

        for article in topic_context["articles"]:
            self.assertIsNotNone(article["author"]["name"])
            self.assertIsNotNone(article["image"])
            self.assertIsNotNone(article["topic"])

        used_categories = list(topic_context["used_categories"].keys())
        for category in all_categories:
            self.assertTrue(category in used_categories)

        used_topics = list(topic_context["groups"].keys())
        for topic in all_groups:
            self.assertTrue(topic in used_topics)

    @vcr.use_cassette("fixtures/vcr_cassettes/get_article_context.yaml")
    def test_get_article_context(self):
        article = api.get_article(
            "canonical-announces-support-for"
            "-ubuntu-on-windows-subsystem-for-linux-2"
        )

        article_context = get_article_context(article)

        self.assertIsNotNone(article_context["article"]["author"]["name"])
        self.assertTrue(
            "cloudinary" in article_context["article"]["content"]["rendered"]
        )
        self.assertIsNotNone(article_context["article"]["topic"])

        self.assertEqual(len(article_context["related_articles"]), 3)

        for tag in article_context["tags"]:
            self.assertTrue(tag["id"] in article["tags"])

        self.assertFalse(article_context["is_in_series"])
