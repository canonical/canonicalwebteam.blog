from django.urls import path, register_converter
from canonicalwebteam.blog.django.views import (
    archives,
    article_redirect,
    article,
    author,
    feed,
    index,
    latest_article,
    latest_news,
    tag,
    upcoming,
)


class FourDigitYearConverter:
    regex = "[0-9]{4}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return "%04d" % value


class TwoDigitMonthConverter:
    regex = "[0-9]{2}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return "%02d" % value


class TwoDigitDayConverter:
    regex = "[0-9]{2}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return "%02d" % value


register_converter(FourDigitYearConverter, "yyyy")
register_converter(TwoDigitMonthConverter, "mm")
register_converter(TwoDigitDayConverter, "dd")


urlpatterns = [
    path("/<yyyy:year>/<mm:month>/<dd:day>/<str:slug>", article_redirect),
    path("/<yyyy:year>/<mm:month>/<str:slug>", article_redirect),
    path("/<yyyy:year>/<str:slug>", article_redirect),
    path("/archives", archives),
    path("/author/<str:username>", author),
    path("/tag/<str:slug>", tag),
    path("/feed", feed),
    path("/upcoming", upcoming),
    path("/latest-news", latest_news),
    path("/latest", latest_article),
    path("/<str:slug>", article, name="article"),
    path("", index),
]
