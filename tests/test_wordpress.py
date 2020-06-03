# Packages
import requests
from vcr_unittest import VCRTestCase

# Local
from canonicalwebteam.blog import NotFoundError, Wordpress


class TestWordpress(VCRTestCase):
    def setUp(self):
        self.api = Wordpress(session=requests.Session())
        return super().setUp()

    def test_get_articles(self):
        articles, metadata = self.api.get_articles()
        # I assume these numbers are only gonna grow
        self.assertTrue(int(metadata["total_pages"]) >= 258)
        self.assertTrue(int(metadata["total_posts"]) >= 3095)

        for article in articles:
            self.assertTrue("rendered" in article["content"])

        with self.assertRaises(NotFoundError):
            self.api.get_article(slug="nonexistent-slug")

        article = self.api.get_article(slug="testing-your-user-contract")

        self.assertEqual(
            article["title"]["rendered"], "Testing your user contract"
        )
        self.assertIn("<p>", article["content"]["rendered"])

    def test_get_users(self):
        user = self.api.get_user_by_id(id=217)
        self.assertEqual(user["name"], "Canonical")
        self.assertEqual(user["slug"], "canonical")

        user = self.api.get_user_by_username(username="canonical")
        self.assertEqual(user["name"], "Canonical")
        self.assertEqual(user["id"], 217)

    def test_get_media(self):
        media = self.api.get_media(id=89203)
        self.assertIn("link", media)

    def test_get_tags(self):
        tag = self.api.get_tag_by_slug(slug="design")
        self.assertEqual(tag["name"], "Design")
        self.assertEqual(tag["id"], 1239)
        self.assertTrue(tag["count"] >= 542)

        tag = self.api.get_tag_by_id(id=1239)
        self.assertEqual(tag["name"], "Design")
        self.assertEqual(tag["slug"], "design")
        self.assertTrue(tag["count"] >= 542)

        tag = self.api.get_tag_by_name(name="Design")
        # Note: This highlights a flaw in this method,
        # it's really just a search.
        # My hunch would be to remove it, but snapcraft needs it
        self.assertEqual(tag["name"], "app design")

    def test_get_categories(self):
        category = self.api.get_category_by_id(id=1453)
        self.assertEqual(category["name"], "Articles")
        self.assertEqual(category["slug"], "articles")

        category = self.api.get_category_by_slug(slug="articles")
        self.assertEqual(category["name"], "Articles")
        self.assertEqual(category["id"], 1453)

        categories = self.api.get_categories()
        self.assertEqual(len(categories), 45)
        for category in categories:
            self.assertIn("count", category)
            self.assertIn("name", category)

    def test_get_groups(self):
        group = self.api.get_group_by_id(id=3367)
        self.assertEqual(group["name"], "AI")
        self.assertEqual(group["slug"], "ai")

        group = self.api.get_group_by_slug(slug="ai")
        self.assertEqual(group["name"], "AI")
        self.assertEqual(group["id"], 3367)
