# Getting Started with AgentParty

This guide will help you set up and use the AgentParty MCP platform.

## Prerequisites

- Docker Desktop installed and running
- VS Code or Windsurf IDE
- OpenAI or Anthropic API key

## Quick Start

### 1. Configure Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and set:
```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Start the Platform

Start all services in development mode:

```bash
docker-compose --profile dev up -d
```

This starts:
- **AgentParty MCP Server** on http://localhost:8000
- **Qdrant** (vector database) on http://localhost:6333
- **Redis** (session store) on localhost:6379

### 3. Verify Services

Check that all services are running:

```bash
docker-compose ps
```

Test the MCP server:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "agentparty-mcp",
  "version": "0.1.0"
}
```

### 4. View Available Resources

List agents:
```bash
curl http://localhost:8000/api/agents
```

List workflows:
```bash
curl http://localhost:8000/api/workflows
```

List jobs:
```bash
curl http://localhost:8000/api/jobs
```

## Using the MCP Platform

### Step 1: Create a Session

First, create a session to authenticate:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "create_session",
      "arguments": {
        "user_id": "your-email@example.com"
      }
    }
  }'
```

Save the `session_id` from the response.

### Step 2: Get Available Jobs

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_available_jobs",
      "arguments": {
        "session_id": "YOUR_SESSION_ID"
      }
    }
  }'
```

### Step 3: Start a Job

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "start_job",
      "arguments": {
        "session_id": "YOUR_SESSION_ID",
        "job_id": "example-feature"
      }
    }
  }'
```

### Step 4: Get Current Task

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_current_task",
      "arguments": {
        "session_id": "YOUR_SESSION_ID"
      }
    }
  }'
```

### Step 5: Submit Work

After implementing the feature:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "submit_work",
      "arguments": {
        "session_id": "YOUR_SESSION_ID",
        "work_description": "Implemented JWT authentication with bcrypt password hashing",
        "artifacts": ["src/auth/routes.py", "src/auth/models.py", "tests/test_auth.py"]
      }
    }
  }'
```

### Step 6: Request Review

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "request_review",
      "arguments": {
        "session_id": "YOUR_SESSION_ID"
      }
    }
  }'
```

The Manager agent will review your work and provide feedback!

## IDE Integration (VS Code/Windsurf)

### Configure MCP in VS Code

Add to your VS Code settings or MCP configuration:

```json
{
  "mcpServers": {
    "agentparty": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "http://localhost:8000/mcp",
        "-H", "Content-Type: application/json",
        "-d", "@-"
      ]
    }
  }
}
```

### Using in Windsurf

Windsurf has built-in MCP support. Add the server:

1. Open Windsurf settings
2. Go to MCP Servers
3. Add new server:
   - **Name**: AgentParty
   - **URL**: http://localhost:8000/mcp

## Common Workflows

### Full Development Workflow

1. **Create session** with your user ID
2. **Get available jobs** to see what you can work on
3. **Start a job** to initialize the workflow
4. **Get current task** to see what to do
5. **Query context** to search relevant codebase info
6. **Ask agent guidance** if you need help
7. **Submit work** when done
8. **Request review** from Manager agent
9. **Check workflow status** to see progress
10. **Get budget status** to monitor API usage

### Consulting an Agent

Need architectural advice?

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_agent_guidance",
      "arguments": {
        "session_id": "YOUR_SESSION_ID",
        "agent_id": "manager",
        "question": "Should I use JWT or session-based auth for this API?"
      }
    }
  }'
```

### Searching Codebase Context

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "query_context",
      "arguments": {
        "session_id": "YOUR_SESSION_ID",
        "query": "How does the existing authentication system work?",
        "limit": 5
      }
    }
  }'
```

## Creating Your Own Content

### Create a New Agent

1. Create directory: `agents/my-agent/`
2. Create `index.yaml`:
```yaml
name: "My Agent"
description: "Agent description"
model:
  provider: "openai"
  model: "gpt-4-turbo-preview"
  temperature: 0.7
prompt_files:
  - system-prompt.md
  - knowledge.md
```

3. Create prompt files with agent instructions
4. Restart the server to load the new agent

### Create a New Workflow

1. Create directory: `workflows/my-workflow/`
2. Create `workflow.yaml`:
```yaml
name: "My Workflow"
version: "1.0"
steps:
  - id: "step1"
    name: "First Step"
    agent: "programmer"
    approvals:
      - agent: "manager"
        type: "review"
    transitions:
      - to: "step2"
        condition: "approved"
```

3. Create `description.md` with workflow overview

### Create a New Job

1. Create directory: `jobs/my-job/`
2. Create `index.yaml`:
```yaml
id: "my-job"
title: "My Job Title"
workflow: "sdlc"
assigned_to: "programmer"
priority: "high"
context_files:
  - overview.md
  - requirements.md
```

3. Create context markdown files with job details

## Monitoring & Debugging

### View Logs

```bash
# All services
docker-compose logs -f

# Just MCP server
docker-compose logs -f agentparty-dev

# Just Redis
docker-compose logs -f redis

# Just Qdrant
docker-compose logs -f qdrant
```

### Access Service UIs

- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **MCP Server Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (if OpenAPI enabled)

### Common Issues

**Services won't start**
```bash
docker-compose down
docker-compose --profile dev up -d --build
```

**Cannot connect to Redis**
- Check Redis is running: `docker-compose ps redis`
- Check logs: `docker-compose logs redis`
- Verify REDIS_URL in `.env`

**Cannot connect to Qdrant**
- Check Qdrant is running: `docker-compose ps qdrant`
- Visit http://localhost:6333/dashboard
- Check logs: `docker-compose logs qdrant`

**LLM API errors**
- Verify API keys in `.env`
- Check budget limits: use `get_budget_status` tool
- Check API key validity with provider

## Production Deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for Azure deployment guide.

Quick production start:

```bash
docker-compose --profile prod up -d
```

## Next Steps

1. **Read the Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system design
2. **Explore Examples**: Check `agents/`, `workflows/`, and `jobs/` directories
3. **Try the Example Job**: Start `example-feature` and complete the workflow
4. **Create Custom Agents**: Build agents for your specific use case
5. **Integrate with IDE**: Set up MCP in VS Code/Windsurf

## Getting Help

- **Documentation**: See `docs/` directory
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Examples**: Check example agents, workflows, and jobs
- **Logs**: Use `docker-compose logs` for debugging

## Budget Management

Monitor your API usage:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_budget_status",
      "arguments": {
        "session_id": "YOUR_SESSION_ID"
      }
    }
  }'
```

Default budget: $100/month (configurable in `.env`)

---

**Happy coding with AgentParty! 🎉**
