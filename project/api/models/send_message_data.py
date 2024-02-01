from pydantic import BaseModel


class SendMessageData(BaseModel):
    channel_id: int
    text: str | list[str]
