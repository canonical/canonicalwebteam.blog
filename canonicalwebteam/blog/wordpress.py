import base64
from urllib.parse import urlencode
from itertools import islice


class NotFoundError(Exception):
    pass


CATEGORY_FIELDS = ["id", "name", "slug", "parent"]
TAG_FIELDS = ["id", "name", "slug"]
USER_FIELDS = [
    "id",
    "name",
    "slug",
    "description",
    "avatar_urls",
    "meta",
    "user_job_title",
    "user_twitter",
    "user_facebook"
]
# Shared fields across detail and list views
COMMON_POST_FIELDS = [
    "id",
    "slug",
    "date_gmt",
    "modified_gmt",
    "categories",
    "tags",
    "_start_day",
    "_start_month",
    "_start_year",
    "_end_day",
    "_end_month",
    "_end_year",
    "author",
    "title.rendered",
    "excerpt.rendered",
]
# Minimal top-level fields for detail pages (keep embedded trimmed)
DEFAULT_POST_FIELDS = [
    *COMMON_POST_FIELDS,
    "content.rendered",
    "_links",
    "_embedded",
    # yoast_head_json.description,
]
# Very small field set for lists (IDs for joins + display basics)
LIST_POST_FIELDS = [
    *COMMON_POST_FIELDS,
    "group",
    "topic",
    "featured_media",
]


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
        # Encourage compressed responses for performance
        if "Accept-Encoding" not in self.session.headers:
            self.session.headers.update(
                {"Accept-Encoding": "gzip, deflate, br"}
            )
        if "Accept" not in self.session.headers:
            self.session.headers.update({"Accept": "application/json"})

    def request(
        self, endpoint, params={}, method="get", embed=True, fields=None
    ):
        """
        Build url to fetch articles from Wordpress api
        :param endpoint: The REST endpoint to fetch data from
        :param params: Dictionary of parameter keys and their values
        :param embed: Whether to request embedded resources via _embed=true
        :param fields: Optional list or comma-separated
                        string of fields to include

        :returns: Response from Wordpress api
        """

        clean_params = {}
        for key, value in params.items():
            if value:
                if type(value) is list:
                    clean_params[key] = ",".join(str(item) for item in value)
                else:
                    clean_params[key] = value

        # Apply field filtering if provided
        if fields:
            if isinstance(fields, list):
                clean_params["_fields"] = ",".join(fields)
            else:
                clean_params["_fields"] = str(fields)

        # Apply embedding only when requested
        if embed:
            clean_params["_embed"] = "true"

        query = urlencode(clean_params)

        response = self.session.request(
            method, f"{self.api_url}/{endpoint}?{query}"
        )
        response.raise_for_status()

        return response

    def get_first_item(self, endpoint, params={}, embed=True, fields=None):
        response = self.request(endpoint, params, embed=embed, fields=fields)

        if len(response.json()) == 0:
            raise NotFoundError(f"No items returned from {response.url}")

        return response.json()[0]

    def _chunk(self, iterable, size):
        it = iter(iterable)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                return
            yield chunk

    def _bulk_fetch_map(self, endpoint, ids, fields):
        """
        Fetch resources by IDs using include batching
        and return {id: obj}.
        """
        id_set = {int(i) for i in ids if i is not None}
        result = {}
        if not id_set:
            return result
        for chunk in self._chunk(sorted(id_set), 100):
            resp = self.request(
                endpoint,
                {
                    "per_page": len(chunk),
                    "include": ",".join(str(i) for i in chunk),
                },
                embed=False,
                fields=fields,
            )
            for obj in resp.json():
                # Each endpoint returns objects with an "id" field
                result[obj.get("id")] = obj
        return result

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
        list_mode=False,
        fields=None,
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
        :param list_mode: If True, use tiny _fields and synthesize _embedded

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
            embed=not list_mode,
            fields=(
                fields
                if fields
                else (
                    LIST_POST_FIELDS
                    if list_mode
                    else DEFAULT_POST_FIELDS
                )
            ),
        )
        total_pages = response.headers.get("X-WP-TotalPages")
        total_posts = response.headers.get("X-WP-Total")

        articles = response.json()

        if list_mode:
            # Collect IDs for bulk fetching
            author_ids = []
            media_ids = []
            category_ids = []
            tag_ids = []

            for a in articles:
                if "author" in a and a["author"]:
                    author_ids.append(a["author"])
                if "featured_media" in a and a["featured_media"]:
                    media_ids.append(a["featured_media"])
                for cid in a.get("categories", []):
                    category_ids.append(cid)
                for tid in a.get("tags", []):
                    tag_ids.append(tid)

            users_map = self._bulk_fetch_map(
                "users", author_ids, ["id", "name", "slug", "avatar_urls"]
            )
            media_map = self._bulk_fetch_map(
                "media", media_ids, ["id", "source_url", "media_details"]
            )
            categories_map = self._bulk_fetch_map(
                "categories", category_ids, ["id", "name", "slug", "parent"]
            )
            tags_map = self._bulk_fetch_map(
                "tags", tag_ids, ["id", "name", "slug"]
            )

            group_ids = groups or []
            # If a group filter is not applied, fetch groups
            if len(group_ids) == 0:
                for gid in a.get("group", []):
                    group_ids.append(gid)

            group_map = self._bulk_fetch_map(
                "group", group_ids, ["id", "name", "slug"]
            )

            # Synthesize _embedded to match WordPress order:
            # wp:term indexes: [0]=category, [1]=post_tag, [2]=topic, [3]=group
            for a in articles:
                embedded = {}
                auth_id = a.get("author")
                if auth_id and auth_id in users_map:
                    embedded["author"] = [users_map[auth_id]]
                fm_id = a.get("featured_media")
                if fm_id and fm_id in media_map:
                    embedded["wp:featuredmedia"] = [media_map[fm_id]]

                cat_terms = [
                    categories_map[cid]
                    for cid in a.get("categories", [])
                    if cid in categories_map
                ]
                tag_terms = [
                    tags_map[tid]
                    for tid in a.get("tags", [])
                    if tid in tags_map
                ]
                wp_term = [cat_terms, tag_terms, [], []]

                # Attach the single filtered group to each post in group lists
                if group_map:
                    # get only group object since we know the id
                    gid = group_ids[0]
                    if gid in group_map:
                        wp_term[3] = [group_map[gid]]

                embedded["wp:term"] = wp_term
                a["_embedded"] = embedded

        return (
            articles,
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
                embed=True,
                fields=DEFAULT_POST_FIELDS,
            )
        except NotFoundError:
            return {}

    def get_tag_by_id(self, id):
        return self.request(
            f"tags/{id}", embed=False, fields=TAG_FIELDS
        ).json()

    def get_tag_by_slug(self, slug):
        try:
            return self.get_first_item(
                "tags", {"slug": slug}, embed=False, fields=TAG_FIELDS
            )
        except NotFoundError:
            return {}

    def get_tag_by_name(self, name):
        try:
            return self.get_first_item(
                "tags", {"search": name}, embed=False, fields=TAG_FIELDS
            )
        except NotFoundError:
            return {}

    def get_categories(self):
        return self.request(
            "categories",
            {"per_page": 100},
            embed=False,
            fields=CATEGORY_FIELDS,
        ).json()

    def get_group_by_slug(self, slug):
        try:
            return self.get_first_item(
                "group", {"slug": slug}, embed=False, fields=CATEGORY_FIELDS
            )
        except NotFoundError:
            return {}

    def get_group_by_id(self, id):
        return self.request(
            f"group/{str(id)}", embed=False, fields=CATEGORY_FIELDS
        ).json()

    def get_category_by_slug(self, slug):
        try:
            return self.get_first_item(
                "categories",
                {"slug": slug},
                embed=False,
                fields=CATEGORY_FIELDS,
            )
        except NotFoundError:
            return {}

    def get_category_by_id(self, id):
        return self.request(
            f"categories/{str(id)}", embed=False, fields=CATEGORY_FIELDS
        ).json()

    def get_media(self, id):
        return self.request(f"media/{str(id)}", embed=False).json()

    def get_user_by_username(self, username):
        try:
            return self.get_first_item(
                "users", {"slug": username}, embed=False, fields=USER_FIELDS
            )
        except NotFoundError:
            return {}

    def get_user_by_id(self, id):
        return self.request(
            (f"users/{str(id)}"), embed=False, fields=USER_FIELDS
        ).json()
