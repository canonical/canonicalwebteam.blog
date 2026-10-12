# Standard library
import re
import xml.etree.ElementTree as ET
from unittest import TestCase

# Local
from canonicalwebteam.blog import BlogViews


class TestBuildFeedAuthor(TestCase):
    """
    WordPress doesn't expose author emails, so RSS feeds must not emit an
    <author> element (which RSS 2.0 requires to be an email address).
    The author's name should instead be exposed via <dc:creator>.
    """

    def setUp(self):
        self.views = BlogViews(api=None)
        self.article = {
            "title": {"rendered": "Test article"},
            "slug": "test-article",
            "excerpt": {"rendered": "A short excerpt"},
            "content": {"rendered": "<p>Some content</p>"},
            "date_gmt": "2024-01-01T00:00:00",
            "modified_gmt": "2024-01-02T00:00:00",
            "_embedded": {"author": [{"name": "Jane Doe"}]},
        }

    def _build_rss(self):
        feed = self.views._build_feed(
            blog_url="https://example.com/blog",
            feed_url="https://example.com/blog/feed",
            feed_title="Example blog",
            feed_description="Example blog feed",
            articles=[self.article],
        )

        return feed.rss_str(pretty=True)

    def test_no_author_element_with_non_email_value(self):
        rss_bytes = self._build_rss()

        for match in re.findall(rb"<author>(.*?)</author>", rss_bytes):
            self.assertIn(b"@", match)

        self.assertNotIn(b"Jane Doe (Jane Doe)", rss_bytes)

    def test_dc_creator_contains_author_name(self):
        rss_bytes = self._build_rss()

        self.assertIn(b"<dc:creator>Jane Doe</dc:creator>", rss_bytes)

    def test_xml_is_well_formed_and_declares_dc_namespace(self):
        rss_bytes = self._build_rss()

        self.assertIn(
            b'xmlns:dc="http://purl.org/dc/elements/1.1/"', rss_bytes
        )

        # Raises if malformed; also confirms the dc namespace resolves.
        root = ET.fromstring(rss_bytes)
        creator = root.find(
            "channel/item/{http://purl.org/dc/elements/1.1/}creator"
        )
        self.assertIsNotNone(creator)
        self.assertEqual(creator.text, "Jane Doe")
