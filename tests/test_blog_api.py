# Packages
import requests
from vcr_unittest import VCRTestCase

# Local
from canonicalwebteam.blog import NotFoundError
from canonicalwebteam.blog.blog_api import BlogAPI


class TestBlogAPI(VCRTestCase):
    def test_get_articles(self):
        self.api = BlogAPI(session=requests.Session())

        articles, metadata = self.api.get_articles()

        for article in articles:
            self.assertTrue(int(metadata["total_pages"]) >= 258)
            self.assertTrue(int(metadata["total_posts"]) >= 3095)

        with self.assertRaises(NotFoundError):
            self.api.get_article(slug="nonexistent-slug")

    def test_get_articles_with_transforming_links(self):
        self.api = BlogAPI(session=requests.Session(), transform_links=True)

        article = self.api.get_article(
            slug="/dell-xps-13-developer-edition-with-ubuntu-20-04"
            + "-lts-pre-installed-is-now-available"
        )

        self.assertNotIn(
            "admin.insights.ubuntu.com/wp-content/uploads",
            article["content"]["rendered"],
        )
        self.assertIn(
            "ubuntu.com/wp-content/uploads", article["content"]["rendered"]
        )

    def test_get_articles_without_transforming_links(self):
        self.api = BlogAPI(session=requests.Session(), transform_links=False)

        article = self.api.get_article(
            slug="/dell-xps-13-developer-edition-with-ubuntu-20-04"
            + "-lts-pre-installed-is-now-available"
        )

        self.assertIn(
            "admin.insights.ubuntu.com/wp-content/uploads",
            article["content"]["rendered"],
        )
