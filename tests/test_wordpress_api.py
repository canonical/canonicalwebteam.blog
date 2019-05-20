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
    @vcr.use_cassette("fixtures/vcr_cassettes/synopsis.yaml")
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

    @patch("canonicalwebteam.http.CachedSession.get")
    def test_getting_articles_fail(self, get):

        get.return_value = FailingMockResponse()

        with self.assertRaises(Exception):
            api.get.articles()
