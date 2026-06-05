# Level 0 and Level 1 Demos

These demos are the first functional path through the curriculum. They are designed for self-paced learners on Mac or Windows.

Use an AI coding assistant while you work, but keep the loop tight:

```text
Orient -> Ask -> Inspect -> Run -> Evaluate -> Explain
```

Prompt cards live in [../docs/ai_coding_assistant_playbook.md](../docs/ai_coding_assistant_playbook.md).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env           # Mac/Linux
copy .env.example .env         # Windows PowerShell
```

Edit `.env` and add:

- `NPS_API_KEY`
- `LLM_PROVIDER`
- `LLM_MODEL`
- a provider key such as `NVIDIA_API_KEY` or `DEEPSEEK_API_KEY`, unless using local Ollama

Provider setup options live in [../docs/model_providers.md](../docs/model_providers.md).

Docker, pgvector, LangChain, and LangGraph are not required for Level 0 or Level 1. They start mattering in Level 3, when learners switch to:

```bash
pip install -r requirements-full.txt
```

## Level 0: First NPS API Call

CLI:

```bash
python levels/level0_first_nps_call.py --park-code yell
```

Chainlit UI:

```bash
chainlit run levels/level0_chainlit_nps.py
```

## Level 1: Generic Inference

CLI:

```bash
python levels/level1_generic_inference.py --mode summarize --park-code yell
python levels/level1_generic_inference.py --mode rewrite --park-code dena
python levels/level1_generic_inference.py --mode classify --text "Can I bring my dog on the trail?"
python levels/level1_generic_inference.py --mode extract --text "Call the visitor center, check road closures, and pack extra water."
```

Chainlit UI:

```bash
chainlit run levels/level1_chainlit_vB.py
```

Try messages like:

```text
summarize yell
summarize yell | Explain this like I'm 5
compare yell
prompts
help
```

### Prompt Playground

The Chainlit UI includes a guided wizard with prompt playground features:

- **Pipe syntax** -- append `| Your custom prompt` to any command to override the system prompt. Example: `summarize yell | Explain this like I'm 5`
- **`compare <park>`** -- runs the same park through 3 different prompt variants and shows them side-by-side so you can compare outputs. Example: `compare yell`
- **`prompts`** -- displays all default prompt templates (summarize, rewrite, classify, extract) so you can see exactly what is being sent to the LLM
- **`edit <mode>`** -- opens the prompt template for a given mode so you can inspect or copy it. Example: `edit summarize`
- **`<park-code>` alone** -- runs all 4 modes (summarize, rewrite, classify, extract) on the park. Example: `yell`

## Level 2: Structured Extraction (Learner Scaffold)

No new dependencies required. The same venv and `.env` from Level 0-1 work here.

The repo provides:
- `nps_client.py` — extended with `fetch_alerts()`, `fetch_campgrounds()`, `fetch_visitor_centers()`, `fetch_events()`
- `schemas.py` — Pydantic models: `ParkExtraction`, `VisitorRisk`, `Logistics`, `Severity`, `Confidence`
- `level2_structured_extraction.py` — CLI scaffold
- `level2_chainlit_extraction.py` — Chainlit UI scaffold

You build:
1. The extraction prompt that tells the LLM to return JSON matching the schema
2. The JSON parsing logic (handle markdown code fences)
3. Pydantic validation of the parsed result

Use the prompt card from `docs/ai_coding_assistant_playbook.md` or the full build prompt from `docs/spoiler_full_build_prompts.md`.

Commands:

```bash
python levels/level2_structured_extraction.py --endpoint parks --park-code yell
python levels/level2_structured_extraction.py --endpoint alerts --park-code acad
chainlit run levels/level2_chainlit_extraction.py
python evals/level2_schema_eval.py
```
