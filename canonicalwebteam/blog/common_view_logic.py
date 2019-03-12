from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog import logic


def get_index_context(page_param, articles, total_pages):

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

    return {
        "current_page": page_param,
        "total_pages": int(total_pages),
        "articles": articles,
        "used_categories": category_cache,
        "groups": group_cache,
    }


def get_article_context(articles):

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

    return {
        "article": transformed_article,
        "related_articles": related_articles,
        "tags": tag_names,
        "is_in_series": is_in_series,
    }
