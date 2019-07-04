from canonicalwebteam.blog.common_view_logic import BlogViews
from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect, render

tag_ids = settings.BLOG_CONFIG["TAG_IDS"]
excluded_tags = settings.BLOG_CONFIG["EXCLUDED_TAGS"]
blog_title = settings.BLOG_CONFIG["BLOG_TITLE"]
tag_name = settings.BLOG_CONFIG["TAG_NAME"]

blog_views = BlogViews(tag_ids, excluded_tags, blog_title, tag_name)


def str_to_int(string):
    try:
        return int(string)
    except ValueError:
        return 1


def index(request, enable_upcoming=True):
    page_param = str_to_int(request.GET.get("page", default="1"))
    category_param = request.GET.get("category", default="")

    try:
        context = blog_views.get_index(
            page=page_param,
            category=category_param,
            enable_upcoming=enable_upcoming,
        )
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return render(request, "blog/index.html", context)


def latest_article(request):
    try:
        context = blog_views.get_latest_article()
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return render(request, "blog/article.html", context)


def group(request, slug, template_path):
    page_param = str_to_int(request.GET.get("page", default="1"))
    category_param = request.GET.get("category", default="")

    try:
        context = blog_views.get_group(slug, page_param, category_param)
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return render(request, template_path, context)


def topic(request, slug, template_path):
    page_param = str_to_int(request.GET.get("page", default="1"))

    try:
        context = blog_views.get_topic(slug, page_param)
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return render(request, template_path, context)


def upcoming(request):
    page_param = str_to_int(request.GET.get("page", default="1"))

    try:
        context = blog_views.get_upcoming(page_param)
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return render(request, "blog/upcoming.html", context)


def author(request, username):
    page_param = str_to_int(request.GET.get("page", default="1"))

    try:
        context = blog_views.get_author(username, page_param)
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    if not context:
        raise Http404("Author not found")

    return render(request, "blog/author.html", context)


def archives(request, template_path="blog/archives.html"):
    page = str_to_int(request.GET.get("page", default="1"))
    group = request.GET.get("group", default="")
    month = request.GET.get("month", default="")
    year = request.GET.get("year", default="")
    category_param = request.GET.get("category", default="")

    try:
        context = blog_views.get_archives(
            page, group, month, year, category_param
        )
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return render(request, template_path, context)


def feed(request):
    try:
        context = blog_views.get_feed(request.build_absolute_uri())
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    return HttpResponse(context, status=200, content_type="txt/xml")


def article_redirect(request, slug, year=None, month=None, day=None):
    return redirect("article", slug=slug)


def article(request, slug):
    try:
        context = blog_views.get_article(slug)
    except Exception as e:
        return HttpResponse("Error: " + str(e), status=502)

    if not context:
        raise Http404("Article not found")

    return render(request, "blog/article.html", context)


def latest_news(request):
    try:
        context = blog_views.get_latest_news()
    except Exception:
        return JsonResponse({"Error": "An error ocurred"}, status=502)

    return JsonResponse(context)


def tag(request, slug):
    page_param = str_to_int(request.GET.get("page", default="1"))

    try:
        context = blog_views.get_tag(slug, page_param)
    except Exception:
        raise Http404("Tag not found")

    return render(request, "blog/tag.html", context)
