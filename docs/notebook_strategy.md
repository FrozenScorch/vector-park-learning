# Notebook Strategy

Short answer: use notebooks, but do not make notebooks the only implementation surface.

Vector Park Learning should use a hybrid structure:

| Surface | Purpose | Learner behavior |
|---|---|---|
| `levels/` Python scripts | Source-of-truth runnable demos | Build, run, debug, and extend with Codex or Claude Code |
| Chainlit apps | User-facing demo surface | See each level as a working mini-product |
| `notebooks/` walkthroughs | Guided explanation and reflection | Read, experiment, inspect outputs, answer checkpoint questions |
| `docs/` | Curriculum, prompts, setup, and references | Understand the learning path and ask better assistant prompts |

This keeps the curriculum practical. Business analysts get notebook-style explanations, but they still learn how real application code is structured and verified.

## Why Not Notebook-Only?

Notebook-only curricula are approachable, but they can hide important production habits:

- environment variables and secrets
- reusable modules
- CLI workflows
- app entry points
- smoke evals
- file diffs
- debugging real scripts
- using coding assistants against a repo instead of one notebook cell

Those habits matter for this curriculum because the goal is not just "understand GenAI." The goal is to understand how GenAI systems are built.

## Recommended Layout

```text
vector-park-learning/
  levels/                 # Runnable demos; source of truth
  notebooks/
    101/
      00_setup_and_api.ipynb
      01_generic_inference.ipynb
      02_structured_extraction.ipynb
    201/
      03_ingestion.ipynb
      04_basic_rag.ipynb
      05_rag_orchestration.ipynb
    301/
      06a_react_agent.ipynb
      06b_planner_executor.ipynb
      07_multi_agent.ipynb
      08_production_review.ipynb
  evals/                  # Smoke evals and regression checks
  docs/                   # Curriculum and assistant prompts
```

Each notebook should call into the `levels/` code instead of duplicating it. For example, the Level 1 notebook should import `levels.nps_client` and `levels.level1_generic_inference`, then explain what those modules do.

## Notebook Cell Pattern

Use the same pattern in every notebook:

1. **Goal:** what the learner is about to build.
2. **Run:** execute the existing demo command or imported function.
3. **Read:** inspect the relevant code path.
4. **Ask Codex/Claude:** provide one small prompt.
5. **Inspect:** review the expected diff.
6. **Verify:** run the CLI, Chainlit app, or eval.
7. **Checkpoint:** answer 3-5 short questions.

## Reference Inspiration

The [langchain-ai/langgraph-101](https://github.com/langchain-ai/langgraph-101) repo is a good reference for this style. It organizes material into:

- `notebooks/101/` for fundamentals
- `notebooks/201/` for production patterns
- `agents/` for standalone implementations that can run outside the notebook

Vector Park Learning should borrow that shape, but adapt it for business analysts and the NPS Field Guide storyline:

- 101: API calls, one LLM call, structured extraction
- 201: ingestion, retrieval, RAG orchestration
- 301: ReAct, planner-executor, multi-agent, production review

## Practical Recommendation

Start by keeping Levels 0 and 1 as scripts plus Chainlit demos. Then add companion notebooks for 0 and 1 that explain and call those scripts. Once that pattern feels good, add the rest of the notebooks track by track.

