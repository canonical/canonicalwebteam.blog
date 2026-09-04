import flask
import requests
import unittest
from flask_reggie import Reggie

from canonicalwebteam.blog import build_blueprint


class StubViews:
    def get_tag(self, slug, page=1):
        if slug == "invalid-page":
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b'{"code":"rest_post_invalid_page_number"}'
            resp.headers = {"Content-Type": "application/json"}
            raise requests.exceptions.HTTPError(response=resp)
        if slug == "bad-json":
            resp = requests.Response()
            resp.status_code = 400
            resp._content = b"not json"
            resp.headers = {"Content-Type": "text/plain"}
            raise requests.exceptions.HTTPError(response=resp)
        if slug == "no-response":
            raise requests.exceptions.HTTPError(response=None)
        if slug == "timeout":
            raise requests.exceptions.Timeout()
        if slug == "conn":
            raise requests.exceptions.ConnectionError()
        if slug == "http404":
            resp = requests.Response()
            resp.status_code = 404
            resp._content = b"{}"
            resp.headers = {"Content-Type": "application/json"}
            raise requests.exceptions.HTTPError(response=resp)
        if slug == "reqexc":
            raise requests.exceptions.RequestException("generic")
        # default: return some context to render
        return {
            "title": "Test",
            "articles": [],
            "current_page": page,
            "total_pages": 1,
            "total_posts": 0,
            "blog_title": "Test",
            "tag": {"id": 1, "name": "t", "slug": "t"},
        }


class TestBlueprintErrorHandlers(unittest.TestCase):
    def setUp(self):
        app = flask.Flask("test")
        Reggie().init_app(app)
        blog = build_blueprint(blog_views=StubViews())
        app.register_blueprint(blog, url_prefix="/")
        # Disable exception propagation so we can assert on status codes
        app.testing = False
        self.client = app.test_client()

    def test_invalid_page_number_maps_to_404(self):
        resp = self.client.get("/tag/invalid-page")
        self.assertEqual(resp.status_code, 404)

    def test_bad_json_unmapped_results_in_500(self):
        resp = self.client.get("/tag/bad-json")
        self.assertEqual(resp.status_code, 500)

    def test_no_response_re_raises_results_in_500(self):
        resp = self.client.get("/tag/no-response")
        self.assertEqual(resp.status_code, 500)

    def test_timeout_returns_504(self):
        resp = self.client.get("/tag/timeout")
        self.assertEqual(resp.status_code, 504)

    def test_connection_error_returns_503(self):
        resp = self.client.get("/tag/conn")
        self.assertEqual(resp.status_code, 503)

    def test_http_404_maps_to_404(self):
        resp = self.client.get("/tag/http404")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
