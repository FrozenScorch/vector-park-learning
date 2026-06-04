# Vector Park Learning

A hands-on, 8-week curriculum that teaches the full GenAI implementation ladder — from a single LLM call to multi-agent orchestration — by building one system over public National Park Service data.

This is opinionated and born from enterprise experience. It teaches the distinctions that matter in production: why RAG orchestration is not the same as an agent, why a planner-executor is not the same as ReAct, and why evals start at Level 1, not Level 8.

## The ladder

```
Level 0 — Setup & First NPS API Call
Level 1 — Generic Inference
Level 2 — Document Understanding & Structured Extraction
Level 3 — RAG Ingestion Substrate
Level 4 — Retrieval Mechanics & Basic RAG
Level 5 — RAG Orchestration
Level 6A — ReAct Single Agent
Level 6B — Planner-Executor Workflow Agent with HITL
Level 7 — Multi-Agent Orchestration
Level 8 — Production Thinking
```

## Prerequisites

- Comfortable reading and writing Python (no ML experience needed)
- A Mac or Windows laptop
- Docker Desktop installed
- An AI coding assistant (Claude Code, Copilot, etc.) to help scaffold your project

## Setup

### 1. Python 3.11+

Install Python 3.11 or higher. Verify with:

```bash
python3 --version
```

Create a virtual environment for the project:

```bash
# using venv
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# or using uv (faster)
uv venv
source .venv/bin/activate
```

### 2. PostgreSQL + pgvector

Run PostgreSQL with the pgvector extension in Docker:

```bash
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=fieldguide \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Verify it's running:

```bash
docker exec -it pgvector psql -U postgres -d fieldguide -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

### 3. NPS API key

The National Park Service API is free and public.

1. Go to [nps.gov/subjects/developer/get-started.htm](https://www.nps.gov/subjects/developer/get-started.htm)
2. Fill out the form — key arrives by email within minutes
3. Save it:

```bash
export NPS_API_KEY="your-key-here"
```

Test it:

```bash
curl -s "https://developer.nps.gov/api/v1/parks?parkCode=yell&limit=1" \
  -H "X-Api-Key: $NPS_API_KEY" | python3 -m json.tool | head -20
```

### 4. NVIDIA NIM API key

This curriculum uses [NVIDIA NIM](https://build.nvidia.com) as the LLM and embedding backend. NIM endpoints are OpenAI-compatible, so LangChain, LangGraph, and the `openai` Python library all work with a base URL swap.

1. Go to [build.nvidia.com](https://build.nvidia.com)
2. Sign in or create a free NVIDIA developer account
3. Click **Get API Key** and generate a key (starts with `nvapi-`)
4. Save it:

```bash
export NVIDIA_API_KEY="nvapi-your-key-here"
```

Test it:

```bash
curl -s https://integrate.api.nvidia.com/v1/models \
  -H "Authorization: Bearer $NVIDIA_API_KEY" | python3 -m json.tool | head -20
```

The free tier includes 1,000 inference credits on signup. Rate limit is 40 requests per minute.

### 5. Python dependencies

```bash
pip install \
  langchain \
  langchain-nvidia-ai-endpoints \
  langgraph \
  chainlit \
  psycopg2-binary \
  pgvector \
  requests \
  pydantic \
  python-dotenv
```

### 6. Environment variables

Create a `.env` file in your project root (and add it to `.gitignore`):

```bash
NPS_API_KEY=your-nps-key
NVIDIA_API_KEY=nvapi-your-nvidia-key
DATABASE_URL=postgresql://postgres:dev@localhost:5432/fieldguide
```

### 7. Chainlit

Verify Chainlit launches:

```bash
# create a minimal app.py
echo 'import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"Echo: {message.content}").send()' > app.py

chainlit run app.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser. Type something. If it echoes back, your UI is ready.

### 8. Verify everything

You should now have:

- [ ] Python 3.11+ with a virtual environment
- [ ] PostgreSQL + pgvector running in Docker
- [ ] NPS API key working (curl returns park data)
- [ ] NVIDIA NIM API key working (curl returns model list)
- [ ] Chainlit launching and echoing messages
- [ ] `.env` file with all keys (and `.gitignore`d)

If all six check, you're ready for Level 0 in the curriculum.

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| LLM + Embeddings | NVIDIA NIM (OpenAI-compatible, via [build.nvidia.com](https://build.nvidia.com)) |
| Orchestration | LangGraph |
| Vector store | PostgreSQL + pgvector |
| Frontend | Chainlit |
| Data source | [NPS API](https://www.nps.gov/subjects/developer/api-documentation.htm) |

## Full curriculum

Read the complete curriculum with learning objectives, NPS API mapping, evaluation guidance, and weekly pacing: **[genai_curriculum.md](genai_curriculum.md)**

## Who this is for

Engineers or technical analysts joining an AI platform team. Comfortable with Python, no prior ML or LLM experience required. Everything else is taught in order.

## License

[MIT](LICENSE)
