import re
import html

from datetime import datetime
from datetime import date


def strip_excerpt(raw_html):
    """Remove tags from a html string

    :param raw_html: The HTML to strip

    :returns: The stripped string
    """
    clean_regex = re.compile("<.*?>")
    clean_text = re.sub(clean_regex, "", raw_html)
    return html.unescape(clean_text).replace("\n", "")


def replace_images_with_cloudinary(content):
    """Prefixes images with cloudinary optimised URLs and adds srcset for
    image scaling

    :param content: The HTML string to convert

    :returns: Update HTML string with converted images
    """
    cloudinary = "https://res.cloudinary.com/"

    urls = [
        cloudinary + r"canonical/image/fetch/q_auto,f_auto,w_350/\g<url>",
        cloudinary + r"canonical/image/fetch/q_auto,f_auto,w_650/\g<url>",
        cloudinary + r"canonical/image/fetch/q_auto,f_auto,w_1300/\g<url>",
        cloudinary + r"canonical/image/fetch/q_auto,f_auto,w_1950/\g<url>",
    ]

    image_match = (
        r'<img(?P<prefix>[^>]*) src="(?P<url>[^"]+)"(?P<suffix>[^>]*)>'
    )
    replacement = (
        r"<img\g<prefix>"
        f' decoding="async"'
        f' src="{urls[1]}"'
        f' srcset="{urls[0]} 350w, {urls[1]} 650w, {urls[2]} 1300w,'
        f' {urls[3]} 1950w"'
        f' sizes="(max-width: 400px) 350w, 650px"'
        r"\g<suffix>>"
    )

    return re.sub(image_match, replacement, content)


def transform_article(
    article, featured_image=None, author=None, optimise_images=False
):
    """Transform article to include featured image, a group, human readable
    date and a stipped version of the excerpt

    :param article: The raw article object
    :param featured_image: The featured image string

    :returns: The transformed article
    """
    article["image"] = featured_image

    article["author"] = author

    if "date_gmt" in article:
        article_gmt = article["date_gmt"]
        article_date = datetime.strptime(article_gmt, "%Y-%m-%dT%H:%M:%S")
        article["date"] = article_date.strftime("%-d %B %Y")

    if "excerpt" in article and "rendered" in article["excerpt"]:
        article["excerpt"]["raw"] = strip_excerpt(
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
        optimise_images
        and "content" in article
        and "rendered" in article["content"]
    ):
        article["content"]["rendered"] = replace_images_with_cloudinary(
            article["content"]["rendered"]
        )

    if (
        article.get("_start_month")
        and article.get("_start_year")
        and article.get("_start_day")
    ):
        start_month_name = get_month_name(int(article["_start_month"]))
        article["start_date"] = "{} {} {}".format(
            article["_start_day"], start_month_name, article["_start_year"]
        )

    if (
        article.get("_end_month")
        and article.get("_end_year")
        and article.get("_end_day")
    ):
        end_month_name = get_month_name(int(article["_end_month"]))
        article["end_date"] = "{} {} {}".format(
            article["_end_day"], end_month_name, article["_end_year"]
        )

    return article


def change_url(feed, host):
    """Change insights urls to <host>/blog

    :param feed: String with urls

    :returns: A string with converted urls
    """
    url_regex = re.compile(
        r"https://admin.insights.ubuntu.com(\/\d{4}\/\d{2}\/\d{2})?"
    )
    updated_feed = re.sub(url_regex, host, feed)

    return updated_feed


def get_tag_id_list(tags):
    """Get a list of tag ids from a list of tag dicts

    :param tags: Tag dict

    :returns: A list of ids
    """

    def get_id(tag):
        return tag["id"]

    return [get_id(tag) for tag in tags]


def is_in_series(tags):
    """Does the list of tags include a tag that starts 'sc:series'

    :param tags: Tag dict

    :returns: Boolean
    """
    for tag in tags:
        if tag["name"].startswith("sc:series"):
            return True

    return False


def get_month_name(month_index):
    """
    Get the month name from it's number, e.g.:
    January
    """

    return date(1900, month_index, 1).strftime("%B")


def get_embedded_categories(embedded):
    """Returns the categories in the embedded response from wp
    The category is in the first object of the wp:term of the response:
    embedded["wp:term"][0]


    :param embedded: The embedded dictionnary in teh response
    :returns: Dictionnary of categories
    """
    terms = embedded.get("wp:term", [{}])
    return terms[0]


def get_embedded_group(embedded):
    """Returns the group in the embedded response from wp.
    The group is in the fourth object of the wp:term list of the response:
    embedded["wp:term"][3]


    :param embedded: The embedded dictionnary in the response
    :returns: Dictionnary of group
    """
    if "wp:term" in embedded and embedded["wp:term"][3]:
        return embedded["wp:term"][3][0]
    return {}


def get_embedded_author(embedded):
    """Returns the author in the embedded response from wp.
    embedded["author"]


    :param embedded: The embedded dictionnary in the response
    :returns: Dictionnary of author
    """
    authors = embedded.get("author", [{}])
    return authors[0]


def get_embedded_featured_media(embedded):
    """Returns the featured media in the embedded response from wp.
    embedded["wp:featuredmedia"]


    :param embedded: The embedded dictionnary in the response
    :returns: List of featuredmedia
    """
    return embedded.get("wp:featuredmedia", [])


def get_embedded_tags(embedded):
    """Returns the tags in the embedded response from wp.
    The group is in the fourth object of the wp:term list of the response:
    embedded["wp:term"][1]


    :param embedded: The embedded dictionnary in the response
    :returns: Dictionnary of tags
    """
    terms = embedded.get("wp:term", [{}, {}])
    return terms[1]
