from pydantic import BaseModel


class FiltersData(BaseModel):
    type_of_bet: str | None = None
    count_of_outcomes: int | None = None
    users: dict[str, list[str]] | None = None
    include_sports: bool | None = None


class UpdateChannelFiltersData(BaseModel):
    channel_id: int
    filters: FiltersData


