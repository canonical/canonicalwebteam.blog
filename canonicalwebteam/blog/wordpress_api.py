import os

from canonicalwebteam.http import CachedSession


API_URL = os.getenv(
    "BLOG_API", "https://admin.insights.ubuntu.com/wp-json/wp/v2"
)


api_session = CachedSession(fallback_cache_duration=3600)

tags = {}


def process_response(response):
    response.raise_for_status()

    return response.json()


def build_get_article_url(
    tags=[],
    per_page=12,
    page=1,
    tags_exclude=[],
    exclude=[],
    categories=[],
    sticky="",
    groups=[],
    after="",
    before="",
    author="",
):
    """
    Build url to fetch articles from Wordpress api
    :param tags: Array of tag ids to fetch articles for
    :param per_page: Articles to get per page
    :param page: Page number to get
    :param tags_exclude: Array of IDs of tags that will be excluded
    :param exclude: Array of article IDs to be excluded
    :param category: Array of categories, which articles
        should be fetched for
    :param sticky: string 'true' or 'false' to only get featured articles
    :param before: ISO8601 compliant date string to limit by date
    :param after: ISO8601 compliant date string to limit by date

    :returns: URL to Wordpress api
    """
    url = (
        f"{API_URL}/posts?per_page={per_page}"
        f"&tags={','.join(str(id) for id in tags)}"
        f"&page={page}"
        f"&group={','.join(str(id) for id in groups)}"
        f"&tags_exclude={','.join(str(id) for id in tags_exclude)}"
        f"&categories={','.join(str(id) for id in categories)}"
        f"&exclude={','.join(str(id) for id in exclude)}"
        f"&author={author}"
    )
    if sticky != "":
        url = url + f"&sticky={sticky}"
    if before != "":
        url = url + f"&before={before}"
    if after != "":
        url = url + f"&after={after}"

    return url


def get_articles_with_metadata(**kwargs):
    """
    Get articles from Wordpress api
    :param tags: Array of tag ids to fetch articles for
    :param per_page: Articles to get per page
    :param page: Page number to get
    :param tags_exclude: Array of IDs of tags that will be excluded
    :param exclude: Array of article IDs to be excluded
    :param category: Array of categories, which articles
        should be fetched for
    :param sticky: string 'true' or 'false' to only get featured articles
    :param before: ISO8601 compliant date string to limit by date
    :param after: ISO8601 compliant date string to limit by date

    :returns: response, metadata dictionary
    """
    url = build_get_article_url(**kwargs)

    response = api_session.get(url)
    total_pages = response.headers.get("X-WP-TotalPages")
    total_posts = response.headers.get("X-WP-Total")

    return (
        process_response(response),
        {"total_pages": total_pages, "total_posts": total_posts},
    )


def get_articles(**kwargs):
    """
    Get articles from Wordpress api
    :param tags: Array of tag ids to fetch articles for
    :param per_page: Articles to get per page
    :param page: Page number to get
    :param tags_exclude: Array of IDs of tags that will be excluded
    :param exclude: Array of article IDs to be excluded
    :param category: Array of categories, which articles
        should be fetched for
    :param sticky: string 'true' or 'false' to only get featured articles
    :param before: ISO8601 compliant date string to limit by date
    :param after: ISO8601 compliant date string to limit by date

    :returns: array of articles, total amount of pages
    """

    url = build_get_article_url(**kwargs)

    response = api_session.get(url)
    # TODO: Remove this.
    # Functions that need this data should use get_articles_with_metadata.
    # Needs more testing to refactor safely

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


def get_group_by_slug(slug):
    url = "".join([API_URL, "/group?", f"slug={slug}"])

    response = api_session.get(url)

    if not response.ok:
        return None
    try:
        groups_response = process_response(response)
        return groups_response[0]
    except Exception:
        return None


def get_group_by_id(id):
    url = "".join([API_URL, "/group/", str(id)])

    response = api_session.get(url)
    group = process_response(response)
    return group


def get_category_by_slug(slug):
    url = "".join([API_URL, "/categories?", f"slug={slug}"])

    response = api_session.get(url)

    if not response.ok:
        return None
    try:
        category = process_response(response)
        return category[0]
    except Exception:
        return None


def get_category_by_id(id):
    url = "".join([API_URL, "/categories/", str(id)])

    response = api_session.get(url)
    category = process_response(response)
    return category


def get_tag_by_slug(slug):
    url = "".join([API_URL, "/tags/", f"?slug={slug}"])

    response = api_session.get(url)

    try:
        tag = process_response(response)
        return tag[0]
    except Exception:
        return None


def get_media(media_id):
    url = "".join([API_URL, "/media/", str(media_id)])
    response = api_session.get(url)

    if not response.ok:
        return None

    return process_response(response)


def get_user_by_username(username):
    url = "".join([API_URL, "/users?slug=", username])
    response = api_session.get(url)

    if not response.ok:
        return None

    processed_response = process_response(response)
    if not processed_response:
        return None
    else:
        return processed_response[0]


def get_user(user_id):
    url = "".join([API_URL, "/users/", str(user_id)])
    response = api_session.get(url)

    return process_response(response)


def get_feed(tag):
    response = api_session.get(
        "https://admin.insights.ubuntu.com/?tag={}&feed=rss".format(tag)
    )

    if not response.ok:
        return None

    return response.text
