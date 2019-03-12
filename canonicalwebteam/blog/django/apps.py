from django.apps import AppConfig


class DjangoBlogConfig(AppConfig):
    def __init__(self, tags_id):
        self.tags_id = tags_id

    name = "canonicalwebteam.blog.django"
