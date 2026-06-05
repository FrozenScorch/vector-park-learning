"""Pydantic schemas for Level 2 structured extraction."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    unknown = "unknown"


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class VisitorRisk(BaseModel):
    """A single risk extracted from park or alert text."""

    risk: str = Field(description="Short description of the risk")
    severity: Severity = Field(description="Assessed severity level")
    evidence: str = Field(description="Exact quote or paraphrase from the source text supporting this risk")


class Logistics(BaseModel):
    """Logistical details extracted from source text."""

    fees: list[str] = Field(default_factory=list, description="Entrance fees, camping fees, etc.")
    locations: list[str] = Field(default_factory=list, description="Named locations mentioned")
    hours: list[str] = Field(default_factory=list, description="Operating hours or seasons")
    reservation_notes: list[str] = Field(default_factory=list, description="Reservation requirements or notes")


class ParkExtraction(BaseModel):
    """Complete structured extraction from a single NPS document."""

    summary: str = Field(description="One-paragraph summary of the source document")
    key_facts: list[str] = Field(description="3-5 key facts extracted from the text")
    visitor_risks: list[VisitorRisk] = Field(default_factory=list, description="Risks identified in the text")
    logistics: Logistics = Field(default_factory=Logistics)
    open_questions: list[str] = Field(default_factory=list, description="Important questions the source text does not answer")
    confidence: Confidence = Field(description="Overall confidence in the extraction")
