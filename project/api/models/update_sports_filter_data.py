from pydantic import BaseModel


class SportData(BaseModel):
    sport: str
    min_multiplier: float | None = None
    max_multiplier: float | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    filter_uuid: str | None = None


class UpdateSportsFilterData(BaseModel):
    sports_data: list[SportData]
    channel_id: int
