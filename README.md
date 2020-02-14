# Canonical blog extension

This extension allows you to add a simple frontend section to your flask app. All the articles
are pulled from [Canonical's Wordpress back-end](https://admin.insights.ubuntu.com/wp-admin/) through the JSON API.

This extension provides a blueprint with 3 routes:

- "/": that returns the list of articles
- "/<slug>": the article page
- "/feed": provides a RSS feed for the page.

## How to install

To install this extension as a requirement in your project, you can use PIP;

```bash
pip install canonicalwebteam.blog
```

See also the documentation for (pip install)[https://pip.pypa.io/en/stable/reference/pip_install/].

## How to use

### Templates

The module expects HTML templates at `blog/index.html`, `blog/article.html`, `blog/blog-card.html`, `blog/archives.html`, `blog/upcoming.html` and `blog/author.html`.

An example of these templates can be found at https://github.com/canonical-websites/jp.ubuntu.com/tree/master/templates/blog.

### Flask

In your app you can then:

``` python3
    import flask
    from canonicalwebteam.blog import BlogViews
    from canonicalwebteam.blog.flask import build_blueprint

    app = flask.Flask(__name__)

    # ...

    blog_views = BlogViews()
    app.register_blueprint(build_blueprint(blog_views), url_prefix="/blog")
```

You can customise the blog through the following optional arguments:

``` python3
    blog_views = BlogViews(
        blog_title="Blog",
        tag_ids=[1, 12, 112],
        exclude_tags=[26, 34],
        feed_description="The Ubuntu Blog Feed",
        per_page=12, # OPTIONAL (defaults to 12)
    )
    app.register_blueprint(build_blueprint(blog_views), url_prefix="/blog")
```

## Development

The blog extension leverages [poetry](https://poetry.eustace.io/) for dependency management.

### Regenerate setup.py

``` bash
poetry install
poetry run poetry-setup
```

## Testing

All tests can be run with `poetry run pytest`.

### Regenerating Fixtures

All API calls are caught with [VCR](https://vcrpy.readthedocs.io/en/latest/) and saved as fixtures in the `fixtures` directory. If the API updates, all fixtures can easily be updated by just removing the `fixtures` directory and rerunning the tests.

To do this run `rm -rf fixtures && poetry run pytest`.
