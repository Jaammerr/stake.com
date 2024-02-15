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
    channel = ForeignKeyField(
        TelegramChannel, backref="filters", column_name="channel_id"
    )
    uuid = UUIDField()
    types_of_bet = JSONField(null=True)
    type_of_bet_v1 = CharField(max_length=10, null=True)
    count_of_outcomes = IntegerField(null=True)
    include_sports = BooleanField(null=True)
    include_commands = BooleanField(null=True)
    include_leagues = BooleanField(null=True)
    users = JSONField(null=True)
    valid_commands = JSONField(null=True)
    valid_leagues = JSONField(null=True)
    invalid_commands = JSONField(null=True)
    invalid_leagues = JSONField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey("channel", "uuid")

    @classmethod
    def get_channel_data(cls, channel_id: int):
        filters = cls.select().where(cls.channel_id == channel_id)

        if filters:
            for filter in filters:
                return {
                    "filter_uuid": str(filter.uuid),
                    "types_of_bet": filter.types_of_bet,
                    "count_of_outcomes": filter.count_of_outcomes,
                    "type_of_bet_v1": filter.type_of_bet_v1,
                    "users": filter.users,
                    "include_sports": filter.include_sports,
                    "include_commands": filter.include_commands,
                    "include_leagues": filter.include_leagues,
                    "valid_commands": filter.valid_commands,
                    "valid_leagues": filter.valid_leagues,
                    "invalid_commands": filter.invalid_commands,
                    "invalid_leagues": filter.invalid_leagues,
                }

        return {
            "filter_uuid": str(uuid.uuid4()),
            "types_of_bet": {"values": []},
            "type_of_bet_v1": "All",
            "count_of_outcomes": 0,
            "users": {"values": []},
            "valid_commands": {"values": []},
            "valid_leagues": {"values": []},
            "invalid_commands": {"values": []},
            "invalid_leagues": {"values": []},
            "include_sports": False,
            "include_commands": False,
            "include_leagues": False,
        }

    @classmethod
    def get_all_filters(cls) -> list[dict]:
        filters = cls.select()
        return [
            {
                "channel_id": filter.channel_id,
                "filter_uuid": str(filter.uuid),
                "types_of_bet": filter.types_of_bet,
                "type_of_bet_v1": filter.type_of_bet_v1,
                "count_of_outcomes": filter.count_of_outcomes,
                "users": filter.users,
                "valid_commands": filter.valid_commands,
                "valid_leagues": filter.valid_leagues,
                "invalid_commands": filter.invalid_commands,
                "invalid_leagues": filter.invalid_leagues,
                "include_sports": filter.include_sports,
                "include_commands": filter.include_commands,
                "include_leagues": filter.include_leagues,
            }
            for filter in filters
        ]

    @classmethod
    def delete_filters(cls, channel_id: int) -> bool:
        try:
            cls.delete().where(cls.channel_id == channel_id).execute()
            return True
        except Exception as error:
            logger.error(
                f"Error while deleting channel filters with ID {channel_id}: {error}"
            )
            return False

    @classmethod
    def update_channel_filters(cls, channel_id: int, filters: dict):
        users = filters.get("users", [])
        valid_commands = filters.get("valid_commands", [])
        valid_leagues = filters.get("valid_leagues", [])
        invalid_commands = filters.get("invalid_commands", [])
        invalid_leagues = filters.get("invalid_leagues", [])
        types_of_bet = filters.get("types_of_bet", {"values": []})

        filter_uuid = filters.get("filter_uuid", str(uuid.uuid4()))
        cls.delete().where(cls.channel_id == channel_id).execute()

        filter_instance = cls.create(channel_id=channel_id, uuid=filter_uuid, **filters)
        if users:
            filter_instance.users = users
        if valid_commands:
            filter_instance.valid_commands = valid_commands
        if valid_leagues:
            filter_instance.valid_leagues = valid_leagues
        if invalid_commands:
            filter_instance.invalid_commands = invalid_commands
        if invalid_leagues:
            filter_instance.invalid_leagues = invalid_leagues
        if types_of_bet:
            filter_instance.types_of_bet = types_of_bet
