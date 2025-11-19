from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es = Elasticsearch("http://localhost:9200")

# ------------------------------
# CLEANUP OLD INDICES
# ------------------------------
es.indices.delete(index="test_products", ignore_unavailable=True)
es.indices.delete(index="test_reviews", ignore_unavailable=True)

# ------------------------------
# CREATE INDICES
# ------------------------------
es.indices.create(index="test_products")
es.indices.create(index="test_reviews")

# ------------------------------
# INSERT PRODUCTS
# ------------------------------
products = [
    {
        "_index": "test_products",
        "_id": 1,
        "_source": {
            "title": "Wireless Headphones",
            "description": "Noise-cancelling over-ear Bluetooth headphones with 20h battery.",
            "category": "audio",
            "price": 99.99,
        },
    },
    {
        "_index": "test_products",
        "_id": 2,
        "_source": {
            "title": "Mechanical Keyboard",
            "description": "RGB backlit mechanical keyboard with tactile switches.",
            "category": "peripherals",
            "price": 79.99,
        },
    },
    {
        "_index": "test_products",
        "_id": 3,
        "_source": {
            "title": "Smartwatch",
            "description": "Fitness tracking smartwatch with heart-rate monitor.",
            "category": "wearables",
            "price": 149.99,
        },
    },
]
bulk(es, products)

# ------------------------------
# INSERT REVIEWS
# ------------------------------
reviews = [
    {
        "_index": "test_reviews",
        "_id": 1,
        "_source": {
            "product_id": 1,
            "rating": 5,
            "text": "Excellent sound and comfort!",
        },
    },
    {
        "_index": "test_reviews",
        "_id": 2,
        "_source": {"product_id": 1, "rating": 4, "text": "Battery life is great."},
    },
    {
        "_index": "test_reviews",
        "_id": 3,
        "_source": {
            "product_id": 2,
            "rating": 3,
            "text": "Good typing experience, but loud.",
        },
    },
    {
        "_index": "test_reviews",
        "_id": 4,
        "_source": {
            "product_id": 3,
            "rating": 5,
            "text": "Very helpful for tracking workouts.",
        },
    },
]
bulk(es, reviews)

# ------------------------------
# SEARCH PRODUCTS - Full-text
# ------------------------------
print("\n🔍 Search products with keyword 'keyboard':")
res = es.search(index="test_products", query={"match": {"description": "keyboard"}})
for hit in res["hits"]["hits"]:
    print(hit["_source"])

# ------------------------------
# FILTER PRODUCTS - By category/price
# ------------------------------
print("\n💡 Products in category 'audio' under $100:")
res = es.search(
    index="test_products",
    query={
        "bool": {
            "must": [{"match": {"category": "audio"}}],
            "filter": [{"range": {"price": {"lte": 100}}}],
        }
    },
)
for hit in res["hits"]["hits"]:
    print(hit["_source"])

# ------------------------------
# AGGREGATE REVIEWS - Avg rating per product
# ------------------------------
print("\n⭐ Average rating per product:")
res = es.search(
    index="test_reviews",
    size=0,
    aggs={
        "avg_rating_by_product": {
            "terms": {"field": "product_id"},
            "aggs": {"avg_rating": {"avg": {"field": "rating"}}},
        }
    },
)

for bucket in res["aggregations"]["avg_rating_by_product"]["buckets"]:
    print(
        f"Product ID {bucket['key']} has average rating {bucket['avg_rating']['value']:.2f}"
    )

# ------------------------------
# MANUAL JOIN - Show product with reviews
# ------------------------------
print("\n🔗 Product details with reviews:")
product_docs = es.search(index="test_products", query={"match_all": {}}, size=100)[
    "hits"
]["hits"]
review_docs = es.search(index="test_reviews", query={"match_all": {}}, size=100)[
    "hits"
]["hits"]

# Organize reviews by product_id
review_map = {}
for r in review_docs:
    pid = r["_source"]["product_id"]
    review_map.setdefault(pid, []).append(r["_source"])

# Join manually
for p in product_docs:
    product = p["_source"]
    pid = int(p["_id"])
    print(f"\n🛍️ {product['title']} (${product['price']})")
    print(f"Description: {product['description']}")
    for review in review_map.get(pid, []):
        print(f"  - Rating {review['rating']}: {review['text']}")

# ------------------------------
# DELETE REVIEW
# ------------------------------
print("\n🗑️ Deleting review with rating 3 (too loud)")
res = es.search(index="test_reviews", query={"match": {"rating": 3}})
for hit in res["hits"]["hits"]:
    es.delete(index="reviews", id=hit["_id"])
    print(f"Deleted review id={hit['_id']}")

print("\n✅ Remaining reviews:")
res = es.search(index="test_reviews", query={"match_all": {}})
for hit in res["hits"]["hits"]:
    print(hit["_source"])
