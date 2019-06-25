from canonicalwebteam.blog.flask.views import build_blueprint


class BlogExtension(object):
    def __init__(
        self,
        app=None,
        blog_title=None,
        tag_id=None,
        tag_name=None,
        url_prefix=None,
        excluded_tags=[],
        enable_upcoming=True,
    ):
        self.app = app
        if app is not None:
            self.init_app(
                app,
                blog_title,
                tag_id,
                tag_name,
                url_prefix,
                excluded_tags,
                enable_upcoming,
            )

    def init_app(
        self,
        app,
        blog_title,
        tag_id,
        tag_name,
        url_prefix,
        excluded_tags=[],
        enable_upcoming=True,
    ):
        blog = build_blueprint(
            blog_title, tag_id, tag_name, excluded_tags, enable_upcoming
        )
        app.register_blueprint(blog, url_prefix=url_prefix)
