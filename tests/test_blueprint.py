# Standard library
import os

# Packages
import flask
import requests
from flask_reggie import Reggie
from bs4 import BeautifulSoup
from vcr_unittest import VCRTestCase

# Local
from canonicalwebteam.blog import build_blueprint, BlogViews
from canonicalwebteam.blog.blog_api import BlogAPI

this_dir = os.path.dirname(os.path.realpath(__file__))


class TestBlueprint(VCRTestCase):
    def setUp(self):
        super().setUp()

        app = flask.Flask(
            "main", template_folder=f"{this_dir}/fixtures/templates"
        )
        Reggie().init_app(app)

        blog = build_blueprint(
            blog_views=BlogViews(
                blog_title="Snapcraft Blog",
                blog_path="/",
                api=BlogAPI(session=requests.Session()),
            )
        )
        app.register_blueprint(blog, url_prefix="/")

        app.testing = True

        self.test_client = app.test_client()

    def test_article(self):
        response = self.test_client.get("/testing-your-user-contract")

        self.assertIn(
            b"<title>Testing your user contract</title>", response.data
        )
        self.assertIn(b"<time>10 February 2020</time>", response.data)
        self.assertIn(b'<a rel="author">Jeff Pihach</a>', response.data)

    def test_article_not_exist(self):
        response = self.test_client.get("/not-exist")

        self.assertEqual(response.status_code, 404)

    def test_article_with_image(self):
        response = self.test_client.get(
            "/dell-xps-13-developer-edition-with-ubuntu-20-04"
            + "-lts-pre-installed-is-now-available"
        )

        self.assertNotIn(
            b"admin.insights.ubuntu.com/wp-content/uploads", response.data
        )
        self.assertIn(b"ubuntu.com/wp-content/uploads", response.data)

        image_src = (
            "src=&#34;https://res.cloudinary.com/canonical/image/fetch/"
            "f_auto,q_auto,fl_sanitize,c_fill,w_720/"
            "https://ubuntu.com/wp-content/uploads/2e4c/dell-xps-2004.jpg&#34;"
        )

        self.assertIn(str.encode(image_src), response.data)

    def test_article_with_relative_path_image(self):
        response = self.test_client.get(
            "/the-ubuntu-community-contributes-towards-saving-the-iberian-lynx"
        )

        self.assertEqual(response.status_code, 200)

        image_src = (
            "src=&#34;../wp-content/uploads//2010/10/iberian_lynx.jpg&#34;"
        )

        self.assertIn(str.encode(image_src), response.data)

    def test_article_redirect(self):
        response = self.test_client.get(
            "/2022/12/12/testing-your-user-contract"
        )
        self.assertEqual(
            response.headers["Location"],
            "http://localhost/testing-your-user-contract",
        )

    def test_homepage(self):
        response = self.test_client.get("/")

        soup = BeautifulSoup(response.data, "html.parser")

        self.assertEqual(soup.find(id="current-page").text, "1")
        self.assertEqual(soup.find(id="total-pages").text, "262")

        articles = soup.find(id="articles").findAll("li")
        featured = soup.find(id="featured").findAll("li")
        events = soup.find(id="events").findAll("li")

        self.assertEqual(len(articles), 12)
        self.assertEqual(len(featured), 12)
        self.assertEqual(len(events), 3)

        for article in articles + featured:
            author = article.find("span", {"class": "author"}).text
            slug = article.find("span", {"class": "slug"}).text
            title = article.find("span", {"class": "title"}).text
            self.assertTrue(len(author) > 0)
            self.assertTrue(len(slug) > 0)
            self.assertTrue(len(title) > 0)

            image = article.find("img")
            if image is not None:
                self.assertIn(
                    "https://res.cloudinary.com/canonical/image/fetch/"
                    "f_auto,q_auto,fl_sanitize,e_sharpen,c_fill,w_330,h_185/"
                    "https://ubuntu.com/wp-content/uploads",
                    image.get("src"),
                )

        for article in events:
            title = article.find("span", {"class": "title"}).text
            slug = article.find("span", {"class": "slug"}).text
            date = article.find("span", {"class": "date"}).text
            self.assertTrue(len(title) > 0)
            self.assertTrue(len(slug) > 0)
            self.assertTrue(len(date) > 0)

            image = article.find("img")
            if image is not None:
                self.assertIn(
                    "https://res.cloudinary.com/canonical/image/fetch/"
                    "f_auto,q_auto,fl_sanitize,e_sharpen,c_fill,w_330,h_185/"
                    "https://ubuntu.com/wp-content/uploads",
                    image.get("src"),
                )

    def test_latest_redirect(self):
        homepage_response = self.test_client.get("/")
        latest_response = self.test_client.get("/latest")

        homepage_soup = BeautifulSoup(homepage_response.data, "html.parser")

        first_article = homepage_soup.find(id="articles").findAll("li")[0]
        first_slug = first_article.find("span", {"class": "slug"}).text
        first_url = f"http://localhost/{first_slug}"
        self.assertEqual(latest_response.headers["Location"], first_url)

    def test_category_not_exist(self):
        response = self.test_client.get("/archives?category=not-exist")

        self.assertEqual(response.status_code, 200)

    def test_archive_int_year_month(self):
        response = self.test_client.get(
            "/archives?group=phone-and-tablet&month=11%27%5B0%5D&year=2015das"
        )

        self.assertEqual(response.status_code, 200)

    def test_feed(self):
        response = self.test_client.get("/feed")

        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.test_client.get("/author/nottrobin")

        self.assertEqual(response.status_code, 200)

    def test_author_not_exist(self):
        response = self.test_client.get("/author/not-exist")

        self.assertEqual(response.status_code, 404)

    def test_author_feed(self):
        response = self.test_client.get("/author/nottrobin/feed")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.headers["Content-Type"], "application/rss+xml"
        )

    def test_author_feed_not_exist(self):
        response = self.test_client.get("/author/not-exist/feed")

        self.assertEqual(response.status_code, 404)

    def test_group(self):
        response = self.test_client.get("/group/design")

        self.assertEqual(response.status_code, 200)

    def test_group_not_exist(self):
        response = self.test_client.get("/group/not-exist")

        self.assertEqual(response.status_code, 200)

    def test_group_feed(self):
        response = self.test_client.get("/group/design/feed")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.headers["Content-Type"], "application/rss+xml"
        )

    def test_group_feed_not_exist(self):
        response = self.test_client.get("/group/not-exist/feed")

        self.assertEqual(response.status_code, 404)

    def test_group_feed_works_with_image_without_src(self):
        response = self.test_client.get("/group/phone-and-tablet/feed")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'&lt;img alt=""/&gt;', response.data)

    def test_topic(self):
        response = self.test_client.get("/topic/design")

        self.assertEqual(response.status_code, 200)

    def test_topic_not_exists(self):
        response = self.test_client.get("/topic/not-exists")

        self.assertEqual(response.status_code, 200)

    def test_topic_feed(self):
        response = self.test_client.get("/topic/design/feed")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.headers["Content-Type"], "application/rss+xml"
        )

    def test_topic_feed_not_exists(self):
        response = self.test_client.get("/topic/not-exists/feed")

        self.assertEqual(response.status_code, 404)

    def test_tag(self):
        response = self.test_client.get("/tag/design")

        self.assertEqual(response.status_code, 200)

    def test_tag_not_exist(self):

        response = self.test_client.get("/tag/not-exist")

        self.assertEqual(response.status_code, 404)

    def test_events_and_webinars(self):
        response = self.test_client.get("/events-and-webinars")

        self.assertEqual(response.status_code, 200)

    def test_archives(self):
        response = self.test_client.get("/archives")

        self.assertEqual(response.status_code, 200)
