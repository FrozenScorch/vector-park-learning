"""Level 1 Chainlit variant A: Side-by-side comparison of NPS source text and LLM result.

Run with:
    chainlit run levels/level1_chainlit_vA.py --port 8001

Features:
- Shows original NPS text alongside the LLM output for comparison
- Displays the exact prompt template being sent to the model
- Supports custom prompt override via --prompt flag
- Welcome message with command reference and examples
- Prominent mode name header on every response
"""

from __future__ import annotations

import re
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
        "Extract action items from the source text. Return valid JSON with this shape: "
        '{"action_items":[{"task":"string","owner":"unknown","deadline":"unknown","evidence":"string"}]}. '
        "Use unknown when the source does not say."
    ),
}

MODE_EMOJI = {
    "summarize": "clipboard",
    "rewrite": "pencil",
    "classify": "label",
    "extract": "wrench",
}

WELCOME_MESSAGE = """## Welcome to Vector Park Learning - Level 1 Variant A

This tool lets you explore **LLM inference modes** over live National Park Service data.
You will see the **original NPS text** and the **LLM result** side by side, along with
the exact prompt template sent to the model.

---

### Available Commands

| Command | What it does |
|---|---|
| `summarize <park_code>` | Summarize park info for a first-time visitor |
| `rewrite <park_code>` | Rewrite park info for a family audience |
| `classify <park_code>` | Classify what kind of visitor question the text answers |
| `extract <park_code>` | Extract action items as structured JSON |

### Custom Prompt Override

Add `--prompt "your custom prompt"` to any command to replace the default template:

```
summarize yell --prompt "Summarize in 2 sentences for kids"
```

### Examples

- `summarize yell` - Summarize Yellowstone
- `rewrite acad` - Rewrite Acadia for families
- `classify grca` - Classify Grand Canyon text
- `extract yose` - Extract action items from Yosemite
- `summarize yell --prompt "Give me 3 fun facts only"`

### Park Codes

Try: `yell` (Yellowstone), `acad` (Acadia), `grca` (Grand Canyon),
`yose` (Yosemite), `zion` (Zion), `drto` (Dry Tortugas)

---

**Type a command to get started!**
"""

load_dotenv()


def fetch_park_text(park_code: str) -> str:
    """Fetch park data from the NPS API and format it for inference."""
    park = fetch_park(park_code)
    return format_park_text_for_inference(park)


def build_user_prompt(mode: Mode, text: str, custom_prompt: str | None = None) -> str:
    """Build the full user prompt, optionally using a custom override."""
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


def parse_message(raw: str) -> tuple[Mode, str, str | None]:
    """Parse a user message into (mode, park_code_or_text, custom_prompt).

    Supports:
        summarize yell
        summarize yell --prompt "custom prompt here"
        summarize some freeform text
    """
    raw = raw.strip()
    parts = raw.split(maxsplit=1)
    if not parts or parts[0].lower() not in {"summarize", "rewrite", "classify", "extract"}:
        raise ValueError(
            "Start your message with `summarize`, `rewrite`, `classify`, or `extract`."
        )
    if len(parts) == 1:
        raise ValueError("Add a park code (e.g. `yell`) or text after the mode.")

    mode = parts[0].lower()
    rest = parts[1].strip()

    # Check for --prompt override
    custom_prompt = None
    prompt_match = re.search(r'--prompt\s+"([^"]+)"', rest)
    if not prompt_match:
        prompt_match = re.search(r"--prompt\s+'([^']+)'", rest)
    if prompt_match:
        custom_prompt = prompt_match.group(1)
        rest = rest[: prompt_match.start()].strip() + " " + rest[prompt_match.end() :].strip()
        rest = rest.strip()

    if not rest:
        raise ValueError("Add a park code (e.g. `yell`) or text after the mode.")

    return mode, rest, custom_prompt  # type: ignore[return-value]


def is_park_code(value: str) -> bool:
    """Heuristic: short alphanumeric strings are likely park codes."""
    return len(value) <= 5 and value.isalnum()


def format_response(
    mode: Mode,
    source_text: str,
    llm_result: str,
    park_code: str | None = None,
    custom_prompt: str | None = None,
    model_info: str = "",
) -> str:
    """Build the side-by-side comparison markdown response."""
    mode_label = mode.upper()
    template_used = custom_prompt if custom_prompt else PROMPT_TEMPLATES[mode]
    template_source = "custom override" if custom_prompt else "default template"

    header = f"## {mode_label} Mode"
    if park_code:
        header += f" - `{park_code}`"

    sections = [
        header,
        "",
        "---",
        "",
        "### Prompt Template",
        f"*{template_source}*",
        "",
        "```",
        template_used,
        "```",
        "",
        "---",
        "",
        "### Source Text (NPS Data)",
        "",
        source_text,
        "",
        "---",
        "",
        "### LLM Result",
        "",
        llm_result,
    ]

    if model_info:
        sections += [
            "",
            "---",
            "",
            f"*Model: {model_info}*",
        ]

    return "\n".join(sections)


def get_model_display_name() -> str:
    """Get a short display string for the configured model."""
    try:
        _, config = make_llm_client()
        return f"{config.provider}/{config.model}"
    except Exception:
        return "unknown"


@cl.on_chat_start
async def on_chat_start() -> None:
    """Send welcome message when the chat starts."""
    await cl.Message(content=WELCOME_MESSAGE).send()


@cl.on_message
async def main(message: cl.Message) -> None:
    """Handle incoming user messages."""
    try:
        mode, value, custom_prompt = parse_message(message.content)

        # Determine source text: park code or freeform text
        park_code = None
        if is_park_code(value):
            park_code = value.lower()
            source_text = fetch_park_text(park_code)
        else:
            source_text = value

        # Run inference
        llm_result = run_inference(mode, source_text, custom_prompt)

        # Get model info for display
        model_display = get_model_display_name()

    except ValueError as exc:
        await cl.Message(content=f"**Input error:** {exc}").send()
        return
    except Exception as exc:
        await cl.Message(content=f"**Error:** {exc}").send()
        return

    # Format and send the comparison response
    response_md = format_response(
        mode=mode,
        source_text=source_text,
        llm_result=llm_result,
        park_code=park_code,
        custom_prompt=custom_prompt,
        model_info=model_display,
    )
    await cl.Message(content=response_md).send()
