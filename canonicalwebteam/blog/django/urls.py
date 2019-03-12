from django.conf.urls import url
from .views import test, index, article_redirect, article


urlpatterns = [
    url(
        r"(?P<year>[0-9]{4})/(?P<month>[0-9]{2})"
        + "/(?P<day>[0-9]{2})/(?P<slug>\w+)",
        article_redirect,
    ),
    url(
        r"(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<slug>\w+)",
        article_redirect,
    ),
    url(r"(?P<year>[0-9]{4})/(?P<slug>\w+)", article_redirect),
    url(r"feed", test),
    url(r"(?P<slug>\w+)", article, name="article"),
]
