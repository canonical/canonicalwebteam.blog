# Canonical blog extension

This extension allows you to add a simple frontend section to your flask app. All the articles
are pulled from [Canonical's Wordpress back-end](https://admin.insights.ubuntu.com/wp-admin/) through the JSON API.

This extension provides a blueprint with 3 routes:

- "/": that returns the list of articles
- "/<slug>": the article page
- "/feed": provides a RSS feed for the page.

## Installation

To install this extension as a requirement in your project, you can use PIP;

```bash
pip3 install canonicalwebteam.blog
```

See also the documentation for [pip install](https://pip.pypa.io/en/stable/reference/pip_install/).

## Usage

### Local development

For local development, it's best to test this module with one of our website projects like [ubuntu.com](https://github.com/canonical-web-and-design/ubuntu.com/). For more information, follow [this guide (internal only)](https://discourse.canonical.com/t/how-to-run-our-python-modules-for-local-development/308).
    
### Templates

The module expects HTML templates at `blog/index.html`, `blog/article.html`, `blog/blog-card.html`, `blog/archives.html`, `blog/upcoming.html` and `blog/author.html`.

An example of these templates can be found at https://github.com/canonical-websites/jp.ubuntu.com/tree/master/templates/blog.

### Usage

In your app you can then do the following:

```python3
import flask
import talisker.requests
from flask_reggie import Reggie
from canonicalwebteam.blog import BlogViews, build_blueprint, BlogAPI

app = flask.Flask(__name__)
Reggie().init_app(app)
session = talisker.requests.get_session()

blog = build_blueprint(
    BlogViews(
        api=BlogAPI(session=session),
    )
)
app.register_blueprint(blog, url_prefix="/blog")
```

You can customise the blog through the following optional arguments:

```python3
blog = build_blueprint(
    BlogViews(
        blog_title="Blog",
        blog_path="blog",
        tag_ids=[1, 12, 112],
        exclude_tags=[26, 34],
        per_page=12,
        feed_description="The Ubuntu Blog Feed",
        api=BlogAPI(
            session=session,
            use_image_template=True,
            thumbnail_width=330,
            thumbnail_height=185,
        ),
    )
)
```

## Testing

All tests can be run with `./setup.py test`.

### Regenerating Fixtures

All API calls are caught with [VCR](https://vcrpy.readthedocs.io/en/latest/) and saved as fixtures in the `fixtures` directory. If the API updates, all fixtures can easily be updated by just removing the `fixtures` directory and rerunning the tests.

To do this run `rm -rf fixtures && ./setup.py test`.
