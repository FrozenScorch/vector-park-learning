# GenAI Implementation Curriculum: National Parks Field Guide

## What this is

A hands-on curriculum that teaches how GenAI systems are built, from single LLM calls to multi-agent workflows. Learners build one system — a National Parks Field Guide assistant — over 8 weeks, using public National Park Service data.

The theme is parks. The point is not parks. The point is learning how structured and unstructured data become reliable AI workflows.

```text
setup → single inference → document understanding → ingestion substrate → retrieval mechanics → RAG routing → ReAct agent → planner-executor workflow → multi-agent workflow → production review
```

## Who this is for

Business analysts and technical analysts joining an AI or data team. You should be comfortable reading basic Python, but you do not need prior ML or LLM experience. Everything else is taught in order.

The preferred format is self-paced: learners run a functional demo first, then read the explanation, then make a small change and run a lightweight eval.

## How this curriculum is taught

This is an AI-assisted build curriculum. Learners are expected to use Codex, Claude Code, Copilot, Cursor, or a similar coding assistant while they build.

The learning loop is:

```text
Orient → Ask → Inspect → Run → Evaluate → Explain
```

The assistant can draft code, explain errors, and suggest tests. The learner owns the intent, reviews the diff, runs the demo, and explains what happened. See [docs/ai_coding_assistant_playbook.md](docs/ai_coding_assistant_playbook.md) for reusable prompt cards.

## 101 / 201 / 301 track structure

The numbered levels form three learning tracks:

| Track | Levels | What changes in the system |
|---|---:|---|
| Field Guide 101 | 0–2 | One NPS record becomes useful output through API calls, prompts, and schemas |
| Field Guide 201 | 3–5 | Many NPS endpoints become a searchable, cited knowledge system |
| Field Guide 301 | 6–8 | Live NPS APIs become tools inside controlled agent and workflow patterns |

See [docs/learning_tracks.md](docs/learning_tracks.md) for the full track map.

This follows the useful shape of [langchain-ai/langgraph-101](https://github.com/langchain-ai/langgraph-101): notebooks for guided 101/201 learning and standalone code for runnable agents. Vector Park Learning uses the same idea, but keeps the NPS Field Guide assistant as the single through-line.

## Notebook guidance

Use notebooks as companion walkthroughs, not as the only implementation.

- `levels/` should contain the runnable source-of-truth demos.
- `evals/` should contain smoke checks and regression checks.
- `notebooks/` should explain the concepts, call into `levels/`, show outputs, and ask checkpoint questions.
- `docs/` should hold setup, curriculum, and Codex/Claude prompt guidance.

This lets business analysts learn in a notebook-friendly format while still practicing real repo-based development with Codex or Claude Code. See [docs/notebook_strategy.md](docs/notebook_strategy.md).

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.11+ | Ecosystem fit for LangChain/LangGraph |
| Orchestration | LangGraph | Graph-based agent workflows with explicit state |
| Vector store | PostgreSQL + pgvector | Practical database for vector search, keyword search, and metadata filters |
| LLM + Embeddings | OpenAI-compatible providers: NVIDIA NIM, DeepSeek, Ollama/local, or custom endpoints | Lets learners use a hosted key or local inference without changing the demo code |
| Frontend | Chainlit | Pre-built chat UI, Python-native, see below |
| Data source | [NPS API](https://www.nps.gov/subjects/developer/api-documentation.htm) | Free, public, rich structured + unstructured data |

## The data source

The [National Park Service API](https://developer.nps.gov/api/v1/) is the data source for this curriculum. It provides both structured data (park codes, coordinates, fee amounts, activity categories) and unstructured data (park descriptions, alert text, article bodies, tour narratives). That mix makes it a useful stand-in for real workplace data.

The NPS API is the example that carries the course:

- A single `/parks` response teaches API plumbing.
- Descriptions and weather notes teach prompt design.
- Alerts and campground text teach structured extraction.
- Multiple endpoints teach ingestion, chunking, metadata, and retrieval.
- Live alerts, campgrounds, visitor centers, and weather become agent tools.
- A trip-readiness report becomes the planner-executor workflow.

### NPS API endpoint inventory

| Endpoint | Data type | What it returns |
|---|---|---|
| `/parks` | structured + unstructured | Location, contact, hours, fees, descriptions, photos, activities, topics |
| `/alerts` | structured + unstructured | Hazard/closure/caution announcements per park |
| `/campgrounds` | structured + unstructured | Location, fees, hours, amenities, accessibility, descriptions |
| `/visitorcenters` | structured + unstructured | Location, hours, services, descriptions |
| `/events` | structured + unstructured | Date, time, fee, description of park events |
| `/thingstodo` | mostly unstructured | Recommended activities with descriptions, duration, season |
| `/articles` | unstructured | Titles, images, descriptions about NPS features |
| `/newsreleases` | unstructured | Title, abstract, link to park news |
| `/places` | structured + unstructured | Named places within parks with descriptions |
| `/tours` | unstructured | Tours with stops at places, campgrounds, visitor centers |
| `/activities` | structured | Activity categories (hiking, stargazing, etc.) |
| `/activities/parks` | structured | Which parks map to which activities |
| `/topics` | structured | Topic categories (Civil War, wildlife, etc.) |
| `/topics/parks` | structured | Which parks map to which topics |
| `/amenities` | structured | Amenity types available |
| `/amenities/parksplaces` | structured | Places with specific amenities |
| `/amenities/parksvisitorcenters` | structured | Visitor centers with specific amenities |
| `/feespasses` | structured | Entrance fees and passes |
| `/parkinglots` | structured | Parking lot info |
| `/passportstamplocations` | structured | Passport stamp locations |
| `/multimedia/audio` | media | Audio files |
| `/multimedia/videos` | media | Videos |
| `/multimedia/galleries` | media | Photo galleries |
| `/webcams` | media | Live webcams |
| `/lessonplans` | unstructured | Educational lesson plans |
| `/mapdata/parkboundaries` | geospatial | GeoJSON park boundaries |

Common query parameters across all endpoints: `parkCode`, `stateCode`, `limit`, `start` (0-based), `q`, `fields`.

Not every endpoint is used at every level. The curriculum introduces them progressively.

## The starter UI

Learners should not spend time building a frontend. This curriculum uses a **Chainlit chat interface** that learners wire their backend into at each level.

Why Chainlit:

- Pure Python — no JavaScript build step
- Native LangGraph integration
- Handles streaming responses out of the box
- Manages conversation history (solves multi-turn)
- Displays intermediate agent steps (invaluable for debugging Levels 5–7)
- Open source

The UI stays roughly the same throughout. What changes at each level is what happens behind the chat input — the underlying APIs, retrieval strategies, and orchestration logic. This mirrors how real products work: the interface is stable, the capabilities grow.

### How the UI maps to each level

| Level | Chainlit interaction model |
|---|---|
| 0 | Type a park code, see raw NPS API response — proof that plumbing works |
| 1 | Type or paste text, get back a summary / rewrite / classification / extraction |
| 2 | Send a park description or alert, get back structured JSON |
| 3 | **Not through Chainlit** — ingestion runs as a backend script from the terminal |
| 4 | Ask questions about parks, get cited answers from the vector store |
| 5 | Same as 4, but the system shows which retrieval path it chose |
| 6A | Ask tasks, watch the agent reason through tool calls in the intermediate steps panel |
| 6B | Request a report, review the proposed plan, approve it, receive the final output |
| 7 | Same as 6B, but multiple agents appear in the step trace |
| 8 | Discussion-level — production readiness exercises |

---

## Level 0 — Setup and First API Call

### Objective

Get the development environment running and make the first NPS API call. Zero AI. Just plumbing.

### NPS API endpoints used

`/parks` — fetch a single park to verify connectivity.

### Setup steps

Follow the quick-start setup instructions in the [README](README.md). By the end of Level 0 you should have:

1. **Python 3.11+** with a virtual environment
2. **NPS API key** - free at [nps.gov/subjects/developer](https://www.nps.gov/subjects/developer/get-started.htm)
3. **Python dependencies** - `pip install -r requirements.txt`
4. **`.env` file** with `NPS_API_KEY`
5. **Chainlit** installed and ready to launch

Docker, PostgreSQL, pgvector, embeddings, and LangGraph are intentionally not required yet. They start when ingestion and retrieval become the lesson.

Use an AI coding assistant (Claude Code, Copilot, Codex, Cursor, etc.) to help verify each step.

### Functional demo

Run the CLI demo:

```bash
python levels/level0_first_nps_call.py --park-code yell
```

Run the Chainlit demo:

```bash
chainlit run levels/level0_chainlit_nps.py
```

Open [http://localhost:8000](http://localhost:8000), then type a park code such as `yell`, `acad`, or `grca`.

### AI assistant task

Use Codex or Claude Code to make one small change:

```text
Inspect the Level 0 files. Then modify the Chainlit demo so it also displays one more NPS field, such as weatherInfo, directionsInfo, or activities. Keep the code beginner-readable and tell me what command to run.
```

### Project structure

```text
field-guide-copilot/
├── app.py                  # Chainlit entry point
├── backend/
│   ├── chains/             # LangGraph graphs per level
│   ├── ingestion/          # Level 3 pipeline
│   ├── retrieval/          # Level 4 retrieval strategies
│   ├── agents/             # Level 6+ agent definitions
│   ├── tools/              # Tool functions for agents
│   └── evals/              # Eval scripts and golden datasets
├── data/                   # Raw + processed NPS data
├── prompts/                # Prompt templates
├── tests/                  # Unit and integration tests
└── docs/                   # Your notes and diagrams
```

### Exercise

Modify the Chainlit handler so it also displays one additional field from the NPS response, such as `weatherInfo`, `directionsInfo`, or `activities`. No LLM involved. Just API to UI.

### Done means

The CLI demo returns real NPS data. The Chainlit app launches. You can type a park code and see real park information come back. Learners understand where the API key lives, what an HTTP request returns, and how the UI is connected to backend code.

---

## Level 1 — Generic Inference

### Objective

Build a single-call LLM feature. No RAG. No vector DB. No agents.

### NPS API endpoints used

**`/parks`** — fetch 3–5 parks. Grab the `description` and `weatherInfo` fields. That's your input text.

### What learners build

The Chainlit app now routes user input to an LLM. Learners run and modify four inference modes over real park text:

- Summarize Yellowstone's overview for a first-time visitor.
- Rewrite a dense Denali weather warning for a family audience.
- Classify a visitor question into categories: trip planning, safety/alerts, camping, hiking, accessibility, fees/logistics, not enough information.
- Extract action items from a park operations-style note.

The NPS API is just the data source here. Learners reuse the Level 0 NPS client, grab the text fields, and pass them to the LLM.

### Functional demo

Run one mode from the terminal:

```bash
python levels/level1_generic_inference.py --mode summarize --park-code yell
```

Run the Chainlit demo:

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

Then run the smoke eval:

```bash
python evals/level1_smoke_eval.py
```

### AI assistant task

Use Codex or Claude Code to improve one mode:

```text
Inspect the Level 1 inference demo. Improve the summarize prompt so it is more useful for a first-time park visitor, but make sure it stays grounded in the source text. Then explain the diff and tell me which command verifies the change.
```

### What learners should understand

- Prompt framing and system vs. user instructions
- Temperature and output length
- Basic hallucination risks
- Streaming responses — why and how (Chainlit handles this, but learners should understand SSE)
- Why a chatbot response is not automatically workflow-ready
- The difference between "the model sounds right" and "the output is correct"

### How to evaluate

Evaluation starts here, not at Level 8. At this level, keep it simple:

- Build a small golden dataset: 10–15 input texts with expected outputs (or expected properties of outputs).
- Write assertions: does the classification output one of the valid categories? Does the summary stay under the target length? Does the extraction produce valid JSON?
- Run the dataset through your pipeline. Track pass/fail. This is your first eval harness.

The habit matters more than the framework. If learners build evals from Level 1, they will never ship something they cannot measure.

### Done means

The Chainlit app can take raw text and return a useful, constrained answer for at least 4 inference modes: summary, rewrite, classification, action-item extraction. A basic eval harness exists and passes.

---

## Level 2 — Document Understanding and Structured Extraction

### Objective

Move from "the model wrote text" to "the model produced usable structured data."

This is **not ingestion yet**. This level works on one document or pasted text at a time. No embeddings, no vector DB.

### NPS API endpoints used

**`/parks`**, **`/alerts`**, **`/campgrounds`**, **`/visitorcenters`**, **`/events`**

Now the inputs get more varied. Learners fetch real data from each endpoint and run extraction on the unstructured text fields. The key insight: each NPS endpoint returns a mix of structured fields (lat/lon, parkCode, fees as numbers) and unstructured fields (description, weatherInfo, directionsInfo). The LLM's job is to extract structure from the unstructured parts, not duplicate what the API already gives you.

### Example park tasks

Input: park description, alert text, campground description, visitor-center page, event description.

Output:

```json
{
  "summary": "string",
  "key_facts": ["string"],
  "visitor_risks": [
    {
      "risk": "string",
      "severity": "low | medium | high | unknown",
      "evidence": "string"
    }
  ],
  "logistics": {
    "fees": ["string"],
    "locations": ["string"],
    "hours": ["string"],
    "reservation_notes": ["string"]
  },
  "open_questions": ["string"],
  "confidence": "low | medium | high"
}
```

### What learners should understand

- Structured output schemas and JSON mode
- Validation (schema validation, not just "looks right")
- Unknown/null handling — the model must say "I don't know" as structured data
- Confidence fields and evidence snippets
- Unsupported claims vs. supported claims
- The difference between summarization and extraction
- Why structured extraction is a bridge to workflows

### How to evaluate

- Schema validation: does every output conform to the JSON schema? Use Pydantic or jsonschema.
- Fact-checking: given a source document with known facts, does the extraction include them? Does it invent any?
- Build 5–10 test cases with known-good extractions. Automate the comparison.

### Done means

Given a single text input, the system produces valid JSON, does not invent missing facts, and handles unknowns gracefully. Schema validation passes on all test cases.

---

## Level 3 — RAG Ingestion Substrate

### Objective

Build the document ingestion pipeline. This is where learners build the substrate that makes RAG possible.

**This level runs from the terminal, not through Chainlit.** Ingestion is a backend pipeline. You would not type "ingest 400 parks" into a chat window.

Before starting Level 3, install the full dependency set and start pgvector:

```bash
pip install -r requirements-full.txt
```

Then follow the Docker instructions in the [README](README.md#later-setup-for-level-3).

### NPS API endpoints used

**`/parks`**, **`/alerts`**, **`/campgrounds`**, **`/visitorcenters`**, **`/events`**, **`/thingstodo`**, **`/articles`**, **`/newsreleases`**, **`/places`**, **`/tours`**

This is the big fetch. Learners consume the bulk of the NPS API and load it into pgvector. The structured endpoints (`/activities`, `/topics`, `/activities/parks`, `/topics/parks`) become categorical metadata for filtering — they are not embedded.

### Understanding embeddings

Before building the pipeline, learners must understand what embeddings are and why they work.

**Core concepts:**

- An embedding is a dense vector (list of numbers) that captures the semantic meaning of text. Similar meanings produce similar vectors.
- Cosine similarity measures how close two vectors are. High similarity = semantically related.
- Embedding models are separate from LLMs. They are trained specifically for this task.
- Dimensionality matters: higher dimensions capture more nuance but cost more storage and compute. Common ranges: 384, 768, 1024, 1536.
- Embeddings are only as good as the text you feed them. Garbage in, garbage out — which is why chunking and preprocessing matter.

**Choosing an embedding model:**

Consider these factors:

- Dimension size vs. retrieval quality trade-off
- Whether the model supports instructions/task prefixes (e.g., "search_document:" vs. "search_query:")
- Open-source vs. API-hosted (cost, latency, data residency)
- Benchmark performance on retrieval tasks (MTEB leaderboard)
- Whether the model fits your deployment constraints

For this curriculum, pick one embedding backend and keep it consistent. A hosted option is NVIDIA NIM via `build.nvidia.com`, with models such as `nvidia/nv-embedqa-e5-v5` and `nvidia/nv-embed-v2`. A local option can be introduced later if learners have the hardware and patience for it. The important lesson is consistency: switching embedding models mid-project means re-embedding everything.

### Pipeline

```text
fetch/load → parse → normalize → deduplicate → chunk → enrich metadata → embed selected text → store documents/chunks → run ingestion evals
```

### What to vectorize

Do **not** blindly vectorize every raw JSON field.

Vectorize text that helps semantic retrieval:

- park full name and description
- designation
- activities/topics as text
- alert title + description
- article title + body
- campground and visitor center descriptions
- accessibility notes
- fees/reservation notes
- safety/hazard language
- thingstodo descriptions
- tour narratives
- place descriptions
- generated searchable summary if useful

Do **not** primarily rely on embeddings for:

- latitude/longitude, state codes, park codes
- fee amounts, dates, exact names, IDs, URLs
- event start/end times, boolean fields
- activity and topic category IDs

Those belong in metadata or structured filters.

### Metadata to preserve

Every chunk should include:

```json
{
  "document_id": "string",
  "chunk_id": "string",
  "source_name": "National Park Service",
  "source_url": "string",
  "retrieved_at": "YYYY-MM-DD",
  "content_type": "park | alert | campground | visitor_center | event | article | thingstodo | place | tour | news_release",
  "park_code": "string | null",
  "park_name": "string | null",
  "states": ["string"],
  "activities": ["string"],
  "topics": ["string"],
  "lat": "number | null",
  "lon": "number | null",
  "date_start": "string | null",
  "date_end": "string | null",
  "alert_category": "string | null",
  "page_or_section": "string | null"
}
```

### Chunking strategies to teach

Start simple, then compare:

1. Fixed-size chunks with overlap
2. Paragraph-aware chunks
3. Heading/section-aware chunks
4. Record-aware chunks for JSON/API objects
5. Parent-child chunks: child chunk for retrieval, parent document for final context
6. Summary chunk + source chunks: summary helps retrieval, source chunks preserve evidence

### Introducing observability

Start logging now, not at Level 8. At minimum:

- Log every embedding call: input text length, model used, latency
- Log chunk counts and metadata completeness per ingestion run
- Log deduplication decisions
- Store ingestion run metadata (timestamp, source count, chunk count, errors)

Use Python logging or a simple structured logger. The point is to build the habit. At later levels this expands into full tracing.

### How to evaluate

- **Chunk quality**: manually inspect 20+ chunks. Are they coherent? Do they split mid-sentence? Do parent-child relationships hold?
- **Metadata completeness**: what percentage of chunks have all expected metadata fields populated?
- **Embedding sanity check**: pick 5 known-similar documents (e.g., campground descriptions from parks in the same state). Are their embeddings close (cosine similarity > 0.8)? Pick 5 known-unrelated documents. Are they distant?
- **Deduplication**: ingest the same data twice. Does the system handle it?
- **Retrieval sanity check**: run 10 natural-language queries against the vector store. Do the top-5 results make sense? This is a preview of Level 4.

### Done means

The system can ingest a small corpus and pass tests for: chunks created, metadata preserved, duplicate handling, semantic search sanity check, metadata filter sanity check, source traceability. Observability logs exist and are useful.

---

## Level 4 — Retrieval Mechanics and Basic RAG

### Objective

Build cited Q&A over the ingested corpus, while teaching retrieval mechanics. This is still not a general agent. It is a retrieval + answer pipeline.

**Back to Chainlit.** Users ask questions in chat, the system retrieves from the vector store and streams a cited answer back.

### NPS API endpoints used

**None directly** — this level works entirely against the ingested corpus from Level 3.

### Retrieval modes to include

Minimum:

1. Vector search (semantic similarity)
2. Keyword search (BM25 or PostgreSQL full-text search)
3. Metadata filtering (exact match on structured fields)
4. Hybrid search (combine vector + keyword + filters)
5. Multi-query / RAG fusion
6. Optional reranking

### RAG Fusion

User asks:

> Which Utah parks are good for hiking but may have safety alerts this weekend?

System generates several retrieval queries:

```text
Utah national parks hiking
current safety alerts Utah parks
campgrounds and hiking national parks Utah
visitor warnings trail closures Utah national parks
```

Then it retrieves for each query, merges/ranks results, optionally reranks, and passes the best evidence to the answer step.

### Hybrid search

Use hybrid retrieval when the query needs both meaning and exact filters. The NPS data makes this obvious:

- semantic: "good for a quiet beginner camping trip"
- exact metadata: `stateCode = UT`, `activities contains Camping`
- date/event filter: this weekend
- content type filter: `alert` or `campground`

### Multi-turn conversation

This is where conversation memory enters the system.

The Chainlit frontend maintains a conversation thread. The backend must now handle follow-up questions:

- User: "Tell me about Zion." → retrieval + answer
- User: "What about camping there?" → the system must understand "there" = Zion

Approaches to teach:

1. **Conversation buffer**: pass the last N messages as context to the LLM alongside retrieved documents. Simple, effective, and the right starting point.
2. **Query rewriting**: use the LLM to rewrite the follow-up as a standalone query before retrieval. "What about camping there?" → "Camping options at Zion National Park."
3. **Conversation summary**: for longer conversations, summarize earlier turns instead of passing them raw.

Start with approach 1, then add approach 2 when learners see why naive follow-ups retrieve poorly.

### Output schema

```json
{
  "answer": "string",
  "citations": [
    {
      "source_url": "string",
      "document_id": "string",
      "chunk_id": "string",
      "reason_used": "string"
    }
  ],
  "retrieval_debug": {
    "query_type": "vector | keyword | hybrid | rag_fusion",
    "filters_used": {},
    "top_k": 5,
    "rewritten_query": "string | null"
  },
  "confidence": "low | medium | high",
  "missing_information": ["string"]
}
```

### How to evaluate

- **Retrieval quality**: build a golden dataset of 20+ questions with known-relevant document IDs. Measure precision@5 and recall@5. How often is the correct document in the top 5?
- **Answer quality**: does the answer use only retrieved evidence? Does it cite correctly? Does it refuse when evidence is insufficient?
- **Retrieval strategy comparison**: run the same queries through vector-only, keyword-only, and hybrid. Compare results. This teaches learners *why* hybrid exists, not just *that* it exists.
- **Multi-turn**: test 5+ conversation threads where follow-up questions reference prior context. Does the system resolve references correctly?

### Done means

The system can answer with citations, refuse insufficient-evidence questions, explain which retrieval strategy was used, and handle multi-turn follow-ups. Retrieval evals exist and show measurable quality.

---

## Level 5 — RAG Orchestration / Controlled Agentic RAG

### Objective

Build a LangGraph graph that chooses the right retrieval and answer path. This is "agentic-ish RAG," but it should **not** be a free-form ReAct loop yet.

### NPS API endpoints used

**None directly** — still works against the ingested corpus.

The NPS data's variety of content types (parks, alerts, campgrounds, articles, tours, thingstodo) is what makes routing non-trivial. Different intents need different content types, and the orchestrator must choose.

### Why this is not Level 6

Level 5 is controlled orchestration:

```text
classify intent → choose retrieval plan → retrieve → review evidence → synthesize → return
```

The model may help classify or plan retrieval, but it is not repeatedly deciding arbitrary tool calls.

### Supported intents

- Direct answer with no retrieval
- Answer from documents
- Summarize a specific document
- Compare parks
- Extract structured fields
- Generate a table
- Ask clarifying question
- Insufficient evidence / refuse
- Route to workflow agent if the task needs multiple tools

### Example request

> Compare Yosemite, Zion, and Acadia for a family camping trip and include any safety issues.

Orchestrator behavior:

1. Classify as compare + safety/logistics
2. Use metadata filters for park codes
3. Retrieve descriptions, campgrounds, alerts
4. Review evidence for missing facts
5. Synthesize table with citations
6. List missing info

### Chainlit interaction

In the chat UI, Chainlit's intermediate steps panel shows the orchestration path: which intent was classified, which retrieval strategy was selected, how many chunks were retrieved. Learners should see the routing decision, not just the final answer.

### LangGraph implementation note

This is where LangGraph's value becomes concrete. The orchestration graph should have explicit nodes for intent classification, retrieval planning, retrieval execution, evidence review, and synthesis. Edges between nodes should be conditional on the classified intent. This is not a linear chain — it is a graph with branching paths.

Learners should be able to visualize their graph and explain why each node exists.

### How to evaluate

- **Routing accuracy**: given 20+ queries with known intents, does the orchestrator classify and route correctly?
- **Path explanation**: can the system explain which path it took and why?
- **Comparison with Level 4**: run the same queries through Level 4 (basic RAG) and Level 5. Where does orchestration improve results? Where doesn't it matter?

### Done means

The system does not retrieve blindly. It chooses a path and can explain its path. Routing evals show measurable improvement over naive retrieval.

---

## Level 6A — ReAct Single Agent

### Objective

Introduce a narrow tool-using agent. The agent can reason step-by-step and choose tools, but the scope is constrained.

### NPS API endpoints used

**`/parks`**, **`/alerts`**, **`/campgrounds`**, **`/visitorcenters`** — **live API calls as tools**

This is where NPS API calls re-enter the system as real-time tools alongside the vector store. The agent decides: do I search my ingested corpus, or do I call the live API for fresh data? Alerts are the clearest case — the ingested alerts might be stale, but `GET /alerts?parkCode=yell` gives you what's active right now.

### What learners should understand

This is where function calling / tool use becomes explicit.

- The LLM does not "run" tools. It decides which tool to call and with what arguments. Your code runs the tool and returns the result.
- ReAct = Reason + Act. The agent thinks about what to do, acts (calls a tool), observes the result, and decides the next step.
- This is a loop, and loops need exit conditions.
- Tool schemas must be explicit and well-documented — the LLM can only use tools it understands.

### Tools

The tool set maps directly to NPS API endpoints plus the vector store:

```python
search_documents(query, filters)      # vector store from Level 3
get_park_details(park_code)           # GET /parks?parkCode=X
get_alerts(park_code)                 # GET /alerts?parkCode=X
get_campgrounds(park_code)            # GET /campgrounds?parkCode=X
get_visitor_centers(park_code)        # GET /visitorcenters?parkCode=X
calculator(expression)                # simple math
draft_note(title, body)               # compose a visitor note
```

### Chainlit interaction

Chainlit's intermediate steps panel shows each tool call as the agent makes it: the reasoning, the tool invoked, the arguments, and the observation. This is the most visually informative level — learners watch the agent think.

### Example tasks

- "Find parks in Arizona with hiking and current alerts."
- "Look up campgrounds near Grand Canyon and summarize reservation concerns."
- "Search the docs for accessibility notes and draft a short visitor note."

### Hard constraints

- Max tool calls per turn (e.g., 8)
- Tool schemas are explicit
- No external writes without approval
- Final answer must cite tool evidence
- The agent must stop if evidence is insufficient

### How to evaluate

- **Task completion**: given 10 tasks with known answers, does the agent complete them correctly?
- **Tool efficiency**: how many tool calls does it take? Are there unnecessary calls?
- **Constraint adherence**: does it respect the max tool call limit? Does it stop when evidence is insufficient?
- **Failure modes**: give it a question no tool can answer. Does it fail gracefully?

### Done means

Learners understand ReAct as tool selection plus observation loops, not independent decision-making without limits. The agent completes tasks within constraints and fails gracefully.

---

## Level 6B — Planner-Executor Workflow Agent with HITL

### Objective

Build a more realistic workflow agent that prepares a preset report by coordinating multiple data sources. This is the missing level between a simple ReAct agent and a true multi-agent system.

### NPS API endpoints used

**`/parks`**, **`/alerts`**, **`/campgrounds`**, **`/visitorcenters`**, **`/thingstodo`**, **`/events`** + **external [NWS Weather API](https://api.weather.gov)** (free, no key required)

The NWS API pairing is natural: the NPS `/parks` endpoint gives you lat/lon coordinates for every park, and the NWS API gives you weather forecasts at those coordinates. No separate API key needed.

### Pattern

```text
user request → planner creates workflow plan → human reviews/edits plan → executor runs fixed workflow steps → evidence reviewer checks completeness → final report generator
```

This is more reliable than letting a ReAct agent wander.

### Chainlit interaction

This is where HITL becomes tangible. The Chainlit UI shows the proposed plan as an intermediate step. The learner (acting as the human reviewer) can approve, edit, or reject the plan before execution continues. Chainlit's `ask_user` feature handles the interrupt.

### Workflow 1: Weekend Camping Trip Readiness Report

User request:

> Prepare me for a camping trip this weekend near Shenandoah. I care about hikes, campground availability, closures/alerts, weather, and what to pack.

Plan steps:

1. Resolve destination / candidate parks → `GET /parks?stateCode=VA`
2. Fetch park details → `GET /parks?parkCode=shen`
3. Fetch alerts → `GET /alerts?parkCode=shen`
4. Fetch campgrounds → `GET /campgrounds?parkCode=shen`
5. Fetch visitor centers or relevant facilities → `GET /visitorcenters?parkCode=shen`
6. Fetch things to do → `GET /thingstodo?parkCode=shen`
7. Fetch weather by coordinates → `GET api.weather.gov/points/{lat},{lon}/forecast`
8. Retrieve unstructured safety/trail/visitor docs → vector store search
9. Compile readiness report
10. Ask for human approval before finalizing

Output:

```json
{
  "trip_goal": "string",
  "destination_candidates": [],
  "recommended_option": "string",
  "weather_summary": "string",
  "alerts_and_closures": [],
  "campground_notes": [],
  "hiking_options": [],
  "packing_checklist": [],
  "risks": [],
  "missing_information": [],
  "citations": [],
  "human_review_required": true
}
```

### Workflow 2: Geographic Coverage Report

User request:

> Show which campgrounds and visitor centers are available within a rough geographic area, and summarize gaps.

Plan steps:

1. Parse geographic intent
2. Identify candidate parks by state/region → `GET /parks?stateCode=X`
3. Fetch campgrounds → `GET /campgrounds?stateCode=X`
4. Fetch visitor centers → `GET /visitorcenters?stateCode=X`
5. Compute distance/coverage if coordinates exist
6. Retrieve relevant descriptions → vector store search
7. Produce coverage table
8. Identify missing/low-confidence data

### HITL interrupt

Require human review at one or more points:

- After planner generates the proposed plan
- Before using external APIs above a threshold
- Before producing an itinerary as a recommendation
- Before drafting/sending anything
- When evidence is incomplete or conflicting

### How to evaluate

- **Plan quality**: given 5 requests, does the planner produce sensible, complete plans?
- **Execution fidelity**: does the executor follow the plan without skipping steps?
- **HITL integration**: does the system actually pause for human review at the right points?
- **Report completeness**: does the final report address all parts of the original request?

### Done means

Learners understand the planner-executor distinction: planner decides the steps, executor runs known tools/workflows, human can approve or edit the plan, final output is evidence-backed.

---

## Level 7 — Multi-Agent Orchestration

### Objective

Build a supervisor/planner that coordinates specialized agents. This should be introduced only after learners can explain why Level 6B is insufficient for certain tasks.

### NPS API endpoints used

**All of the above, distributed across subagents.** Each subagent owns a data domain:

| Subagent | NPS endpoints | Role |
|---|---|---|
| Research/Retrieval Agent | vector store (ingested corpus) | Semantic search over articles, descriptions, tours, places |
| Structured Data Agent | `/parks`, `/campgrounds`, `/visitorcenters`, `/events`, `/thingstodo`, `/amenities` | Live API calls with filters |
| Risk/Safety Reviewer Agent | `/alerts` + NWS weather API | Real-time safety assessment |
| Itinerary/Report Planner Agent | none directly — consumes other agents' outputs | Synthesis and planning |

The NPS API's breadth is what justifies multi-agent here — no single agent should own 10+ endpoints across fundamentally different concerns (safety vs. logistics vs. research).

### Recommended design

Use a planner-executor supervisor with ReAct-capable subagents.

```text
Supervisor Planner
  → Research/Retrieval Agent
  → Structured Data Agent
  → Risk/Safety Reviewer Agent
  → Itinerary/Report Planner Agent
  → Final Synthesizer
```

### Subagent roles

**Research/Retrieval Agent** — searches vector store and unstructured documents.

```json
{
  "evidence": [],
  "unanswered_questions": [],
  "confidence": "low | medium | high"
}
```

**Structured Data Agent** — calls structured NPS API endpoints and applies filters.

```json
{
  "records": [],
  "filters_used": {},
  "data_quality_notes": []
}
```

**Risk/Safety Reviewer Agent** — reviews `/alerts`, NWS weather, missing data, and overclaims.

```json
{
  "risks": [
    {
      "risk": "string",
      "severity": "low | medium | high",
      "evidence": "string",
      "mitigation": "string"
    }
  ],
  "must_include_disclaimers": []
}
```

**Itinerary/Report Planner Agent** — turns evidence into a structured visitor report.

```json
{
  "recommended_plan": [],
  "alternatives": [],
  "assumptions": [],
  "open_questions": []
}
```

**Final Synthesizer** — combines outputs, removes unsupported claims, and produces the final answer.

### Chainlit interaction

In the step trace, learners see which subagent the supervisor invoked, what each subagent returned, and how the synthesizer combined them. This is the most complex step trace in the curriculum.

### When this is justified

Use multi-agent only when the task has meaningfully different workstreams: structured data lookup, unstructured retrieval, safety/risk review, planning/synthesis, evidence checking.

Do not use multi-agent for simple Q&A.

### How to evaluate

- **Subagent contracts**: does each subagent return its specified output schema?
- **Supervisor routing**: does the supervisor invoke the right subagents for a given task?
- **Ablation**: remove one subagent. What breaks? If nothing breaks, that subagent shouldn't exist.
- **End-to-end comparison**: run the same complex queries through Level 6B (single planner-executor) and Level 7 (multi-agent). Where does multi-agent actually improve results?

### Done means

Learners can explain: why each agent exists, what each agent returns, what the shared state is, what the supervisor controls, where HITL belongs, what would break if an agent were removed.

---

## Level 8 — Production Thinking

### Objective

Transition from "it works on my laptop" to "it could run in production." This level is discussion-heavy but includes a concrete deliverable.

### NPS API as production case study

The NPS API teaches real production concerns directly:

- **Rate limits**: hourly limits per API key — what happens when you exceed them?
- **Data freshness**: alerts update every ~2 hours — what if an alert expired since last ingestion?
- **Pagination quirks**: 0-based `start` parameter, max 50 results per call
- **Optional fields**: images require `fields=images` — what if you forget?
- **Availability**: the API can go down — what does your system do?

### Topics

**Identity and access control:**
- OAuth difference: service acts as itself vs. app acts on behalf of a user
- User access scoping and data permissions
- Source-level access control — should the copilot see data the user can't?

**Security:**
- Prompt injection (direct and indirect) — demonstrate real examples
- Data exfiltration via tool calls
- Output filtering and guardrails

**Data integrity:**
- Stale data and alert freshness — what if an alert expired 2 hours ago?
- Embedding drift — what happens when you update the embedding model?
- Source-of-truth conflicts

**Reliability:**
- Rate limits and backpressure
- Failure handling — what happens when the LLM is down? When pgvector is slow?
- Timeout budgets for agent loops
- Graceful degradation

**Observability:**
- Request tracing end-to-end (expand from Level 3's basic logging)
- LLM call logging: prompt, completion, tokens, latency, model version
- Retrieval quality monitoring in production
- Agent step tracing and debugging
- Alerting on quality regressions

**Evaluation in production:**
- Evals are not a one-time thing. They run on every deploy.
- Regression tests: does a model upgrade break existing behavior?
- A/B testing retrieval strategies
- User feedback loops

### Practical exercise

Write a production readiness checklist for the Field Guide Copilot:

```text
Data provenance and freshness
Access controls and user scoping
Citation quality and traceability
Retrieval evals — automated, run on deploy
Agent tool call limits and timeout budgets
Human review points
Monitoring and alerting
Prompt injection mitigations
Known limitations — documented and communicated
Graceful degradation plan
```

### Done means

Learners produce a written production readiness document for their copilot. It should be specific to their implementation, not generic.

---

## Weekly sequence

### Week 1

- Level 0: setup and first API call
- Level 1: generic inference
- Level 2: document understanding / structured extraction
- Set up project structure, Chainlit UI, first eval harness

### Week 2

- Level 3: ingestion substrate
- Focus on embeddings, chunking, metadata, and what not to vectorize
- Introduce observability logging

### Week 3

- Level 4: retrieval mechanics and basic RAG
- Vector, keyword, hybrid, RAG fusion, citations
- Multi-turn conversation with query rewriting

### Week 4

- Level 5: RAG orchestration
- LangGraph graph with conditional routing
- Intent classification and retrieval planning

### Week 5

- Level 6A: ReAct single agent
- Tool use, function calling, constrained loops

### Week 6

- Level 6B: planner-executor workflow agent with HITL
- Plan → review → execute → verify pattern

### Week 7

- Level 7: multi-agent orchestration
- Supervisor, subagent contracts, shared state

### Week 8

- Level 8: production thinking
- Security, observability, evals in production
- Production readiness document

---

## Mentor note

The most important distinction to teach:

```text
RAG answers questions from retrieved evidence.
RAG orchestration chooses the retrieval/answer strategy.
A ReAct agent chooses tools in a loop.
A planner-executor agent creates a plan and executes controlled steps.
A multi-agent system splits specialized responsibilities across agents with contracts.
```

That ladder is the curriculum.

### On evals

If there is one meta-lesson that should persist after the curriculum ends, it is this: **you cannot improve what you do not measure.** Evals are not a Level 8 topic. They start at Level 1 and run through every level. Every "Done means" section includes evaluation criteria. Every level should produce a test suite that outlives the learning exercise.

### On the UI

The Chainlit frontend is support code, not the product. Learners should understand that the UI is intentionally stable so they can focus on the build path. In a real product, the frontend would evolve too — but that is a different curriculum.

---

## Further reading

These are not required. They are useful if a learner wants to go deeper on a specific topic.

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — the original RAG paper
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/) — graph-based agent orchestration
- [pgvector documentation](https://github.com/pgvector/pgvector) — vector similarity search in PostgreSQL
- [Chainlit documentation](https://docs.chainlit.io/) — the chat UI framework
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — embedding model benchmarks
- [NPS API documentation](https://www.nps.gov/subjects/developer/api-documentation.htm) — the data source
- [NWS Weather API](https://www.weather.gov/documentation/services-web-api) — weather forecasts by coordinates (used in Level 6B)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — the ReAct pattern
- [Anthropic's prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — prompt design fundamentals
