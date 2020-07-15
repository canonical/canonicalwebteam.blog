# Standard library
import re
import html
from datetime import date
from datetime import datetime

from canonicalwebteam.blog import Wordpress


class BlogAPI(Wordpress):
    def __init__(
        self,
        session,
        api_url="https://admin.insights.ubuntu.com/wp-json/wp/v2",
        transform_links=True,
    ):
        super().__init__(session, api_url)

        self.transform_links = transform_links

    def get_articles(
        self,
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
        articles, metadata = super().get_articles(
            tags,
            tags_exclude,
            exclude,
            categories,
            sticky,
            before,
            after,
            author,
            groups,
            per_page,
            page,
        )

        return (
            [self._transform_article(a) for a in articles],
            metadata,
        )

    def get_article(self, slug, tags=None, tags_exclude=None):
        article = super().get_article(slug, tags, tags_exclude)

        return self._transform_article(article)

    def _transform_article(self, article):
        """Transform article to include featured image, a group, human readable
        date and a stripped version of the excerpt

        :param article: The raw article object

        :returns: The transformed article
        """

        if "_embedded" in article:
            article["image"] = article["_embedded"].get(
                "wp:featuredmedia", [None]
            )[0]
            article["author"] = article["_embedded"].get("author", [None])[0]

            if "display_category" not in article:
                categories = article["_embedded"].get("wp:term", [[]])[0]

                if categories:
                    article["display_category"] = categories[-1]

            if (
                "wp:term" in article["_embedded"]
                and article["_embedded"]["wp:term"][3]
            ):
                article["group"] = article["_embedded"]["wp:term"][3][0]

        if "date_gmt" in article:
            article_gmt = article["date_gmt"]
            article_date = datetime.strptime(article_gmt, "%Y-%m-%dT%H:%M:%S")
            article["date"] = article_date.strftime("%-d %B %Y")

        if "excerpt" in article and "rendered" in article["excerpt"]:
            article["excerpt"]["raw"] = self._strip_excerpt(
                article["excerpt"]["rendered"]
            )[:340]

            # If the excerpt doesn't end before 340 characters, add ellipsis
            raw_article = article["excerpt"]["raw"]
            # split at the last 3 characters
            raw_article_start = raw_article[:-3]
            raw_article_end = raw_article[-3:]
            # for the last 3 characters replace any part of […]
            raw_article_end = raw_article_end.replace("[", "")
            raw_article_end = raw_article_end.replace("…", "")
            raw_article_end = raw_article_end.replace("]", "")
            # join it back up
            article["excerpt"]["raw"] = "".join(
                [raw_article_start, raw_article_end, " […]"]
            )

        if (
            article.get("_start_month")
            and article.get("_start_year")
            and article.get("_start_day")
        ):
            start_month_name = self._get_month_name(
                int(article["_start_month"])
            )
            article["start_date"] = "{} {} {}".format(
                article["_start_day"], start_month_name, article["_start_year"]
            )

        if (
            article.get("_end_month")
            and article.get("_end_year")
            and article.get("_end_day")
        ):
            end_month_name = self._get_month_name(int(article["_end_month"]))
            article["end_date"] = "{} {} {}".format(
                article["_end_day"], end_month_name, article["_end_year"]
            )

        if self.transform_links:
            # replace url on the blog article page
            article["content"]["rendered"] = self._replace_url(
                article["content"]["rendered"]
            )

            # replace url from the image thumbnail
            if (
                article["image"] is not None
                and "source_url" in article["image"]
            ):
                article["image"]["source_url"] = self._replace_url(
                    article["image"]["source_url"]
                )

        return article

    def _replace_url(self, content):
        """Change insights url to ubuntu.com

        :param content: String to replace url

        :returns: A string with converted urls
        """

        url = "admin.insights.ubuntu.com/wp-content/uploads"
        new_url = "ubuntu.com/wp-content/uploads"

        return content.replace(url, new_url)

    def _strip_excerpt(self, raw_html):
        """Remove tags from a html string

        :param raw_html: The HTML to strip

        :returns: The stripped string
        """
        clean_regex = re.compile("<.*?>")
        clean_text = re.sub(clean_regex, "", raw_html)
        return html.unescape(clean_text).replace("\n", "")

    def _get_month_name(self, month_index):
        """
        Get the month name from it's number, e.g.:
        January
        """

        return date(1900, month_index, 1).strftime("%B")
