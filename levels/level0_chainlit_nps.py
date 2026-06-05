"""Level 0 Chainlit demo: type a park code and see live NPS data."""

from __future__ import annotations

import chainlit as cl
from dotenv import load_dotenv

try:
    from levels.nps_client import fetch_park
except ModuleNotFoundError:
    from nps_client import fetch_park


load_dotenv()


@cl.on_message
async def main(message: cl.Message) -> None:
    park_code = message.content.strip().lower()
    if not park_code:
        await cl.Message(content="Type a park code like `yell`, `acad`, or `grca`.").send()
        return

    try:
        park = fetch_park(park_code)
    except Exception as exc:
        await cl.Message(content=f"Could not fetch park data: {exc}").send()
        return

    content = f"""## {park.get('fullName', 'Unknown park')}

**Park code:** `{park.get('parkCode', park_code)}`

**States:** {park.get('states', 'Unknown')}

{park.get('description') or 'No description returned.'}

**Weather notes:** {park.get('weatherInfo') or 'No weather info returned.'}
"""
    await cl.Message(content=content).send()
