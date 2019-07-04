from datetime import datetime

from canonicalwebteam.blog import logic
from canonicalwebteam.blog import wordpress_api as api
from dateutil.relativedelta import relativedelta


class BlogViews:
    def __init__(self, tag_ids, excluded_tags, blog_title, tag_name):
        self.tag_ids = tag_ids
        self.excluded_tags = excluded_tags
        self.blog_title = blog_title
        self.tag_name = tag_name

    def get_index(self, page=1, category="", enable_upcoming=True):
        categories = []
        if category:
            category_resolved = api.get_category_by_slug(category)
            if category_resolved:
                categories.append(category_resolved.get("id", ""))

        upcoming = []
        featured_articles = []
        if page == 1:
            featured_articles, _ = api.get_articles(
                tags=self.tag_ids,
                tags_exclude=self.excluded_tags,
                page=page,
                sticky="true",
                per_page=3,
            )

            if enable_upcoming:
                # Maybe we can get the IDs since there is no chance
                # this going to move
                events = api.get_category_by_slug("events")
                webinars = api.get_category_by_slug("webinars")
                upcoming, _ = api.get_articles(
                    tags=self.tag_ids,
                    tags_exclude=self.excluded_tags,
                    page=page,
                    per_page=3,
                    categories=[events["id"], webinars["id"]],
                )

        articles, metadata = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            exclude=[article["id"] for article in featured_articles],
            page=page,
            categories=categories,
        )
        total_pages = metadata["total_pages"]

        context = get_index_context(
            page,
            articles,
            total_pages,
            featured_articles=featured_articles,
            upcoming=upcoming,
        )

        context["title"] = self.blog_title
        context["category"] = {"slug": category}
        context["upcoming"] = upcoming

        return context

    def get_article(self, slug):
        article = api.get_article(slug, self.tag_ids, self.excluded_tags)

        if not article:
            return {}

        return get_article_context(article, self.tag_ids, self.excluded_tags)

    def get_latest_article(self):
        articles, _ = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=1,
            per_page=1,
        )

        if not articles:
            return {}

        return get_article_context(
            articles[0], self.tag_ids, self.excluded_tags
        )

    def get_group(self, group_slug, page=1, category_slug=""):
        group = api.get_group_by_slug(group_slug)

        category = {}
        if category_slug:
            category = api.get_category_by_slug(category_slug)

        articles, metadata = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            groups=[group.get("id", "")],
            categories=[category.get("id", "")],
        )
        total_pages = metadata["total_pages"]

        context = get_group_page_context(page, articles, total_pages, group)
        context["title"] = self.blog_title
        context["category"] = {"slug": category_slug}

        return context

    def get_topic(self, topic_slug, page=1):
        tag = api.get_tag_by_slug(topic_slug)

        articles, metadata = api.get_articles(
            tags=self.tag_ids + [tag["id"]],
            tags_exclude=self.excluded_tags,
            page=page,
        )
        total_pages = metadata["total_pages"]

        context = get_topic_page_context(page, articles, total_pages)
        context["title"] = self.blog_title

        return context

    def get_upcoming(self, page=1):
        events = api.get_category_by_slug("events")
        webinars = api.get_category_by_slug("webinars")

        articles, metadata = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            categories=[events["id"], webinars["id"]],
        )
        total_pages = metadata["total_pages"]

        context = get_index_context(page, articles, total_pages)
        context["title"] = self.blog_title

        return context

    def get_author(self, username, page=1):
        author = api.get_user_by_username(username)

        if not author:
            return None

        articles, metadata = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            author=author["id"],
        )

        context = get_index_context(
            page, articles, metadata.get("total_pages")
        )
        context["title"] = self.blog_title
        context["author"] = author
        context["total_posts"] = metadata.get("total_posts", 0)

        return context

    def get_latest_news(self):
        latest_pinned_articles, _ = api.get_articles(
            tags=self.tag_ids,
            exclude=self.excluded_tags,
            page=1,
            per_page=1,
            sticky=True,
        )

        per_page = 3
        if latest_pinned_articles:
            per_page = 4

        latest_articles, _ = api.get_articles(
            tags=self.tag_ids,
            exclude=self.excluded_tags,
            page=1,
            per_page=per_page,
            sticky=False,
        )

        return {
            "latest_articles": latest_articles,
            "latest_pinned_articles": latest_pinned_articles,
        }

    def get_archives(self, page=1, group="", month="", year="", category=""):
        groups = []
        categories = []

        if group:
            group = api.get_group_by_slug(group)
            groups.append(group["id"])

        if category:
            category_slugs = category.split(",")
            for slug in category_slugs:
                category = api.get_category_by_slug(slug)
                categories.append(category["id"])

        after = None
        before = None
        if year:
            year = int(year)
            if month:
                after = datetime(year=year, month=int(month), day=1)
                before = after + relativedelta(months=1)
            else:
                after = datetime(year=year, month=1, day=1)
                before = datetime(year=year, month=12, day=31)

        articles, metadata = api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            groups=groups,
            categories=categories,
            after=after,
            before=before,
        )

        total_pages = metadata["total_pages"]
        total_posts = metadata["total_posts"]

        if group:
            context = get_group_page_context(
                page, articles, total_pages, group
            )
        else:
            context = get_index_context(page, articles, total_pages)

        context["title"] = self.blog_title
        context["total_posts"] = total_posts

        return context

    def get_feed(self, uri):
        feed = api.get_feed(self.tag_name)
        right_urls = logic.change_url(feed, uri.replace("/feed", ""))
        context = right_urls.replace("Ubuntu Blog", self.blog_title)

        return context

    def get_tag(self, slug, page=1):
        tag = api.get_tag_by_slug(slug)

        articles, metadata = api.get_articles(
            tags=self.tag_ids + [tag["id"]],
            tags_exclude=self.excluded_tags,
            page=page,
        )
        total_pages = metadata["total_pages"]

        context = get_topic_page_context(page, articles, total_pages)
        context["title"] = self.blog_title
        context["tag"] = tag

        return context


def get_complete_article(article, group=None):
    """
    This returns any given article from the wordpress API
    as an object that includes all information for the templates,
    some of which will be fetched from the Wordpress API
    """
    featured_images = logic.get_embedded_featured_media(article["_embedded"])
    featured_image = {}
    if featured_images:
        featured_image = featured_images[0]
    author = logic.get_embedded_author(article["_embedded"])
    categories = logic.get_embedded_categories(article["_embedded"])

    for category in categories:
        if "display_category" not in article:
            article["display_category"] = category

    if group:
        article["group"] = group
    else:
        article["group"] = logic.get_embedded_group(article["_embedded"])

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
    context = get_index_context(
        page_param, articles, total_pages, featured_articles
    )
    context["group"] = group

    return context


def get_topic_page_context(page_param, articles, total_pages):
    """
    Build the content for a group page
    :param page_param: String or int for index of the page to get
    :param articles: Array of articles
    :param articles: String of int of total amount of pages
    """

    return get_index_context(page_param, articles, total_pages)


def get_article_context(article, related_tag_ids=[], excluded_tags=[]):
    """
    Build the content for the article page
    :param article: Article to create context for
    """
    transformed_article = get_complete_article(article)

    tags = logic.get_embedded_tags(article["_embedded"])
    is_in_series = logic.is_in_series(tags)

    all_related_articles, _ = api.get_articles(
        tags=[tag["id"] for tag in tags],
        tags_exclude=excluded_tags,
        per_page=3,
        exclude=[article["id"]],
    )

    related_articles = []
    for related_article in all_related_articles:
        if set(related_tag_ids) <= set(related_article["tags"]):
            related_articles.append(logic.transform_article(related_article))

    return {
        "article": transformed_article,
        "related_articles": related_articles,
        "tags": tags,
        "is_in_series": is_in_series,
    }
