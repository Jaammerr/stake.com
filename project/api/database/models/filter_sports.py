import uuid

from peewee import *

from ..settings import db
from .telegram_channel import TelegramChannel
from models import UpdateSportsFilterData
from loguru import logger


class FilterSports(Model):
    channel = ForeignKeyField(TelegramChannel, backref='filters', column_name='channel_id')
    uuid = UUIDField()
    sport = TextField()
    min_multiplier = FloatField(null=True, default=0)
    max_multiplier = FloatField(null=True, default=0)
    min_amount = FloatField(null=True, default=0)
    max_amount = FloatField(null=True, default=0)

    class Meta:
        database = db
        primary_key = CompositeKey('channel', 'uuid')



    @classmethod
    def get_sports_filters(cls, channel_id: int) -> list[dict]:
        filters = cls.select().where(cls.channel_id == channel_id)

        channel_data = []
        for filter in filters:

            channel_data.append({
                "sport": filter.sport,
                "filter_uuid": str(filter.uuid) if filter.uuid else str(uuid.uuid4()),
                "min_multiplier": filter.min_multiplier,
                "max_multiplier": filter.max_multiplier,
                "min_amount": filter.min_amount,
                "max_amount": filter.max_amount,
            })

        return channel_data


    @classmethod
    def get_all_sports_filters(cls) -> list[dict]:
        filters = cls.select()

        channel_data = []
        for filter in filters:

            channel_data.append({
                "channel_id": filter.channel_id,
                "sport": filter.sport,
                "filter_uuid": str(filter.uuid) if filter.uuid else str(uuid.uuid4()),
                "min_multiplier": filter.min_multiplier,
                "max_multiplier": filter.max_multiplier,
                "min_amount": filter.min_amount,
                "max_amount": filter.max_amount,
            })

        return channel_data


    @classmethod
    def delete_sports_filters(cls, channel_id: int) -> bool:
        try:
            cls.delete().where(cls.channel_id == channel_id).execute()
            return True
        except Exception as error:
            logger.error(f"Error while deleting channel sports filters with ID {channel_id}: {error}")
            return False


    @classmethod
    def update_sports_filter(cls, data: UpdateSportsFilterData):
        cls.delete().where(cls.channel_id == data.channel_id).execute()
        print(data.sports_data)

        for filter in data.sports_data:
            if filter.sport == "All":
                # cls.delete().where(cls.channel_id == data.channel_id).execute()
                # cls.create(
                #     channel_id=data.channel_id,
                #     sport=filter.sport,
                #     uuid=str(uuid.uuid4()),
                # )
                return

            # if filter.filter_uuid:
            #     cls.update(
            #         sport=filter.sport,
            #         min_multiplier=filter.min_multiplier if filter.min_multiplier else 0,
            #         max_multiplier=filter.max_multiplier if filter.max_multiplier else 0,
            #         min_amount=filter.min_amount if filter.min_amount else 0,
            #         max_amount=filter.max_amount if filter.max_amount else 0,
            #     ).where(
            #         (cls.channel_id == data.channel_id) & (cls.uuid == filter.filter_uuid)
            #     ).execute()
            #
            # else:
            cls.create(
                channel_id=data.channel_id,
                sport=filter.sport,
                uuid=str(uuid.uuid4()),
                min_multiplier=filter.min_multiplier if filter.min_multiplier else 0,
                max_multiplier=filter.max_multiplier if filter.max_multiplier else 0,
                min_amount=filter.min_amount if filter.min_amount else 0,
                max_amount=filter.max_amount if filter.max_amount else 0,
            )


        # delete another sports filters if they are not in data.sports_data
        # cls.delete().where(
        #     (cls.channel_id == data.channel_id) & (cls.sport.not_in([filter.sport for filter in data.sports_data]))
        # ).execute()
