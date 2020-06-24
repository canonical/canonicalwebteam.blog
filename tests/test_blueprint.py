# Standard library
import os

# Packages
import flask
import requests
from flask_reggie import Reggie
from bs4 import BeautifulSoup
from vcr_unittest import VCRTestCase

# Local
from canonicalwebteam.blog import build_blueprint, BlogViews, Wordpress


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
                api=Wordpress(session=requests.Session()),
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
        self.assertEqual(soup.find(id="total-pages").text, "258")

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

        for article in events:
            title = article.find("span", {"class": "title"}).text
            slug = article.find("span", {"class": "slug"}).text
            date = article.find("span", {"class": "date"}).text
            self.assertTrue(len(title) > 0)
            self.assertTrue(len(slug) > 0)
            self.assertTrue(len(date) > 0)

    def test_latest_redirect(self):
        homepage_response = self.test_client.get("/")
        latest_response = self.test_client.get("/latest")

        homepage_soup = BeautifulSoup(homepage_response.data, "html.parser")

        first_article = homepage_soup.find(id="articles").findAll("li")[0]
        first_slug = first_article.find("span", {"class": "slug"}).text
        first_url = f"http://localhost/{first_slug}"
        self.assertEqual(latest_response.headers["Location"], first_url)

    def test_feed(self):
        response = self.test_client.get("/feed")

        self.assertTrue(response.status_code, 200)

    def test_author(self):
        response = self.test_client.get("/author/nottrobin")

        self.assertTrue(response.status_code, 200)

    def test_author_feed(self):
        response = self.test_client.get("/author/nottrobin/feed")

        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            response.headers["Content-Type"], "application/rss+xml"
        )

    def test_group(self):
        response = self.test_client.get("/group/design")

        self.assertTrue(response.status_code, 200)

    def test_group_feed(self):
        response = self.test_client.get("/group/design/feed")

        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            response.headers["Content-Type"], "application/rss+xml"
        )

    def test_topic(self):
        response = self.test_client.get("/topic/design")

        self.assertTrue(response.status_code, 200)

    def test_topic_feed(self):
        response = self.test_client.get("/topic/design/feed")

        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            response.headers["Content-Type"], "application/rss+xml"
        )

    def test_tag(self):
        response = self.test_client.get("/tag/design")

        self.assertTrue(response.status_code, 200)

    def test_events_and_webinars(self):
        response = self.test_client.get("/events-and-webinars")

        self.assertTrue(response.status_code, 200)

    def test_archives(self):
        response = self.test_client.get("/archives")

        self.assertTrue(response.status_code, 200)
