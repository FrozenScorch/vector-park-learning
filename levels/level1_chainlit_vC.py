"""Level 1 Chainlit variant C: Prompt Playground.

Teaches prompt engineering through experimentation. Users see how different
prompts produce different outputs from the same source text. Supports custom
prompt overrides via pipe syntax, side-by-side comparison of default vs custom
outputs, and a `compare` command that runs 3 prompts on the same text.

Run with:
    chainlit run levels/level1_chainlit_vC.py --port 8003
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


# ---------------------------------------------------------------------------
# Types and constants
# ---------------------------------------------------------------------------

Mode = Literal["summarize", "rewrite", "classify", "extract"]

ALL_MODES: list[Mode] = ["summarize", "rewrite", "classify", "extract"]

SYSTEM_PROMPT = (
    "You are a careful field guide assistant. Ground every answer in the provided "
    "source text. Say when the source does not contain enough information."
)

PROMPT_TEMPLATES: dict[Mode, str] = {
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

COMPARE_PROMPTS: list[tuple[str, str]] = [
    ("default", None),  # uses PROMPT_TEMPLATES["summarize"]
    ("ELI5", "Explain the source text like I am a 5-year-old. Use simple words and short sentences."),
    ("haiku", "Write a haiku (5-7-5 syllables) that captures the essence of the source text."),
]

WELCOME_MESSAGE = """\
## Welcome to the Prompt Playground!

Learn how **different prompts produce different outputs** from the same source text. \
This is the core skill of **prompt engineering** -- crafting instructions that guide \
an LLM toward the output you want.

---

### How it works

Every command fetches live data from the National Park Service API, then applies a \
**prompt template** to that text before sending it to the LLM. You will see:

1. The **original source text** from the NPS (in a collapsible section)
2. The **exact prompt** that was sent (highlighted in a code block)
3. The **LLM output**

---

### Available Commands

| Command | What it does |
|---|---|
| `summarize <park>` | Summarize park info using the default prompt |
| `rewrite <park>` | Rewrite park info for families |
| `classify <park>` | Classify what kind of question the text answers |
| `extract <park>` | Extract structured action items as JSON |
| `compare <park>` | Run 3 different prompts on the same text (default, ELI5, haiku) |
| `prompts` | List all default prompt templates |

### Custom Prompts (the fun part!)

Override the default prompt with the **pipe syntax**:

```
summarize yell | Summarize this in a single tweet-length paragraph
```

Everything after the `|` replaces the default prompt. When you use a custom \
prompt, the output is highlighted as **CUSTOM** and if you already ran the \
default, both results are shown **side by side**.

### Park Codes

`yell` (Yellowstone), `acad` (Acadia), `grca` (Grand Canyon), \
`yose` (Yosemite), `zion` (Zion), `drto` (Dry Tortugas)

---

**Start with `summarize yell` to see the default prompt in action, then try \
customizing it!**
"""

# Session keys
SESSION_HISTORY = "prompt_history"  # dict[str, list[dict]] keyed by "mode:park_code"


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_park_text(park_code: str) -> str:
    """Fetch park data from the NPS API and format for inference."""
    park = fetch_park(park_code)
    return format_park_text_for_inference(park)


def build_user_prompt(mode: Mode, text: str, custom_prompt: str | None = None) -> str:
    """Combine the prompt template (or custom override) with source text."""
    template = custom_prompt if custom_prompt else PROMPT_TEMPLATES[mode]
    return f"{template}\n\nSource text:\n{text}"


def run_inference(mode: Mode, text: str, custom_prompt: str | None = None) -> str:
    """Send the prompt to the LLM and return the response text."""
    client, config = make_llm_client()
    completion_kwargs: dict = {}
    if config.max_tokens:
        completion_kwargs["max_tokens"] = config.max_tokens
    if config.top_p:
        completion_kwargs["top_p"] = config.top_p
    if config.extra_body:
        completion_kwargs["extra_body"] = config.extra_body

    user_content = build_user_prompt(mode, text, custom_prompt)

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


def parse_message(raw: str) -> tuple[Mode | None, str, str | None, bool]:
    """Parse a user message into (mode, park_code, custom_prompt, is_compare).

    Returns:
        (None, park_code, None, False) for `compare <park>`
        (mode, park_code, None, False) for `summarize yell`
        (mode, park_code, custom, False) for `summarize yell | custom prompt`
        (None, "", None, False) for `prompts`
    """
    stripped = raw.strip()
    if not stripped:
        raise ValueError("Type a command. Try `summarize yell` or `prompts`.")

    parts = stripped.split(maxsplit=1)
    first_word = parts[0].lower()

    # "prompts" command
    if first_word == "prompts":
        return None, "", None, False

    # "compare" command
    if first_word == "compare":
        if len(parts) == 1:
            raise ValueError("Add a park code after `compare`. Example: `compare yell`")
        return None, parts[1].strip().lower(), None, True

    # Standard mode commands
    if first_word not in {"summarize", "rewrite", "classify", "extract"}:
        raise ValueError(
            "Start with `summarize`, `rewrite`, `classify`, `extract`, "
            "`compare`, or `prompts`."
        )
    if len(parts) == 1:
        raise ValueError(f"Add a park code after `{first_word}`. Example: `{first_word} yell`")

    mode = first_word
    rest = parts[1].strip()

    # Check for pipe syntax for custom prompt
    custom_prompt = None
    if "|" in rest:
        pipe_idx = rest.index("|")
        park_part = rest[:pipe_idx].strip()
        custom_prompt = rest[pipe_idx + 1:].strip()
        if not custom_prompt:
            raise ValueError("Add your custom prompt after the `|`. Example: `summarize yell | Explain in 2 sentences`")
        rest = park_part

    if not rest:
        raise ValueError(f"Add a park code after `{mode}`. Example: `{mode} yell`")

    # Validate park code
    park_code = rest.split()[0].lower()
    if not park_code.isalnum() or len(park_code) > 5:
        raise ValueError(
            f"`{rest}` does not look like a park code. Use a short code like `yell`, `acad`, `grca`."
        )

    return mode, park_code, custom_prompt, False  # type: ignore[return-value]


def get_history_key(mode: Mode, park_code: str) -> str:
    """Build a session history key from mode and park code."""
    return f"{mode}:{park_code}"


def store_result(
    history: dict[str, list[dict]],
    mode: Mode,
    park_code: str,
    prompt_text: str,
    result: str,
    is_custom: bool,
) -> None:
    """Store an inference result in the session history."""
    key = get_history_key(mode, park_code)
    if key not in history:
        history[key] = []
    history[key].append({
        "prompt": prompt_text,
        "result": result,
        "is_custom": is_custom,
    })


def find_default_result(
    history: dict[str, list[dict]],
    mode: Mode,
    park_code: str,
) -> dict | None:
    """Find the most recent default (non-custom) result for this mode+park."""
    key = get_history_key(mode, park_code)
    entries = history.get(key, [])
    for entry in reversed(entries):
        if not entry["is_custom"]:
            return entry
    return None


def get_model_display_name() -> str:
    """Get a short display string for the configured model."""
    try:
        _, config = make_llm_client()
        return f"{config.provider}/{config.model}"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_default_response(
    mode: Mode,
    park_code: str,
    source_text: str,
    prompt_used: str,
    llm_result: str,
    model_info: str,
) -> str:
    """Format the output for a default prompt run."""
    lines = [
        f"## {mode.upper()} -- `{park_code}`",
        "",
        "---",
        "",
        "### Source Text (NPS Data)",
        "",
        "<details>",
        "<summary>Click to expand the original text</summary>",
        "",
        source_text,
        "",
        "</details>",
        "",
        "---",
        "",
        "### **DEFAULT** Prompt Used",
        "",
        "```",
        prompt_used,
        "```",
        "",
        "---",
        "",
        "### LLM Output",
        "",
        llm_result,
        "",
        "---",
        "",
        f"*Model: {model_info}*",
        "",
        "> Want to customize? Try: `summarize yell | Summarize this in a single tweet-length paragraph`",
    ]
    return "\n".join(lines)


def format_custom_response(
    mode: Mode,
    park_code: str,
    source_text: str,
    custom_prompt: str,
    default_prompt: str,
    llm_result: str,
    previous_default: dict | None,
    model_info: str,
) -> str:
    """Format the output for a custom prompt run, optionally showing side-by-side."""
    lines = [
        f"## {mode.upper()} -- `{park_code}` -- **CUSTOM** Prompt",
        "",
        "---",
        "",
        "### Source Text (NPS Data)",
        "",
        "<details>",
        "<summary>Click to expand the original text</summary>",
        "",
        source_text,
        "",
        "</details>",
        "",
        "---",
        "",
        "### Prompt Comparison",
        "",
        "**Default prompt:**",
        "",
        "```",
        default_prompt,
        "```",
        "",
        "**Your custom prompt:**",
        "",
        "```",
        custom_prompt,
        "```",
        "",
        "---",
    ]

    # Side-by-side with previous default if available
    if previous_default:
        lines += [
            "",
            "### Output Comparison",
            "",
            "| | Output |",
            "|---|---|",
            f"| **Default** | {previous_default['result'][:300]}{'...' if len(previous_default['result']) > 300 else ''} |",
            f"| **Custom** | {llm_result[:300]}{'...' if len(llm_result) > 300 else ''} |",
            "",
            "---",
            "",
            "### Full Custom Output",
            "",
            llm_result,
        ]
    else:
        lines += [
            "",
            "### Custom LLM Output",
            "",
            llm_result,
            "",
            "---",
            "",
            "*Run the default prompt first (`{0} {1}`) to see both outputs side by side!*".format(
                mode, park_code
            ),
        ]

    lines += [
        "",
        "---",
        "",
        f"*Model: {model_info}*",
    ]
    return "\n".join(lines)


def format_compare_response(
    park_code: str,
    source_text: str,
    results: list[tuple[str, str, str]],
    model_info: str,
) -> str:
    """Format the output for the compare command showing 3 prompt variants."""
    lines = [
        f"## COMPARE -- `{park_code}`",
        "",
        "See how **3 different prompts** transform the same source text into very different outputs.",
        "",
        "---",
        "",
        "### Source Text (NPS Data)",
        "",
        "<details>",
        "<summary>Click to expand the original text</summary>",
        "",
        source_text,
        "",
        "</details>",
        "",
        "---",
    ]

    for label, prompt_text, output in results:
        lines += [
            "",
            f"### Prompt: **{label}**",
            "",
            "```",
            prompt_text,
            "```",
            "",
            "**Output:**",
            "",
            output,
            "",
            "---",
        ]

    lines += [
        "",
        f"*Model: {model_info}*",
        "",
        "> Notice how the same source text produces very different outputs depending on the prompt. "
        "Try your own: `summarize yell | Your custom prompt here`",
    ]
    return "\n".join(lines)


def format_prompts_list() -> str:
    """Format the list of all default prompt templates."""
    lines = [
        "## Default Prompt Templates",
        "",
        "These are the built-in prompts used by each mode. Override any of them "
        "with the pipe syntax: `summarize yell | Your custom prompt here`",
        "",
        "---",
    ]
    for mode in ALL_MODES:
        lines += [
            "",
            f"### **{mode}**",
            "",
            "```",
            PROMPT_TEMPLATES[mode],
            "```",
            "",
            "---",
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Chat handlers
# ---------------------------------------------------------------------------

@cl.on_chat_start
async def on_chat_start() -> None:
    """Send welcome message and initialize session state."""
    cl.user_session.set(SESSION_HISTORY, {})
    await cl.Message(content=WELCOME_MESSAGE).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle incoming user messages."""
    raw = message.content.strip()
    if not raw:
        return

    try:
        mode, park_code, custom_prompt, is_compare = parse_message(raw)
    except ValueError as exc:
        await cl.Message(content=f"**Input error:** {exc}").send()
        return

    # "prompts" command
    if mode is None and not park_code and not is_compare:
        await cl.Message(content=format_prompts_list()).send()
        return

    # "compare" command
    if is_compare:
        await _handle_compare(park_code)
        return

    # Standard mode command (with optional custom prompt)
    assert mode is not None
    await _handle_mode(mode, park_code, custom_prompt)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def _handle_mode(mode: Mode, park_code: str, custom_prompt: str | None) -> None:
    """Handle a standard mode command with optional custom prompt override."""
    history: dict = cl.user_session.get(SESSION_HISTORY, {})
    model_display = get_model_display_name()

    # Fetch source text
    try:
        await cl.Message(content=f"**Fetching data for `{park_code.upper()}`...**").send()
        source_text = fetch_park_text(park_code)
    except Exception as exc:
        await cl.Message(content=f"**Error fetching park data:** {exc}").send()
        return

    # Determine which prompt to use
    default_prompt = PROMPT_TEMPLATES[mode]
    is_custom = custom_prompt is not None
    prompt_used = custom_prompt if is_custom else default_prompt

    # Run inference
    try:
        await cl.Message(content="**Sending to LLM...**").send()
        llm_result = run_inference(mode, source_text, custom_prompt)
    except Exception as exc:
        await cl.Message(content=f"**LLM error:** {exc}").send()
        return

    # Store result in session history
    store_result(history, mode, park_code, prompt_used, llm_result, is_custom)
    cl.user_session.set(SESSION_HISTORY, history)

    # Format and send response
    if is_custom:
        previous_default = find_default_result(history, mode, park_code)
        response_md = format_custom_response(
            mode=mode,
            park_code=park_code,
            source_text=source_text,
            custom_prompt=custom_prompt,
            default_prompt=default_prompt,
            llm_result=llm_result,
            previous_default=previous_default,
            model_info=model_display,
        )
    else:
        response_md = format_default_response(
            mode=mode,
            park_code=park_code,
            source_text=source_text,
            prompt_used=prompt_used,
            llm_result=llm_result,
            model_info=model_display,
        )

    await cl.Message(content=response_md).send()


async def _handle_compare(park_code: str) -> None:
    """Handle the compare command: run 3 different prompts on the same text."""
    history: dict = cl.user_session.get(SESSION_HISTORY, {})
    model_display = get_model_display_name()

    # Fetch source text once
    try:
        await cl.Message(content=f"**Running 3 prompts on `{park_code.upper()}`...**").send()
        source_text = fetch_park_text(park_code)
    except Exception as exc:
        await cl.Message(content=f"**Error fetching park data:** {exc}").send()
        return

    results: list[tuple[str, str, str]] = []

    for label, override_prompt in COMPARE_PROMPTS:
        # Determine the actual prompt text to use
        if override_prompt is None:
            prompt_text = PROMPT_TEMPLATES["summarize"]
        else:
            prompt_text = override_prompt

        await cl.Message(content=f"**Running prompt: {label}...**").send()

        try:
            # For the default, use summarize mode; for overrides, pass them as custom prompts
            output = run_inference("summarize", source_text, override_prompt)
        except Exception as exc:
            output = f"*Error: {exc}*"

        results.append((label, prompt_text, output))

    # Store all results
    for label, prompt_text, output in results:
        is_custom = label != "default"
        store_result(
            history, "summarize", park_code, prompt_text, output, is_custom
        )
    cl.user_session.set(SESSION_HISTORY, history)

    # Format and send comparison
    response_md = format_compare_response(
        park_code=park_code,
        source_text=source_text,
        results=results,
        model_info=model_display,
    )
    await cl.Message(content=response_md).send()
