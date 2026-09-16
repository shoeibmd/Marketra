from pydantic import BaseModel, Field


class TransactionCreateRequest(BaseModel):
    symbol: str
    transaction_type: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: str
    symbol: str
    transaction_type: str
    quantity: float
    price: float
    total_value: float
    timestamp: str


class PortfolioSummaryResponse(BaseModel):
    portfolio_name: str
    currency: str
    cash_balance: float
    total_market_value: float
    total_pnl: float
    total_pnl_percent: float
    positions_count: int
