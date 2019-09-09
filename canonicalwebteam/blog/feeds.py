from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator


def build_feed(uri, path, title, description, articles):
    uri = uri.rstrip("/")
    blog_uri = f"{uri}/{path.split('/')[1]}"

    feed = FeedGenerator()
    feed.generator("Python Feedgen")
    feed.title(title)
    feed.description(description)
    feed.link(href=f"{uri}{path}", rel="self")

    for article in articles:
        feed.add_entry(build_entry(article, blog_uri), order="append")

    return feed


def build_entry(article, blog_uri):
    title = article["title"]["rendered"]
    slug = article["slug"]
    author = article["_embedded"]["author"][0]
    description = article["excerpt"]["rendered"]
    content = article["content"]["rendered"]
    published = f'{article["date_gmt"]} GMT'
    updated = f'{article["modified_gmt"]} GMT'
    link = f"{blog_uri}/{slug}"

    categories = []
    for category in article["_embedded"]["wp:term"][1]:
        categories.append(dict(term=category["slug"], label=category["name"]))

    entry = FeedEntry()
    entry.title(title)
    entry.description(description)
    entry.content(content)
    entry.author(name=author["name"], email=author["name"])
    entry.link(href=link)
    entry.category(categories)
    entry.published(published)
    entry.updated(updated)

    return entry
