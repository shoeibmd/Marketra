from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_type: Literal["news_article", "filing", "financial_statement", "quote"]
    source_id: str
    snippet: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class AIResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    model_used: str
    source_facts: list[str] = Field(default_factory=list)
    calculated_metrics: list[str] = Field(default_factory=list)
    interpretation: list[str] = Field(default_factory=list)


class NewsAIAnalysis(BaseModel):
    """Structured AI Analysis for Live News Intelligence."""

    what_happened: str
    primary_company_affected: str
    related_companies: list[str] = Field(default_factory=list)
    event_category: str
    importance_reason: str
    source_facts: list[str] = Field(default_factory=list)
    potential_impact: Literal["POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL", "UNCLEAR"]
    importance_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    ai_confidence: float = Field(..., ge=0.0, le=1.0)
    user_monitoring_checklist: list[str] = Field(default_factory=list)
    related_sector: str
    related_announcements: list[str] = Field(default_factory=list)
    uncertainties_or_gaps: list[str] = Field(default_factory=list)
    model_used: str = "mock-financial-rag-v1"


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    instrument_id: str | None = None
    top_k: int = Field(5, ge=1, le=20)


class AIDocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern="^(10-K|10-Q|NEWS|RESEARCH|NOTE)$")
    instrument_id: str | None = None
    content: str = Field(..., min_length=10)
