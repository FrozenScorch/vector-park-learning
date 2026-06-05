# Start Here

This repo is ready to try for Levels 0 and 1.

You will build a National Parks Field Guide assistant in small steps. The first two levels prove the basic workflow:

- Level 0: call the National Park Service API and display real park data
- Level 1: send park text to an LLM for summary, rewrite, classification, and extraction

## Important: API Keys

Do not paste real API keys into chat or commit them to git.

Create a local `.env` file from `.env.example` and put keys there:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
copy .env.example .env
```

If a real API key was pasted into a chat or shared document, rotate it before using the curriculum with others.

## Fast Path

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

Edit `.env` with:

```bash
NPS_API_KEY=your-nps-key
LLM_PROVIDER=nvidia
LLM_MODEL=google/gemma-4-31b-it
NVIDIA_API_KEY=your-nvidia-api-key
```

Then run:

```bash
python levels/level0_first_nps_call.py --park-code yell
python levels/level1_generic_inference.py --mode summarize --park-code yell
python evals/level1_smoke_eval.py
```

## UI Path

```bash
chainlit run levels/level0_chainlit_nps.py
```

Then:

```bash
chainlit run levels/level1_chainlit_field_guide.py
```

Open [http://localhost:8000](http://localhost:8000).

## Notebook Path

Notebooks are companion walkthroughs. They explain the code, but the runnable source of truth stays in `levels/`.

```bash
pip install -r requirements-notebooks.txt
jupyter lab
```

Open:

- `notebooks/101/00_setup_and_api.ipynb`
- `notebooks/101/01_generic_inference.ipynb`

## Learning Loop

Use Codex or Claude Code, but keep the loop intentional:

```text
Orient -> Ask -> Inspect -> Run -> Evaluate -> Explain
```

Main docs:

- [README.md](README.md)
- [genai_curriculum.md](genai_curriculum.md)
- [docs/ai_coding_assistant_playbook.md](docs/ai_coding_assistant_playbook.md)
- [docs/spoiler_full_build_prompts.md](docs/spoiler_full_build_prompts.md)
