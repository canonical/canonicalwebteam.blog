import flask

from canonicalwebteam.blog.common_view_logic import BlogViews


def build_blueprint(
    blog_title, tag_ids, tag_name, excluded_tags=[], enable_upcoming=True
):
    blog = flask.Blueprint(
        "blog", __name__, template_folder="/templates", static_folder="/static"
    )

    blog_views = BlogViews(tag_ids, excluded_tags, blog_title, tag_name)

    @blog.route("/")
    def homepage():
        page_param = flask.request.args.get("page", default=1, type=int)
        category_param = flask.request.args.get(
            "category", default="", type=str
        )

        try:
            context = blog_views.get_index(
                page=page_param,
                category=category_param,
                enable_upcoming=enable_upcoming,
            )
        except Exception:
            return flask.abort(502)

        return flask.render_template("blog/index.html", **context)

    @blog.route("/latest")
    def lastest_article():
        try:
            context = blog_views.get_latest_article()
        except Exception:
            return flask.abort(502)

        return flask.render_template("blog/article.html", **context)

    @blog.route("/feed")
    def feed():
        try:
            context = blog_views.get_feed(flask.request.base_url)
        except Exception:
            return flask.abort(502)

        return flask.Response(context, mimetype="text/xml")

    @blog.route(
        '/<regex("[0-9]{4}"):year>/<regex("[0-9]{2}"):month>/'
        '<regex("[0-9]{2}"):day>/<slug>'
    )
    @blog.route('/<regex("[0-9]{4}"):year>/<regex("[0-9]{2}"):month>/<slug>')
    @blog.route('/<regex("[0-9]{4}"):year>/<slug>')
    def article_redirect(slug, year, month=None, day=None):
        return flask.redirect(flask.url_for(".article", slug=slug))

    @blog.route("/<slug>")
    def article(slug):
        try:
            context = blog_views.get_article(slug)
        except Exception:
            return flask.abort(502)

        if not context:
            flask.abort(404, "Article not found")

        return flask.render_template("blog/article.html", **context)

    @blog.route("/latest-news")
    def latest_news():
        try:
            context = blog_views.get_latest_news()
        except Exception:
            return flask.jsonify({"Error": "An error ocurred"}), 502

        return flask.jsonify(context)

    @blog.route("/author/<username>")
    def author(username):
        page_param = flask.request.args.get("page", default=1, type=int)
        try:
            context = blog_views.get_author(username, page_param)
        except Exception:
            return flask.abort(502)

        if not context:
            flask.abort(404)

        return flask.render_template("blog/author.html", **context)

    @blog.route("/archives")
    def archives():
        page_param = flask.request.args.get("page", default=1, type=int)
        group_param = flask.request.args.get("group", default="", type=str)
        month_param = flask.request.args.get("month", default="", type=str)
        year_param = flask.request.args.get("year", default="", type=str)
        category_param = flask.request.args.get(
            "category", default="", type=str
        )

        try:
            context = blog_views.get_archives(
                page_param,
                group_param,
                month_param,
                year_param,
                category_param,
            )
        except Exception:
            flask.abort(502)

        return flask.render_template("blog/archives.html", **context)

    @blog.route("/group/<slug>")
    def group(slug):
        page_param = flask.request.args.get("page", default=1, type=int)
        category_param = flask.request.args.get(
            "category", default="", type=str
        )

        try:
            context = blog_views.get_group(slug, page_param, category_param)
        except Exception:
            flask.abort(502)

        return flask.render_template("blog/group.html", **context)

    @blog.route("/topic/<slug>")
    def topic(slug):
        page_param = flask.request.args.get("page", default=1, type=int)

        try:
            context = blog_views.get_topic(slug, page_param)
        except Exception:
            flask.abort(502)

        return flask.render_template("blog/topic.html", **context)

    @blog.route("/upcoming")
    def upcoming():
        page_param = flask.request.args.get("page", default=1, type=int)

        try:
            context = blog_views.get_upcoming(page_param)
        except Exception:
            flask.abort(502)

        return flask.render_template("blog/upcoming.html", **context)

    @blog.route("/tag/<slug>")
    def tag(slug):
        page_param = flask.request.args.get("page", default=1, type=int)

        try:
            context = blog_views.get_tag(slug, page_param)
        except Exception:
            flask.abort(404)

        return flask.render_template("blog/tag.html", **context)

    return blog
