# Standard library
import re
import html
from datetime import date
from datetime import datetime

# Packages
from bs4 import BeautifulSoup
from canonicalwebteam import image_template

# Local
from canonicalwebteam.blog import Wordpress


class BlogAPI(Wordpress):
    def __init__(
        self,
        session,
        api_url="https://admin.insights.ubuntu.com/wp-json/wp/v2",
        use_image_template=True,
    ):
        super().__init__(session, api_url)

        self.use_image_template = use_image_template

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

        # replace url on the blog article page
        article["content"]["rendered"] = self._replace_url(
            article["content"]["rendered"]
        )

        if article["image"] is not None and "source_url" in article["image"]:
            # replace url from the image thumbnail
            article["image"]["source_url"] = self._replace_url(
                article["image"]["source_url"]
            )

            # create default rendered image
            article["image"]["rendered"] = (
                '<img src="'
                + article["image"]["source_url"]
                + '" loading="lazy">'
            )

        if self.use_image_template:
            # apply image template for blog article images
            article["content"]["rendered"] = self._apply_image_template(
                content=article["content"]["rendered"], width="720",
            )

            # apply image template to thumbnail image
            if (
                article["image"] is not None
                and "source_url" in article["image"]
            ):
                article["image"]["rendered"] = self._apply_image_template(
                    content=article["image"]["rendered"],
                    width="330",
                    height="177",
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

    def _apply_image_template(self, content, width, height=None):
        """ Apply image template to the img tags

        :param content: String to replace url
        :param width: Default width of the image
        :param height: Default height of the image

        :returns: HTML images templated
        """

        soup = BeautifulSoup(content, "html.parser")
        for image in soup.findAll("img"):
            img_width = image.get("width")
            img_height = image.get("height")

            new_image = BeautifulSoup(
                image_template(
                    url=image.get("src"),
                    alt="",
                    width=img_width or width,
                    height=img_height or height,
                    hi_def=True,
                    loading="lazy",
                ),
                "html.parser",
            )
            image.replace_with(new_image)

        return str(soup)
