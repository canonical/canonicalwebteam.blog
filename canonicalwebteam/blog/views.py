# Standard library
from datetime import datetime

# Packages
import flask
from dateutil.relativedelta import relativedelta
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator


class BlogViews:
    def __init__(
        self,
        api,
        tag_ids=[],
        excluded_tags=[],
        blog_title="Blog",
        blog_path="blog",
        feed_description=None,
        per_page=12,
    ):
        self.api = api
        self.tag_ids = tag_ids
        self.excluded_tags = excluded_tags
        self.blog_title = blog_title
        self.blog_path = blog_path.strip("/")
        self.feed_description = feed_description or f"{blog_title} feed"
        self.per_page = per_page

    def get_index(self, page=1, category_slug=""):
        categories = []
        if category_slug:
            category_resolved = self.api.get_category_by_slug(category_slug)
            if category_resolved:
                categories.append(category_resolved.get("id", ""))

        events_and_webinars = []
        featured_articles = []
        if page == 1:
            featured_articles, _ = self.api.get_articles(
                tags=self.tag_ids,
                tags_exclude=self.excluded_tags,
                page=page,
                sticky="true",
                per_page=3,
            )

            # Maybe we can get the IDs since there is no chance
            # this going to move
            events = self.api.get_category_by_slug("events")
            webinars = self.api.get_category_by_slug("webinars")
            events_and_webinars, _ = self.api.get_articles(
                tags=self.tag_ids,
                tags_exclude=self.excluded_tags,
                page=page,
                per_page=3,
                categories=[events["id"], webinars["id"]],
            )

        articles, metadata = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            exclude=[article["id"] for article in featured_articles],
            page=page,
            per_page=self.per_page,
            categories=categories,
        )

        return {
            "current_page": int(page),
            "total_pages": int(metadata["total_pages"]),
            "articles": articles,
            "featured_articles": featured_articles,
            "events_and_webinars": events_and_webinars,
            "title": self.blog_title,
            "category": {"slug": category_slug},
        }

    def get_index_feed(self, uri, path):
        articles, _ = self.api.get_articles(
            tags=self.tag_ids, tags_exclude=self.excluded_tags
        )

        url_root = flask.request.url_root

        feed = self._build_feed(
            blog_url=f"{url_root}/{self.blog_path}",
            feed_url=f"{url_root}/{flask.request.path.strip('/')}",
            feed_title=self.blog_title,
            feed_description=self.feed_description,
            articles=articles,
        )

        return feed.rss_str()

    def get_article(self, slug):
        article = self.api.get_article(slug, self.tag_ids, self.excluded_tags)

        if not article:
            return {}

        return self._get_article_context(
            article, self.tag_ids, self.excluded_tags
        )

    def get_latest_article(self):
        articles, _ = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=1,
            per_page=1,
        )

        if not articles:
            return {}

        return self._get_article_context(
            articles[0], self.tag_ids, self.excluded_tags
        )

    def get_group(self, group_slug, page=1, category_slug=""):
        group = self.api.get_group_by_slug(group_slug)

        category = {}
        if category_slug:
            category = self.api.get_category_by_slug(category_slug)

        articles, metadata = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            groups=[group.get("id", "")],
            categories=[category.get("id", "")],
        )

        return {
            "current_page": int(page),
            "total_pages": int(metadata["total_pages"]),
            "articles": articles,
            "group": group,
            "title": self.blog_title,
            "category": {"slug": category_slug},
        }

    def get_group_feed(self, group_slug, uri, path):
        group = self.api.get_group_by_slug(group_slug)

        if not group:
            return None

        articles, _ = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            groups=[group.get("id", "")],
        )

        title = f"{group['name']} - {self.blog_title}"
        url_root = flask.request.url_root

        feed = self._build_feed(
            blog_url=f"{url_root}/{self.blog_path}",
            feed_url=f"{url_root}/{flask.request.path.strip('/')}",
            feed_title=title,
            feed_description=self.feed_description,
            articles=articles,
        )

        return feed.rss_str()

    def get_topic(self, topic_slug, page=1):
        tag = self.api.get_tag_by_slug(topic_slug)

        articles, metadata = self.api.get_articles(
            tags=self.tag_ids + [tag["id"]],
            tags_exclude=self.excluded_tags,
            page=page,
        )

        return {
            "current_page": int(page),
            "total_pages": int(metadata["total_pages"]),
            "articles": articles,
            "title": self.blog_title,
        }

    def get_topic_feed(self, topic_slug, uri, path):
        tag = self.api.get_tag_by_slug(topic_slug)

        if not tag:
            return None

        articles, _ = self.api.get_articles(
            tags=[tag["id"]], tags_exclude=self.excluded_tags
        )

        title = f"{tag['name']} - {self.blog_title}"
        url_root = flask.request.url_root.rstrip("/")

        feed = self._build_feed(
            blog_url=f"{url_root}/{self.blog_path}",
            feed_url=f"{url_root}/{flask.request.path.strip('/')}",
            feed_title=title,
            feed_description=self.feed_description,
            articles=articles,
        )

        return feed.rss_str()

    def get_events_and_webinars(self, page=1):
        events = self.api.get_category_by_slug("events")
        webinars = self.api.get_category_by_slug("webinars")

        articles, metadata = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            categories=[events["id"], webinars["id"]],
        )
        total_pages = metadata["total_pages"]

        return {
            "current_page": int(page),
            "total_pages": int(total_pages),
            "articles": articles,
            "title": self.blog_title,
        }

    def get_author(self, username, page=1):
        author = self.api.get_user_by_username(username)

        if not author:
            return None

        articles, metadata = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            page=page,
            author=author["id"],
        )

        return {
            "current_page": int(page),
            "total_pages": int(metadata.get("total_pages")),
            "articles": articles,
            "title": self.blog_title,
            "total_posts": metadata.get("total_posts", 0),
            "author": author,
        }

    def get_author_feed(self, username, uri, path):
        author = self.api.get_user_by_username(username)

        if not author:
            return None

        articles, _ = self.api.get_articles(
            tags=self.tag_ids,
            tags_exclude=self.excluded_tags,
            author=author["id"],
        )

        title = f"{author['name']} - {self.blog_title}"
        url_root = flask.request.url_root

        feed = self._build_feed(
            blog_url=f"{url_root}/{self.blog_path}",
            feed_url=f"{url_root}/{flask.request.path.strip('/')}",
            feed_title=title,
            feed_description=self.feed_description,
            articles=articles,
        )

        return feed.rss_str()

    def get_latest_news(self, limit=3, tag_ids=None, group_ids=None):
        latest_pinned_articles, _ = self.api.get_articles(
            tags=tag_ids or self.tag_ids,
            tags_exclude=self.excluded_tags,
            groups=group_ids,
            page=1,
            per_page=1,
            sticky=True,
        )

        latest_articles, _ = self.api.get_articles(
            tags=tag_ids or self.tag_ids,
            tags_exclude=self.excluded_tags,
            groups=group_ids,
            exclude=[article["id"] for article in latest_pinned_articles],
            page=1,
            per_page=limit,
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
            group = self.api.get_group_by_slug(group)

            if not group:
                return None

            groups.append(group["id"])

        if category:
            category_slugs = category.split(",")
            for slug in category_slugs:
                category = self.api.get_category_by_slug(slug)
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

        articles, metadata = self.api.get_articles(
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

        context = {
            "current_page": int(page),
            "total_pages": int(total_pages),
            "articles": articles,
            "title": self.blog_title,
            "total_posts": total_posts,
        }

        if group:
            context["group"] = group

        return context

    def get_tag(self, slug, page=1):
        tag = self.api.get_tag_by_slug(slug)

        if not tag:
            return None

        articles, metadata = self.api.get_articles(
            tags=[tag["id"]], tags_exclude=self.excluded_tags, page=page
        )
        total_pages = metadata["total_pages"]

        return {
            "current_page": int(page),
            "total_pages": int(total_pages),
            "articles": articles,
            "title": self.blog_title,
            "tag": tag,
        }

    def _get_article_context(
        self, article, related_tag_ids=[], excluded_tags=[]
    ):
        """
        Build the content for the article page
        :param article: Article to create context for
        """

        tags = article["_embedded"].get("wp:term", [{}, {}])[1]

        all_related_articles, _ = self.api.get_articles(
            tags=[tag["id"] for tag in tags],
            tags_exclude=excluded_tags,
            per_page=3,
            exclude=[article["id"]],
        )

        related_articles = []
        for related_article in all_related_articles:
            if set(related_tag_ids) <= set(related_article["tags"]):
                related_articles.append(related_article)

        return {
            "article": article,
            "related_articles": related_articles,
            "tags": tags,
            "is_in_series": self._is_in_series(tags),
        }

    def _is_in_series(self, tags):
        """Does the list of tags include a tag that starts 'sc:series'

        :param tags: Tag dict

        :returns: Boolean
        """
        for tag in tags:
            if tag["name"].startswith("sc:series"):
                return True

        return False

    def _build_feed(
        self, blog_url, feed_url, feed_title, feed_description, articles
    ):
        """
        Build the content for the feed
        :blog_url: string blog url
        :feed_url: string url
        :feed_title: string title
        :feed_description: string description
        :param articles: Articles to create feed from
        """
        feed = FeedGenerator()
        feed.generator("Python Feedgen")
        feed.title(feed_title)
        feed.description(feed_description)
        feed.link(href=feed_url, rel="self")

        for article in articles:
            title = article["title"]["rendered"]
            slug = article["slug"]
            author = article["_embedded"]["author"][0]
            description = article["excerpt"]["rendered"]
            content = article["content"]["rendered"]
            published = f'{article["date_gmt"]} GMT'
            updated = f'{article["modified_gmt"]} GMT'
            link = f"{blog_url}/{slug}"

            categories = []

            if "wp:term" in article["_embedded"]:
                for category in article["_embedded"]["wp:term"][1]:
                    categories.append(
                        dict(term=category["slug"], label=category["name"])
                    )

            entry = FeedEntry()
            entry.title(title)
            entry.description(description)
            entry.content(content)
            entry.author(name=author["name"], email=author["name"])
            entry.link(href=link)
            entry.category(categories)
            entry.published(published)
            entry.updated(updated)
            feed.add_entry(entry, order="append")

        return feed
