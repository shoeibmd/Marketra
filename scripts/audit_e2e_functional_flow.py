import asyncio
import json
import logging
import sys
from decimal import Decimal
from uuid import uuid4

sys.path.insert(0, "backend")

from httpx import ASGITransport, AsyncClient
from main import app
from app.db.session import PostgresSessionLocal
from app.models.domain import User, Instrument, PaperTradingAccount, PaperPosition, PaperTrade, Quote, OHLCV, NewsArticle, FinancialEvent
from app.core.auth.jwt_handler import create_access_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_e2e")


async def run_e2e_audit():
    logger.info("Starting End-to-End Functional Validation Audit...")
    results = {}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. SETUP TEST USER & AUTH
        async with PostgresSessionLocal() as db:
            user = User(
                id=uuid4(),
                email=f"e2e_audit_{uuid4().hex[:6]}@example.com",
                hashed_password="hashed_password",
                full_name="E2E Auditor",
                role="user",
            )
            db.add(user)

            # Seed Indian Instruments
            inst_tcs = Instrument(
                id=uuid4(),
                symbol="TCS",
                name="Tata Consultancy Services Ltd",
                exchange_code="NSE",
                instrument_type="EQUITY",
                sector="IT",
                currency="INR",
            )
            inst_rel = Instrument(
                id=uuid4(),
                symbol="RELIANCE",
                name="Reliance Industries Ltd",
                exchange_code="NSE",
                instrument_type="EQUITY",
                sector="Energy",
                currency="INR",
            )
            inst_infy = Instrument(
                id=uuid4(),
                symbol="INFY",
                name="Infosys Ltd",
                exchange_code="NSE",
                instrument_type="EQUITY",
                sector="IT",
                currency="INR",
            )
            db.add_all([inst_tcs, inst_rel, inst_infy])

            # Seed Paper Account & Positions
            account = PaperTradingAccount(
                id=uuid4(),
                user_id=user.id,
                name="E2E Paper Account",
                initial_cash=Decimal("1000000.00"),
                available_cash=Decimal("500000.00"),
                portfolio_type="PAPER",
            )
            db.add(account)
            await db.flush()

            pos = PaperPosition(
                id=uuid4(),
                account_id=account.id,
                instrument_id=inst_tcs.id,
                quantity=Decimal("100.00"),
                average_entry_price=Decimal("3500.00"),
            )
            db.add(pos)
            await db.commit()

            token = create_access_token({"sub": user.email, "email": user.email, "role": user.role})
            headers = {"Authorization": f"Bearer {token}"}

        # --- A. AUTHENTICATION ---
        res_me = await client.get("/api/v1/auth/me", headers=headers)
        results["A_Authentication"] = "PASS" if res_me.status_code == 200 else "FAIL"

        # --- B. COMPANY / INSTRUMENT SEARCH ---
        res_search_tcs = await client.get("/api/v1/instruments/search?q=TCS", headers=headers)
        res_search_rel = await client.get("/api/v1/instruments/search?q=RELIANCE", headers=headers)
        res_search_invalid = await client.get("/api/v1/instruments/search?q=ABCXYZ123", headers=headers)

        tcs_found = len(res_search_tcs.json()) >= 1 if res_search_tcs.status_code == 200 else False
        invalid_clean = len(res_search_invalid.json()) == 0 if res_search_invalid.status_code == 200 else False

        results["B_Instrument_Search"] = "PASS" if (tcs_found and invalid_clean) else "FAIL"

        # --- C. COMPANY DETAILS & MARKET DATA ---
        res_inst_detail = await client.get("/api/v1/instruments/TCS", headers=headers)
        res_quote = await client.get("/api/v1/instruments/TCS/quote", headers=headers)
        res_ohlcv = await client.get("/api/v1/market/ohlcv/TCS?interval=1d&days_back=30", headers=headers)

        results["C_Company_Details_Market_Data"] = (
            "PASS"
            if (res_inst_detail.status_code == 200 and res_quote.status_code == 200 and res_ohlcv.status_code == 200)
            else "FAIL"
        )

        # --- D. NEWS SEARCH & COMPANY NEWS ---
        res_news_tcs = await client.get("/api/v1/news?symbol=TCS", headers=headers)
        results["D_Company_News"] = "PASS" if res_news_tcs.status_code == 200 else "FAIL"

        # --- E. FINANCIAL EVENTS & MARKET CONTEXT ---
        res_events = await client.get("/api/v1/events", headers=headers)
        results["E_Financial_Events"] = "PASS" if res_events.status_code == 200 else "FAIL"

        # --- F. MARKET INTELLIGENCE ---
        res_market_ov = await client.get("/api/v1/market-intelligence/overview")
        res_breadth = await client.get("/api/v1/market-intelligence/breadth")
        res_sectors = await client.get("/api/v1/market-intelligence/sectors")
        res_regime = await client.get("/api/v1/market-intelligence/regime")
        res_anomalies = await client.get("/api/v1/market-intelligence/anomalies")

        results["F_Market_Intelligence"] = (
            "PASS"
            if (
                res_market_ov.status_code == 200
                and res_breadth.status_code == 200
                and res_sectors.status_code == 200
                and res_regime.status_code == 200
                and res_anomalies.status_code == 200
            )
            else "FAIL"
        )

        # --- G. AI RESEARCH ASSISTANT ---
        res_ai = await client.post(
            "/api/v1/ai/research",
            json={"query": "Summarize financial performance and risks of TCS"},
            headers=headers,
        )
        results["G_AI_Research_Assistant"] = "PASS" if res_ai.status_code == 200 else "FAIL"

        # --- H. PORTFOLIO & MULTI-PORTFOLIO ---
        res_ports = await client.get("/api/v1/portfolios", headers=headers)
        res_compare = await client.get("/api/v1/portfolios/compare", headers=headers)
        res_consolidated = await client.get("/api/v1/portfolios/consolidated", headers=headers)

        results["H_Multi_Portfolio"] = (
            "PASS"
            if (res_ports.status_code == 200 and res_compare.status_code == 200 and res_consolidated.status_code == 200)
            else "FAIL"
        )

        # --- I. PORTFOLIO RISK & COMMAND CENTER ---
        res_cmd = await client.get("/api/v1/portfolio/risk-command-center", headers=headers)
        res_var = await client.get("/api/v1/portfolio/risk/var", headers=headers)
        res_stress = await client.post(
            "/api/v1/portfolio/risk/stress-test",
            json={"market_shock_pct": -10.0},
            headers=headers,
        )

        results["I_Risk_Command_Center"] = (
            "PASS"
            if (res_cmd.status_code == 200 and res_var.status_code == 200 and res_stress.status_code == 200)
            else "FAIL"
        )

        # --- J. RISK ALERTS & MONITORING ---
        res_alerts = await client.get("/api/v1/portfolio/risk/alerts/active", headers=headers)
        res_pref = await client.get("/api/v1/portfolio/risk/alerts/preferences", headers=headers)

        results["J_Risk_Alerts_Monitoring"] = (
            "PASS" if (res_alerts.status_code == 200 and res_pref.status_code == 200) else "FAIL"
        )

        # --- K. BRIEFINGS & CHANGE DETECTION ---
        res_briefing_gen = await client.post(
            "/api/v1/portfolio/briefings/generate",
            json={"briefing_type": "DAILY"},
            headers=headers,
        )
        res_briefings = await client.get("/api/v1/portfolio/briefings", headers=headers)
        res_changes = await client.get("/api/v1/portfolio/briefings/changes", headers=headers)

        results["K_Portfolio_Briefings"] = (
            "PASS"
            if (res_briefing_gen.status_code == 200 and res_briefings.status_code == 200 and res_changes.status_code == 200)
            else "FAIL"
        )

    logger.info("E2E Audit Results Summary:")
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    asyncio.run(run_e2e_audit())
