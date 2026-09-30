import uuid
import pytest
from app.services.news.matcher import CompanyMatcher, normalize_text


def test_alias_normalization() -> None:
    assert normalize_text("Reliance Industries Ltd.") == "RELIANCE INDUSTRIES LTD"


@pytest.mark.asyncio
async def test_company_matcher_logic() -> None:
    # Test text mentioning multiple companies
    title = "Reliance Industries and Tata Consultancy Services enter strategic joint venture"
    content = "RIL and TCS announce partnership for digital infrastructure."

    # Using dummy session
    class DummySession:
        async def execute(self, stmt):
            class DummyResult:
                def scalar_one_or_none(self):
                    return None

                def scalars(self):
                    class ScalarList:
                        def all(self):
                            class Inst1:
                                id = uuid.UUID("11111111-1111-1111-1111-111111111111")
                                symbol = "RELIANCE"
                                name = "Reliance Industries Ltd"
                                isin = "INERELIANCEISIN"
                                sector = "Energy / Conglomerate"
                                is_active = True

                            class Inst2:
                                id = uuid.UUID("22222222-2222-2222-2222-222222222222")
                                symbol = "TCS"
                                name = "Tata Consultancy Services"
                                isin = "INETCSISIN"
                                sector = "Information Technology"
                                is_active = True

                            return [Inst1(), Inst2()]

                    return ScalarList()

            return DummyResult()

    session = DummySession()
    matches = await CompanyMatcher.match_instruments(title, content, session)  # type: ignore[arg-type]

    matched_symbols = [m[1] for m in matches]
    assert "RELIANCE" in matched_symbols
    assert "TCS" in matched_symbols


@pytest.mark.asyncio
async def test_duplicate_company_names_and_unknown_matching() -> None:
    title = "Unknown Startup XYZ announces new product line"
    content = "No public listed company is mentioned here."

    class DummySession:
        async def execute(self, stmt):
            class DummyResult:
                def scalar_one_or_none(self):
                    return None

                def scalars(self):
                    class ScalarList:
                        def all(self):
                            class Inst1:
                                id = uuid.UUID("33333333-3333-3333-3333-333333333333")
                                symbol = "INFY"
                                name = "Infosys Ltd"
                                isin = "INEINFYSISIN"
                                sector = "Information Technology"
                                is_active = True

                            class Inst2:
                                id = uuid.UUID("44444444-4444-4444-4444-444444444444")
                                symbol = "INFY"
                                name = "Infosys Ltd (Duplicate)"
                                isin = "INEINFYS2ISIN"
                                sector = "Information Technology"
                                is_active = True

                            return [Inst1(), Inst2()]

                    return ScalarList()

            return DummyResult()

    matches = await CompanyMatcher.match_instruments(title, content, DummySession())  # type: ignore[arg-type]
    assert len(matches) == 0
