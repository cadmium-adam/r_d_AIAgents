```bash
curl -X POST \
  http://localhost:5678/webhook-test/e500dfd5-e6c5-4d58-bf87-11e208f07048 \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Artificial intelligence has revolutionized numerous industries in recent years. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions with unprecedented accuracy. From healthcare diagnostics to autonomous vehicles, AI applications are transforming how we work and live. Natural language processing has enabled chatbots and virtual assistants to understand and respond to human queries more effectively. Computer vision systems can analyze images and videos for security, manufacturing quality control, and medical imaging. Deep learning networks, inspired by the human brain, have achieved breakthrough performance in tasks like image recognition, language translation, and game playing. However, the rapid advancement of AI also raises important questions about ethics, privacy, and the future of employment. As AI systems become more sophisticated, ensuring they remain beneficial and aligned with human values becomes increasingly critical.",
    "summaryType": "general",
    "maxLength": 100,
    "includeAnalysis": true
  }'
```
