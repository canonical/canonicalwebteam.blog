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
    "user_facebook",
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
    "group",
]

# Minimal top-level fields for detail pages (keep embedded trimmed)
DEFAULT_POST_FIELDS = [
    *COMMON_POST_FIELDS,
    "_links",
    "_embedded",
]
POST_DETAILS_FIELDS = [
    *DEFAULT_POST_FIELDS,
    "content.rendered",
    "yoast_head_json.description",
]

# Very small field set for lists (IDs for joins + display basics)
LIST_POST_FIELDS = [
    *COMMON_POST_FIELDS,
    "topic",
    "featured_media",
]

FEED_POST_FIELDS = [
    *LIST_POST_FIELDS,
    "content.rendered",
]
