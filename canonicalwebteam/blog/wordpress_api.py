import os

from canonicalwebteam.http import CachedSession


API_URL = os.getenv(
    "BLOG_API", "https://admin.insights.ubuntu.com/wp-json/wp/v2"
)


api_session = CachedSession(fallback_cache_duration=3600)


def process_response(response):
    response.raise_for_status()

    return response.json()


def get_articles(
    tags=[],
    per_page=12,
    page=1,
    tags_exclude=[],
    exclude=[],
    categories=[],
    sticky="",
):
    """
    Get articles from Wordpress api
    :param tags: Array of tag ids to fetch articles for
    :param per_page: Articles to get per page
    :param page: Page number to get
    :param tags_exclude: Array of IDs of tags that will be excluded
    :param exclude: Array of article IDs to be excluded
    :param category: Array of categories, which articles
        should be fetched for
    """
    url = (
        f"{API_URL}/posts?per_page={per_page}"
        f"&tags={','.join(str(id) for id in tags)}"
        f"&page={page}"
        f"&tags_exclude={','.join(str(id) for id in tags_exclude)}"
        f"&categories={','.join(str(id) for id in categories)}"
        f"&exclude={','.join(str(id) for id in exclude)}"
    )
    if sticky != "":
        url = url + f"&sticky={sticky}"

    response = api_session.get(url)
    total_pages = response.headers.get("X-WP-TotalPages")

    return process_response(response), total_pages


def get_article(slug="", tags=[], tags_exclude=[]):
    """
    Get an article from Wordpress api
    :param slug: Article slug to fetch
    :param tags: Array tags to fetch articles for
    :param tags_exclude: Array of IDs of tags that will be excluded
        should be fetched
    """
    url = (
        f"{API_URL}/posts?slug={slug}"
        f"&tags={','.join(str(id) for id in tags)}"
        f"&tags_exclude={','.join(str(id) for id in tags_exclude)}"
    )

    response = api_session.get(url)

    data = process_response(response)
    if len(data) > 0:
        return data[0]
    else:
        return None


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
