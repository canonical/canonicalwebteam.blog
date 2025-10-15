import base64
from urllib.parse import urlencode


class NotFoundError(Exception):
    pass


class Wordpress:
    def __init__(
        self,
        session,
        api_url="https://admin.insights.ubuntu.com/wp-json/wp/v2",
        wordpress_username=None,
        wordpress_password=None,
    ):
        """
        Wordpress API object, for making calls to the wordpress API
        """

        self.session = session
        self.api_url = api_url
        self.wordpress_username = wordpress_username
        self.wordpress_password = wordpress_password

        if self.wordpress_username and self.wordpress_password:
            creds = f"{self.wordpress_username}:{self.wordpress_password}"
            encoded_credentials = base64.b64encode(creds.encode()).decode()
            self.session.headers.update(
                {"Authorization": f"Basic {encoded_credentials}"}
            )

    def request(self, endpoint, params={}, method="get"):
        """
        Build url to fetch articles from Wordpress api
        :param endpoint: The REST endpoint to fetch data from
        :param params: Dictionary of parameter keys and their values

        :returns: URL to Wordpress api
        """

        clean_params = {}
        for key, value in params.items():
            if value:
                if type(value) is list:
                    clean_params[key] = ",".join(str(item) for item in value)
                else:
                    clean_params[key] = value

        query = urlencode({**clean_params, "_embed": "true"})

        response = self.session.request(
            method, f"{self.api_url}/{endpoint}?{query}"
        )
        response.raise_for_status()

        return response

    def get_first_item(self, endpoint, params={}):
        response = self.request(endpoint, params)

        if len(response.json()) == 0:
            raise NotFoundError(f"No items returned from {response.url}")

        return response.json()[0]

    def get_articles(
        self,
        tags=None,
        tags_exclude=None,
        exclude=None,
        categories=None,
        sticky=None,
        before=None,
        after=None,
        author=None,
        groups=None,
        per_page=12,
        page=1,
        status=None,
    ):
        """
        Get articles from Wordpress api
        :param tags: Array of tag ids to fetch articles for
        :param per_page: Articles to get per page
        :param page: Page number to get
        :param tags_exclude: Array of IDs of tags that will be excluded
        :param exclude: Array of article IDs to be excluded
        :param categories: Array of categories, which articles
            should be fetched for
        :param sticky: string 'true' or 'false' to only get featured articles
        :param before: ISO8601 compliant date string to limit by date
        :param after: ISO8601 compliant date string to limit by date
        :param author: Name of the author to fetch articles from
        :param status: Array of post statuses to include
            (e.g., ['publish', 'draft'])

        :returns: response, metadata dictionary
        """
        response = self.request(
            "posts",
            {
                "tags": tags,
                "per_page": per_page,
                "page": page,
                "tags_exclude": tags_exclude,
                "exclude": exclude,
                "categories": categories,
                "group": groups,
                "sticky": sticky,
                "before": before,
                "after": after,
                "author": author,
                "status": status,
            },
        )
        total_pages = response.headers.get("X-WP-TotalPages")
        total_posts = response.headers.get("X-WP-Total")

        return (
            response.json(),
            {"total_pages": total_pages, "total_posts": total_posts},
        )

    def get_article(self, slug, tags=None, tags_exclude=None, status=None):
        """
        Get an article from Wordpress api
        :param slug: Article slug to fetch
        :param status: Array of post statuses to include
            (e.g., ['publish', 'draft'])
        """
        try:
            return self.get_first_item(
                "posts",
                {
                    "slug": slug,
                    "tags": tags,
                    "tags_exclude": tags_exclude,
                    "status": status,
                },
            )
        except NotFoundError:
            return {}

    def get_tag_by_id(self, id):
        return self.request(f"tags/{id}").json()

    def get_tag_by_slug(self, slug):
        try:
            return self.get_first_item("tags", {"slug": slug})
        except NotFoundError:
            return {}

    def get_tag_by_name(self, name):
        try:
            return self.get_first_item("tags", {"search": name})
        except NotFoundError:
            return {}

    def get_categories(self):
        return self.request("categories", {"per_page": 100}).json()

    def get_group_by_slug(self, slug):
        try:
            return self.get_first_item("group", {"slug": slug})
        except NotFoundError:
            return {}

    def get_group_by_id(self, id):
        return self.request(f"group/{str(id)}").json()

    def get_category_by_slug(self, slug):
        try:
            return self.get_first_item("categories", {"slug": slug})
        except NotFoundError:
            return {}

    def get_category_by_id(self, id):
        return self.request(f"categories/{str(id)}").json()

    def get_media(self, id):
        return self.request(f"media/{str(id)}").json()

    def get_user_by_username(self, username):
        try:
            return self.get_first_item("users", {"slug": username})
        except NotFoundError:
            return {}

    def get_user_by_id(self, id):
        return self.request((f"users/{str(id)}")).json()
