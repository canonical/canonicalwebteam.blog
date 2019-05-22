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


def build_url(
    endpoint,
    tags=[],
    per_page="",
    page="",
    tags_exclude=[],
    exclude=[],
    categories=[],
    sticky="",
    groups=[],
    after="",
    before="",
    author="",
    slug="",
    search="",
    include="",
):
    """
    Build url to fetch articles from Wordpress api
    :param endpoint: The endpoint of the API to be queried
    :param tags: Array of tag ids to fetch articles for
    :param per_page: Articles to get per page
    :param page: Page number to get
    :param tags_exclude: Array of IDs of entities that will be excluded
    :param exclude: Array of entity IDs to be excluded
    :param category: Array of categories, which articles
        should be fetched for
    :param sticky: string 'true' or 'false' to only get featured articles
    :param before: ISO8601 compliant date string to limit by date
    :param after: ISO8601 compliant date string to limit by date
    :param slug: A slug to describe an entity
    :param search: Search term to filter the result on the API
    :param include: IDs of entities to be included in results

    :returns: URL to Wordpress api
    """

    url = f"{API_URL}/{endpoint}"

    params = {
        "per_page": per_page,
        "tags": ",".join(str(id) for id in tags),
        "page": page,
        "group": ",".join(str(id) for id in groups),
        "tags_exclude": ",".join(str(id) for id in tags_exclude),
        "categories": ",".join(str(id) for id in categories),
        "exclude": ",".join(str(id) for id in exclude),
        "author": author,
        "sticky": sticky,
        "before": before,
        "after": after,
        "slug": slug,
        "search": search,
        "include": ",".join(str(id) for id in include),
    }

    # this will build the querystring with an appended &
    # it does not matter to the API and avoids more logic
    querystring = "?"
    for param, value in params.items():
        if value and value is not []:
            querystring += f"{param}={value}&"

    return url + querystring


def get_articles_with_metadata(per_page=12, page=1, **kwargs):
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
    url = build_url("posts", per_page=per_page, page=page, **kwargs)

    response = api_session.get(url)
    total_pages = response.headers.get("X-WP-TotalPages")
    total_posts = response.headers.get("X-WP-Total")

    return (
        process_response(response),
        {"total_pages": total_pages, "total_posts": total_posts},
    )


def get_articles(per_page=12, page=1, **kwargs):
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

    url = build_url("posts", per_page=per_page, page=page, **kwargs)

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
    url = build_url("posts", slug=slug, tags=tags, tags_exclude=tags_exclude)

    response = api_session.get(url)

    data = process_response(response)
    if len(data) > 0:
        return data[0]
    else:
        return None


def get_tag_by_name(name):
    url = build_url("tags", search=name)

    response = api_session.get(url)

    return process_response(response)


def get_tags_by_ids(ids):
    url = build_url("tags", include=ids)

    response = api_session.get(url)

    return process_response(response)


def get_categories():
    url = build_url("categories", per_page=100)

    response = api_session.get(url)

    return process_response(response)


def get_group_by_slug(slug):
    url = build_url("group", slug=slug)

    response = api_session.get(url)

    if not response.ok:
        return None
    try:
        groups_response = process_response(response)
        return groups_response[0]
    except Exception:
        return None


def get_group_by_id(id):
    url = build_url(f"group/{id}")

    response = api_session.get(url)
    group = process_response(response)
    return group


def get_category_by_slug(slug):
    url = build_url("categories", slug=slug)

    response = api_session.get(url)

    if not response.ok:
        return None
    try:
        category = process_response(response)
        return category[0]
    except Exception:
        return None


def get_category_by_id(id):
    url = build_url(f"categories/{id}")

    response = api_session.get(url)
    category = process_response(response)
    return category


def get_tag_by_slug(slug):
    url = build_url("tags", slug=slug)

    response = api_session.get(url)

    try:
        tag = process_response(response)
        return tag[0]
    except Exception:
        return None


def get_media(media_id):
    url = build_url(f"media/{media_id}")
    response = api_session.get(url)

    if not response.ok:
        return None

    return process_response(response)


def get_user_by_username(username):
    url = build_url("users", slug=username)
    response = api_session.get(url)

    if not response.ok:
        return None

    processed_response = process_response(response)
    if not processed_response:
        return None
    else:
        return processed_response[0]


def get_user(user_id):
    url = build_url(f"users/{user_id}")
    response = api_session.get(url)

    return process_response(response)


def get_feed(tag):
    response = api_session.get(f"{API_URL}/?tag={tag}&feed=rss")

    if not response.ok:
        return None

    return response.text
