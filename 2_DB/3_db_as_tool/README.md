# Educational Database Tools AI Agent

An interactive AI agent that demonstrates how different database technologies work as tools in AI systems. This educational project helps students understand practical applications of various databases in AI agent workflows.

## 🎯 Learning Objectives

- **Database Selection Logic**: Understand when to use each database type
- **Tool Integration**: See how databases function as tools in AI workflows
- **Data Relationships**: Learn how data flows between different systems
- **Performance Trade-offs**: Observe strengths and limitations of each technology
- **Real-world Applications**: Experience practical e-commerce use cases

## 🛠 Supported Databases

| Database          | Purpose            | Use Cases                             |
| ----------------- | ------------------ | ------------------------------------- |
| **MSSQL Server**  | Relational data    | Users, products, orders, transactions |
| **MongoDB**       | Document store     | User sessions, reviews, analytics     |
| **Elasticsearch** | Search & analytics | Product search, trending queries      |
| **Qdrant**        | Vector database    | Similarity search, recommendations    |
| **MinIO**         | Object storage     | Images, files, media                  |

## 🚀 Quick Start

### Prerequisites

**Choose your AI Provider:**

**Option A: Ollama (Local, Free)**

1. **Install Ollama**

   ```bash
   # Download from https://ollama.ai/
   # Or using curl:
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama and download a model**
   ```bash
   ollama serve
   ollama pull llama3.2
   ```

**Option B: OpenAI (Cloud, Requires API Key)**

1. **Get OpenAI API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an API key
   - Ensure you have credits/billing set up

### Configuration

1. **Copy environment template**

   ```bash
   cp .env.example .env
   ```

2. **Edit .env file** to configure your AI provider:

   **For Ollama (default):**

   ```bash
   AI_PROVIDER=ollama
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3.2:latest
   ```

   **For OpenAI:**

   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_actual_api_key_here
   OPENAI_MODEL=gpt-4o
   ```

3. **Easy Provider Switching**
   - Change `AI_PROVIDER` in `.env` file
   - Or set environment variable: `export AI_PROVIDER=openai`
   - Or run with inline variable: `AI_PROVIDER=openai python main.py`

### Run the Agent

```bash
uv run main.py
```

## 🔄 AI Provider Comparison

| Feature             | Ollama                  | OpenAI                     |
| ------------------- | ----------------------- | -------------------------- |
| **Cost**            | Free                    | Pay-per-token              |
| **Privacy**         | Fully local             | Cloud-based                |
| **Performance**     | Depends on hardware     | Consistent, high-quality   |
| **Internet**        | Not required            | Required                   |
| **Setup**           | Download models locally | API key only               |
| **Models**          | Open-source models      | GPT-4, GPT-3.5, etc.       |
| **Tool Calling**    | ✅ Supported            | ✅ Excellent               |
| **Educational Use** | Perfect for learning    | Great for production demos |

**Recommendation:**

- **Students/Learning**: Use Ollama (free, private, educational)
- **Production Demos**: Use OpenAI (reliable, high-quality responses)
- **Development**: Switch between both to compare results!

## 💬 Interactive Chat Interface

The agent provides an interactive chat interface where you can ask natural language questions about data. The agent will:

1. **Analyze your query** and determine which database(s) to use
2. **Execute appropriate tool calls** to gather data
3. **Explain its reasoning** for tool selection
4. **Present results** in an educational format

### Chat Commands

- `help` or `h` - Show example queries
- `quit`, `exit`, or `q` - Exit the application
- `Ctrl+C` - Force exit

## 📚 Example Queries

### Customer Analysis (Cross-Database)

```
Show me details about user David Jones and his recent purchase behavior.
```

**Learning**: See how MSSQL (user data) and MongoDB (behavior data) complement each other.

### Product Recommendations (Vector Search)

```
Find products similar to tennis ball.
```

**Learning**: Understand how Qdrant performs semantic similarity search for AI-powered recommendations.

### Search Analytics (Full-Text Search)

```
What are customers searching for most this month?
```

**Learning**: Experience Elasticsearch's real-time analytics and aggregation capabilities.

### Visual Content (Object Storage)

```
Give me product images urls for the top-rated electronics.
```

**Learning**: See how MinIO integrates with structured data for complete applications.

### Business Intelligence

```
How many orders were placed for year 2025 and what's the total revenue?
```

**Learning**: Understand when to use SQL databases for business reporting.

### User Behavior Analysis

```
Show me user session data for mobile users from last week
```

**Learning**: See Elastic's flexibility for behavioral analytics.

### Advanced Queries

#### Multi-Database Analysis

```
Compare search trends with actual sales data - are people searching for what they buy?
```

#### Performance Analysis

```
Which database would be best for storing real-time chat messages?
```

#### Data Architecture Questions

```
Explain why you would use different databases for different parts of an e-commerce system
```

## 🎓 Educational Features

### Tool Selection Reasoning

The agent explains why it chose each database:

- **MSSQL**: For structured, transactional data requiring ACID properties
- **MongoDB**: For flexible schemas and rapid development
- **Elasticsearch**: For full-text search and real-time analytics
- **Qdrant**: For AI-powered semantic search and recommendations
- **MinIO**: For scalable object storage and media handling

### Cross-Database Workflows

See how modern applications use multiple databases together:

1. Query user profile from MSSQL
2. Get behavior data from MongoDB
3. Find similar products in Qdrant
4. Retrieve product images from MinIO
5. Log search queries to Elasticsearch

### Performance Insights

Learn about database performance characteristics:

- **MSSQL**: ACID compliance, complex queries, transactions
- **MongoDB**: Horizontal scaling, flexible schemas
- **Elasticsearch**: Near real-time search, aggregations
- **Qdrant**: Vector similarity, machine learning integration
- **MinIO**: High throughput, distributed storage

## Model Performance

**Ollama:**

- Use larger models (llama3.1:8b, llama3.1:70b) for better tool selection
- Ensure sufficient RAM (8GB+ recommended)
- Consider GPU acceleration for better performance

**OpenAI:**

- GPT-4o recommended for best tool selection
- GPT-3.5-turbo works but may be less reliable with complex tool calls
- Monitor token usage for cost control

## 📚 Further Learning

- [Ollama Documentation](https://ollama.ai/docs)
- [Database Design Patterns](https://www.martinfowler.com/articles/enterprisePatterns.html)
- [Vector Databases Explained](https://www.pinecone.io/learn/vector-database/)
- [AI Agent Architectures](https://lilianweng.github.io/posts/2023-06-23-agent/)

---
