# AI Coding Assistant Playbook

Learners are expected to use Codex, Claude Code, Copilot, Cursor, or a similar AI coding assistant while working through this curriculum.

That is part of the course design. The point is not to type every line from memory. The point is to learn how GenAI systems are shaped, inspected, tested, and improved.

## The Rule

The assistant can help write code. The learner owns the intent, review, and verification.

Good use:

- Ask the assistant to inspect existing files before changing anything
- Ask for one small change at a time
- Ask it to explain the code it drafted
- Ask it to add a smoke test or eval
- Run the demo yourself and inspect the output

Risky use:

- Asking for a whole application without constraints
- Accepting code you cannot explain
- Pasting API keys into chat
- Skipping verification because the assistant sounded confident
- Letting the assistant introduce new frameworks before the curriculum calls for them

## The Build Loop

Use this loop at every level:

```text
Orient -> Ask -> Inspect -> Run -> Evaluate -> Explain
```

### 1. Orient

Ask the assistant to read the relevant files and summarize the current implementation.

Prompt:

```text
Inspect this repo and explain the Level 0 demo. Tell me which files are involved, where the NPS API call happens, and what command I should run. Do not edit files yet.
```

### 2. Ask

Ask for a narrow, observable change.

Prompt:

```text
Modify the Level 0 Chainlit demo so it also displays weatherInfo from the NPS park response. Keep the change small and follow the existing style.
```

### 3. Inspect

Review what changed before running it.

Prompt:

```text
Explain the diff you just made in plain English. What changed? What could break? What should I run to verify it?
```

### 4. Run

Run the exact command from the docs.

Prompt:

```text
I ran the command and got this error. Diagnose it from the traceback, then make the smallest fix.
```

### 5. Evaluate

Ask for a basic check.

Prompt:

```text
Add a tiny smoke eval for this level. It should be simple enough for a beginner to read and should fail clearly when the output is wrong.
```

### 6. Explain

Close the loop by explaining the system back.

Prompt:

```text
Quiz me on this level. Ask me five short questions that check whether I understand the API call, the environment variables, and the verification command.
```

## Prompt Cards By Level

### Level 0: API To UI

```text
Help me build Level 0. I want a minimal Python demo that calls the NPS /parks endpoint with a parkCode, reads NPS_API_KEY from .env, and prints the park name, states, description, and weatherInfo. Keep it beginner-readable.
```

```text
Now wrap the Level 0 API call in Chainlit. The user should type a park code like yell, acad, or grca and see the park summary in chat. Do not add an LLM yet.
```

### Level 1: One LLM Call

```text
Help me build Level 1. Use the existing NPS fetch function to get park description and weatherInfo, then make one chat completion call through the OpenAI-compatible client. Support the configured provider from .env. Add modes for summarize, rewrite, classify, and extract.
```

```text
Review the Level 1 prompts. Make them more grounded: the model should only use the provided source text, avoid invented facts, and say when there is not enough information.
```

### Level 2: Structured Output

```text
Design a Pydantic schema for extracting visitor risks, logistics, open questions, confidence, and evidence from NPS alert or park text. Then update the demo to validate the model output against the schema.
```

### Level 3: Ingestion

```text
Help me design an ingestion script for NPS parks, alerts, campgrounds, visitor centers, and articles. Separate raw API records, normalized documents, chunks, metadata, and embeddings. Do not build retrieval yet.
```

### Level 4: Retrieval

```text
Help me build a basic retrieval demo over the ingested NPS chunks. Include metadata filters for park_code and content_type, return top results, and preserve source URLs for citations.
```

### Level 5: RAG Orchestration

```text
Help me add a simple routing layer before retrieval. The router should classify whether the user needs direct answer, park lookup, safety/alerts, comparison, or insufficient information.
```

### Level 6A: ReAct Agent

```text
Help me turn live NPS API calls into explicit tools: get_park_details, get_alerts, get_campgrounds, and search_documents. Build a constrained ReAct agent with a max tool-call limit.
```

### Level 6B: Planner-Executor

```text
Help me build a planner-executor workflow for a weekend park readiness report. The planner should propose steps, pause for human approval, then the executor should call known tools in order.
```

### Level 7: Multi-Agent

```text
Help me split the workflow into specialized subagents: structured data, retrieval research, risk/safety review, and final report synthesis. Define each subagent's input and output contract before writing code.
```

### Level 8: Production Review

```text
Review this Field Guide Copilot like a production AI system. Identify risks around data freshness, citations, prompt injection, access control, observability, eval coverage, and graceful degradation.
```

## What Learners Should Record

At the end of each level, write a short note:

```text
What I built:
What API/model/tool was used:
What I asked the coding assistant:
What changed:
How I verified it:
What I still do not fully understand:
```

This note is more important than a perfect implementation. It shows whether the learner understands the system they just built.

## Spoiler / Rescue Prompts

If you are stuck after a real attempt, use [spoiler_full_build_prompts.md](spoiler_full_build_prompts.md). Those prompts ask Codex or Claude Code to draft a whole level.

They are intentionally not the main path. Use them for recovery, catch-up, or comparison after you have tried the normal build loop.
