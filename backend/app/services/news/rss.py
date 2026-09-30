import logging
from datetime import UTC, datetime
from typing import Any

from app.services.news.base import BaseNewsProvider, NormalizedNewsItem
from app.services.news.deduplication import compute_content_hash

logger = logging.getLogger("terminal.news.rss")

FEEDS_REGISTRY = [
    {
        "source_name": "Reserve Bank of India (RBI)",
        "source_url": "https://www.rbi.org.in",
        "category": "central_bank",
        "feed_url": "https://www.rbi.org.in/rss/pressrelease.xml",
        "sample_items": [
            {
                "title": "RBI Monetary Policy Committee announces Repo Rate decision",
                "summary": "Reserve Bank of India maintains policy repo rate under Liquidity Adjustment Facility at current stance.",
                "url": "https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=58102",
                "published_at": "2025-01-15T09:30:00Z",
                "category": "monetary_policy",
            }
        ],
    },
    {
        "source_name": "Securities and Exchange Board of India (SEBI)",
        "source_url": "https://www.sebi.gov.in",
        "category": "regulator",
        "feed_url": "https://www.sebi.gov.in/sebiweb/home/rss/pressrelease.xml",
        "sample_items": [
            {
                "title": "SEBI issues framework for equity derivatives and margin requirements",
                "summary": "SEBI circular outlining enhanced risk management and position limit monitoring for NSE/BSE derivative segments.",
                "url": "https://www.sebi.gov.in/legal/circulars/jan-2025/derivatives-framework_81020.html",
                "published_at": "2025-01-14T11:00:00Z",
                "category": "regulation",
            }
        ],
    },
    {
        "source_name": "NSE Corporate Announcements",
        "source_url": "https://www.nseindia.com",
        "category": "exchange_corporate",
        "feed_url": "https://www.nseindia.com/rss/corporate_announcements.xml",
        "sample_items": [
            {
                "title": "Reliance Industries Limited - Financial Results for Q3 FY25",
                "summary": "Reliance Industries Ltd has submitted to the Exchange Q3 FY25 financial results and segment revenue report.",
                "url": "https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE#announcements",
                "published_at": "2025-01-16T12:15:00Z",
                "symbol": "RELIANCE",
                "company": "Reliance Industries Ltd",
                "exchange": "NSE",
                "category": "corporate_earnings",
            },
            {
                "title": "Tata Consultancy Services - Board Meeting Outcome and Dividend Declaration",
                "summary": "TCS announces interim dividend of INR 10 per share and board approval for Q3 strategic expansion.",
                "url": "https://www.nseindia.com/get-quotes/equity?symbol=TCS#announcements",
                "published_at": "2025-01-15T14:00:00Z",
                "symbol": "TCS",
                "company": "Tata Consultancy Services",
                "exchange": "NSE",
                "category": "corporate_actions",
            },
        ],
    },
    {
        "source_name": "BSE Public Announcements",
        "source_url": "https://www.bseindia.com",
        "category": "exchange_corporate",
        "feed_url": "https://www.bseindia.com/rss/corporate_announcements.xml",
        "sample_items": [
            {
                "title": "Infosys Limited - Press Release on AI Enterprise Contracts",
                "summary": "Infosys Ltd signs multi-year digital transformation agreement with European enterprise client.",
                "url": "https://www.bseindia.com/xml-data/corpfiling/AttachLive/infosys-press-release.pdf",
                "published_at": "2025-01-13T10:00:00Z",
                "symbol": "INFY",
                "company": "Infosys Ltd",
                "exchange": "BSE",
                "category": "business_update",
            }
        ],
    },
]


class RSSNewsProvider(BaseNewsProvider):
    """Provider for public RSS/Corporate Feed sources (NSE, BSE, SEBI, RBI)."""

    def __init__(self) -> None:
        super().__init__(provider_name="RSS_PUBLIC_FEEDS")

    async def fetch_news(self) -> list[NormalizedNewsItem]:
        normalized_items: list[NormalizedNewsItem] = []

        for feed in FEEDS_REGISTRY:
            source_name = feed["source_name"]
            source_url = feed["source_url"]

            for item in feed["sample_items"]:
                pub_time = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                symbol = item.get("symbol")
                company = item.get("company")
                exchange = item.get("exchange")
                category = item.get("category", "general")

                content_hash = compute_content_hash(item["title"], pub_time.isoformat(), company)

                norm_item = NormalizedNewsItem(
                    title=item["title"],
                    summary=item.get("summary"),
                    content=item.get("summary"),
                    source_name=source_name,
                    source_url=source_url,
                    original_url=item["url"],
                    published_at=pub_time,
                    company=company,
                    symbol=symbol,
                    exchange=exchange,
                    category=category,
                    raw_metadata={"feed_url": feed["feed_url"], "source": source_name},
                    content_hash=content_hash,
                    processing_status="normalized",
                )
                normalized_items.append(norm_item)

        return normalized_items
