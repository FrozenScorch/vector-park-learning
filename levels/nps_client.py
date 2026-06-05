"""Shared National Park Service API helpers for the curriculum demos."""

from __future__ import annotations

import os
from typing import Any

import requests


NPS_BASE_URL = "https://developer.nps.gov/api/v1"


def get_nps_api_key() -> str:
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        raise RuntimeError("Missing NPS_API_KEY. Add it to your .env file.")
    return api_key


def fetch_park(park_code: str) -> dict[str, Any]:
    response = requests.get(
        f"{NPS_BASE_URL}/parks",
        params={"parkCode": park_code, "limit": 1},
        headers={"X-Api-Key": get_nps_api_key()},
        timeout=20,
    )
    response.raise_for_status()

    parks = response.json().get("data", [])
    if not parks:
        raise RuntimeError(f"No park found for park code '{park_code}'. Try yell, acad, or grca.")

    return parks[0]


def format_park_summary(park: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Name: {park.get('fullName', 'Unknown')}",
            f"Park code: {park.get('parkCode', 'Unknown')}",
            f"States: {park.get('states', 'Unknown')}",
            "",
            "Description:",
            park.get("description") or "No description returned.",
            "",
            "Weather:",
            park.get("weatherInfo") or "No weather info returned.",
        ]
    )


def format_park_text_for_inference(park: dict[str, Any]) -> str:
    fields = [
        f"Park: {park.get('fullName', 'Unknown')}",
        f"Description: {park.get('description', '')}",
        f"Weather: {park.get('weatherInfo', '')}",
    ]
    return "\n\n".join(field for field in fields if field.strip())

