# Packages
import requests
from vcr_unittest import VCRTestCase

# Local
from canonicalwebteam.blog.blog_api import BlogAPI


class TestBlogAPI(VCRTestCase):
    def test_get_articles(self):
        self.api = BlogAPI(session=requests.Session())

        articles, metadata = self.api.get_articles()

        for article in articles:
            self.assertTrue(int(metadata["total_pages"]) >= 258)
            self.assertTrue(int(metadata["total_posts"]) >= 3095)

        no_article = self.api.get_article(slug="nonexistent-slug")
        self.assertEqual(no_article, {})

    def test_get_articles_with_transforming_links(self):
        self.api = BlogAPI(
            session=requests.Session(),
            use_image_template=False,
        )

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

    def test_it_transforms_article_image(self):
        self.api = BlogAPI(
            session=requests.Session(),
            use_image_template=True,
        )

        article = self.api.get_article(
            slug="/dell-xps-13-developer-edition-with-ubuntu-20-04"
            + "-lts-pre-installed-is-now-available"
        )

        self.assertIn(
            'src="https://res.cloudinary.com/canonical/image/fetch/f_auto,'
            "q_auto,fl_sanitize,c_fill,w_720/https://ubuntu.com"
            '/wp-content/uploads/2e4c/dell-xps-2004.jpg"',
            article["content"]["rendered"],
        )

    def test_it_transforms_article_with_fixed_dimensions_image(self):
        self.api = BlogAPI(
            session=requests.Session(),
            use_image_template=True,
        )

        article = self.api.get_article(
            slug="/design-and-web-team-summary-20th-july-2020"
        )

        self.assertIn(
            'src="https://res.cloudinary.com/canonical/image/fetch/f_auto,'
            "q_auto,fl_sanitize,c_fill,w_266,h_286/"
            "https://lh5.googleusercontent.com/"
            "PKCTzU1ENAow2PDqhPo-K6drMTKwQduAAqKNUbHWVnJmmQXjI8GsXgSQhsVg6Q-"
            "0vZrKRCFNUxYvG1iIDVQ3MSTzgx-"
            'UWtGlLR6lgZQWcEt0P967bjqQCePnSJXOd3FWVjo0hzTG"',
            article["content"]["rendered"],
        )

    def test_it_transforms_article_with_percent_width_dimension_image(self):
        self.api = BlogAPI(
            session=requests.Session(),
            use_image_template=True,
        )

        article = self.api.get_article(
            slug="/top-10-linux-apps-for-entertainment-and-leisure"
        )

        self.assertNotIn(
            'src="https://res.cloudinary.com/canonical/image/fetch/'
            "f_auto,q_auto,fl_sanitize,c_fill,w_100%",
            article["content"]["rendered"],
        )
        self.assertIn(
            'src="https://res.cloudinary.com/canonical/image/fetch/'
            "f_auto,q_auto,fl_sanitize,c_fill,w_720",
            article["content"]["rendered"],
        )

    def test_it_does_not_transform_article_image(self):
        self.api = BlogAPI(
            session=requests.Session(),
            use_image_template=False,
        )

        article = self.api.get_article(
            slug="/dell-xps-13-developer-edition-with-ubuntu-20-04"
            + "-lts-pre-installed-is-now-available"
        )

        self.assertIn(
            'src="https://ubuntu.com/'
            'wp-content/uploads/2e4c/dell-xps-2004.jpg"',
            article["content"]["rendered"],
        )

    def test_get_thumbnail_setting(self):
        self.api = BlogAPI(
            session=requests.Session(),
            thumbnail_width=354,
            thumbnail_height=199,
        )

        article = self.api.get_article(
            slug="/dell-xps-13-developer-edition-with-ubuntu-20-04"
            + "-lts-pre-installed-is-now-available"
        )

        self.assertIn("w_354", article["image"]["rendered"],)
        self.assertIn("h_199", article["image"]["rendered"],)
