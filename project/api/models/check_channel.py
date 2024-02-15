from pydantic import BaseModel


class CheckChannelData(BaseModel):
    channel_id: int
