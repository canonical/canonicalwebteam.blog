import os

from canonicalwebteam.http import CachedSession


API_URL = os.getenv(
    "BLOG_API", "https://admin.insights.ubuntu.com/wp-json/wp/v2"
)


api_session = CachedSession(fallback_cache_duration=3600)


def process_response(response):
    if not response.ok:
        raise Exception("Error from api: " + response.status_code)

    return response.json()


def get_articles(tags, per_page=12, page=1, exclude=None, category=None):
    url_parts = [
        API_URL,
        "/posts?tags=",
        "".join(str(tag) for tag in tags),
        "&per_page=",
        str(per_page),
        "&page=",
        str(page),
    ]

    if exclude:
        url_parts = url_parts + ["&exclude=", str(exclude)]

    if category:
        url_parts = url_parts + ["&categories=", str(category)]

    url = "".join(url_parts)

    response = api_session.get(url)
    total_pages = response.headers.get("X-WP-TotalPages")

    return process_response(response), total_pages


def get_article(tags, slug):
    url = "".join(
        [
            API_URL,
            "/posts?slug=",
            slug,
            "&tags=",
            "".join(str(tag) for tag in tags),
        ]
    )

    response = api_session.get(url)

    return process_response(response)


def get_tag_by_name(name):
    url = "".join([API_URL, "/tags?search=", name])

    response = api_session.get(url)

    return process_response(response)


def get_tags_by_ids(ids):
    url = "".join([API_URL, "/tags?include=", ",".join(str(id) for id in ids)])

    response = api_session.get(url)

    return process_response(response)


def get_categories():
    url = "".join([API_URL, "/categories?", "per_page=100"])

    response = api_session.get(url)

    return process_response(response)


def get_group_by_id(id):
    url = "".join([API_URL, "/group/", str(id)])

    response = api_session.get(url)

    return process_response(response)


def get_category_by_id(id):
    url = "".join([API_URL, "/categories/", str(id)])

    response = api_session.get(url)

    return process_response(response)


def get_media(media_id):
    url = "".join([API_URL, "/media/", str(media_id)])
    response = api_session.get(url)

    if not response.ok:
        return None

    return process_response(response)


def get_user(user_id):
    url = "".join([API_URL, "/users/", str(user_id)])
    response = api_session.get(url)

    if not response.ok:
        return None

    return process_response(response)


def get_feed(tag):
    response = api_session.get(
        "https://admin.insights.ubuntu.com/?tag={}&feed=rss".format(tag)
    )

    if not response.ok:
        return None

    return response.text
