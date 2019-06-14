import unittest
import vcr

from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog.common_view_logic import (
    get_complete_article,
    get_index_context,
    get_group_page_context,
    get_topic_page_context,
    get_article_context,
    BlogViews,
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
            complete_article["group"]["name"], "Canonical announcements"
        )

    @vcr.use_cassette("fixtures/vcr_cassettes/get_index_context.yaml")
    def test_get_index_context(self):
        articles, total_pages = api.get_articles()

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

    @vcr.use_cassette("fixtures/vcr_cassettes/get_group_context.yaml")
    def test_get_group_page_context(self):
        articles, total_pages = api.get_articles()

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

    @vcr.use_cassette("fixtures/vcr_cassettes/get_topic_context.yaml")
    def test_get_topic_page_context(self):
        articles, total_pages = api.get_articles()

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

    @vcr.use_cassette("fixtures/vcr_cassettes/get_article_context.yaml")
    def test_get_article_context(self):
        article = api.get_article(
            "canonical-announces-support-for"
            "-ubuntu-on-windows-subsystem-for-linux-2"
        )

        article_context = get_article_context(article)

        self.assertIsNotNone(article_context["article"]["author"]["name"])
        self.assertIsNotNone(article_context["article"]["image"])
        self.assertIsNotNone(article_context["article"]["topic"])

        self.assertEqual(len(article_context["related_articles"]), 3)

        for tag in article_context["tags"]:
            self.assertTrue(tag["id"] in article["tags"])

        self.assertFalse(article_context["is_in_series"])

    @vcr.use_cassette("fixtures/vcr_cassettes/get_tag.yaml")
    def test_get_tag_page_context(self):
        views = BlogViews([], [], "test", "")
        tag_context = views.get_tag("snappy")
        tag_id = api.get_tag_by_slug("snappy")["id"]

        self.assertEqual(tag_context["current_page"], 1)
        self.assertEqual(tag_context["total_pages"], 1)
        self.assertEqual(tag_context["title"], "test")
        self.assertEqual(tag_context["tag"]["id"], tag_id)

        for article in tag_context["articles"]:
            self.assertTrue(tag_id in article["tags"])
