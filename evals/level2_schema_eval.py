"""Level 2 schema and extraction eval harness.

Section A tests Pydantic schema validation (always runs).
Section B tests end-to-end extraction (requires extract_structured() to be implemented).
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from levels.schemas import ParkExtraction, VisitorRisk, Logistics, Severity, Confidence  # noqa: E402


def test_schema_validation() -> list[str]:
    """Test that Pydantic schemas validate correctly."""
    failures = []

    # Valid extraction should pass
    try:
        ParkExtraction(
            summary="Test summary",
            key_facts=["Fact 1", "Fact 2"],
            visitor_risks=[
                VisitorRisk(risk="Test risk", severity=Severity.high, evidence="Test evidence")
            ],
            logistics=Logistics(fees=["$30 entrance"]),
            open_questions=["What are the current trail conditions?"],
            confidence=Confidence.medium,
        )
    except Exception as e:
        failures.append(f"Valid extraction failed: {e}")

    # Missing required field should fail
    try:
        ParkExtraction(summary="Test")  # type: ignore[call-arg]
        failures.append("Missing key_facts should have failed validation")
    except Exception:
        pass  # Expected (Pydantic raises ValidationError, a subclass of ValueError)

    # Invalid severity should fail
    try:
        VisitorRisk(risk="Test", severity="extreme", evidence="Test")  # type: ignore[call-arg]
        failures.append("Invalid severity should have failed validation")
    except Exception:
        pass  # Expected

    return failures


def test_extraction() -> list[str]:
    """Test end-to-end structured extraction. TODO: implement after building extract_structured()."""
    failures = []

    # TODO: Uncomment and implement after building extract_structured()
    # from levels.level2_structured_extraction import extract_structured, fetch_source_text
    #
    # source_text = fetch_source_text("parks", "yell")
    # result = extract_structured(source_text)
    #
    # if not result.key_facts:
    #     failures.append("key_facts should not be empty")
    # if not isinstance(result.confidence, Confidence):
    #     failures.append(f"confidence should be a Confidence enum, got {type(result.confidence)}")
    # for risk in result.visitor_risks:
    #     if not risk.evidence:
    #         failures.append(f"Risk '{risk.risk}' missing evidence")
    #     if not isinstance(risk.severity, Severity):
    #         failures.append(f"Risk '{risk.risk}' has invalid severity: {risk.severity}")

    return failures


def main() -> None:
    load_dotenv()

    print("=== Section A: Schema Validation ===")
    schema_failures = test_schema_validation()
    if schema_failures:
        print("FAIL")
        for f in schema_failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print("PASS: Schema validation tests passed.\n")

    print("=== Section B: End-to-End Extraction ===")
    extraction_failures = test_extraction()
    if extraction_failures:
        print("FAIL")
        for f in extraction_failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print("PASS: Extraction tests passed.")


if __name__ == "__main__":
    main()
