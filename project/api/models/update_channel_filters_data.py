from pydantic import BaseModel


class FiltersData(BaseModel):
    types_of_bet: dict[str, list[str]] | None = None
    type_of_bet_v1: str | None = None
    count_of_outcomes: int | None = None
    users: dict[str, list[str]] | None = None
    valid_commands: dict[str, list[str]] | None = None
    valid_leagues: dict[str, list[str]] | None = None
    invalid_commands: dict[str, list[str]] | None = None
    invalid_leagues: dict[str, list[str]] | None = None
    include_sports: bool | None = None
    include_commands: bool | None = None
    include_leagues: bool | None = None


class UpdateChannelFiltersData(BaseModel):
    channel_id: int
    filters: FiltersData
