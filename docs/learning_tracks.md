# Learning Tracks

Vector Park Learning is organized like a 101/201/301 path. Learners keep building the same National Parks Field Guide assistant, but each track teaches a different build pattern.

The track structure is inspired by [langchain-ai/langgraph-101](https://github.com/langchain-ai/langgraph-101): guided notebooks for learning tracks, plus standalone runnable implementations for demos.

## Track Map

| Track | Levels | What learners build | NPS API analogy | Main lesson |
|---|---:|---|---|---|
| Field Guide 101 | 0-2 | First API call, first LLM call, structured extraction | A park record becomes useful app output | Models are useful only when wrapped in clear inputs, prompts, schemas, and checks |
| Field Guide 201 | 3-5 | Ingestion, retrieval, cited answers, RAG routing | Many NPS endpoints become a searchable knowledge base | Grounding and retrieval strategy matter more than chat polish |
| Field Guide 301 | 6-8 | Tool-using agents, planner-executor workflows, multi-agent workflows, production review | Live NPS APIs become tools with different responsibilities | Agents are controlled workflows with tools, state, limits, evidence, and human review |

## Field Guide 101: Functional GenAI Demos

Audience: business analysts and technical analysts who can read basic Python but have no prior GenAI experience.

Learners should finish 101 able to explain:

- What an API request is
- What goes into an LLM call
- Why prompt instructions shape output
- Why structured output is different from a nice paragraph
- Why evals start early
- How to use Codex or Claude Code to draft code without blindly trusting it

Levels:

- **Level 0:** Call `GET /parks` and display real NPS data
- **Level 1:** Send park text to an LLM for summary, rewrite, classification, and extraction
- **Level 2:** Turn messy descriptions and alerts into validated JSON

## Field Guide 201: Retrieval Systems

Audience: learners who understand a single LLM call and are ready to ask, "How does the model answer from our data?"

Learners should finish 201 able to explain:

- Why RAG starts with ingestion, not chat
- What should be embedded vs. stored as metadata
- Why chunking choices affect answer quality
- The difference between vector search, keyword search, filters, hybrid search, and reranking
- Why RAG orchestration is not the same thing as an agent

Levels:

- **Level 3:** Ingest multiple NPS endpoints into a searchable substrate
- **Level 4:** Build cited question-answering over the ingested corpus
- **Level 5:** Route questions through different retrieval and answer paths

## Field Guide 301: Agents And Production Workflows

Audience: learners who can explain RAG and now need to understand when agent patterns are justified.

Learners should finish 301 able to explain:

- What a tool is
- How a ReAct loop differs from controlled orchestration
- Why planner-executor is safer for repeatable business workflows
- Where human-in-the-loop belongs
- Why multi-agent systems need contracts, not just many prompts
- What production readiness means for an AI workflow

Levels:

- **Level 6A:** Build a narrow ReAct agent with live NPS API tools
- **Level 6B:** Build a planner-executor workflow with human review
- **Level 7:** Split work across specialized subagents
- **Level 8:** Write a production readiness review

## Teaching Pattern

Each level follows the same loop:

1. **Run it:** start with a working demo.
2. **Read it:** identify the API call, model call, schema, retrieval step, or agent step.
3. **Ask an assistant:** use Codex or Claude Code to make one scoped change.
4. **Inspect the diff:** understand what changed before running it.
5. **Verify it:** run the script, UI, or eval.
6. **Explain it:** write a short note in plain English.

This is intentionally close to modern work. The skill is not memorizing every Python import. The skill is knowing what you are trying to build, prompting an assistant clearly, reviewing the result, and proving it works.
