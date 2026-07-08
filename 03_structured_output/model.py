from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentAnalysis(BaseModel):
    """Structured output model for an incident/log analysis result."""

    problem_summary: str = Field(description="A short summary of the problem")
    severity: Severity = Field(description="Estimated severity level")
    possible_root_causes: List[str] = Field(description="Possible root causes")
    next_steps: List[str] = Field(description="Recommended troubleshooting steps")
    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score between 0 and 1",
    )


if __name__ == "__main__":
    example = IncidentAnalysis(
        problem_summary="Service returns 500 errors after deployment.",
        severity=Severity.HIGH,
        possible_root_causes=[
            "Database connection pool exhausted",
            "A required environment variable is missing",
            "New deployment introduced an incompatible config change",
        ],
        next_steps=[
            "Check recent deployment diff and config changes",
            "Inspect application logs around the first 500 error",
            "Verify database connection metrics and error rate",
        ],
        confidence=0.82,
    )

    print(example.model_dump_json(indent=2))
