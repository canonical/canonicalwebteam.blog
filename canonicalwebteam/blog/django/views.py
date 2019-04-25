from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog import logic
from canonicalwebteam.blog.common_view_logic import (
    get_index_context,
    get_article_context,
)

tags_id = settings.BLOG_CONFIG["TAGS_ID"]
excluded_tags = settings.BLOG_CONFIG["EXCLUDED_TAGS"]
blog_title = settings.BLOG_CONFIG["BLOG_TITLE"]
tag_name = settings.BLOG_CONFIG["TAG_NAME"]


def index(request):
    page_param = request.GET.get("page", default=1)

    try:
        articles, total_pages = api.get_articles(
            tags=tags_id, exclude=excluded_tags, page=page_param
        )
    except Exception as e:
        return HttpResponse("Error: " + e, status=502)

    context = get_index_context(page_param, articles, total_pages)
    context["title"] = blog_title

    return render(request, "blog/index.html", context)


def feed(request):
    try:
        feed = api.get_feed(tag_name)
    except Exception as e:
        return HttpResponse("Error: " + e, status=502)

    right_urls = logic.change_url(
        feed, request.build_absolute_uri().replace("/feed", "")
    )

    right_title = right_urls.replace("Ubuntu Blog", blog_title)

    return HttpResponse(right_title, status=200, content_type="txt/xml")


def article_redirect(request, slug, year=None, month=None, day=None):
    return redirect("article", slug=slug)


def article(request, slug):
    try:
        article = api.get_article(slug)
    except Exception as e:
        return HttpResponse("Error: " + e, status=502)

    if not article:
        return HttpResponseNotFound("Article not found")
    context = get_article_context(article)

    return render(request, "blog/article.html", context)


def latest_news(request):

    try:
        latest_pinned_articles = api.get_articles(
            tags=tags_id,
            exclude=excluded_tags,
            page=1,
            per_page=1,
            sticky=True,
        )
        # check if the number of returned articles is 0
        if len(latest_pinned_articles[0]) == 0:
            latest_articles = api.get_articles(
                tags=tags_id,
                exclude=excluded_tags,
                page=1,
                per_page=4,
                sticky=False,
            )
        else:
            latest_articles = api.get_articles(
                tags=tags_id,
                exclude=excluded_tags,
                page=1,
                per_page=3,
                sticky=False,
            )

    except Exception:
        return JsonResponse({"Error": "An error ocurred"}, status=502)
    return JsonResponse(
        {
            "latest_articles": latest_articles,
            "latest_pinned_articles": latest_pinned_articles,
        }
    )
