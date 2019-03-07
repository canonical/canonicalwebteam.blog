from django.http import JsonResponse
from canonicalwebteam.blog import wordpress_api as api


def test(request):
    data = {"route": "test"}
    return JsonResponse(data)


def index(request):
    data = {"route": "index"}
    return JsonResponse(data)
