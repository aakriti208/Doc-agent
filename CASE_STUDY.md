# doc-agent — Case Study

**A serverless RAG assistant on AWS that answers questions from company documents and takes real actions through an agent.**

---

## The Problem

Customer support was painful — agents answered the same questions repeatedly while customers waited. Internal knowledge was scattered across wikis, shared drives, and people's heads. New hires had no good way to get up to speed. On top of that, prompts were hardcoded into application code, making changes require full deployments with no audit trail.

---

## The Solution

doc-agent is a fully serverless AI assistant built on AWS. Documents live in S3, get chunked and embedded into a vector store via Bedrock Knowledge Bases, and are retrieved at query time by an agent running on Bedrock AgentCore. The agent answers with source citations or calls a tool (like creating a support ticket) when action is needed. When documents change, an EventBridge + Lambda pipeline re-syncs the knowledge base automatically. Prompts are versioned in Bedrock Prompt Management — no hardcoding, full audit trail.

**Stack:** Claude Sonnet 4.5 · Bedrock AgentCore · Bedrock Knowledge Bases · OpenSearch Serverless · S3 · EventBridge · Lambda · CDK · Strands (agent framework)

---

## Key Decisions

- **RAG over fine-tuning** — documents change frequently; retrieval at query time keeps answers grounded in the current source of truth and enables citations
- **Bedrock Knowledge Bases over self-managed** — managed chunking, embedding, and S3 sync removed operational overhead without meaningful flexibility tradeoff at this scale
- **LRU session cache** — up to 128 in-process sessions with conversation history, bounded to prevent memory leaks; durable session store planned as scale grows
- **Versioned prompts** — Bedrock Prompt Management replaces hardcoded prompts; every change is auditable and deployable without a code push

---

## Build Log

> This section grows with the project. Each entry captures a real problem hit, how it was diagnosed, and what was done.

### August 24 2026 — Initial Deployment

**Problem:** IAM user `BedrockAPIKey-vl76` lacked `cloudformation:DescribeStacks`, blocking the deploy. CDK bootstrap then failed with `CloudFormationStack object does not hold a stack` — the `CDKToolkit` stack was in a broken state from a prior partial run.

**Fix:** Added CloudFormation permissions to the IAM user. Deleted the broken `CDKToolkit` stack, re-ran `cdk bootstrap`, then redeployed successfully.

**Lesson:** Plan deployment IAM roles upfront. Treat CDK bootstrap as real infrastructure — a broken bootstrap stack silently blocks all future deploys.

### August 25 2026 — Gateway to Knowledge Base: CLI vs. Console

**Problem:** Connecting the Bedrock Knowledge Base to the agent through AgentCore Gateway kept failing. The `create-gateway-target` CLI command returned `AccessDeniedException` on `bedrock-agentcore:CreateGatewayTarget` — even after confirming full AdministratorAccess, no permissions boundary, no explicit deny, clean billing, and a personal (non-org) account. Standard IAM fixes didn't resolve it.

**Fix:** Diagnosed that the block wasn't an IAM permissions gap — a full admin being denied ruled out user policies, boundaries, and SCPs. Switched from the CLI to the AgentCore console, added the target to the existing gateway using the "Connectors" source type (the pre-built `bedrock-knowledge-bases` connector rather than "MCP server"), and set Outbound Auth to IAM Role (required for KB targets).

**Result:** The Knowledge Base target was created successfully. The agent now has a `Retrieve` tool exposed through the gateway, giving it grounded, cited RAG over the document set — without custom integration code.

**Lesson:** When a CLI command fails on a preview-stage AWS service despite valid permissions, the console can offer a working alternative path. The console sometimes handles connector flow and intermediate steps differently than the raw API.

---

## What's Next

Scaling to a **multi-agent system**: an orchestrator routing to specialized agents for customer support, internal knowledge, developer docs, and action execution — each with its own scoped knowledge base and tools.

---

_Built by Aakriti Dhakal_
