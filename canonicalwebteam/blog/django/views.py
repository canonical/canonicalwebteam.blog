from canonicalwebteam.blog.common_view_logic import BlogViews
from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect, render


tag_ids = settings.BLOG_CONFIG["TAG_IDS"]
excluded_tags = settings.BLOG_CONFIG["EXCLUDED_TAGS"]
blog_title = settings.BLOG_CONFIG["BLOG_TITLE"]
feed_description = settings.BLOG_CONFIG.get("FEED_DESCRIPTION")
per_page = settings.BLOG_CONFIG.get("PER_PAGE", 12)


blog_views = BlogViews(
    tag_ids=tag_ids,
    excluded_tags=excluded_tags,
    blog_title=blog_title,
    feed_description=feed_description,
    per_page=per_page,
)


def str_to_int(string):
    try:
        return int(string)
    except ValueError:
        return 1


def index(request, enable_upcoming=True):
    page_param = str_to_int(request.GET.get("page", default="1"))
    category_param = request.GET.get("category", default="")

    context = blog_views.get_index(
        page=page_param,
        category=category_param,
        enable_upcoming=enable_upcoming,
    )

    return render(request, "blog/index.html", context)


def index_feed(request, title=blog_title, subtitle=""):
    feed = blog_views.get_index_feed(
        uri=request.build_absolute_uri("/"),
        path=request.path,
        title=title,
        subtitle=subtitle,
    )

    return HttpResponse(feed, status=200, content_type="application/rss+xml")


def latest_article(request):
    context = blog_views.get_latest_article()

    return redirect("article", slug=context.get("article").get("slug"))


def group(request, slug, template_path):
    page_param = str_to_int(request.GET.get("page", default="1"))
    category_param = request.GET.get("category", default="")
    context = blog_views.get_group(slug, page_param, category_param)

    if not context:
        raise Http404("Group not found")

    return render(request, template_path, context)


def group_feed(request, slug, title=blog_title, subtitle=""):
    feed = blog_views.get_group_feed(
        group_slug=slug,
        uri=request.build_absolute_uri("/"),
        path=request.path,
        title=title,
        subtitle=subtitle,
    )

    if not feed:
        raise Http404()

    return HttpResponse(feed, status=200, content_type="application/rss+xml")


def topic(request, slug, template_path):
    page_param = str_to_int(request.GET.get("page", default="1"))
    context = blog_views.get_topic(slug, page_param)

    return render(request, template_path, context)


def topic_feed(request, slug, title=blog_title, subtitle=""):
    feed = blog_views.get_topic_feed(
        topic_slug=slug,
        uri=request.build_absolute_uri("/"),
        path=request.path,
        title=title,
        subtitle=subtitle,
    )

    if not feed:
        raise Http404()

    return HttpResponse(feed, status=200, content_type="application/rss+xml")


def upcoming(request):
    page_param = str_to_int(request.GET.get("page", default="1"))
    context = blog_views.get_upcoming(page_param)

    return render(request, "blog/upcoming.html", context)


def author(request, username):
    page_param = str_to_int(request.GET.get("page", default="1"))
    context = blog_views.get_author(username, page_param)

    if not context:
        raise Http404("Author not found")

    return render(request, "blog/author.html", context)


def author_feed(request, username, title=blog_title, subtitle=""):
    feed = blog_views.get_author_feed(
        username=username,
        uri=request.build_absolute_uri("/"),
        path=request.path,
        title=title,
        subtitle=subtitle,
    )

    if not feed:
        raise Http404()

    return HttpResponse(feed, status=200, content_type="application/rss+xml")


def archives(request, template_path="blog/archives.html"):
    page = str_to_int(request.GET.get("page", default="1"))
    group = request.GET.get("group", default="")
    month = request.GET.get("month", default="")
    year = request.GET.get("year", default="")
    category_param = request.GET.get("category", default="")

    context = blog_views.get_archives(page, group, month, year, category_param)

    if not context:
        raise Http404("Group not found")

    return render(request, template_path, context)


def article_redirect(request, slug, year=None, month=None, day=None):
    return redirect("article", slug=slug)


def article(request, slug):
    context = blog_views.get_article(slug)

    if not context:
        raise Http404("Article not found")

    return render(request, "blog/article.html", context)


def latest_news(request):
    context = blog_views.get_latest_news()

    return JsonResponse(context)


def tag(request, slug):
    page_param = str_to_int(request.GET.get("page", default="1"))
    context = blog_views.get_tag(slug, page_param)

    if not context:
        raise Http404("Tag not found")

    return render(request, "blog/tag.html", context)
