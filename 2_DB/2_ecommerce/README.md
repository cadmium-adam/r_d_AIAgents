# Multi-Database E-commerce Demo

A comprehensive demonstration of SQL, NoSQL, Full-text Search, and Vector databases working together in an e-commerce scenario. Each database type serves specific use cases where it excels, demonstrating polyglot persistence in action.

## 🚀 Quick Start

### Prerequisites

- **Docker and Docker Compose** - For running database services
- **Python 3.9+** - For running the applications
- **uv** - Python package manager (install with `pip install uv`)
- **Node.js 18+** - For the React UI application
- **npm** - Node package manager (comes with Node.js)
- **8GB+ RAM recommended** - For optimal performance

### 1. Start Database Services

Start all database containers in the background:

```bash
docker-compose -p my-ecommerce-db up -d
```

**Wait for services to be ready** (about 30-60 seconds). You can check status with:

```bash
docker compose ps
```

### 2. Setup Projects

Each database has its own independent uv project, plus the shared data generator:

```bash
# Setup shared data generator first (required for faker library)
cd shared_data && uv sync && cd ..

# Setup all database projects
cd 1_MSSQL && uv sync && cd ..
cd 2_MongoDB && uv sync && cd ..
cd 3_Elasticsearch && uv sync && cd ..
cd 4_Qdrant && uv sync && cd ..
```

### 3. Generate Shared Data

First, generate the shared dataset that all databases will use:

```bash
# Generate realistic e-commerce data
cd shared_data && uv run data_generator.py && cd ..
```

This creates:

- 55 products across 5 categories with AI-generated images
- 8 users with realistic profiles
- 53 orders with complex relationships
- Product reviews and ratings

### 4. Populate Databases

Load data into each database (run in order for dependencies):

```bash
# 1. MSSQL - Core business data
cd 1_MSSQL && uv run scripts/populate_data.py && cd ..

# 2. MongoDB - Flexible schema data
cd 2_MongoDB && uv run scripts/populate_data.py && cd ..

# 3. Elasticsearch - Search indices
cd 3_Elasticsearch && uv run scripts/populate_data.py && cd ..

# 4. Qdrant - Vector embeddings (takes longest)
cd 4_Qdrant && uv run scripts/populate_data.py && cd ..
```

**Note**: Qdrant population takes 5-10 minutes as it generates ML embeddings.

### 5. Start API Services

Start each FastAPI service in separate terminals:

```bash
# Terminal 1 - MSSQL API
cd 1_MSSQL && uv run api/main.py        # Port 8001

# Terminal 2 - MongoDB API
cd 2_MongoDB && uv run api/main.py      # Port 8002

# Terminal 3 - Elasticsearch API
cd 3_Elasticsearch && uv run api/main.py  # Port 8003

# Terminal 4 - Qdrant API
cd 4_Qdrant && uv run api/main.py     # Port 8004
```

### 6. Start the React UI Application

In a new terminal, start the frontend application:

```bash
# Terminal 5 - React UI
cd UI && npm install && npm run dev     # Port 3000
```

Open your browser to http://localhost:3000 to see the complete e-commerce application.

### 7. Test the System

Test each API to ensure everything works:

```bash
# Test health endpoints
curl http://localhost:8001/health  # MSSQL
curl http://localhost:8002/health  # MongoDB
curl http://localhost:8003/health  # Elasticsearch
curl http://localhost:8004/health  # Qdrant

# Test core functionality
curl http://localhost:8001/products                    # Get products from SQL
curl http://localhost:8002/reviews/product/1           # Get reviews from MongoDB
curl "http://localhost:8003/search?q=laptop"           # Search in Elasticsearch
curl http://localhost:8004/similar/1                   # AI similarity from Qdrant
```

### 8. Access Database UIs (Optional)

**Kibana Dashboard (Elasticsearch)**

```bash
open http://localhost:5601
```

**MinIO Console (Object Storage for Product Images)**

```bash
open http://localhost:9001
# Login: admin / adminpass
```

## 🖥️ UI Features

The React UI demonstrates all database integrations in a real e-commerce experience:

### Pages Available

1. **Home** - Database status dashboard showing all connections
2. **Products** - Browse catalog with pagination (MSSQL)
3. **Search** - Full-text search with filters and autocomplete (Elasticsearch)
4. **Cart** - Shopping cart management (MongoDB)
5. **AI Recommendations** - Three AI-powered features (Qdrant):
   - Personalized recommendations
   - Similar products
   - Semantic search
6. **Orders** - Order history with details (MSSQL)
7. **User Selection** - Switch between different users to test scenarios

### Key Features Implemented

- **Real-time product search** with typo tolerance
- **Shopping cart** with session management
- **AI-powered recommendations** based on user behavior
- **Product image display** from MinIO object storage
- **Pagination** for product catalog and search results
- **User switching** to test different customer scenarios
- **Order management** with ACID transactions
- **Cross-database integration** for seamless user experience

## 🎯 API Endpoints Overview

### MSSQL API (Port 8001) - Core Business Data

- `GET /products` - Product catalog with filtering and pagination
- `GET /products/{id}` - Product details
- `GET /users` - List all users with order statistics
- `GET /users/{id}` - User details
- `POST /orders` - Create order (ACID transaction)
- `GET /users/{id}/orders` - Order history
- `GET /reports/sales` - Business analytics
- `GET /categories` - Product categories

### MongoDB API (Port 8002) - Flexible Schema Data

- `GET /reviews/product/{id}` - Product reviews with nested comments
- `POST /reviews` - Create product review
- `GET /cart/{user_id}` - Get user's shopping cart
- `POST /cart/{user_id}/add` - Add item to cart
- `DELETE /cart/{user_id}/item/{product_id}` - Remove from cart
- `GET /users/{id}/session` - User session tracking
- `GET /recommendations/trending` - Real-time trending products
- `GET /analytics/realtime` - Real-time analytics data

### Elasticsearch API (Port 8003) - Search & Discovery

- `GET /search` - Advanced product search with aggregations
- `GET /autocomplete` - Search suggestions as you type
- `GET /analytics/popular-searches` - Popular search terms
- `GET /analytics/search-performance` - Search performance metrics
- `POST /products/index` - Index new products
- `POST /analytics/search` - Track search analytics

### Qdrant API (Port 8004) - AI-Powered Features

- `GET /similar/{product_id}` - Find similar products using vector similarity
- `POST /recommendations/{user_id}` - Personalized recommendations
- `POST /search/semantic` - Natural language product search
- `GET /collections/info` - Vector database collection info
- `GET /status` - Vector database and model status

## 📊 Database Services

| Database      | Port  | Use Case                         | API Port | UI/Dashboard   |
| ------------- | ----- | -------------------------------- | -------- | -------------- |
| MSSQL         | 1433  | Core business data, transactions | 8001     | -              |
| MongoDB       | 27017 | Sessions, reviews, flexible data | 8002     | -              |
| Elasticsearch | 9200  | Search and discovery             | 8003     | Kibana (5601)  |
| Qdrant        | 6333  | AI-powered recommendations       | 8004     | -              |
| MinIO         | 9000  | Object storage for images        | -        | Console (9001) |

## 🏗️ Project Structure

```
├── docker-compose.yml          # Database services configuration
├── shared_data/                # Common data generation (uv project)
│   ├── pyproject.toml         # uv project configuration
│   ├── data_generator.py      # Creates consistent test data
│   ├── users.json             # Generated user data
│   ├── products.json          # Generated product data
│   └── orders.json            # Generated order data
├── 1_MSSQL/                   # MSSQL independent project
│   ├── pyproject.toml         # uv project configuration
│   ├── scripts/
│   │   └── populate_data.py   # Load MSSQL data
│   └── api/
│       └── main.py            # FastAPI service (port 8001)
├── 2_MongoDB/                 # MongoDB independent project
│   ├── pyproject.toml         # uv project configuration
│   ├── scripts/
│   │   └── populate_data.py   # Load MongoDB data
│   └── api/
│       └── main.py            # FastAPI service (port 8002)
├── 3_Elasticsearch/           # Elasticsearch independent project
│   ├── pyproject.toml         # uv project configuration
│   ├── scripts/
│   │   └── populate_data.py   # Load Elasticsearch data
│   └── api/
│       └── main.py            # FastAPI service (port 8003)
├── 4_Qdrant/                  # Qdrant independent project
│   ├── pyproject.toml         # uv project configuration
│   ├── scripts/
│   │   └── populate_data.py   # Load Qdrant data
│   └── api/
│       └── main.py            # FastAPI service (port 8004)
└── UI/                        # React frontend application
    ├── package.json           # Node.js dependencies
    ├── tsconfig.json          # TypeScript configuration
    ├── vite.config.ts         # Vite build configuration
    └── src/
        ├── pages/             # React page components
        ├── components/        # Reusable components
        ├── services/          # API service clients
        └── types/             # TypeScript type definitions
```

## 🧪 Example Usage Scenarios

### 1. Product Discovery Journey

```bash
# 1. Search for products
curl "http://localhost:8003/search?q=laptop&category=Electronics"

# 2. Get detailed product info
curl http://localhost:8001/products/1

# 3. Read reviews
curl http://localhost:8002/reviews/product/1

# 4. Find similar products
curl http://localhost:8004/similar/1
```

### 2. Order Processing

```bash
# 1. Add items to cart
curl -X POST http://localhost:8002/cart/1/add \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# 2. Create order (ACID transaction)
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "items": [{"product_id": 1, "quantity": 2}],
    "shipping_address": {"street": "123 Main St", "city": "Seattle"},
    "payment_method": "credit_card"
  }'
```

### 3. Analytics & Recommendations

```bash
# Business analytics
curl http://localhost:8001/reports/sales

# Real-time user behavior
curl http://localhost:8002/analytics/realtime

# AI-powered recommendations
curl -X POST http://localhost:8004/recommendations/1 \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "hybrid", "limit": 10}'
```

## 🔧 Known Issues & Solutions

### Data Consistency

- **Issue**: Qdrant vector database may have products that don't exist in MSSQL
- **Solution**: The Qdrant API now filters out non-existent products automatically

### User Data

- **Issue**: User `total_orders` field may not match actual order count
- **Solution**: The `/users` endpoint calculates real-time statistics from the database

### Product Images

- **Issue**: Some products might not have images
- **Solution**: UI displays placeholder icons when images are missing

## 🛠️ Troubleshooting

### Database Connection Issues

```bash
# Check if services are running
docker-compose ps

# View service logs
docker-compose logs mssql
docker-compose logs mongodb
docker-compose logs elasticsearch
docker-compose logs kibana
docker-compose logs qdrant
docker-compose logs minio
```

### Data Loading Issues

```bash
# Reset and reload data
docker-compose down -v
docker-compose up -d
# Wait 60 seconds for services to start

# Regenerate data
cd shared_data && uv run data_generator.py && cd ..

# Reload each database
cd 1_MSSQL && uv run scripts/populate_data.py && cd ..
cd 2_MongoDB && uv run scripts/populate_data.py && cd ..
cd 3_Elasticsearch && uv run scripts/populate_data.py && cd ..
cd 4_Qdrant && uv run scripts/populate_data.py && cd ..
```

### Memory Issues

If you encounter memory issues:

1. Ensure Docker has at least 6GB of memory allocated
2. Reduce the number of concurrent services
3. Use the existing small dataset (55 products, 8 users)

### API Documentation

Each API service provides interactive documentation:

- MSSQL: http://localhost:8001/docs
- MongoDB: http://localhost:8002/docs
- Elasticsearch: http://localhost:8003/docs
- Qdrant: http://localhost:8004/docs

## 🎓 Learning Objectives

This project demonstrates several key concepts:

- **Polyglot Persistence**: Using the right database for the right job
- **Data Consistency**: Managing consistency across multiple databases
- **API Design**: RESTful APIs tailored to each database's strengths
- **Modern Architecture**: Microservices with database per service pattern
- **Performance Trade-offs**: Speed vs. consistency vs. flexibility
- **AI Integration**: Vector embeddings for ML-powered features
- **Full-stack Development**: React UI with TypeScript and modern tooling

Each database excels in its designated use case while working together to provide a complete e-commerce platform that showcases the power of choosing the right tool for each specific requirement.

## 📚 Architecture Details

### Why Each Database?

**MSSQL (SQL Server)**

- ACID transactions for orders and payments
- Complex joins for reporting
- Referential integrity for business data
- Strong consistency guarantees

**MongoDB**

- Flexible schema for reviews with nested comments
- Real-time session tracking
- Shopping cart with dynamic structure
- User behavior analytics

**Elasticsearch**

- Full-text search with typo tolerance
- Faceted search with aggregations
- Real-time search analytics
- Autocomplete suggestions

**Qdrant (Vector Database)**

- Semantic search using embeddings
- Product similarity calculations
- Personalized recommendations
- AI-powered features

**MinIO (Object Storage)**

- Scalable image storage
- S3-compatible API
- Presigned URLs for security
- CDN-ready architecture

## 🚀 Future Enhancements

Potential improvements to explore:

1. **GraphQL API** - Unified query layer across all databases
2. **Redis Cache** - Performance optimization layer
3. **Apache Kafka** - Event streaming between services
4. **TimescaleDB** - Time-series data for metrics
5. **Neo4j** - Graph database for recommendation engine
6. **Apache Spark** - Big data analytics pipeline

## 📝 License

This project is for educational purposes and demonstrates database integration patterns in modern applications.
