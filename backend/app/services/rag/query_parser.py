import re
from app.schemas.ai import ResearchQueryParsed, ResearchSessionContext

INDIAN_SECTORS = [
    "BANKING",
    "IT",
    "SOFTWARE",
    "AUTOMOBILE",
    "PHARMA",
    "ENERGY",
    "METALS",
    "TELECOM",
    "FMCG",
    "INFRASTRUCTURE",
    "REAL ESTATE",
    "FINANCIAL SERVICES",
]

EVENT_KEYWORDS = {
    "ACQUISITION": ["ACQUISITION", "ACQUIRE", "ACQUIRED", "BUYOUT", "TAKEOVER"],
    "MERGER": ["MERGER", "MERGE", "AMALGAMATION"],
    "INVESTMENT": ["INVESTMENT", "INVESTED", "FUNDING", "RAISED", "CAPITAL"],
    "CONTRACT": ["CONTRACT", "ORDER", "AGREEMENT", "DEAL", "TENDER"],
    "RESULTS": ["RESULTS", "EARNINGS", "PROFIT", "REVENUE", "Q1", "Q2", "Q3", "Q4", "QUARTERLY"],
    "DIVIDEND": ["DIVIDEND", "PAYOUT", "BONUS"],
    "REGULATORY_ACTION": ["REGULATORY", "SEBI", "RBI", "CIRCULAR", "PENALTY", "COMPLIANCE"],
}

SYMBOL_ALIASES = {
    "RELIANCE": "RELIANCE",
    "RIL": "RELIANCE",
    "TCS": "TCS",
    "INFY": "INFY",
    "INFOSYS": "INFY",
    "HDFC": "HDFCBANK",
    "HDFCBANK": "HDFCBANK",
    "ICICI": "ICICIBANK",
    "ICICIBANK": "ICICIBANK",
    "SBI": "SBIN",
    "SBIN": "SBIN",
    "AIRTEL": "BHARTIARTL",
    "BHARTIARTL": "BHARTIARTL",
    "ITC": "ITC",
    "KOTAK": "KOTAKBANK",
    "LT": "LT",
    "LARSEN": "LT",
}


class ResearchQueryParser:
    """Parses natural language financial queries into structured intent and filters with context resolution."""

    @staticmethod
    def parse_query(query: str, previous_context: ResearchSessionContext | None = None) -> ResearchQueryParsed:
        q_upper = query.upper().strip()

        # 1. Date Range Extraction
        days = 30
        if "TODAY" in q_upper:
            days = 1
        elif "YESTERDAY" in q_upper:
            days = 2
        elif "LAST 7 DAYS" in q_upper or "THIS WEEK" in q_upper:
            days = 7
        elif "LAST 30 DAYS" in q_upper or "THIS MONTH" in q_upper:
            days = 30
        elif "THIS QUARTER" in q_upper:
            days = 90

        # 2. Symbol / Company Resolution
        found_symbol = None
        for alias, sym in SYMBOL_ALIASES.items():
            if re.search(r"\b" + re.escape(alias) + r"\b", q_upper):
                found_symbol = sym
                break

        # Fallback to previous context if user asks follow-up (e.g., "Show only acquisitions")
        if not found_symbol and previous_context and previous_context.symbol:
            found_symbol = previous_context.symbol

        # 3. Sector Extraction
        found_sector = None
        for sec in INDIAN_SECTORS:
            if sec in q_upper:
                found_sector = sec
                break
        if not found_sector and previous_context and previous_context.sector:
            found_sector = previous_context.sector

        # 4. Event Type Extraction
        found_event_type = None
        for ev_type, kws in EVENT_KEYWORDS.items():
            if any(kw in q_upper for kw in kws):
                found_event_type = ev_type
                break
        if not found_event_type and previous_context and previous_context.event_type:
            found_event_type = previous_context.event_type

        # 5. Intent Determination
        intent = "COMPANY_RESEARCH"
        if "COMPARE" in q_upper or "VS" in q_upper:
            intent = "MULTI_COMPANY_RESEARCH"
        elif found_sector and not found_symbol:
            intent = "SECTOR_RESEARCH"
        elif found_event_type and not found_symbol:
            intent = "EVENT_SEARCH"
        elif "TIMELINE" in q_upper or "HISTORY" in q_upper:
            intent = "COMPANY_TIMELINE"
        elif "RELATIONSHIP" in q_upper or "NETWORK" in q_upper:
            intent = "COMPANY_RELATIONSHIPS"

        return ResearchQueryParsed(
            intent=intent,  # type: ignore[arg-type]
            symbol=found_symbol,
            company=found_symbol or previous_context.company if previous_context else None,
            sector=found_sector,
            event_type=found_event_type,
            date_range_days=days,
        )
