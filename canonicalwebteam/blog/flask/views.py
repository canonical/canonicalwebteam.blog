import flask

from canonicalwebteam.blog.common_view_logic import BlogViews
from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog import logic
from canonicalwebteam.blog.common_view_logic import (
    get_index_context,
    get_article_context,
)


def build_blueprint(blog_title, tag_ids, tag_name, excluded_tags=[], enable_upcoming=True):
    blog = flask.Blueprint(
        "blog", __name__, template_folder="/templates", static_folder="/static"
    )

    blog_views = BlogViews(tag_ids, excluded_tags, blog_title, tag_name)

    @blog.route("/")
    def homepage():
        page_param = flask.request.args.get("page", default=1, type=int)
        category_param = flask.request.args.get("category", default="", type=str)

        try:
            context = blog_views.get_index(
                page=page_param,
                category=category_param,
                enable_upcoming=enable_upcoming,
            )
        except Exception:
            return flask.abort(502)

        return flask.render_template("blog/index.html", **context)

    @blog.route("/feed")
    def feed():
        try:
            context = blog_views.get_feed(flask.request.base_url)
        except Exception as e:
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
            articles = api.get_article(slug, tag_ids)
        except Exception:
            return flask.abort(502)

        if not articles:
            flask.abort(404, "Article not found")

        context = get_article_context(articles, tag_ids)

        return flask.render_template("blog/article.html", **context)

    @blog.route("/latest-news")
    def latest_news():
        try:
            latest_pinned_articles = api.get_articles(
                tags=tag_ids,
                exclude=excluded_tags,
                page=1,
                per_page=1,
                sticky=True,
            )
            # check if the number of returned articles is 0
            if len(latest_pinned_articles[0]) == 0:
                latest_articles = api.get_articles(
                    tags=tag_ids,
                    exclude=excluded_tags,
                    page=1,
                    per_page=4,
                    sticky=False,
                )
            else:
                latest_articles = api.get_articles(
                    tags=tag_ids,
                    exclude=excluded_tags,
                    page=1,
                    per_page=3,
                    sticky=False,
                )
        except Exception:
            return flask.jsonify({"Error": "An error ocurred"}), 502

        return flask.jsonify(
            {
                "latest_articles": latest_articles,
                "latest_pinned_articles": latest_pinned_articles,
            }
        )

    return blog
