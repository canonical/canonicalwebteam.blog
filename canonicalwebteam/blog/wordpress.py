from .constants import (
    CATEGORY_FIELDS,
    TAG_FIELDS,
    USER_FIELDS,
    LIST_POST_FIELDS,
    DEFAULT_POST_FIELDS,
)
import base64
from urllib.parse import urlencode
from itertools import islice

# Max IDs per request when using
# the `include` parameter
BULK_INCLUDE_CHUNK = 100


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
        Fetch resources by IDs using batched `include` requests and
        return a mapping of `{id: obj}`.

        - Deduplicates and normalizes IDs to ints.
        - Batches by `BULK_INCLUDE_CHUNK` to avoid oversized queries.
        - Skips invalid IDs gracefully.
        """
        id_set = set()
        for i in ids or []:
            try:
                id_set.add(int(i))
            except (TypeError, ValueError):
                continue

        if not id_set:
            return {}

        result = {}
        for chunk in self._chunk(sorted(id_set), BULK_INCLUDE_CHUNK):
            resp = self.request(
                endpoint,
                {
                    "per_page": len(chunk),
                    "include": ",".join(map(str, chunk)),
                },
                embed=False,
                fields=fields,
            )
            result.update(
                {obj["id"]: obj for obj in resp.json() if "id" in obj}
            )
        return result

    def _synthesize_embedded(self, articles, groups=None):
        """
        Build a trimmed _embedded structure for provided articles, fetching
        related entities in bulk for performance and preserving WordPress
        term ordering (category, post_tag, topic, group).

        :param articles: Iterable of article dicts to mutate in place
        :param groups: Optional group filter list (used for fallback)
        """
        # Deduplicate IDs across all articles
        author_ids = {a.get("author") for a in articles if a.get("author")}
        media_ids = {
            a.get("featured_media")
            for a in articles
            if a.get("featured_media")
        }
        category_ids = {
            cid for a in articles for cid in a.get("categories", [])
        }
        tag_ids = {tid for a in articles for tid in a.get("tags", [])}
        group_ids = set(groups or [])
        for a in articles:
            group_ids.update(a.get("group", []))

        # Bulk-fetch related entities
        users_map = self._bulk_fetch_map(
            "users",
            author_ids,
            ["id", "name", "slug", "avatar_urls"],
        )
        media_map = self._bulk_fetch_map(
            "media",
            media_ids,
            ["id", "source_url", "media_details"],
        )
        categories_map = self._bulk_fetch_map(
            "categories",
            category_ids,
            CATEGORY_FIELDS,
        )
        tags_map = self._bulk_fetch_map("tags", tag_ids, TAG_FIELDS)
        group_map = self._bulk_fetch_map(
            "group",
            group_ids,
            ["id", "name", "slug"],
        )

        # Synthesize _embedded to match WordPress order:
        # wp:term: [category, post_tag, topic, group]
        for a in articles:
            auth_id = a.get("author")
            fm_id = a.get("featured_media")
            cat_terms = [
                categories_map[cid]
                for cid in a.get("categories", [])
                if cid in categories_map
            ]
            tag_terms = [
                tags_map[tid] for tid in a.get("tags", []) if tid in tags_map
            ]
            group_terms = [
                group_map[gid]
                for gid in a.get("group", [])
                if gid in group_map
            ]
            # Fallback: if filtered by a single group but the post doesn't
            # carry group terms, inject that group to preserve coherence.
            if not group_terms and groups and len(groups) == 1:
                gid = groups[0]
                if gid in group_map:
                    group_terms = [group_map[gid]]

            # The third position in wp:term is the 'topic' taxonomy in
            # WordPress (order: category, post_tag, topic, group). We don't
            # synthesize topics in compact mode, so leave it empty to
            # preserve the expected array structure.
            topic_terms = []
            embedded = {
                "wp:term": [cat_terms, tag_terms, topic_terms, group_terms]
            }
            if auth_id in users_map:
                embedded["author"] = [users_map[auth_id]]
            if fm_id in media_map:
                embedded["wp:featuredmedia"] = [media_map[fm_id]]
            a["_embedded"] = embedded

        return articles

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
        compact_mode=True,
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
        :param compact_mode: If True, use tiny _fields and synthesize _embedded

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
            embed=not compact_mode,
            fields=(
                fields
                if fields
                else (
                    LIST_POST_FIELDS if compact_mode else DEFAULT_POST_FIELDS
                )
            ),
        )
        total_pages = response.headers.get("X-WP-TotalPages")
        total_posts = response.headers.get("X-WP-Total")

        articles = response.json()

        if compact_mode:
            self._synthesize_embedded(articles, groups)

        return (
            articles,
            {"total_pages": total_pages, "total_posts": total_posts},
        )

    def get_article(
        self,
        slug,
        tags=None,
        tags_exclude=None,
        status=None,
        compact_mode=True,
        fields=None,
    ):
        """
        Get an article from Wordpress api
        :param slug: Article slug to fetch
        :param status: Array of post statuses to include
            (e.g., ['publish', 'draft'])
        """
        try:
            article = self.get_first_item(
                "posts",
                {
                    "slug": slug,
                    "tags": tags,
                    "tags_exclude": tags_exclude,
                    "status": status,
                },
                embed=not compact_mode,
                fields=(fields if fields else DEFAULT_POST_FIELDS),
            )

            if compact_mode and article:
                # Reuse shared synthesis for a single article
                self._synthesize_embedded([article])

            return article
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
