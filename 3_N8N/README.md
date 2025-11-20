# Run

## Official

```bash
docker volume create n8n_data

docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n:next
```

## Custom

```bash
docker volume create n8n_custom_data
docker build -t n8n-custom .
docker run -d --name n8n-custom -p 5678:5678 -v n8n_custom_data:/home/node/.n8n -e NODE_FUNCTION_ALLOW_EXTERNAL=yahoo-finance2,axios n8n-custom
```

# API

`http://localhost:5678/api/v1/docs/`
