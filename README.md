# Blog flask extension

This extension allows you to add a simple blog frontend to your flask app. All the articles
are pulled from the WordPress API that has the plugin WP-JSON.

This extension provides a blueprint with 3 routes:
- "/": that returns the list of articles
- "/<slug>": the article page
- "/feed": provides a RSS feed for the page.

## How to use

In your app you can:

    import canonicalwebteam.Flask_Blog import BlogExtension
    blog = BlogExtension(app, "Blog title", [1], "tag_name", "/url-prefix")

If you use the factory pattern you can also:

    import canonicalwebteam.Flask_Blog import BlogExtension
    blog = BlogExtension()
    blog.init_app(app, "Blog title", [1], "tag_name", "/url-prefix")
