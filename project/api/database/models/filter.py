import json
import uuid

from peewee import *
from loguru import logger

from ..settings import db
from .telegram_channel import TelegramChannel



class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class Filter(Model):
    channel = ForeignKeyField(TelegramChannel, backref='filters', column_name='channel_id')
    uuid = UUIDField()
    type_of_bet = CharField(max_length=8, null=True)
    count_of_outcomes = IntegerField(null=True)
    include_sports = BooleanField(null=True)
    users = JSONField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('channel', 'uuid')

    @classmethod
    def get_channel_data(cls, channel_id: int):
        filters = cls.select().where(cls.channel_id == channel_id)

        if filters:
            for filter in filters:
                return {
                    "filter_uuid": str(filter.uuid),
                    "type_of_bet": filter.type_of_bet,
                    "count_of_outcomes": filter.count_of_outcomes,
                    "users": filter.users,
                    "include_sports": filter.include_sports,
                }

        return {
            "filter_uuid": str(uuid.uuid4()),
            "type_of_bet": "All",
            "count_of_outcomes": 0,
            "users": {"values": []},
            "include_sports": False,
        }


    @classmethod
    def get_all_filters(cls) -> list[dict]:
        filters = cls.select()
        return [
            {
                "channel_id": filter.channel_id,
                "filter_uuid": str(filter.uuid),
                "type_of_bet": filter.type_of_bet,
                "count_of_outcomes": filter.count_of_outcomes,
                "users": filter.users,
                "include_sports": filter.include_sports,
            }
            for filter in filters
        ]


    @classmethod
    def delete_filters(cls, channel_id: int) -> bool:
        try:
            cls.delete().where(cls.channel_id == channel_id).execute()
            return True
        except Exception as error:
            logger.error(f"Error while deleting channel filters with ID {channel_id}: {error}")
            return False


    @classmethod
    def update_channel_filters(cls, channel_id: int, filters: dict):
        users = filters.get("users", [])

        filter_uuid = filters.get("filter_uuid", str(uuid.uuid4()))
        cls.delete().where(cls.channel_id == channel_id).execute()

        filter_instance = cls.create(channel_id=channel_id, uuid=filter_uuid, **filters)
        if users:
            filter_instance.users = users




