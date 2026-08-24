# doc-agent

A serverless RAG assistant on AWS that answers questions from your own documents and can take actions (like creating a support ticket) through an agent.

## What it does

- Answers questions grounded in your documents, with source citations
- Takes actions via an agent tool (e.g. creates a support ticket)
- Automatically re-syncs its knowledge base when documents change
- Centralizes and versions its prompts instead of hardcoding them
- Logs prompt changes and model interactions for auditing


## AWS services

- **Amazon Bedrock** – model inference and embeddings
- **Bedrock Knowledge Bases** – RAG pipeline
- **OpenSearch Serverless** – vector store
- **Amazon S3** – document storage
- **EventBridge + Lambda** – auto-sync on document change
- **Bedrock AgentCore** – agent and tool use
- **Bedrock Prompt Management** – versioned prompts
- **CloudTrail + CloudWatch Logs** – audit and monitoring
- **IAM** – access control

## How it works

1. Documents are uploaded to S3.
2. A Knowledge Base chunks, embeds, and stores them for retrieval.
3. When a document changes, an S3 event triggers a Lambda that re-syncs the Knowledge Base.
4. A user asks a question. The agent either retrieves a grounded answer from the Knowledge Base or calls a Lambda tool to take an action.
5. Prompt changes and model interactions are logged for auditing.

## Setup

```bash
git clone https://github.com/<your-username>/doc-agent.git
cd doc-agent
# deployment steps in infrastructure/
```

## Cost

Runs on pay-per-use and free-tier services for small workloads. The vector store is the main standing cost — run `scripts/cleanup.sh` after testing to avoid charges.

## License

MIT
