# Blog flask extension

This extension allows you to add a simple blog frontend to your flask app. All the articles
are pulled from the WordPress API that has the plugin WP-JSON.

This extension provides a blueprint with 3 routes:
- "/": that returns the list of articles
- "/<slug>": the article page
- "/feed": provides a RSS feed for the page.

## How to use

### Flask

In your app you can:

```python
    import canonicalwebteam.blog_extension import BlogExtension
    blog = BlogExtension(app, "Blog title", [1], "tag_name", "/url-prefix")
```
If you use the factory pattern you can also:
```python
    import canonicalwebteam.blog_extension import BlogExtension
    blog = BlogExtension()
    blog.init_app(app, "Blog title", [1], "tag_name", "/url-prefix")
```

### Django


- Add the blog module as a dependency to your Django project
- Load it at the desired path (f.e. "/blog") in the `urls.py` file
```python
from django.urls import path, include
urlpatterns = [path(r"blog/", include("canonicalwebteam.blog.django.urls"))]
```
- In your Django project settings (`settings.py`) you have to specify the following parameters:
```python
BLOG_CONFIG = {
    # the id for tags that should be fetched for this blog
    "TAGS_ID": [3184],
    # the title of the blog
    "BLOG_TITLE": "TITLE OF THE BLOG",
    # the tag name for generating a feed
    "TAG_NAME": "TAG NAME FOR GENERATING A FEED",
}
```
- You can now use the data from the blog. To display it the module expects templates at `blog/index.html`, `blog/article.html` and `blog/blog-card.html`. Inspiration can be found at https://github.com/canonical-websites/jp.ubuntu.com/tree/master/templates/blog.

- Run your project and verify that the blog is displaying at the path you specified (f.e. '/blog')
