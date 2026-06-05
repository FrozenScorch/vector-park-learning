# Spoiler Prompts: Full Build Help

This file is intentionally a spoiler.

Use it only after you have tried the normal learning loop:

```text
Orient -> Ask -> Inspect -> Run -> Evaluate -> Explain
```

The goal of the curriculum is not to have Codex or Claude Code build everything while you watch. The goal is to learn how each GenAI system pattern works by making one scoped change at a time, reviewing the diff, running it, and explaining it back.

Use these prompts when:

- You are stuck after a real attempt
- Your environment is broken and you need help recovering
- You missed a session and need to catch up
- You want to compare your implementation against a complete draft

Do not paste real API keys into an AI coding assistant chat. Keep keys in `.env`.

## How To Use A Spoiler Prompt

1. Start a fresh Codex or Claude Code session in the repo root.
2. Paste one prompt, not the whole file.
3. Review every changed file before running it.
4. Run the verification command.
5. Write a short note explaining what was built.

## Level 0 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 0, "Setup and First NPS API Call."

Context:
- Audience is business analysts / technical analysts with basic Python.
- Keep code beginner-readable.
- Do not add an LLM.
- Read NPS_API_KEY from .env.
- Use the National Park Service /parks endpoint.
- Support a CLI demo and a Chainlit demo.

Tasks:
1. Inspect the repo first and summarize the relevant files.
2. Create or update a CLI script that accepts --park-code and prints:
   - park full name
   - park code
   - states
   - description
   - weatherInfo
3. Create or update a Chainlit app where the user types a park code and sees the same fields in chat.
4. Add clear error messages for missing NPS_API_KEY and unknown park codes.
5. Do not introduce new frameworks.
6. Tell me exactly which commands to run.

Verification:
- python levels/level0_first_nps_call.py --park-code yell
- chainlit run levels/level0_chainlit_nps.py

Before editing, explain your plan briefly. After editing, explain the diff and what I should look for in the output.
```

## Level 1 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 1, "Generic Inference."

Context:
- Level 0 already fetches NPS park data.
- Level 1 should make exactly one LLM call per user request.
- No RAG, no vector database, no agents, no LangGraph.
- The code should use the configured OpenAI-compatible provider from .env:
  - LLM_PROVIDER
  - LLM_MODEL
  - provider key such as NVIDIA_API_KEY, DEEPSEEK_API_KEY, or local Ollama config
- Keep code beginner-readable.

Tasks:
1. Inspect the existing Level 0 and Level 1 files.
2. Add or update a small provider helper for OpenAI-compatible chat completion backends.
3. Create or update a CLI script that supports:
   - --mode summarize
   - --mode rewrite
   - --mode classify
   - --mode extract
   - --park-code for fetching park description/weather text
   - --text for passing direct text
4. Create or update a Chainlit app with the same four modes.
5. Ground prompts in the provided source text. The model should not invent facts.
6. Add or update a tiny smoke eval that checks classification/extraction constraints.
7. Do not add RAG, tools, agents, or LangGraph yet.

Verification:
- python levels/level1_generic_inference.py --mode summarize --park-code yell
- python levels/level1_generic_inference.py --mode classify --text "Can I bring my dog on the trail?"
- python evals/level1_smoke_eval.py
- chainlit run levels/level1_chainlit_field_guide.py

Before editing, explain your plan briefly. After editing, explain the diff, likely failure points, and how to verify each mode.
```

## Level 2 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 2, "Document Understanding and Structured Extraction."

Context:
- Level 1 makes generic LLM calls.
- Level 2 should produce validated structured output from one document at a time.
- No ingestion, no embeddings, no vector database, no agents.
- Use NPS text from /parks, /alerts, /campgrounds, /visitorcenters, or /events.

Tasks:
1. Inspect the repo and summarize how Level 1 works.
2. Define a Pydantic schema for structured extraction with:
   - summary
   - key_facts
   - visitor_risks with severity and evidence
   - logistics
   - open_questions
   - confidence
3. Build a CLI demo that fetches or accepts text, calls the configured LLM, parses JSON, and validates with Pydantic.
4. Build a Chainlit demo where the learner can paste text or request an endpoint/park code.
5. Add examples where the model must use "unknown" rather than invent missing facts.
6. Add a small eval that validates schema conformance and one known extraction case.
7. Keep the implementation readable for technical analysts.

Verification:
- python levels/level2_structured_extraction.py --endpoint alerts --park-code yell
- python evals/level2_schema_eval.py
- chainlit run levels/level2_chainlit_extraction.py

Before editing, explain your plan briefly. After editing, explain the diff and how schema validation protects the workflow.
```

## Level 3 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 3, "RAG Ingestion Substrate."

Context:
- This level is backend-only and runs from the terminal.
- It should fetch multiple NPS endpoints and prepare documents/chunks for retrieval.
- This is ingestion, not chat.
- Use PostgreSQL + pgvector only after confirming setup instructions are present.

Tasks:
1. Inspect the repo and identify current Level 0-2 patterns.
2. Create an ingestion script that can fetch a small subset first:
   - /parks
   - /alerts
   - /campgrounds
   - /visitorcenters
   - /articles
3. Separate raw records, normalized documents, chunks, metadata, and embeddings.
4. Preserve source URL, park_code, content_type, retrieved_at, states, and title/name metadata.
5. Add logging for counts, failures, chunk sizes, and embedding calls.
6. Add a dry-run mode that does not call embeddings or write to the database.
7. Add an ingestion smoke eval for metadata completeness and duplicate handling.
8. Do not build the RAG answer chain yet.

Verification:
- python levels/level3_ingest.py --park-code yell --dry-run
- python evals/level3_ingestion_eval.py

Before editing, explain your plan briefly. After editing, explain what data is fetched, what gets embedded, and what stays as metadata.
```

## Level 4 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 4, "Retrieval Mechanics and Basic RAG."

Context:
- Level 3 created chunks and metadata.
- Level 4 answers questions from retrieved evidence.
- This is still not an agent.

Tasks:
1. Inspect the ingestion output and database schema.
2. Implement basic retrieval over stored chunks:
   - vector search
   - metadata filtering by park_code and content_type
   - optional keyword search if easy in PostgreSQL
3. Build a CLI question-answering demo that returns:
   - answer
   - cited source chunks
   - insufficient-evidence response when retrieval is weak
4. Build a Chainlit version that displays citations.
5. Add a small retrieval eval with 5 questions and expected citation/source properties.
6. Do not add agents or autonomous tool loops.

Verification:
- python levels/level4_basic_rag.py --question "What should I know before visiting Yellowstone?"
- python evals/level4_retrieval_eval.py
- chainlit run levels/level4_chainlit_rag.py

Before editing, explain your plan briefly. After editing, explain how retrieval, citations, and refusal work.
```

## Level 5 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 5, "RAG Orchestration."

Context:
- Level 4 retrieves and answers.
- Level 5 chooses the retrieval/answer path before answering.
- This is controlled orchestration, not a ReAct agent.

Tasks:
1. Inspect the Level 4 retrieval flow.
2. Add an intent router for:
   - direct answer
   - park lookup
   - safety/alerts
   - comparison
   - insufficient information
3. Add retrieval planning based on intent and metadata filters.
4. Add an evidence review step before synthesis.
5. Show the chosen path in CLI output and Chainlit.
6. Add routing evals with at least 10 example queries.
7. Do not allow arbitrary tool loops.

Verification:
- python levels/level5_rag_orchestration.py --question "Compare Zion and Acadia for family hiking."
- python evals/level5_routing_eval.py

Before editing, explain your plan briefly. After editing, explain why this is not yet an agent.
```

## Level 6A Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 6A, "ReAct Single Agent."

Context:
- Level 5 is controlled RAG orchestration.
- Level 6A introduces a narrow tool-using agent.
- Tools should be explicit and limited.

Tasks:
1. Inspect the existing RAG and NPS client code.
2. Define tools:
   - get_park_details
   - get_alerts
   - get_campgrounds
   - get_visitor_centers
   - search_documents
3. Build a constrained ReAct agent with:
   - max tool calls
   - clear tool schemas
   - cited final answers
   - graceful failure when tools cannot answer
4. Show intermediate tool steps in Chainlit if possible.
5. Add evals for task completion, tool efficiency, and failure handling.

Verification:
- python levels/level6a_react_agent.py --question "Find current alerts for Yellowstone and summarize visitor impact."
- python evals/level6a_agent_eval.py

Before editing, explain your plan briefly. After editing, explain the reason/action/observation loop and where the limits are enforced.
```

## Level 6B Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 6B, "Planner-Executor Workflow Agent with Human Review."

Context:
- This is not a free-form ReAct loop.
- The planner proposes steps.
- The human approves or edits.
- The executor runs known steps.

Tasks:
1. Inspect the Level 6A tools.
2. Build a weekend park readiness report workflow:
   - resolve park
   - fetch park details
   - fetch alerts
   - fetch campgrounds
   - fetch visitor centers
   - fetch things to do
   - fetch weather from NWS using park coordinates
   - retrieve supporting docs
   - compile report
3. Add a human approval pause before execution.
4. Add evidence review before final report generation.
5. Add evals for plan quality and execution fidelity.

Verification:
- python levels/level6b_planner_executor.py --request "Prepare me for a weekend camping trip near Shenandoah."
- python evals/level6b_workflow_eval.py

Before editing, explain your plan briefly. After editing, explain how planner-executor differs from ReAct.
```

## Level 7 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 7, "Multi-Agent Orchestration."

Context:
- Multi-agent is justified only when responsibilities are meaningfully different.
- Each subagent needs a contract.

Tasks:
1. Inspect the Level 6B workflow.
2. Define subagent contracts before coding:
   - structured data agent
   - retrieval research agent
   - risk/safety reviewer
   - itinerary/report planner
   - final synthesizer
3. Build a supervisor that delegates to subagents.
4. Keep shared state explicit.
5. Show subagent outputs in logs or Chainlit steps.
6. Add evals for routing, subagent schema conformance, and ablation.

Verification:
- python levels/level7_multi_agent.py --request "Compare Yosemite, Zion, and Acadia for a safe family camping trip."
- python evals/level7_multi_agent_eval.py

Before editing, explain your plan briefly. After editing, explain why each subagent exists and what would break if it were removed.
```

## Level 8 Full Build Prompt

```text
You are helping me with the Vector Park Learning curriculum.

Goal: build Level 8, "Production Thinking."

Context:
- This level is mostly review and documentation.
- It should produce a production readiness document specific to the learner's implementation.

Tasks:
1. Inspect the implementation across all levels.
2. Create a production readiness checklist covering:
   - data freshness
   - source citations
   - rate limits
   - API failures
   - model/provider failures
   - prompt injection
   - access control
   - observability
   - eval coverage
   - human review
   - graceful degradation
3. Identify concrete gaps in the current implementation.
4. Propose the next three hardening tasks.
5. Do not claim the system is production-ready if it is not.

Verification:
- Review the generated production readiness document.
- Confirm every risk is tied to a concrete part of the implementation.

Before editing, explain your plan briefly. After editing, summarize the highest-priority production risks.
```
