# Packages
import flask


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
        month_param = flask.request.args.get("month", default="", type=str)
        year_param = flask.request.args.get("year", default="", type=str)
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

    return blueprint
