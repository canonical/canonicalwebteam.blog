# Standard library
from unittest import TestCase
from unittest.mock import MagicMock

# Local
from canonicalwebteam.blog import BlogViews


class TestGetLatestNews(TestCase):
    def _make_views(self):
        api = MagicMock()
        api.get_articles.return_value = (
            [{"id": 1}],
            {"total_pages": "1", "total_posts": "1"},
        )
        return BlogViews(api=api), api

    def test_default_splits_pinned_and_latest(self):
        views, api = self._make_views()

        result = views.get_latest_news()

        # One call for the sticky (pinned) post, one for the rest
        self.assertEqual(api.get_articles.call_count, 2)
        pinned_call, latest_call = api.get_articles.call_args_list
        self.assertTrue(pinned_call.kwargs["sticky"])
        self.assertFalse(latest_call.kwargs["sticky"])
        self.assertEqual(result["latest_pinned_articles"], [{"id": 1}])

    def test_all_articles_fetches_single_list_without_sticky(self):
        views, api = self._make_views()

        result = views.get_latest_news(all_articles=True)

        # A single call, with no sticky filtering applied
        self.assertEqual(api.get_articles.call_count, 1)
        self.assertNotIn("sticky", api.get_articles.call_args.kwargs)
        self.assertEqual(result["latest_pinned_articles"], [])
        self.assertEqual(result["latest_articles"], [{"id": 1}])

    def test_all_articles_respects_limit(self):
        views, api = self._make_views()

        views.get_latest_news(limit=5, all_articles=True)

        self.assertEqual(api.get_articles.call_args.kwargs["per_page"], 5)
