from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect
from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog import logic
from canonicalwebteam.blog.common_view_logic import (
    get_index_context,
    get_article_context,
)

tags_id = settings.BLOG_CONFIG.TAGS_ID
blog_title = settings.BLOG_CONFIG.BLOG_TITLE
tag_name = settings.BLOG_CONFIG.TAG_NAME


def index(request):

    page_param = request.GET.get("page", default=1)

    try:
        articles, total_pages = api.get_articles(tags=tags_id, page=page_param)
    except Exception:
        return HttpResponse(status=502)

    context = get_index_context(page_param, articles, total_pages)

    return render(request, "blog/index.html", context)


def feed(request):
    try:
        feed = api.get_feed(tag_name)
    except Exception:
        return HttpResponse(status=502)

    right_urls = logic.change_url(
        feed, request.build_absolute_uri().replace("/feed", "")
    )

    right_title = right_urls.replace("Ubuntu Blog", blog_title)

    return HttpResponse(right_title, status=200, content_type="txt/xml")


def article_redirect(request, slug, year=None, month=None, day=None):
    return redirect("article", slug=slug)


def article(request, slug):
    try:
        articles = api.get_article(tags_id, slug)
    except Exception:
        return HttpResponse(status=502)

    if not articles:
        return HttpResponseNotFound("Article not found")
    context = get_article_context(articles)

    return render(request, "blog/article.html", context)
