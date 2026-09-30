import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument

COMPANY_ALIASES: dict[str, list[str]] = {
    "RELIANCE": ["RELIANCE INDUSTRIES", "RIL", "RELIANCE INDUSTRIES LTD", "RELIANCE INDUSTRIES LIMITED"],
    "TCS": ["TATA CONSULTANCY SERVICES", "TATA CONSULTANCY", "TCS LTD"],
    "INFY": ["INFOSYS", "INFOSYS LTD", "INFOSYS LIMITED"],
    "HDFCBANK": ["HDFC BANK", "HDFC BANK LTD", "HOUSING DEVELOPMENT FINANCE CORPORATION"],
    "ICICIBANK": ["ICICI BANK", "ICICI BANK LTD"],
    "SBIN": ["STATE BANK OF INDIA", "SBI"],
    "BHARTIARTL": ["BHARTI AIRTEL", "AIRTEL", "BHARTI AIRTEL LTD"],
    "ITC": ["ITC LTD", "ITC LIMITED"],
    "KOTAKBANK": ["KOTAK MAHINDRA BANK", "KOTAK BANK"],
    "LT": ["LARSEN TOUBRO", "LARSEN AND TOUBRO", "L&T", "LT LTD"],
}

COMPANY_SECTORS: dict[str, str] = {
    "RELIANCE": "Energy / Conglomerate",
    "TCS": "Information Technology",
    "INFY": "Information Technology",
    "HDFCBANK": "Financial Services / Banking",
    "ICICIBANK": "Financial Services / Banking",
    "SBIN": "Financial Services / Banking",
    "BHARTIARTL": "Telecommunications",
    "ITC": "Fast Moving Consumer Goods",
    "KOTAKBANK": "Financial Services / Banking",
    "LT": "Engineering & Construction",
    "AXISBANK": "Financial Services / Banking",
    "ASIANPAINT": "Consumer Durables",
    "MARUTI": "Automobile",
    "TITAN": "Consumer Durables",
    "BAJFINANCE": "Financial Services / NBFC",
}


def normalize_text(text: str) -> str:
    """Clean and normalize string for matching."""
    cleaned = re.sub(r"[^\w\s]", " ", text.upper())
    return " ".join(cleaned.split())


class CompanyMatcher:
    """Matches news article text to one or multiple instruments across the Indian universe."""

    @staticmethod
    async def match_instruments(
        title: str,
        content: str | None,
        db_session: AsyncSession,
        hint_symbol: str | None = None,
        hint_isin: str | None = None,
    ) -> list[tuple[uuid.UUID, str, str | None, float]]:
        """Extract matching instruments and return list of (instrument_id, symbol, sector, relevance_score)."""
        combined_text = normalize_text(f"{title} {content or ''}")
        matches: dict[uuid.UUID, tuple[str, str | None, float]] = {}

        # 1. Direct ISIN match
        if hint_isin:
            stmt = select(Instrument).where(Instrument.isin == hint_isin.upper().strip())
            res = await db_session.execute(stmt)
            inst = res.scalar_one_or_none()
            if inst:
                sector = inst.sector or COMPANY_SECTORS.get(inst.symbol, "General Equity")
                matches[inst.id] = (inst.symbol, sector, 1.0)

        # 2. Query active instruments from database
        stmt_all = select(Instrument).where(Instrument.is_active == True)  # noqa: E712
        res_all = await db_session.execute(stmt_all)
        instruments = res_all.scalars().all()

        for inst in instruments:
            sym = inst.symbol.upper()
            comp_name = normalize_text(inst.name)
            sector = inst.sector or COMPANY_SECTORS.get(sym, "General Equity")

            score = 0.0

            # Match symbol boundary or explicit hint
            if hint_symbol and hint_symbol.upper() == sym:
                score = max(score, 1.0)

            # Match whole word symbol in text
            if re.search(r"\b" + re.escape(sym) + r"\b", combined_text):
                score = max(score, 0.95)

            # Match company full name
            if comp_name in combined_text:
                score = max(score, 0.90)

            # Match known aliases
            aliases = COMPANY_ALIASES.get(sym, [])
            for alias in aliases:
                norm_alias = normalize_text(alias)
                if norm_alias in combined_text:
                    score = max(score, 0.85)

            if score > 0.5:
                matches[inst.id] = (sym, sector, score)

        return [(inst_id, data[0], data[1], data[2]) for inst_id, data in matches.items()]
