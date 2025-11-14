# Packages
import flask
import requests
from werkzeug.exceptions import (
    NotFound,
    ServiceUnavailable,
    GatewayTimeout,
)


def build_blueprint(blog_views):
    blueprint = flask.Blueprint("blog", __name__)

    @blueprint.route("/")
    def homepage():
        context = blog_views.get_index(
            page=flask.request.args.get("page", type=int) or 1,
            category_slug=flask.request.args.get("category") or "",
        )

        return flask.render_template("blog/index.html", **context)

    @blueprint.route("/feed")
    def homepage_feed():
        feed = blog_views.get_index_feed(
            uri=flask.request.url_root, path=flask.request.path
        )

        return flask.Response(feed, mimetype="application/rss+xml")

    @blueprint.route("/latest")
    def lastest_article():
        context = blog_views.get_latest_article()

        return flask.redirect(
            flask.url_for(".article", slug=context.get("article").get("slug"))
        )

    @blueprint.route(
        '/<regex("[0-9]{4}"):year>/<regex("[0-9]{2}"):month>/'
        '<regex("[0-9]{2}"):day>/<slug>'
    )
    @blueprint.route(
        '/<regex("[0-9]{4}"):year>/<regex("[0-9]{2}"):month>/<slug>'
    )
    @blueprint.route('/<regex("[0-9]{4}"):year>/<slug>')
    def article_redirect(slug, year, month=None, day=None):
        return flask.redirect(flask.url_for(".article", slug=slug))

    @blueprint.route("/<slug>")
    def article(slug):
        context = blog_views.get_article(slug)

        if not context:
            flask.abort(404, "Article not found")

        return flask.render_template("blog/article.html", **context)

    @blueprint.route("/latest-news")
    def latest_news():
        context = blog_views.get_latest_news(
            tag_ids=flask.request.args.getlist("tag-id"),
            group_ids=flask.request.args.getlist("group-id"),
            limit=flask.request.args.get("limit", "3"),
        )

        return flask.jsonify(context)

    @blueprint.route("/author/<username>")
    def author(username):
        page_param = flask.request.args.get("page", default=1, type=int)
        context = blog_views.get_author(username, page_param)

        if not context:
            flask.abort(404)

        return flask.render_template("blog/author.html", **context)

    @blueprint.route("/author/<username>/feed")
    def author_feed(username):
        feed = blog_views.get_author_feed(
            username=username,
            uri=flask.request.url_root,
            path=flask.request.path,
        )

        if not feed:
            flask.abort(404)

        return flask.Response(feed, mimetype="application/rss+xml")

    @blueprint.route("/archives")
    def archives():
        page_param = flask.request.args.get("page", default=1, type=int)
        group_param = flask.request.args.get("group", default="", type=str)
        month_param = flask.request.args.get("month", default="", type=int)
        year_param = flask.request.args.get("year", default="", type=int)
        category_param = flask.request.args.get(
            "category", default="", type=str
        )

        context = blog_views.get_archives(
            page_param, group_param, month_param, year_param, category_param
        )

        if not context:
            flask.abort(404)

        return flask.render_template("blog/archives.html", **context)

    @blueprint.route("/group/<slug>")
    def group(slug):
        page_param = flask.request.args.get("page", default=1, type=int)
        category_param = flask.request.args.get(
            "category", default="", type=str
        )

        context = blog_views.get_group(slug, page_param, category_param)

        if not context:
            flask.abort(404)

        return flask.render_template("blog/group.html", **context)

    @blueprint.route("/group/<slug>/feed")
    def group_feed(slug):
        feed = blog_views.get_group_feed(
            group_slug=slug,
            uri=flask.request.url_root,
            path=flask.request.path,
        )

        if not feed:
            flask.abort(404)

        return flask.Response(feed, mimetype="application/rss+xml")

    @blueprint.route("/topic/<slug>")
    def topic(slug):
        page_param = flask.request.args.get("page", default=1, type=int)
        context = blog_views.get_topic(slug, page_param)

        return flask.render_template("blog/topic.html", **context)

    @blueprint.route("/topic/<slug>/feed")
    def topic_feed(slug):
        feed = blog_views.get_topic_feed(
            topic_slug=slug,
            uri=flask.request.url_root,
            path=flask.request.path,
        )

        if not feed:
            flask.abort(404)

        return flask.Response(feed, mimetype="application/rss+xml")

    @blueprint.route("/events-and-webinars")
    def events_and_webinars():
        page_param = flask.request.args.get("page", default=1, type=int)
        context = blog_views.get_events_and_webinars(page_param)

        return flask.render_template(
            "blog/events-and-webinars.html", **context
        )

    @blueprint.route("/tag/<slug>")
    def tag(slug):
        page_param = flask.request.args.get("page", default=1, type=int)
        context = blog_views.get_tag(slug, page_param)

        if not context:
            flask.abort(404)

        return flask.render_template("blog/tag.html", **context)

    # Error handling
    @blueprint.app_errorhandler(requests.exceptions.HTTPError)
    def handle_http_error(error):
        """
        Handle HTTP errors from WordPress API requests.

        - Maps specific WP API client errors to 404 to preserve UX
        - Logs parsing and format issues but preserves original behavior
        - Falls back to re-raising the error for non-mapped cases
        """
        response = getattr(error, "response", None)

        # If the HTTPError includes a Response, inspect it for known cases
        if response is not None:
            status = getattr(response, "status_code", None)

            # Convert known pagination error to 404
            if status == 400:
                try:
                    # Only attempt parsing when Content-Type indicates JSON
                    content_type = (response.headers or {}).get(
                        "Content-Type", ""
                    )
                    if "json" in content_type:
                        error_data = response.json()
                    else:
                        error_data = {}

                    # Page number is higher than available pagination
                    if (
                        isinstance(error_data, dict)
                        and error_data.get("code")
                        == "rest_post_invalid_page_number"
                    ):
                        flask.current_app.logger.warning(
                            "Mapping WP API 400 invalid_page_number to 404"
                        )
                        return flask.current_app.handle_http_exception(
                            NotFound()
                        )
                except (
                    ValueError,
                    KeyError,
                    TypeError,
                    AttributeError,
                ) as parse_err:
                    # Log, but fall through to default behavior (re-raise)
                    flask.current_app.logger.debug(
                        f"Failed to parse WP API error JSON: {parse_err}"
                    )

            # If WP API returns 404, propagate as NotFound for consistency
            if status == 404:
                flask.current_app.logger.info("Mapping WP API 404 to NotFound")
                return flask.current_app.handle_http_exception(NotFound())

        # No actionable mapping – preserve original behavior
        flask.current_app.logger.error(
            "Unmapped HTTPError from WP API; re-raising", exc_info=error
        )
        raise error

    @blueprint.app_errorhandler(requests.exceptions.Timeout)
    def handle_timeout(error):
        """Map network timeouts to Gateway Timeout (504)."""
        flask.current_app.logger.error(
            "WordPress API request timed out", exc_info=error
        )
        return flask.current_app.handle_http_exception(GatewayTimeout())

    @blueprint.app_errorhandler(requests.exceptions.ConnectionError)
    def handle_connection_error(error):
        """Map connection errors to Service Unavailable (503)."""
        flask.current_app.logger.error(
            "WordPress API connection error", exc_info=error
        )
        return flask.current_app.handle_http_exception(ServiceUnavailable())

    return blueprint
