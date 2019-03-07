from django.conf.urls import url
from .views import test, index


urlpatterns = [url(r".", index), url(r"hallo", test)]
