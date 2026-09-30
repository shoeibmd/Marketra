from typing import Any, Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_type: Literal["news_article", "filing", "financial_statement", "quote", "financial_event"]
    source_id: str
    snippet: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    url: str | None = None


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


class CompanyRoleMapping(BaseModel):
    company_name: str
    symbol: str | None = None
    role: Literal[
        "PRIMARY_SUBJECT",
        "ACQUIRER",
        "TARGET",
        "INVESTOR",
        "INVESTEE",
        "PARTNER",
        "CUSTOMER",
        "SUPPLIER",
        "COMPETITOR",
        "SUBSIDIARY",
        "REGULATOR",
        "LENDER",
        "BORROWER",
        "OTHER",
    ] = "PRIMARY_SUBJECT"
    relationship_note: str | None = None


class StructuredFinancialEvent(BaseModel):
    """Phase 10: Extracted Structured Financial Event."""

    event_type: Literal[
        "ACQUISITION",
        "MERGER",
        "INVESTMENT",
        "FUNDRAISING",
        "PARTNERSHIP",
        "NEW_PROJECT",
        "EXPANSION",
        "CAPACITY_EXPANSION",
        "CONTRACT",
        "ORDER",
        "TENDER",
        "PRODUCT_LAUNCH",
        "RESULTS",
        "REVENUE_UPDATE",
        "PROFIT_UPDATE",
        "DIVIDEND",
        "BUYBACK",
        "BONUS",
        "STOCK_SPLIT",
        "MANAGEMENT_CHANGE",
        "BOARD_CHANGE",
        "REGULATORY_ACTION",
        "LEGAL_ACTION",
        "RATING_CHANGE",
        "DEBT",
        "FUNDING",
        "IPO",
        "STAKE_SALE",
        "STAKE_PURCHASE",
        "SUBSIDIARY_EVENT",
        "JOINT_VENTURE",
        "STRATEGIC_UPDATE",
        "ESG_EVENT",
        "CYBERSECURITY_EVENT",
        "OTHER",
        "UNKNOWN",
        "UNCLASSIFIED",
    ] = "OTHER"
    event_title: str
    event_summary: str
    primary_company: str
    primary_symbol: str | None = None
    company_roles: list[CompanyRoleMapping] = Field(default_factory=list)
    sector: str = "General Equity"
    importance: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    confidence: float = Field(0.90, ge=0.0, le=1.0)
    verified_facts: list[str] = Field(default_factory=list)
    ai_analysis_text: str
    potential_impact: Literal["POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL", "UNCLEAR"] = "NEUTRAL"
    uncertainties: list[str] = Field(default_factory=list)
    cluster_id: str | None = None


# Phase 11: AI Research Assistant Schemas
class ResearchSessionContext(BaseModel):
    company: str | None = None
    symbol: str | None = None
    sector: str | None = None
    event_type: str | None = None
    date_range: str | None = None
    last_query: str | None = None


class ResearchQueryParsed(BaseModel):
    intent: Literal[
        "COMPANY_RESEARCH",
        "EVENT_SEARCH",
        "SECTOR_RESEARCH",
        "NEWS_SUMMARY",
        "EVENT_SUMMARY",
        "COMPANY_TIMELINE",
        "COMPANY_RELATIONSHIPS",
        "MARKET_CONTEXT",
        "MULTI_COMPANY_RESEARCH",
        "SOURCE_LOOKUP",
    ] = "COMPANY_RESEARCH"
    company: str | None = None
    symbol: str | None = None
    sector: str | None = None
    event_type: str | None = None
    keyword: str | None = None
    date_range_days: int = 30
    importance: str | None = None


class SourceGroundedAnswer(BaseModel):
    answer_summary: str
    key_facts: list[str] = Field(default_factory=list)
    recent_events: list[dict[str, Any]] = Field(default_factory=list)
    ai_analysis: str
    potential_impact: str
    uncertainties: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    related_companies: list[dict[str, Any]] = Field(default_factory=list)
    market_context: dict[str, Any] | None = None
    evidence_confidence: Literal["HIGH", "MEDIUM", "LOW"] = "HIGH"
    context_used: ResearchSessionContext = Field(default_factory=ResearchSessionContext)


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    context: ResearchSessionContext | None = None


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    instrument_id: str | None = None
    top_k: int = Field(5, ge=1, le=20)


class AIDocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern="^(10-K|10-Q|NEWS|RESEARCH|NOTE)$")
    instrument_id: str | None = None
    content: str = Field(..., min_length=10)
