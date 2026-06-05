"""Level 1 Chainlit demo (Variant B): step-by-step guided wizard with prompt playground.

Runs on port 8000:
    chainlit run levels/level1_chainlit_vB.py --port 8000

Teaches generic LLM inference through a tutorial-like interface that reveals
each stage of the pipeline: fetch data, build prompt, call LLM, display result.

New in this version -- prompt playground features:
  - `prompts` command to view all default prompt templates
  - Pipe syntax for custom prompts: `summarize yell | Your custom prompt here`
  - `compare <park_code>` runs summarize with 3 different prompts side-by-side
  - `edit <mode>` shows the current default prompt for that mode
  - After every result, suggests prompt customization
"""

from __future__ import annotations

from typing import Literal

import chainlit as cl
from dotenv import load_dotenv

try:
    from levels.llm_provider import make_llm_client
    from levels.nps_client import fetch_park, format_park_text_for_inference
except ModuleNotFoundError:
    from llm_provider import make_llm_client
    from nps_client import fetch_park, format_park_text_for_inference


Mode = Literal["summarize", "rewrite", "classify", "extract"]

ALL_MODES: list[Mode] = ["summarize", "rewrite", "classify", "extract"]

MODE_PROMPTS: dict[Mode, str] = {
    "summarize": (
        "Summarize the source text for a first-time national park visitor. "
        "Use 4 bullets. Keep it practical and do not add facts not present in the source."
    ),
    "rewrite": (
        "Rewrite the source text for a family audience planning a trip. "
        "Use plain language, keep safety nuance, and do not add new facts."
    ),
    "classify": (
        "Classify the visitor question into exactly one category: trip planning, "
        "safety/alerts, camping, hiking, accessibility, fees/logistics, or not enough information. "
        "Return the category and one sentence explaining why."
    ),
    "extract": (
        'Extract action items from the source text. Return valid JSON with this shape: '
        '{"action_items":[{"task":"string","owner":"unknown","deadline":"unknown","evidence":"string"}]}. '
        "Use unknown when the source does not say."
    ),
}

SYSTEM_PROMPT = (
    "You are a careful field guide assistant. Ground every answer in the provided "
    "source text. Say when the source does not contain enough information."
)

MODE_DESCRIPTIONS: dict[Mode, str] = {
    "summarize": "Condense park info into 4 practical bullet points for a first-time visitor.",
    "rewrite": "Rephrase the text for families planning a trip, keeping safety warnings intact.",
    "classify": "Categorize a visitor question (e.g. trip planning, safety, hiking, fees, etc.).",
    "extract": "Pull structured action items as JSON from park information.",
}

COMPARE_PROMPTS: list[tuple[str, str]] = [
    (
        "default",
        MODE_PROMPTS["summarize"],
    ),
    (
        "kid-friendly",
        "Explain this park to a 5-year-old in 3 simple sentences.",
    ),
    (
        "haiku",
        "Write a haiku about this park based only on the facts.",
    ),
]


load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_park_text(park_code: str) -> str:
    park = fetch_park(park_code)
    return format_park_text_for_inference(park)


def build_prompt(mode: Mode, text: str) -> str:
    return f"{MODE_PROMPTS[mode]}\n\nSource text:\n{text}"


def run_inference(mode: Mode, text: str, custom_prompt: str | None = None) -> str:
    """Run LLM inference. When custom_prompt is provided, it replaces the mode's default template."""
    client, config = make_llm_client()
    completion_kwargs: dict = {}
    if config.max_tokens:
        completion_kwargs["max_tokens"] = config.max_tokens
    if config.top_p:
        completion_kwargs["top_p"] = config.top_p
    if config.extra_body:
        completion_kwargs["extra_body"] = config.extra_body

    user_content = (
        f"{custom_prompt}\n\nSource text:\n{text}"
        if custom_prompt
        else build_prompt(mode, text)
    )

    response = client.chat.completions.create(
        model=config.model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        **completion_kwargs,
    )
    return response.choices[0].message.content or ""


def parse_message(raw: str) -> tuple[Mode | None, str, str | None]:
    """Parse user input into (mode, value, custom_prompt).

    Returns (None, park_code, None) when the user typed just a park code.
    Returns (mode, value, custom_prompt) for explicit mode commands.
    Returns (None, command_name, None) for meta-commands like help/prompts/compare/edit.
    Raises ValueError on bad input.
    """
    stripped = raw.strip()
    if not stripped:
        raise ValueError("Type a command like `summarize yell` or just a park code like `yell`.")

    parts = stripped.split(maxsplit=1)
    first_word = parts[0].lower()

    # Meta-commands that don't fit the mode pattern
    if first_word == "help":
        return None, "help", None
    if first_word == "prompts":
        return None, "prompts", None
    if first_word == "compare":
        if len(parts) == 1:
            raise ValueError("Add a park code after `compare`. Example: `compare yell`")
        return None, f"compare:{parts[1].strip().lower()}", None
    if first_word == "edit":
        if len(parts) == 1:
            raise ValueError("Add a mode name after `edit`. Example: `edit summarize`")
        mode_arg = parts[1].strip().lower()
        if mode_arg not in MODE_PROMPTS:
            raise ValueError(
                f"Unknown mode `{mode_arg}`. Choose from: {', '.join(ALL_MODES)}"
            )
        return None, f"edit:{mode_arg}", None

    # User typed an explicit mode command -- check for pipe syntax
    if first_word in {"summarize", "rewrite", "classify", "extract"}:
        if len(parts) == 1:
            raise ValueError(f"Add a park code or text after `{first_word}`. Example: `{first_word} yell`")

        remainder = parts[1].strip()
        custom_prompt: str | None = None

        # Check for pipe syntax: "summarize yell | custom prompt text"
        if "|" in remainder:
            value_part, _, prompt_part = remainder.partition("|")
            value = value_part.strip()
            custom_prompt = prompt_part.strip()
            if not value:
                raise ValueError("Missing park code or text before `|`. Example: `summarize yell | Your prompt`")
            if not custom_prompt:
                raise ValueError("Missing custom prompt after `|`. Example: `summarize yell | Your prompt`")
        else:
            value = remainder

        return first_word, value, custom_prompt  # type: ignore[return-value]

    # Treat bare word as a park code
    if first_word.isalnum() and len(first_word) <= 5:
        return None, first_word, None

    raise ValueError(
        "Unknown command. Start with `summarize`, `rewrite`, `classify`, or `extract`, "
        "or type a park code like `yell`. Type `help` for examples."
    )


def _mode_label(mode: Mode) -> str:
    return mode.upper()


def _mode_followup(mode: Mode) -> list[str]:
    """Return suggested next commands after completing a given mode."""
    other_modes = [m for m in ALL_MODES if m != mode]
    suggestions = [f"`{m} yell`" for m in other_modes[:2]]
    return suggestions


def _customization_hint(mode: Mode, park_code: str | None = None) -> str:
    """Return the post-result customization suggestion block."""
    park_hint = park_code or "yell"
    return (
        "\n\n---\n\n"
        "**Want to tweak the prompt?** Try:\n"
        f"`{mode} {park_hint} | Summarize this in a single tweet-length paragraph`\n\n"
        "Or see how different prompts compare:\n"
        f"`compare {park_hint}`"
    )


# ---------------------------------------------------------------------------
# Chat start: welcome screen
# ---------------------------------------------------------------------------

@cl.on_chat_start
async def on_chat_start() -> None:
    welcome = """\
## Welcome to Level 1: Generic LLM Inference

This level teaches you how a **generic large language model** can be used to process \
National Park Service data through different *inference modes* — each one applying a \
different prompt template to the same underlying text.

### How it works

You type a command and the wizard walks you through every step of the pipeline:

1. **Fetch** live park data from the NPS API
2. **Build** the exact prompt that gets sent to the LLM
3. **Send** the prompt to the model
4. **Display** the formatted result

### The 4 inference modes

| Mode | What it does |
|------|-------------|
| `summarize <park>` | Condense park info into 4 practical bullets |
| `rewrite <park>` | Rephrase for families, keeping safety nuance |
| `classify <text>` | Categorize a visitor question |
| `extract <park>` | Pull structured action items as JSON |

### Custom prompts

Use **pipe syntax** to write your own prompt:

`summarize yell | Explain this park like I'm 5`

Everything after the `|` replaces the default prompt template. Experiment freely — \
that's how you learn what works!

### Park codes to try

| Code | Park | State |
|------|------|-------|
| `yell` | Yellowstone | WY/MT/ID |
| `acad` | Acadia | ME |
| `grca` | Grand Canyon | AZ |
| `yose` | Yosemite | CA |
| `zion` | Zion | UT |
| `dena` | Denali | AK |

### Quick start

- **`summarize yell`** — step-by-step with the default prompt
- **`summarize acad | Write this as a haiku`** — try your own prompt
- **`compare grca`** — see 3 different prompts on the same park
- **`yell`** — run all 4 modes on Yellowstone
- **`prompts`** — view all default prompt templates
- **`help`** — full command reference
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

    # Handle bare "help" and "prompts" early
    if raw.lower() == "help":
        await _send_help()
        return
    if raw.lower() == "prompts":
        await _send_prompts()
        return

    try:
        mode, value, custom_prompt = parse_message(raw)
    except ValueError as exc:
        await cl.Message(content=f"**Input error:** {exc}").send()
        return

    # Meta-commands routed through parse_message
    if mode is None:
        if value == "help":
            await _send_help()
            return
        if value == "prompts":
            await _send_prompts()
            return
        if value.startswith("compare:"):
            park_code = value.split(":", 1)[1]
            await _run_compare(park_code)
            return
        if value.startswith("edit:"):
            mode_name = value.split(":", 1)[1]
            await _show_edit(mode_name)  # type: ignore[arg-type]
            return

        # Bare park code -- run all 4 modes
        await _run_all_modes(value.lower())
        return

    # Explicit mode command (with optional custom prompt)
    if mode is not None:
        await _run_single_mode(mode, value, custom_prompt)


# ---------------------------------------------------------------------------
# Single-mode step-by-step flow
# ---------------------------------------------------------------------------

async def _run_single_mode(mode: Mode, value: str, custom_prompt: str | None = None) -> None:
    """Execute one inference mode with a step-by-step visual progression."""

    # Determine source text
    is_park_code = len(value) <= 5 and value.replace(" ", "").isalnum() and " " not in value

    if mode in ("summarize", "rewrite") and is_park_code:
        park_code = value.lower()

        # Step 1: Fetch park data
        await cl.Message(content=f"Step 1\uFE0F\u20E3  Fetching park data for **{park_code.upper()}**...").send()
        await cl.sleep(0.5)
        try:
            source_text = fetch_park_text(park_code)
        except Exception as exc:
            await cl.Message(content=f"**Error fetching park data:** {exc}").send()
            return

        await cl.Message(
            content=(
                f"**Raw NPS data for {park_code.upper()}:**\n\n"
                f"<details>\n<summary>Click to expand source text</summary>\n\n"
                f"{source_text}\n\n"
                f"</details>"
            )
        ).send()
        await cl.sleep(0.5)

    else:
        # Freeform text mode
        source_text = value
        park_code = None
        await cl.Message(content="Step 1\uFE0F\u20E3  Using your provided text as source.").send()
        await cl.sleep(0.3)

        await cl.Message(
            content=(
                "**Source text:**\n\n"
                f"<details>\n<summary>Click to expand</summary>\n\n"
                f"{source_text}\n\n"
                f"</details>"
            )
        ).send()
        await cl.sleep(0.5)

    # Step 2: Build prompt
    if custom_prompt:
        prompt_label = "**Using YOUR custom prompt:**"
        prompt_text = f"{custom_prompt}\n\nSource text:\n{source_text}"
    else:
        prompt_label = f"**Using DEFAULT {_mode_label(mode)} prompt:**"
        prompt_text = build_prompt(mode, source_text)

    await cl.Message(content="Step 2\uFE0F\u20E3  Building prompt...").send()
    await cl.sleep(0.5)

    await cl.Message(
        content=(
            f"{prompt_label}\n\n"
            f"```\n{prompt_text}\n```"
        )
    ).send()
    await cl.sleep(0.5)

    # Step 3: Send to LLM
    client, config = make_llm_client()
    await cl.Message(content=f"Step 3\uFE0F\u20E3  Sending to LLM (**{config.model}**)...").send()
    await cl.sleep(0.5)

    try:
        result = run_inference(mode, source_text, custom_prompt=custom_prompt)
    except Exception as exc:
        await cl.Message(content=f"**LLM error:** {exc}").send()
        return

    # Store last result in session
    cl.user_session.set("last_result", result)

    # Step 4: Show result
    await cl.sleep(0.5)
    result_header = f"Step 4\uFE0F\u20E3  **{_mode_label(mode)} result:**\n\n"
    await cl.Message(content=result_header + result + _customization_hint(mode, park_code or value)).send()


# ---------------------------------------------------------------------------
# All-modes comparison (user typed just a park code)
# ---------------------------------------------------------------------------

async def _run_all_modes(park_code: str) -> None:
    """Run all 4 modes on a single park code so the user can compare."""

    # Fetch once, reuse across modes
    await cl.Message(content=f"**Running all 4 modes on `{park_code.upper()}`**\n\nFetching park data...").send()
    await cl.sleep(0.5)

    try:
        source_text = fetch_park_text(park_code)
    except Exception as exc:
        await cl.Message(content=f"**Error fetching park data:** {exc}").send()
        return

    await cl.Message(
        content=(
            f"**Source text for {park_code.upper()}:**\n\n"
            f"<details>\n<summary>Click to expand</summary>\n\n"
            f"{source_text}\n\n"
            f"</details>"
        )
    ).send()
    await cl.sleep(0.5)

    for i, mode in enumerate(ALL_MODES, start=1):
        await cl.Message(
            content=f"---\n\n**Mode {i}/4: {mode.upper()}**\n_{MODE_DESCRIPTIONS[mode]}_"
        ).send()
        await cl.sleep(0.3)

        # Show the prompt
        prompt = build_prompt(mode, source_text)
        await cl.Message(content=f"**Prompt:**\n```\n{prompt}\n```").send()
        await cl.sleep(0.3)

        # Run inference
        try:
            result = run_inference(mode, source_text)
        except Exception as exc:
            await cl.Message(content=f"**Error in {mode}:** {exc}").send()
            continue

        await cl.Message(content=f"**Result:**\n\n{result}").send()
        await cl.sleep(0.5)

    await cl.Message(
        content=(
            "---\n\n**All 4 modes complete!** You can see how the same source text produces very "
            "different outputs depending on the prompt template.\n\n"
            "Try another park code (`acad`, `grca`, `yose`, `zion`, `dena`) or type `help` for more commands."
        )
    ).send()


# ---------------------------------------------------------------------------
# Compare command: 3 prompts, same park
# ---------------------------------------------------------------------------

async def _run_compare(park_code: str) -> None:
    """Run summarize on the same park with 3 different prompts side-by-side."""

    await cl.Message(
        content=f"**Comparing 3 prompts on `{park_code.upper()}`**\n\nFetching park data..."
    ).send()
    await cl.sleep(0.5)

    try:
        source_text = fetch_park_text(park_code)
    except Exception as exc:
        await cl.Message(content=f"**Error fetching park data:** {exc}").send()
        return

    await cl.Message(
        content=(
            f"**Source text for {park_code.upper()}:**\n\n"
            f"<details>\n<summary>Click to expand</summary>\n\n"
            f"{source_text}\n\n"
            f"</details>"
        )
    ).send()
    await cl.sleep(0.5)

    for i, (label, prompt_template) in enumerate(COMPARE_PROMPTS, start=1):
        await cl.Message(
            content=f"---\n\n**Prompt {i}/3: _{label}_**\n\n```\n{prompt_template}\n```"
        ).send()
        await cl.sleep(0.3)

        try:
            result = run_inference("summarize", source_text, custom_prompt=prompt_template)
        except Exception as exc:
            await cl.Message(content=f"**Error with {label} prompt:** {exc}").send()
            continue

        await cl.Message(content=f"**{label} result:**\n\n{result}").send()
        await cl.sleep(0.5)

    # Store last result in session
    cl.user_session.set("last_result", "")

    await cl.Message(
        content=(
            "---\n\n**Comparison complete!** Notice how the same park data produces very "
            "different outputs when the prompt changes.\n\n"
            "Try your own custom prompt:\n"
            f"`summarize {park_code} | Write a limerick about this park`\n\n"
            "Or compare on a different park:\n"
            "`compare acad`"
        )
    ).send()


# ---------------------------------------------------------------------------
# Prompts command: show all default templates
# ---------------------------------------------------------------------------

async def _send_prompts() -> None:
    """Display all 4 default prompt templates in formatted code blocks."""
    sections: list[str] = ["## Prompt Templates\n"]

    for mode in ALL_MODES:
        sections.append(f"### `{mode}` — {MODE_DESCRIPTIONS[mode]}\n")
        sections.append(f"```\n{MODE_PROMPTS[mode]}\n```\n")

    sections.append(
        "---\n\n"
        "**Try a custom prompt:** `summarize yell | Summarize this as a tweet`\n\n"
        "**Compare prompts:** `compare yell`\n\n"
        "**Edit a prompt:** `edit summarize`"
    )

    await cl.Message(content="\n".join(sections)).send()


# ---------------------------------------------------------------------------
# Edit command: show a single mode's prompt
# ---------------------------------------------------------------------------

async def _show_edit(mode: Mode) -> None:
    """Show the current default prompt for a mode and explain how to override."""
    await cl.Message(
        content=(
            f"## Current `{mode}` prompt\n\n"
            f"```\n{MODE_PROMPTS[mode]}\n```\n\n"
            f"---\n\n"
            f"Use pipe syntax to override: `{mode} yell | your custom prompt`\n\n"
            "Or view all prompts: `prompts`"
        )
    ).send()


# ---------------------------------------------------------------------------
# Help command
# ---------------------------------------------------------------------------

async def _send_help() -> None:
    help_text = """\
## Command Reference

### Single-mode commands

Run one inference mode with step-by-step visualization:

- **`summarize <park_code>`** -- Summarize park info in 4 practical bullets
  - Example: `summarize yell`
- **`rewrite <park_code>`** -- Rephrase park text for a family audience
  - Example: `rewrite acad`
- **`classify <question>`** -- Categorize a visitor question into one of 7 categories
  - Example: `classify Can I bring my dog to Yellowstone?`
- **`extract <park_code>`** -- Pull structured action items as JSON
  - Example: `extract grca`

### Custom prompts (pipe syntax)

Override the default prompt with your own:

- **`summarize yell | Summarize this in a single tweet-length paragraph`**
- **`rewrite acad | Rewrite this as a children's story`**

Everything after the `|` replaces the default prompt template.

### Prompt playground

- **`prompts`** -- View all 4 default prompt templates
- **`edit <mode>`** -- Show the current prompt for a mode (e.g. `edit summarize`)
- **`compare <park_code>`** -- Run summarize with 3 different prompts side-by-side
  - Example: `compare yell`

### Park code comparison

Type just a **park code** to run all 4 modes on that park:

| Code | Park | State |
|------|------|-------|
| `yell` | Yellowstone | WY/MT/ID |
| `acad` | Acadia | ME |
| `grca` | Grand Canyon | AZ |
| `yose` | Yosemite | CA |
| `zion` | Zion | UT |
| `dena` | Denali | AK |

### How it works

Each command triggers a 4-step pipeline:

1. Fetch live data from the NPS API (or use your provided text)
2. Build the prompt by combining the mode template with the source text
3. Send the prompt to the LLM
4. Display and explain the result

### The 4 prompt templates

**summarize:** Summarize the source text for a first-time national park visitor. Use 4 bullets. Keep it practical and do not add facts not present in the source.

**rewrite:** Rewrite the source text for a family audience planning a trip. Use plain language, keep safety nuance, and do not add new facts.

**classify:** Classify the visitor question into exactly one category: trip planning, safety/alerts, camping, hiking, accessibility, fees/logistics, or not enough information. Return the category and one sentence explaining why.

**extract:** Extract action items from the source text. Return valid JSON: `{"action_items":[{"task":"...","owner":"unknown","deadline":"unknown","evidence":"..."}]}`

### Tips

- Start with `summarize yell` to see the full step-by-step flow
- Then try `yell` alone to compare all modes at once
- Use `classify` with your own question to see how the LLM categorizes it
- Use `prompts` to inspect templates, then customize with pipe syntax
- Use `compare yell` to see how prompt changes affect output
"""
    await cl.Message(content=help_text).send()
