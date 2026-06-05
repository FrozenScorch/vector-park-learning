"""Level 2 Chainlit scaffold: structured extraction with guided wizard UI.

This is a LEARNER SCAFFOLD. The extract_structured() function is a TODO.
Build it using your AI coding assistant with the prompt card from
docs/ai_coding_assistant_playbook.md.

Run on port 8000:
    chainlit run levels/level2_chainlit_extraction.py
"""

from __future__ import annotations

from typing import Any

import chainlit as cl
from dotenv import load_dotenv

try:
    from levels.llm_provider import make_llm_client
    from levels.nps_client import (
        fetch_park,
        fetch_alerts,
        fetch_campgrounds,
        format_park_text_for_inference,
        format_alert_text,
        format_campground_text,
    )
    from levels.schemas import ParkExtraction
except ModuleNotFoundError:
    from llm_provider import make_llm_client
    from nps_client import (
        fetch_park,
        fetch_alerts,
        fetch_campgrounds,
        format_park_text_for_inference,
        format_alert_text,
        format_campground_text,
    )
    from schemas import ParkExtraction


load_dotenv()

PARK_CODES = {
    "yell": ("Yellowstone", "WY/MT/ID"),
    "acad": ("Acadia", "ME"),
    "grca": ("Grand Canyon", "AZ"),
    "yose": ("Yosemite", "CA"),
    "zion": ("Zion", "UT"),
    "dena": ("Denali", "AK"),
}

ENDPOINTS = {
    "parks": "Park descriptions, weather, directions",
    "alerts": "Hazard, closure, and caution announcements",
    "campgrounds": "Location, fees, amenities, descriptions",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_source_text(endpoint: str, park_code: str) -> str:
    """Fetch and format text from the chosen NPS endpoint."""
    if endpoint == "parks":
        park = fetch_park(park_code)
        return format_park_text_for_inference(park)
    elif endpoint == "alerts":
        alerts = fetch_alerts(park_code)
        if not alerts:
            return f"No alerts found for park code '{park_code}'."
        return "\n\n---\n\n".join(format_alert_text(a) for a in alerts)
    elif endpoint == "campgrounds":
        campgrounds = fetch_campgrounds(park_code)
        if not campgrounds:
            return f"No campgrounds found for park code '{park_code}'."
        return "\n\n---\n\n".join(format_campground_text(c) for c in campgrounds)
    else:
        raise ValueError(f"Unknown endpoint: {endpoint}")


# TODO: Implement the structured extraction function.
# ...
# Steps:
# 1. Call make_llm_client() to get the OpenAI client and config
# 2. Build a prompt that asks the LLM to return JSON matching the ParkExtraction schema
#    - Include the full schema in the prompt
#    - Tell the model to use "unknown" for missing information
#    - Require evidence quotes for every risk
#    - Return ONLY valid JSON, no markdown fences
# 3. Send to the LLM with temperature=0 for deterministic output
# 4. Parse the response as JSON (handle markdown code fences if present)
# 5. Validate with ParkExtraction.model_validate(parsed_json)
# 6. Return the validated extraction
#
# Use the Level 2 prompt card from docs/ai_coding_assistant_playbook.md
# or the full build prompt from docs/spoiler_full_build_prompts.md.
def extract_structured(source_text: str) -> ParkExtraction:
    """Extract structured data from source text using the LLM.

    TODO: Implement this function.
    """
    raise NotImplementedError(
        "extract_structured() is not implemented yet.\n\n"
        "Use your AI coding assistant with the Level 2 prompt card from\n"
        "docs/ai_coding_assistant_playbook.md to build this function."
    )


def parse_command(raw: str) -> tuple[str, str]:
    """Parse user input into (endpoint, park_code).

    Examples:
        'extract yell' -> ('parks', 'yell')
        'extract alerts acad' -> ('alerts', 'acad')
        'extract campgrounds grca' -> ('campgrounds', 'grca')
        'yell' -> ('parks', 'yell')
    """
    stripped = raw.strip().lower()
    if not stripped:
        raise ValueError("Type a command like `extract yell` or `extract alerts acad`.")

    parts = stripped.split()

    # "schema" and "help" are handled before calling parse_command
    if parts[0] == "extract":
        if len(parts) == 1:
            raise ValueError("Add a park code or endpoint + park code. Example: `extract yell` or `extract alerts yell`")
        if parts[1] in ENDPOINTS:
            if len(parts) == 2:
                raise ValueError(f"Add a park code. Example: `extract {parts[1]} yell`")
            return parts[1], parts[2]
        # Bare park code after "extract"
        return "parks", parts[1]

    # Bare park code
    if parts[0] in PARK_CODES:
        return "parks", parts[0]

    raise ValueError(
        "Unknown command. Try `extract yell`, `extract alerts acad`, "
        "`schema`, or `help`."
    )


# ---------------------------------------------------------------------------
# Chat start: welcome screen
# ---------------------------------------------------------------------------

@cl.on_chat_start
async def on_chat_start() -> None:
    park_table = "\n".join(
        f"| `{code}` | {name} | {state} |"
        for code, (name, state) in PARK_CODES.items()
    )
    endpoint_table = "\n".join(
        f"| `{ep}` | {desc} |"
        for ep, desc in ENDPOINTS.items()
    )

    welcome = f"""\
## Welcome to Level 2: Structured Extraction

Level 2 teaches the jump from **free text** to **validated structured data**.

In Level 1, the LLM returned paragraphs. In Level 2, it returns **JSON** that must \
conform to a Pydantic schema — with risks, severity levels, evidence quotes, and \
confidence scores.

### The extraction schema

| Field | Type | Purpose |
|-------|------|---------|
| `summary` | string | One-paragraph summary |
| `key_facts` | string list | 3-5 key facts |
| `visitor_risks` | list of risks | Each with severity + evidence |
| `logistics` | object | Fees, locations, hours, reservations |
| `open_questions` | string list | What the source doesn't answer |
| `confidence` | enum | low / medium / high |

### Commands

- **`extract <park_code>`** — Extract from park description
- **`extract alerts <park_code>`** — Extract from alerts
- **`extract campgrounds <park_code>`** — Extract from campgrounds
- **`schema`** — Display the full extraction schema
- **`help`** — Full command reference

### Park codes

| Code | Park | State |
|------|------|-------|
{park_table}

### Endpoints

| Endpoint | What it returns |
|----------|----------------|
{endpoint_table}

### Quick start

- **`extract yell`** — step-by-step extraction from Yellowstone
- **`extract alerts acad`** — extract from Acadia's alerts
- **`schema`** — see the full Pydantic schema
"""
    await cl.Message(content=welcome).send()


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------

@cl.on_message
async def on_message(message: cl.Message) -> None:
    raw = message.content.strip()
    if not raw:
        return

    lower = raw.lower().strip()

    if lower == "help":
        await _send_help()
        return
    if lower == "schema":
        await _send_schema()
        return

    try:
        endpoint, park_code = parse_command(raw)
    except ValueError as exc:
        await cl.Message(content=f"**Input error:** {exc}").send()
        return

    await _run_extraction(endpoint, park_code)


# ---------------------------------------------------------------------------
# Step-by-step extraction flow
# ---------------------------------------------------------------------------

async def _run_extraction(endpoint: str, park_code: str) -> None:
    """Execute a structured extraction with step-by-step visualization."""

    park_info = PARK_CODES.get(park_code, (park_code.upper(), ""))

    # Step 1: Fetch data
    await cl.Message(
        content=f"Step 1\uFE0F\u20E3  Fetching **{endpoint}** data for **{park_info[0]}**..."
    ).send()
    await cl.sleep(0.5)

    try:
        source_text = fetch_source_text(endpoint, park_code)
    except Exception as exc:
        await cl.Message(content=f"**Error fetching data:** {exc}").send()
        return

    await cl.Message(
        content=(
            f"**Source text ({endpoint} for {park_info[0]}):**\n\n"
            f"<details>\n<summary>Click to expand ({len(source_text)} chars)</summary>\n\n"
            f"{source_text}\n\n"
            f"</details>"
        )
    ).send()
    await cl.sleep(0.5)

    # Step 2: Show schema
    await cl.Message(
        content="Step 2\uFE0F\u20E3  Validating against **ParkExtraction** schema..."
    ).send()
    await cl.sleep(0.3)
    await cl.Message(
        content=(
            "**Schema fields:** summary, key_facts, visitor_risks (risk + severity + evidence), "
            "logistics (fees, locations, hours, reservations), open_questions, confidence"
        )
    ).send()
    await cl.sleep(0.5)

    # Step 3: Call LLM (TODO)
    await cl.Message(content="Step 3\uFE0F\u20E3  Sending to LLM for structured extraction...").send()
    await cl.sleep(0.5)

    try:
        result = extract_structured(source_text)
    except NotImplementedError as exc:
        await cl.Message(
            content=(
                "### TODO: Build the extraction\n\n"
                f"```\n{exc}\n```\n\n"
                "---\n\n"
                "**The source text is ready above.** Now use your AI coding assistant "
                "to implement `extract_structured()` in this file:\n\n"
                "```text\n"
                "levels/level2_chainlit_extraction.py\n"
                "```\n\n"
                "Use the Level 2 prompt card from `docs/ai_coding_assistant_playbook.md`."
            )
        ).send()
        return
    except Exception as exc:
        await cl.Message(content=f"**Extraction error:** {exc}").send()
        return

    # Step 4: Parse and validate (handled inside extract_structured)
    await cl.Message(content="Step 4\uFE0F\u20E3  Parsing and validating JSON...").send()
    await cl.sleep(0.3)

    # Step 5: Display result
    await cl.Message(
        content=f"Step 5\uFE0F\u20E3  **Extraction result:**\n\n```json\n{result.model_dump_json(indent=2)}\n```"
    ).send()

    await cl.Message(
        content=(
            "---\n\n**Extraction complete!**\n\n"
            "Try another endpoint:\n"
            f"- `extract alerts {park_code}`\n"
            f"- `extract campgrounds {park_code}`\n\n"
            "Or a different park:\n"
            "- `extract acad`\n"
            "- `extract alerts grca`"
        )
    ).send()


# ---------------------------------------------------------------------------
# Schema display
# ---------------------------------------------------------------------------

async def _send_schema() -> None:
    await cl.Message(
        content="""\
## ParkExtraction Schema

```python
class VisitorRisk(BaseModel):
    risk: str           # Short description
    severity: Severity  # low | medium | high | unknown
    evidence: str       # Quote from source text

class Logistics(BaseModel):
    fees: list[str]              # Entrance/camping fees
    locations: list[str]         # Named locations
    hours: list[str]             # Operating hours/seasons
    reservation_notes: list[str] # Reservation requirements

class ParkExtraction(BaseModel):
    summary: str                    # One-paragraph summary
    key_facts: list[str]            # 3-5 key facts
    visitor_risks: list[VisitorRisk] # Risks with severity + evidence
    logistics: Logistics             # Fees, locations, hours, reservations
    open_questions: list[str]        # What the source doesn't answer
    confidence: Confidence           # low | medium | high
```

See `levels/schemas.py` for the full Pydantic definitions.
"""
    ).send()


# ---------------------------------------------------------------------------
# Help command
# ---------------------------------------------------------------------------

async def _send_help() -> None:
    park_table = "\n".join(
        f"| `{code}` | {name} | {state} |"
        for code, (name, state) in PARK_CODES.items()
    )
    help_text = f"""\
## Command Reference

### Extraction commands

- **`extract <park_code>`** — Extract structured data from park description
  - Example: `extract yell`
- **`extract alerts <park_code>`** — Extract from alerts
  - Example: `extract alerts acad`
- **`extract campgrounds <park_code>`** — Extract from campgrounds
  - Example: `extract campgrounds grca`

### Meta commands

- **`schema`** — Display the full extraction schema
- **`help`** — This reference

### Park codes

| Code | Park | State |
|------|------|-------|
{park_table}

### How the 5-step flow works

1. **Fetch** live data from the NPS API
2. **Show schema** — what fields we expect
3. **Send** to LLM for structured extraction
4. **Parse & validate** JSON against Pydantic schema
5. **Display** the validated result

### Learner TODO

The `extract_structured()` function is a stub. Build it using your AI coding assistant:
- Use the prompt card from `docs/ai_coding_assistant_playbook.md`
- Or the full build prompt from `docs/spoiler_full_build_prompts.md`
"""
    await cl.Message(content=help_text).send()
