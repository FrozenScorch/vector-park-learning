# Vector Park Learning

A hands-on, 8-week curriculum that teaches how GenAI systems are built - from a single LLM call to multi-agent workflows - by building one system over public National Park Service data.

It focuses on practical distinctions: why RAG routing is not the same as an agent, why a planner-executor workflow is not the same as ReAct, and why evals start at Level 1, not Level 8.

## Start Here

If you are trying this repo for the first time, begin with [START_HERE.md](START_HERE.md).

## The ladder

```text
Level 0 - Setup & First NPS API Call
Level 1 - Generic Inference
Level 2 - Document Understanding & Structured Extraction
Level 3 - RAG Ingestion Substrate
Level 4 - Retrieval Mechanics & Basic RAG
Level 5 - RAG Orchestration
Level 6A - ReAct Single Agent
Level 6B - Planner-Executor Workflow Agent with HITL
Level 7 - Multi-Agent Orchestration
Level 8 - Production Thinking
```

## Learning Tracks

The curriculum can also be read as a 101/201/301 path:

| Track | Levels | Focus |
|---|---:|---|
| Field Guide 101 | 0-2 | API calls, first LLM calls, prompts, structured output |
| Field Guide 201 | 3-5 | Ingestion, embeddings, retrieval, cited RAG, routing |
| Field Guide 301 | 6-8 | Tools, ReAct agents, planner-executor workflows, multi-agent systems, production review |

See [docs/learning_tracks.md](docs/learning_tracks.md) for the full track map.

This structure is inspired by [langchain-ai/langgraph-101](https://github.com/langchain-ai/langgraph-101), which uses notebooks for 101/201 learning tracks and standalone agent implementations for runnable demos.

## Who this is for

Business analysts and technical analysts who are comfortable reading basic Python and want to understand how GenAI systems are built. No ML or LLM experience is required.

The curriculum is designed to be self-paced. Each level has a working demo first, then a small extension exercise, then an evaluation habit.

Notebooks are useful as companion walkthroughs, but the runnable source of truth should stay in `levels/` and `evals/`. See [docs/notebook_strategy.md](docs/notebook_strategy.md).

## How Learners Use AI Coding Assistants

Learners are expected to use Codex, Claude Code, Copilot, Cursor, or a similar coding assistant while building the demos.

That is intentional. The course teaches a modern build loop:

```text
Orient -> Ask -> Inspect -> Run -> Evaluate -> Explain
```

The learner owns the intent and verification. The assistant helps draft code, explain errors, and add checks. See [docs/ai_coding_assistant_playbook.md](docs/ai_coding_assistant_playbook.md) for prompt cards learners can reuse at each level.

## Prerequisites

- A Mac or Windows laptop
- Python 3.11 or higher
- A free National Park Service API key
- One LLM backend: NVIDIA NIM, DeepSeek API, local Ollama, or another OpenAI-compatible endpoint
- Codex, Claude Code, Copilot, Cursor, or another AI coding assistant
- Docker Desktop, starting at Level 3 when pgvector is introduced

## Quick Start For Levels 0 and 1

Levels 0 and 1 do not require Docker, PostgreSQL, pgvector, LangGraph, or embeddings. The goal is to get to functional demos quickly.

### 1. Clone and enter the repo

```bash
git clone https://github.com/FrozenScorch/vector-park-learning.git
cd vector-park-learning
```

### 2. Create a virtual environment

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Mac/Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
copy .env.example .env
```

Edit `.env` and add:

```bash
NPS_API_KEY=your-nps-key
LLM_PROVIDER=nvidia
LLM_MODEL=google/gemma-4-31b-it
NVIDIA_API_KEY=your-nvidia-api-key
```

Get keys:

- NPS API: [nps.gov/subjects/developer/get-started.htm](https://www.nps.gov/subjects/developer/get-started.htm)
- NVIDIA NIM: [build.nvidia.com](https://build.nvidia.com)
- DeepSeek API: [api-docs.deepseek.com](https://api-docs.deepseek.com/)

For DeepSeek, local Ollama, or a custom OpenAI-compatible endpoint, see [docs/model_providers.md](docs/model_providers.md).

## Run The First Demos

### Level 0: First NPS API call

CLI:

```bash
python levels/level0_first_nps_call.py --park-code yell
```

Chainlit UI:

```bash
chainlit run levels/level0_chainlit_nps.py
```

Open [http://localhost:8000](http://localhost:8000), then type a park code such as `yell`, `acad`, or `grca`.

### Level 1: Generic inference

CLI:

```bash
python levels/level1_generic_inference.py --mode summarize --park-code yell
python levels/level1_generic_inference.py --mode rewrite --park-code dena
python levels/level1_generic_inference.py --mode classify --text "Can I bring my dog on the trail?"
python levels/level1_generic_inference.py --mode extract --text "Call the visitor center, check road closures, and pack extra water."
```

Chainlit UI:

```bash
chainlit run levels/level1_chainlit_field_guide.py
```

Try:

```text
summarize yell
rewrite dena
classify Can I bring my dog on the trail?
extract Call the visitor center, check road closures, and pack extra water.
```

Optional smoke eval:

```bash
python evals/level1_smoke_eval.py
```

## Optional Notebook Walkthroughs

Install notebook dependencies:

```bash
pip install -r requirements-notebooks.txt
jupyter lab
```

Open:

- [notebooks/101/00_setup_and_api.ipynb](notebooks/101/00_setup_and_api.ipynb)
- [notebooks/101/01_generic_inference.ipynb](notebooks/101/01_generic_inference.ipynb)

The notebooks call into `levels/`; they do not replace the runnable demos.

## Later Setup For Level 3+

PostgreSQL, pgvector, LangChain, and LangGraph are introduced when the curriculum reaches ingestion, retrieval, and agents.

Install the full dependency set:

```bash
pip install -r requirements-full.txt
```

Then run PostgreSQL with the pgvector extension in Docker:

```bash
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=fieldguide \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Verify it:

```bash
docker exec -it pgvector psql -U postgres -d fieldguide -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| LLM + Embeddings | OpenAI-compatible providers: NVIDIA NIM, DeepSeek, Ollama/local, or custom |
| Orchestration | LangGraph |
| Vector store | PostgreSQL + pgvector |
| Frontend | Chainlit |
| Data source | [NPS API](https://www.nps.gov/subjects/developer/api-documentation.htm) |

## Full Curriculum

Read the complete curriculum with learning objectives, NPS API mapping, evaluation guidance, and weekly pacing: **[genai_curriculum.md](genai_curriculum.md)**

Supporting docs:

- [Start here](START_HERE.md)
- [Learning tracks](docs/learning_tracks.md)
- [AI coding assistant playbook](docs/ai_coding_assistant_playbook.md)
- [Model providers](docs/model_providers.md)
- [Notebook strategy](docs/notebook_strategy.md)
- [Spoiler full-build prompts](docs/spoiler_full_build_prompts.md)

## License

[MIT](LICENSE)
