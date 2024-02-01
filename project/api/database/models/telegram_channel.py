import datetime

from loguru import logger
from peewee import *

from ..settings import db


class TelegramChannel(Model):
    channel_id = BigIntegerField(primary_key=True)
    channel_title = CharField(max_length=200)
    channel_created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

    @classmethod
    def add_new_channel(
            cls,
            channel_id: int,
            channel_title: str,
    ) -> bool:
        try:
            if cls.is_exists(channel_id):
                logger.warning(f"Channel with ID {channel_id} already exists")
                return False

            cls.create(
                channel_id=channel_id,
                channel_title=channel_title,
            )

            logger.debug(f"Added new channel to db: {channel_id}")
            return True

        except Exception as error:
            logger.error(f"Error while creating channel data: {error}")

    @classmethod
    def is_exists(cls, channel_id: int) -> bool:
        return cls.select().where(cls.channel_id == channel_id).exists()


    @classmethod
    def get_all_channels(cls) -> list[dict]:
        channels = [channel for channel in cls.select()]
        return [
            {
                "channel_id": channel.channel_id,
                "channel_title": channel.channel_title,
                "channel_created_at": str(channel.channel_created_at)
            }
            for channel in channels
        ]


    @classmethod
    def delete_channel(cls, channel_id: int) -> bool:
        try:
            cls.delete().where(cls.channel_id == channel_id).execute()
            logger.debug(f"Deleted channel with ID {channel_id}")
            return True
        except Exception as error:
            logger.error(f"Error while deleting channel with ID {channel_id}: {error}")
            return False
