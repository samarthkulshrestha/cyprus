from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RiskCategory(str, Enum):
    UNACCEPTABLE = "unacceptable_risk"
    HIGH = "high_risk"
    LIMITED = "limited_risk"
    MINIMAL = "minimal_risk"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PROHIBITED = "prohibited"
    REQUIRES_ACTION = "requires_action"


@dataclass(frozen=True)
class Violation:
    """A single compliance violation or unmet requirement."""
    article: str          # e.g., "art5_1a"
    title: str            # e.g., "Article 5(1)(a)"
    reason: str           # Human-readable explanation
    severity: str         # "prohibited", "required", "recommended"


@dataclass(frozen=True)
class ModelCompliance:
    """Compliance assessment for a single model."""
    model_id: str
    status: ComplianceStatus
    prohibited: list[Violation] = field(default_factory=list)
    unmet_requirements: list[Violation] = field(default_factory=list)
    systemic_risk: bool = False
    high_risk: bool = False
    transparency_required: bool = False
    can_deploy: bool = False

    @property
    def violation_count(self) -> int:
        return len(self.prohibited) + len(self.unmet_requirements)


@dataclass(frozen=True)
class ComplianceResult:
    """Complete compliance assessment for all models."""
    models: dict[str, ModelCompliance]
    policy_name: str
    policy_version: str
    timestamp: datetime
    articles_evaluated: list[str]

    @property
    def total_models(self) -> int:
        return len(self.models)

    @property
    def prohibited_count(self) -> int:
        return sum(1 for m in self.models.values() if m.status == ComplianceStatus.PROHIBITED)

    @property
    def compliant_count(self) -> int:
        return sum(1 for m in self.models.values() if m.can_deploy)
