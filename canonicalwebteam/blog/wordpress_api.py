import os

from urllib.parse import urlencode

from canonicalwebteam.http import CachedSession


BLOG_URL = os.getenv("BLOG_URL", "https://admin.insights.ubuntu.com")
API_URL = os.getenv(
    "BLOG_API", "https://admin.insights.ubuntu.com/wp-json/wp/v2"
)


api_session = CachedSession(
    fallback_cache_duration=300, file_cache_directory=".webcache_blog"
)

tags = {}


def process_response(response):
    response.raise_for_status()

    return response.json()


def build_url(endpoint, params={}):
    """
    Build url to fetch articles from Wordpress api
    :param endpoint: The REST endpoint to fetch data from
    :param params: Dictionary of parameter keys and their values

    :returns: URL to Wordpress api
    """

    clean_params = {}
    for key, value in params.items():
        if value:
            if type(value) is list:
                clean_params[key] = ",".join(str(item) for item in value)
            else:
                clean_params[key] = value

    query = urlencode(clean_params)

    return (
        f"{API_URL}/{endpoint}?{query}&_embed"
        if query
        else f"{API_URL}/{endpoint}&_embed"
    )


def get_articles(
    tags=None,
    tags_exclude=None,
    exclude=None,
    categories=None,
    sticky=None,
    before=None,
    after=None,
    author=None,
    groups=None,
    per_page=12,
    page=1,
):
    """
    Get articles from Wordpress api
    :param tags: Array of tag ids to fetch articles for
    :param per_page: Articles to get per page
    :param page: Page number to get
    :param tags_exclude: Array of IDs of tags that will be excluded
    :param exclude: Array of article IDs to be excluded
    :param categories: Array of categories, which articles
        should be fetched for
    :param sticky: string 'true' or 'false' to only get featured articles
    :param before: ISO8601 compliant date string to limit by date
    :param after: ISO8601 compliant date string to limit by date
    :param author: Name of the author to fetch articles from

    :returns: response, metadata dictionary
    """
    url = build_url(
        "posts",
        {
            "tags": tags,
            "per_page": per_page,
            "page": page,
            "tags_exclude": tags_exclude,
            "exclude": exclude,
            "categories": categories,
            "group": groups,
            "sticky": sticky,
            "before": before,
            "after": after,
            "author": author,
        },
    )

    response = api_session.get(url)
    total_pages = response.headers.get("X-WP-TotalPages")
    total_posts = response.headers.get("X-WP-Total")

    return (
        process_response(response),
        {"total_pages": total_pages, "total_posts": total_posts},
    )


def get_article(slug, tags=None, tags_exclude=None):
    """
    Get an article from Wordpress api
    :param slug: Article slug to fetch
    """
    url = build_url(
        "posts", {"slug": slug, "tags": tags, "tags_exclude": tags_exclude}
    )

    response = api_session.get(url)

    data = process_response(response)
    if len(data) > 0:
        return data[0]
    else:
        return None


def get_tag_by_name(name):
    url = build_url("tags", {"search": name})

    response = api_session.get(url)

    try:
        tag_response = process_response(response)
        return tag_response[0]
    except Exception:
        return None


def get_tags_by_ids(ids):
    url = build_url("tags", {"include": ids})

    response = api_session.get(url)

    return process_response(response)


def get_categories():
    url = build_url("categories", {"per_page": 100})

    response = api_session.get(url)

    return process_response(response)


def get_group_by_slug(slug):
    url = build_url("group", {"slug": slug})

    response = api_session.get(url)

    if not response.ok:
        return None
    try:
        groups_response = process_response(response)
        return groups_response[0]
    except Exception:
        return None


def get_group_by_id(id):
    url = build_url(f"group/{str(id)}")

    response = api_session.get(url)
    group = process_response(response)
    return group


def get_category_by_slug(slug):
    url = build_url("categories", {"slug": slug})

    response = api_session.get(url)

    if not response.ok:
        return None
    try:
        category = process_response(response)
        return category[0]
    except Exception:
        return None


def get_category_by_id(id):
    url = build_url(f"categories/{str(id)}")

    response = api_session.get(url)
    category = process_response(response)
    return category


def get_tag_by_slug(slug):
    url = build_url("tags", {"slug": slug})

    response = api_session.get(url)

    try:
        tag = process_response(response)
        return tag[0]
    except Exception:
        return None


def get_media(media_id):
    url = build_url(f"media/{str(media_id)}")
    response = api_session.get(url)

    if not response.ok:
        return None

    return process_response(response)


def get_user_by_username(username):
    url = build_url("users", {"slug": username})
    response = api_session.get(url)

    if not response.ok:
        return None

    processed_response = process_response(response)
    if not processed_response:
        return None
    else:
        return processed_response[0]


def get_user(user_id):
    url = build_url(f"users/{str(user_id)}")
    response = api_session.get(url)

    return process_response(response)


def get_feed(tag):
    response = api_session.get(f"{BLOG_URL}/?tag={tag}&feed=rss")

    if not response.ok:
        return None

    return response.text
