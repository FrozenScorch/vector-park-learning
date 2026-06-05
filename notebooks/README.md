# Notebooks

These notebooks are planned as guided walkthroughs for the runnable demos in `levels/`.

They should explain and call the source code rather than replace it. The source of truth remains:

- `levels/` for runnable demos
- `evals/` for smoke checks
- `docs/` for curriculum and assistant prompts

Recommended tracks:

- `101/` - setup, first API call, generic inference, structured extraction
- `201/` - ingestion, retrieval, RAG orchestration
- `301/` - agents, planner-executor workflows, multi-agent orchestration, production review

Reference inspiration: [langchain-ai/langgraph-101](https://github.com/langchain-ai/langgraph-101)

To run locally:

```bash
pip install -r requirements-notebooks.txt
jupyter lab
```
