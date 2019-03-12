from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from canonicalwebteam.blog import wordpress_api as api


def test(request):
    data = {"route": "test"}
    return render(request, "test.html", data)


def index(request):
    data = {"route": "index"}
    return JsonResponse(data)

    def homepage():
        page_param = flask.request.args.get("page", default=1, type=int)

        try:
            articles, total_pages = api.get_articles(
                tags=tags_id, page=page_param
            )
        except Exception:
            return flask.abort(502)

        category_cache = {}
        group_cache = {}

        for article in articles:
            try:
                featured_image = api.get_media(article["featured_media"])
            except Exception:
                featured_image = None

            try:
                author = api.get_user(article["author"])
            except Exception:
                author = None

            category_ids = article["categories"]

            for category_id in category_ids:
                if category_id not in category_cache:
                    category_cache[category_id] = {}

            group_id = article["group"][0]
            if group_id not in group_cache:
                group_cache[group_id] = {}

            article = logic.transform_article(
                article, featured_image=featured_image, author=author
            )

        for key, category in category_cache.items():
            try:
                resolved_category = api.get_category_by_id(key)
            except Exception:
                resolved_category = None

            category_cache[key] = resolved_category

        for key, group in group_cache.items():
            try:
                resolved_group = api.get_group_by_id(key)
            except Exception:
                resolved_group = None

            group_cache[key] = resolved_group

        context = {
            "current_page": page_param,
            "total_pages": int(total_pages),
            "articles": articles,
            "used_categories": category_cache,
            "groups": group_cache,
        }

        return flask.render_template("blog/index.html", **context)

    def feed():
        try:
            feed = api.get_feed(tag_name)
        except Exception as e:
            print(e)
            return flask.abort(502)

        right_urls = logic.change_url(
            feed, flask.request.base_url.replace("/feed", "")
        )

        right_title = right_urls.replace("Ubuntu Blog", blog_title)

        return flask.Response(right_title, mimetype="text/xml")

    def article_redirect(slug, year, month=None, day=None):
        return flask.redirect(flask.url_for(".article", slug=slug))

    def article(slug):
        try:
            articles = api.get_article(tags_id, slug)
        except Exception:
            return flask.abort(502)

        if not articles:
            flask.abort(404, "Article not found")

        article = articles[0]

        try:
            author = api.get_user(article["author"])
        except Exception:
            author = None

        transformed_article = logic.transform_article(
            article, author=author, optimise_images=True
        )

        tags = article["tags"]
        tag_names = []
        try:
            tag_names_response = api.get_tags_by_ids(tags)
        except Exception:
            tag_names_response = None

        if tag_names_response:
            for tag in tag_names_response:
                tag_names.append({"id": tag["id"], "name": tag["name"]})

        is_in_series = logic.is_in_series(tag_names)

        try:
            related_articles, total_pages = api.get_articles(
                tags=tags, per_page=3, exclude=article["id"]
            )
        except Exception:
            related_articles = None

        if related_articles:
            for related_article in related_articles:
                related_article = logic.transform_article(related_article)

        context = {
            "article": transformed_article,
            "related_articles": related_articles,
            "tags": tag_names,
            "is_in_series": is_in_series,
        }

        return flask.render_template("blog/article.html", **context)
