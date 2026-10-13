from enum import Enum
from pydantic import BaseModel, Field, field_validator


class RiskCategory(str, Enum):
    UNACCEPTABLE = "unacceptable_risk"
    HIGH = "high_risk"
    LIMITED = "limited_risk"
    MINIMAL = "minimal_risk"


class UseCase(str, Enum):
    SOCIAL_SCORING = "social_scoring"
    COGNITIVE_MANIPULATION = "cognitive_manipulation"
    BIOMETRIC_SURVEILLANCE = "biometric_surveillance"
    GENERAL_PURPOSE = "general_purpose"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    LAW_ENFORCEMENT = "law_enforcement"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    CONTENT_GENERATION = "content_generation"
    CODE_GENERATION = "code_generation"
    RESEARCH = "research"


class RedTeamingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TrainingData(BaseModel):
    source: str
    quality_score: float = Field(ge=0.0, le=1.0)
    size_tokens: float = Field(gt=0)
    documentation_status: str


class BiasAssessment(BaseModel):
    methodology: str
    status: str
    score: float = Field(ge=0.0, le=1.0)


class PerformanceMetrics(BaseModel):
    f1_score: float = Field(ge=0.0, le=1.0)
    benchmark: str
    task: str


class SecurityMeasures(BaseModel):
    access_control: str
    audit_logging: bool


class GovernanceFacts(BaseModel):
    training_data: TrainingData
    bias_assessment: BiasAssessment
    performance: PerformanceMetrics
    security: SecurityMeasures


class ModelEntry(BaseModel):
    """Schema for a single AI model's metadata."""
    model_id: str = Field(pattern=r"^[a-z0-9_]+$")
    organization: str
    compute_flops: float = Field(ge=0)
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_category: RiskCategory
    use_case: UseCase
    red_teaming_status: RedTeamingStatus
    deployment_regions: list[str] = Field(min_length=1)
    capabilities: list[str] = Field(min_length=1)
    governance: GovernanceFacts

    @field_validator("deployment_regions")
    @classmethod
    def validate_regions(cls, v: list[str]) -> list[str]:
        valid = {"eu", "us", "uk", "cn", "jp", "kr", "in", "br", "au", "ca", "global"}
        for region in v:
            if region not in valid:
                raise ValueError(f"Invalid region '{region}'. Valid: {valid}")
        return v
