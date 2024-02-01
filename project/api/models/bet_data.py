import datetime

from pydantic import BaseModel


class OutCome(BaseModel):
    outcome_id: str
    sport: str
    market: str
    odds: float
    outcome_name: str
    start_time: datetime.datetime | str
    is_live: bool
    live_score: str | None = None
    live_status: str | None = None
    home: str | None = None
    away: str | None = None


class ProcessBetData(BaseModel):
    bet_type: str
    bet_id: str
    url: str
    user: str | None = None
    amount: float
    amount_usd: float | None = None
    currency: str
    total_multiplier: float
    created_at: datetime.datetime | str
    outcomes: list[OutCome]


