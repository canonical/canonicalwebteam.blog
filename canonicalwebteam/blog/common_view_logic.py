from canonicalwebteam.blog import wordpress_api as api
from canonicalwebteam.blog import logic

category_cache = {}
group_cache = {}


class BlogViews:
    def __init__(self, tag_ids, excluded_tags, blog_title, tag_name):
        self.tag_ids = tag_ids
        self.excluded_tags = excluded_tags
        self.blog_title = blog_title
        self.tag_name = tag_name

    def get_index(self, page=1, category_type="", enable_upcoming=True):
        upcoming = []

        category_id = ""
        if category_type != "":
            category = api.get_category_by_slug(category_type)
            category_id = category["id"]


        featured_articles = []
        featured_article_ids = []
        if page == "1":
            featured_articles, total_pages = api.get_articles(
                tags=self.tag_ids,
                tags_exclude=self.excluded_tags,
                page=page,
                sticky="true",
                per_page=3,
            )

            featured_article_ids = [
                article["id"] for article in featured_articles
            ]


            if enable_upcoming:
                events = api.get_category_by_slug("events")
                webinars = api.get_category_by_slug("webinars")
                upcoming, _ = api.get_articles(
                    tags=self.tag_ids,
                    tags_exclude=self.excluded_tags,
                    page=page,
                    per_page=3,
                    categories=[events["id"], webinars["id"]],
                )

        articles, total_pages = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            exclude=featured_article_ids,
            page=page,
            categories=[category_id],
        )

        context = get_index_context(
            page,
            articles,
            total_pages,
            featured_articles=featured_articles,
            upcoming=upcoming,
        )

        context["title"] = self.blog_title
        context["category"] = {"slug": category_type}
        context["upcoming"] = upcoming

        return context


def get_complete_article(article, group=None):
    """
    This returns any given article from the wordpress API
    as an object that includes all information for the templates,
    some of which will be fetched from the Wordpress API
    """
    featured_image = {}
    if "wp:featuredmedia" in article["_embedded"]:
        featured_image = article["_embedded"]["wp:featuredmedia"][0]

    author = {}
    if "author" in article["_embedded"]:
        author = article["_embedded"]["author"][0]

    category_ids = article["categories"]

    # Can these calls be bundled?
    first_item = True
    for category_id in category_ids:
        if category_id not in category_cache:
            resolved_category = api.get_category_by_id(category_id)
            category_cache[category_id] = resolved_category
        if first_item:
            article["display_category"] = category_cache[category_id]
            first_item = False

    if group:
        article["group"] = group
    else:
        first_item = True
        for group_id in article["group"]:
            if group_id not in group_cache:
                resolved_group = api.get_group_by_id(group_id)
                group_cache[group_id] = resolved_group
            if first_item:
                article["group"] = group_cache[group_id]
                first_item = False

    return logic.transform_article(
        article, featured_image=featured_image, author=author
    )


def get_index_context(
    page_param, articles, total_pages, featured_articles=[], upcoming=[]
):
    """
    Build the content for the index page
    :param page_param: String or int for index of the page to get
    :param articles: Array of articles
    :param articles: String of int of total amount of pages
    :param featured_articles: List of featured articles
    :param upcoming_articles: List of upcoming articles
    """

    transformed_articles = []
    transformed_featured_articles = []
    transformed_upcoming_articles = []

    for article in articles:
        transformed_articles.append(get_complete_article(article))

    for article in featured_articles:
        transformed_featured_articles.append(get_complete_article(article))

    for article in upcoming:
        transformed_upcoming_articles.append(get_complete_article(article))

    return {
        "current_page": int(page_param),
        "total_pages": int(total_pages),
        "articles": transformed_articles,
        "used_categories": category_cache,
        "groups": group_cache,
        "featured_articles": transformed_featured_articles,
        "upcoming": transformed_upcoming_articles,
    }


def get_group_page_context(
    page_param, articles, total_pages, group, featured_articles=[]
):
    """
    Build the content for a group page
    :param page_param: String or int for index of the page to get
    :param articles: Array of articles
    :param articles: String of int of total amount of pages
    :param group: Article group
    """

    transformed_articles = []
    transformed_featured_articles = []
    for article in articles:
        transformed_articles.append(get_complete_article(article, group))

    for article in featured_articles:
        transformed_featured_articles.append(
            get_complete_article(article, group)
        )

    return {
        "current_page": int(page_param),
        "total_pages": int(total_pages),
        "articles": transformed_articles,
        "used_categories": category_cache,
        "group": group,
        "groups": group_cache,
        "featured_articles": transformed_featured_articles,
    }


def get_topic_page_context(page_param, articles, total_pages):
    """
    Build the content for a group page
    :param page_param: String or int for index of the page to get
    :param articles: Array of articles
    :param articles: String of int of total amount of pages
    """

    transformed_articles = []
    for article in articles:
        transformed_articles.append(get_complete_article(article))

    return {
        "current_page": int(page_param),
        "total_pages": int(total_pages),
        "articles": transformed_articles,
        "used_categories": category_cache,
        "groups": group_cache,
    }


def get_article_context(article, related_tag_ids=[]):
    """
    Build the content for the article page
    :param article: Article to create context for
    """

    author = api.get_user(article["author"])

    transformed_article = logic.transform_article(
        article, author=author, optimise_images=True
    )

    tags = article["tags"]
    tag_names = []
    tag_names_response = api.get_tags_by_ids(tags)

    if tag_names_response:
        for tag in tag_names_response:
            tag_names.append(
                {"id": tag["id"], "name": tag["name"], "slug": tag["slug"]}
            )

    is_in_series = logic.is_in_series(tag_names)

    all_related_articles, total_pages = api.get_articles(
        tags=tags, per_page=3, exclude=[article["id"]]
    )

    related_articles = []
    if all_related_articles:
        for related_article in all_related_articles:
            if set(related_tag_ids).issubset(related_article["tags"]):
                related_articles.append(
                    logic.transform_article(related_article)
                )

    for group_id in article["group"]:
        if group_id not in group_cache:
            resolved_group = api.get_group_by_id(group_id)
            group_cache[group_id] = resolved_group
            article["group"] = resolved_group
            break
        else:
            article["group"] = group_cache[group_id]

    return {
        "article": transformed_article,
        "related_articles": related_articles,
        "tags": tag_names,
        "is_in_series": is_in_series,
    }
