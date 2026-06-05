"""Level 0 demo: fetch one National Park Service park record.

This is intentionally not an AI demo. It proves that Python, environment
variables, HTTP requests, and the NPS API key are working.
"""

from __future__ import annotations

import argparse

from dotenv import load_dotenv

try:
    from levels.nps_client import fetch_park, format_park_summary
except ModuleNotFoundError:
    from nps_client import fetch_park, format_park_summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--park-code", default="yell", help="NPS park code, for example yell, acad, grca")
    args = parser.parse_args()

    load_dotenv()
    park = fetch_park(args.park_code.strip().lower())
    print(format_park_summary(park))


if __name__ == "__main__":
    main()
