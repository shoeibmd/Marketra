# Phase 11 — AI Financial Research Assistant Architecture

## Overview
Marketra Phase 11 introduces a source-grounded AI Financial Research Assistant:
```text
USER QUESTION -> QUERY PARSER -> RAG MULTI-SOURCE RETRIEVAL -> EVIDENCE RANKING -> AI PROMPT ENRICHMENT -> GROUNDED RESPONSE & CITATIONS
```

## Supported Query Intents
- `COMPANY_RESEARCH`
- `EVENT_SEARCH`
- `SECTOR_RESEARCH`
- `NEWS_SUMMARY`
- `EVENT_SUMMARY`
- `COMPANY_TIMELINE`
- `COMPANY_RELATIONSHIPS`
- `MARKET_CONTEXT`
- `MULTI_COMPANY_RESEARCH`
- `SOURCE_LOOKUP`

## Conversational Follow-Up Context
Maintains lightweight `ResearchSessionContext` (symbol, company, sector, event_type, date_range) allowing natural follow-ups such as *"Show only acquisitions"* without repeating the company name.

## Prompt Injection & Hallucination Protections
- Retrieved article text is treated as untrusted DATA, stripping instruction hijacking phrases.
- Facts and AI analysis are explicitly separated.
- When no database evidence matches, the assistant outputs *"Insufficient information available in current database records"*.
