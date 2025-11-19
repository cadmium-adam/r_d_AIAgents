# Database Schema Documentation

## Multi-Database E-commerce Project

This document provides a comprehensive overview of the database schemas used in this multi-database e-commerce demonstration project. Each database serves specific use cases where it excels, showcasing practical applications of different database technologies.

## Infrastructure Overview

The project uses Docker Compose to orchestrate 6 database services:

| Database          | Port      | Container Name          | Purpose                          |
| ----------------- | --------- | ----------------------- | -------------------------------- |
| **MSSQL Server**  | 1433      | ecommerce-mssql         | Core business transactions       |
| **MongoDB**       | 27017     | ecommerce-mongodb       | Flexible schema & real-time data |
| **Elasticsearch** | 9200      | ecommerce-elasticsearch | Search & analytics               |
| **Qdrant**        | 6333      | ecommerce-qdrant        | Vector embeddings & AI features  |
| **Kibana**        | 5601      | ecommerce-kibana        | Elasticsearch visualization      |
| **MinIO**         | 9000/9001 | ecommerce-minio         | Object storage                   |

---

## 1. MSSQL Database - Core Business Data

**Database Name**: `ECommerceDB`  
**Port**: 1433  
**Use Case**: ACID-compliant transactions, complex relationships, financial data

### Schema Tables

#### `Users` Table

Primary key: `Id` (INT IDENTITY)

| Column             | Type          | Description                    |
| ------------------ | ------------- | ------------------------------ |
| `Id`               | INT IDENTITY  | Primary key                    |
| `Email`            | NVARCHAR(255) | Unique user email              |
| `FirstName`        | NVARCHAR(100) | User's first name              |
| `LastName`         | NVARCHAR(100) | User's last name               |
| `Phone`            | NVARCHAR(20)  | Contact phone number           |
| `DateOfBirth`      | DATE          | User's birth date              |
| `Street`           | NVARCHAR(255) | Shipping address               |
| `City`             | NVARCHAR(100) | Shipping city                  |
| `State`            | NVARCHAR(100) | Shipping state/province        |
| `ZipCode`          | NVARCHAR(20)  | Postal code                    |
| `Country`          | NVARCHAR(100) | Country                        |
| `TotalOrders`      | INT           | Number of orders placed        |
| `TotalSpent`       | DECIMAL(10,2) | Total amount spent             |
| `NewsletterOptIn`  | BIT           | Newsletter subscription status |
| `SMSNotifications` | BIT           | SMS notification preference    |
| `IsActive`         | BIT           | Account status                 |
| `JoinDate`         | DATETIME2     | Account creation date          |
| `LastLogin`        | DATETIME2     | Last login timestamp           |

#### `Categories` Table

Primary key: `Id` (INT IDENTITY)

| Column        | Type          | Description          |
| ------------- | ------------- | -------------------- |
| `Id`          | INT IDENTITY  | Primary key          |
| `Name`        | NVARCHAR(100) | Category name        |
| `Description` | NVARCHAR(500) | Category description |
| `CreatedAt`   | DATETIME2     | Creation timestamp   |

#### `Products` Table

Primary key: `Id` (INT)

| Column          | Type          | Description               |
| --------------- | ------------- | ------------------------- |
| `Id`            | INT           | Primary key               |
| `Name`          | NVARCHAR(255) | Product name              |
| `Description`   | NVARCHAR(MAX) | Product description       |
| `CategoryId`    | INT           | Foreign key to Categories |
| `Price`         | DECIMAL(10,2) | Product price             |
| `StockQuantity` | INT           | Available inventory       |
| `Brand`         | NVARCHAR(100) | Brand name                |
| `SKU`           | NVARCHAR(100) | Stock keeping unit        |
| `Weight`        | DECIMAL(8,2)  | Product weight (kg)       |
| `Length`        | DECIMAL(8,2)  | Dimensions (cm)           |
| `Width`         | DECIMAL(8,2)  | Dimensions (cm)           |
| `Height`        | DECIMAL(8,2)  | Dimensions (cm)           |
| `Rating`        | DECIMAL(3,2)  | Average rating            |
| `ReviewCount`   | INT           | Number of reviews         |
| `MainImageUrl`  | NVARCHAR(500) | Main product image        |
| `ThumbnailUrl`  | NVARCHAR(500) | Thumbnail image           |
| `Features`      | NVARCHAR(MAX) | JSON features data        |
| `IsActive`      | BIT           | Product status            |
| `CreatedAt`     | DATETIME2     | Creation timestamp        |
| `UpdatedAt`     | DATETIME2     | Last update timestamp     |

#### `Orders` Table

Primary key: `Id` (INT)

| Column            | Type          | Description          |
| ----------------- | ------------- | -------------------- |
| `Id`              | INT           | Primary key          |
| `UserId`          | INT           | Foreign key to Users |
| `OrderDate`       | DATETIME2     | Order timestamp      |
| `Status`          | NVARCHAR(50)  | Order status         |
| `Subtotal`        | DECIMAL(10,2) | Items subtotal       |
| `ShippingCost`    | DECIMAL(10,2) | Shipping cost        |
| `TaxAmount`       | DECIMAL(10,2) | Tax amount           |
| `TotalAmount`     | DECIMAL(10,2) | Total order amount   |
| `ShippingStreet`  | NVARCHAR(255) | Shipping address     |
| `ShippingCity`    | NVARCHAR(100) | Shipping city        |
| `ShippingState`   | NVARCHAR(100) | Shipping state       |
| `ShippingZipCode` | NVARCHAR(20)  | Shipping postal code |
| `ShippingCountry` | NVARCHAR(100) | Shipping country     |
| `PaymentMethod`   | NVARCHAR(50)  | Payment method used  |
| `TrackingNumber`  | NVARCHAR(100) | Shipment tracking    |

#### `OrderItems` Table

Primary key: `Id` (INT IDENTITY)

| Column        | Type          | Description             |
| ------------- | ------------- | ----------------------- |
| `Id`          | INT IDENTITY  | Primary key             |
| `OrderId`     | INT           | Foreign key to Orders   |
| `ProductId`   | INT           | Foreign key to Products |
| `ProductName` | NVARCHAR(255) | Product name snapshot   |
| `Quantity`    | INT           | Quantity ordered        |
| `UnitPrice`   | DECIMAL(10,2) | Price per unit          |
| `TotalPrice`  | DECIMAL(10,2) | Line total              |

#### `Payments` Table

Primary key: `Id` (INT IDENTITY)

| Column          | Type          | Description             |
| --------------- | ------------- | ----------------------- |
| `Id`            | INT IDENTITY  | Primary key             |
| `OrderId`       | INT           | Foreign key to Orders   |
| `PaymentMethod` | NVARCHAR(50)  | Payment method          |
| `Amount`        | DECIMAL(10,2) | Payment amount          |
| `Status`        | NVARCHAR(50)  | Payment status          |
| `TransactionId` | NVARCHAR(255) | External transaction ID |
| `ProcessedAt`   | DATETIME2     | Processing timestamp    |

---

## 2. MongoDB Database - Flexible Schema Data

**Database Name**: `ecommerce`  
**Port**: 27017  
**Use Case**: Real-time data, flexible schemas, nested documents, rapid prototyping

### Collections

**Note**: User sessions, user behavior, and analytics collections have been migrated to Elasticsearch for better time-series and search capabilities.

#### `product_reviews` Collection

Product reviews with nested comments and metadata

```json
{
  "_id": ObjectId,
  "product_id": "number",
  "product_name": "string",
  "product_category": "string",
  "user_id": "number",
  "user_name": "string",
  "rating": "number (1-5)",
  "title": "string",
  "comment": "string",
  "pros": ["string"],
  "cons": ["string"],
  "helpful_votes": "number",
  "total_votes": "number",
  "helpfulness_ratio": "number",
  "verified_purchase": "boolean",
  "early_reviewer": "boolean",
  "vine_customer": "boolean",
  "device_used": "string",
  "photos": [
    {
      "url": "string",
      "caption": "string"
    }
  ],
  "sentiment_score": "number",
  "status": "approved|pending|rejected",
  "flagged_reasons": ["string"],
  "moderator_notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### `shopping_carts` Collection

User shopping cart state

```json
{
  "_id": ObjectId,
  "user_id": "number",
  "items": [
    {
      "product_id": "number",
      "product_name": "string",
      "quantity": "number",
      "unit_price": "number",
      "total_price": "number",
      "added_at": "datetime"
    }
  ],
  "total_items": "number",
  "subtotal": "number",
  "estimated_tax": "number",
  "estimated_shipping": "number",
  "estimated_total": "number",
  "coupon_code": "string",
  "discount_amount": "number",
  "session_id": "string",
  "device_type": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### `recommendations` Collection

AI-generated product recommendations

```json
{
  "_id": ObjectId,
  "user_id": "number",
  "algorithm": "collaborative|content_based|hybrid",
  "products": [
    {
      "product_id": "number",
      "score": "number",
      "reason": "string"
    }
  ],
  "page_type": "homepage|product|cart|checkout",
  "user_segment": "string",
  "session_activity": ["string"],
  "impressions": "number",
  "clicks": "number",
  "conversions": "number",
  "ctr": "number",
  "created_at": "datetime",
  "expires_at": "datetime"
}
```

---

## 3. Elasticsearch Database - Search & Analytics

**Database Name**: Multiple indices  
**Port**: 9200  
**Use Case**: Full-text search, autocomplete, search analytics, real-time indexing, time-series data, event logs

### Indices

#### `products` Index

Product search and discovery

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "integer" },
      "name": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "autocomplete": {
            "type": "text",
            "analyzer": "autocomplete"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "standard"
      },
      "category": { "type": "keyword" },
      "brand": { "type": "keyword" },
      "price": { "type": "float" },
      "stock_quantity": { "type": "integer" },
      "rating": { "type": "float" },
      "review_count": { "type": "integer" },
      "is_active": { "type": "boolean" },
      "tags": { "type": "keyword" },
      "attributes": {
        "type": "nested",
        "properties": {
          "name": { "type": "keyword" },
          "value": { "type": "keyword" }
        }
      },
      "images": {
        "properties": {
          "main": { "type": "keyword" },
          "thumbnail": { "type": "keyword" }
        }
      },
      "suggest": {
        "type": "completion",
        "analyzer": "simple",
        "search_analyzer": "simple"
      },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" }
    }
  }
}
```

#### `search_analytics` Index

Search behavior and performance metrics

```json
{
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "query": { "type": "text" },
      "user_id": { "type": "integer" },
      "session_id": { "type": "keyword" },
      "results_count": { "type": "integer" },
      "clicked_product_id": { "type": "integer" },
      "clicked_position": { "type": "integer" },
      "search_time_ms": { "type": "integer" },
      "filters_applied": {
        "type": "nested",
        "properties": {
          "filter_type": { "type": "keyword" },
          "filter_value": { "type": "keyword" }
        }
      },
      "device_type": { "type": "keyword" },
      "location": { "type": "geo_point" },
      "converted": { "type": "boolean" }
    }
  }
}
```

#### `popular_searches` Index

Trending and popular search queries

```json
{
  "mappings": {
    "properties": {
      "query": { "type": "keyword" },
      "search_count": { "type": "integer" },
      "last_searched": { "type": "date" },
      "trending_score": { "type": "float" },
      "category": { "type": "keyword" },
      "suggestions": { "type": "keyword" }
    }
  }
}
```

#### `user_sessions` Index

User browsing sessions

```json
{
  "mappings": {
    "properties": {
      "session_id": { "type": "keyword" },
      "user_id": { "type": "integer" },
      "start_time": { "type": "date" },
      "end_time": { "type": "date" },
      "duration_minutes": { "type": "float" },
      "pages_viewed": {
        "type": "nested",
        "properties": {
          "url": { "type": "keyword" },
          "timestamp": { "type": "date" },
          "time_spent_seconds": { "type": "integer" }
        }
      },
      "device_info": {
        "properties": {
          "type": { "type": "keyword" },
          "os": { "type": "keyword" },
          "browser": { "type": "keyword" },
          "screen_resolution": { "type": "keyword" }
        }
      },
      "location": {
        "properties": {
          "country": { "type": "keyword" },
          "city": { "type": "keyword" },
          "ip_address": { "type": "ip" }
        }
      },
      "referrer": { "type": "keyword" },
      "is_active": { "type": "boolean" },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" }
    }
  }
}
```

#### `user_behavior` Index

User interaction events

```json
{
  "mappings": {
    "properties": {
      "user_id": { "type": "integer" },
      "session_id": { "type": "keyword" },
      "event_type": { "type": "keyword" },
      "timestamp": { "type": "date" },
      "page_url": { "type": "keyword" },
      "device_info": {
        "properties": {
          "type": { "type": "keyword" },
          "os": { "type": "keyword" },
          "browser": { "type": "keyword" }
        }
      },
      "product_id": { "type": "integer" },
      "search_query": {
        "type": "text",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "filters": {
        "properties": {
          "category": { "type": "keyword" },
          "price_range": { "type": "keyword" },
          "brand": { "type": "keyword" }
        }
      },
      "order_total": { "type": "float" },
      "items_count": { "type": "integer" }
    }
  }
}
```

#### `analytics` Index

Aggregated business metrics

```json
{
  "mappings": {
    "properties": {
      "date": { "type": "date" },
      "metric_type": { "type": "keyword" },
      "unique_visitors": { "type": "integer" },
      "returning_visitors": { "type": "integer" },
      "new_visitors": { "type": "integer" },
      "page_views": { "type": "integer" },
      "sessions": { "type": "integer" },
      "bounce_rate": { "type": "float" },
      "avg_session_duration": { "type": "float" },
      "conversion_rate": { "type": "float" },
      "revenue": { "type": "float" },
      "orders": { "type": "integer" },
      "avg_order_value": { "type": "float" },
      "top_products": {
        "type": "nested",
        "properties": {
          "product_id": { "type": "integer" },
          "name": { "type": "keyword" },
          "views": { "type": "integer" },
          "sales": { "type": "integer" }
        }
      },
      "top_categories": {
        "type": "nested",
        "properties": {
          "category": { "type": "keyword" },
          "views": { "type": "integer" },
          "sales": { "type": "integer" }
        }
      },
      "traffic_sources": {
        "properties": {
          "direct": { "type": "integer" },
          "search": { "type": "integer" },
          "social": { "type": "integer" },
          "referral": { "type": "integer" }
        }
      },
      "device_breakdown": {
        "properties": {
          "desktop": { "type": "integer" },
          "mobile": { "type": "integer" },
          "tablet": { "type": "integer" }
        }
      }
    }
  }
}
```

---

## 4. Qdrant Database - Vector Embeddings

**Database Name**: Collections  
**Port**: 6333  
**Use Case**: Semantic search, AI recommendations, similarity matching

### Collections

#### `product_embeddings` Collection

Product vector embeddings for similarity search

**Configuration:**

- **Vector Size**: 384 dimensions
- **Distance**: Cosine similarity
- **Model**: all-MiniLM-L6-v2

**Payload Structure:**

```json
{
  "content": "string - full text representation used for embedding",
  "metadata": {
    "id": "number",
    "name": "string",
    "description": "string",
    "category": "string",
    "brand": "string",
    "price": "number",
    "rating": "number",
    "features": ["string"],
    "tags": ["string"]
  }
}
```

#### `user_preference_embeddings` Collection

User preference vectors for personalized recommendations

**Configuration:**

- **Vector Size**: 384 dimensions
- **Distance**: Cosine similarity
- **Model**: all-MiniLM-L6-v2

**Payload Structure:**

```json
{
  "content": "string - user preference text representation",
  "metadata": {
    "id": "number",
    "email": "string",
    "preferences": {
      "categories": ["string"],
      "brands": ["string"],
      "price_range": "string"
    },
    "purchase_history": {
      "total_orders": "number",
      "total_spent": "number",
      "avg_order_value": "number"
    },
    "demographics": {
      "age_group": "string",
      "location": "string"
    },
    "top_category": "string"
  }
}
```

---

## 5. MinIO Object Storage

**Service Name**: MinIO S3-compatible storage  
**API Port**: 9000  
**Console Port**: 9001  
**Use Case**: File storage, media assets, backups

### Bucket Structure

#### `product-images` Bucket

Product photographs and media

**Structure:**

```
product-images/
├── original/
│   ├── {product_id}/
│   │   ├── main.jpg
│   │   ├── gallery/
│   │   │   ├── image1.jpg
│   │   │   ├── image2.jpg
│   │   │   └── ...
│   │   └── 360/
│   │       ├── frame001.jpg
│   │       └── ...
│   └── ...
├── thumbnails/
│   ├── {product_id}/
│   │   ├── small.jpg (150x150)
│   │   ├── medium.jpg (300x300)
│   │   └── large.jpg (600x600)
│   └── ...
└── optimized/
    ├── {product_id}/
    │   ├── webp/
    │   └── avif/
    └── ...
```

#### `user-uploads` Bucket

User-generated content

**Structure:**

```
user-uploads/
├── reviews/
│   ├── {user_id}/
│   │   ├── {review_id}/
│   │   │   ├── photo1.jpg
│   │   │   └── ...
│   │   └── ...
│   └── ...
├── avatars/
│   ├── {user_id}/
│   │   ├── original.jpg
│   │   ├── thumbnail.jpg
│   │   └── ...
│   └── ...
└── support/
    ├── {ticket_id}/
    │   ├── attachment1.pdf
    │   └── ...
    └── ...
```

#### `data-exports` Bucket

Generated reports and backups

**Structure:**

```
data-exports/
├── reports/
│   ├── daily/
│   │   ├── {date}/
│   │   │   ├── sales_report.pdf
│   │   │   ├── inventory_report.xlsx
│   │   │   └── ...
│   │   └── ...
│   ├── monthly/
│   └── yearly/
├── backups/
│   ├── databases/
│   │   ├── {timestamp}/
│   │   │   ├── mssql_backup.bak
│   │   │   ├── mongodb_dump.gz
│   │   │   └── ...
│   │   └── ...
│   └── configurations/
└── ml-models/
    ├── recommendation_engine/
    │   ├── model_v1.pkl
    │   └── ...
    └── ...
```

---

## Data Relationships & Integration

### Cross-Database Relationships

1. **Product Data Flow:**

   - MSSQL: Authoritative product catalog
   - MongoDB: Product reviews and ratings
   - Elasticsearch: Search index with aggregated data
   - Qdrant: Product embeddings for similarity

2. **User Data Flow:**

   - MSSQL: User accounts and order history
   - MongoDB: Shopping carts and AI recommendations
   - Elasticsearch: Session data, behavior tracking, search history, and analytics
   - Qdrant: User preference embeddings

3. **Order Data Flow:**
   - MSSQL: Transactional order data
   - MongoDB: Cart state and checkout analytics
   - Elasticsearch: Order search and reporting

### Synchronization Strategy

- **Shared Data Generation**: `/shared_data/` contains JSON files used to populate all databases consistently
- **Event-Driven Updates**: Changes in MSSQL trigger updates to other databases
- **Batch Synchronization**: Nightly jobs sync aggregated data
- **Real-time Streaming**: User behavior flows immediately to MongoDB and Elasticsearch

### Data Consistency

- **MSSQL**: Source of truth for financial and inventory data
- **MongoDB**: Eventually consistent for user behavior
- **Elasticsearch**: Near real-time for search indices
- **Qdrant**: Batch updated for embedding refreshes
- **MinIO**: Immediate consistency for file operations

---

## Connection Details

### Database Credentials

| Database      | Host      | Port  | Username | Password    | Database/Collection |
| ------------- | --------- | ----- | -------- | ----------- | ------------------- |
| MSSQL         | localhost | 1433  | sa       | Heslo_1234  | ECommerceDB         |
| MongoDB       | localhost | 27017 | admin    | admin123    | ecommerce           |
| Elasticsearch | localhost | 9200  | -        | -           | Multiple indices    |
| Qdrant        | localhost | 6333  | -        | -           | Collections         |
| MinIO         | localhost | 9000  | admin    | password123 | Buckets             |

### Health Check Endpoints

- **MSSQL**: SQL query `SELECT 1`
- **MongoDB**: `db.runCommand("ping").ok`
- **Elasticsearch**: `GET /_cluster/health`
- **Qdrant**: `GET /health`
- **MinIO**: `GET /minio/health/live`

---

## Performance Characteristics

### MSSQL

- **Strengths**: ACID compliance, complex joins, reporting
- **Use Cases**: Financial transactions, inventory management
- **Scaling**: Vertical scaling, read replicas

### MongoDB

- **Strengths**: Flexible schema, horizontal scaling, real-time
- **Use Cases**: Product reviews, shopping carts, AI recommendations
- **Scaling**: Horizontal sharding, replica sets

### Elasticsearch

- **Strengths**: Full-text search, aggregations, near real-time, time-series optimization
- **Use Cases**: Product search, user sessions, behavior analytics, business metrics
- **Scaling**: Horizontal clustering, index sharding

### Qdrant

- **Strengths**: Vector similarity, AI/ML integration
- **Use Cases**: Recommendations, semantic search
- **Scaling**: Horizontal clustering, vector quantization

### MinIO

- **Strengths**: S3 compatibility, high throughput, object storage
- **Use Cases**: Media files, backups, static assets
- **Scaling**: Distributed storage, erasure coding

This multi-database architecture demonstrates practical use cases where each technology excels, providing hands-on experience with different data modeling approaches and their trade-offs in a real-world e-commerce scenario.
