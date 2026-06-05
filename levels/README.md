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
chainlit run levels/level1_chainlit_field_guide.py
```

Try messages like:

```text
summarize yell
rewrite dena
classify Can I bring my dog on the trail?
extract Call the visitor center, check road closures, and pack extra water.
```
