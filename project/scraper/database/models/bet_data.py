import datetime
from typing import Any

from peewee import *
from database import db
from loguru import logger


class BetData(Model):
    bet_type = CharField(max_length=8)
    bet_id = CharField(max_length=20, primary_key=True)
    url = CharField(max_length=100)
    user = CharField(max_length=40, null=True)
    amount = FloatField()
    amount_usd = FloatField(null=True)
    currency = CharField(max_length=10)
    total_multiplier = FloatField()
    created_at = DateTimeField()

    class Meta:
        database = db

    @classmethod
    def add_new_bet(
        cls,
        bet_type: str,
        bet_id: str,
        url: str | None,
        user: str,
        amount: float,
        currency: str,
        total_multiplier: float,
        created_at: datetime.datetime,
        amount_usd: float | None = None,
    ):
        try:
            if cls.is_exists(bet_id):
                logger.warning(f"Bet with ID {bet_id} already exists")
                return False

            query_result = cls.create(
                bet_type=bet_type,
                bet_id=bet_id,
                url=url,
                user=user,
                amount=amount,
                amount_usd=amount_usd,
                currency=currency,
                total_multiplier=total_multiplier,
                created_at=created_at,
            )

            logger.debug(f"Added new bet to db: {bet_id}")
            return query_result

        except Exception as error:
            logger.error(f"Error while creating bet data: {error}")

    @classmethod
    def is_exists(cls, bet_id: str) -> bool:
        return cls.select().where(cls.bet_id == bet_id).exists()


class OutComes(Model):
    bet = ForeignKeyField(BetData, backref="outcomes", column_name="bet_id")
    outcome_id = CharField(max_length=50)
    sport = CharField(max_length=20)
    market = CharField(max_length=200)
    odds = FloatField()
    outcome_name = CharField(max_length=200)
    start_time = DateTimeField()
    is_live = BooleanField()
    live_score = CharField(max_length=10, null=True)
    live_status = CharField(max_length=200, null=True)
    home = CharField(max_length=200)
    away = CharField(max_length=200)

    class Meta:
        database = db
        primary_key = CompositeKey("bet", "outcome_id")

    @classmethod
    def add_new_outcome(
        cls,
        bet: Any,
        outcome_id: str,
        sport: str,
        market: str,
        odds: float,
        outcome_name: str,
        start_time: datetime.datetime,
        is_live: bool,
        live_score: str | None,
        live_status: str | None,
        home: str,
        away: str,
    ):
        try:
            return cls.create(
                bet=bet,
                outcome_id=outcome_id,
                sport=sport,
                market=market,
                odds=odds,
                outcome_name=outcome_name,
                start_time=start_time,
                is_live=is_live,
                live_score=live_score,
                live_status=live_status,
                home=home,
                away=away,
            )

        except IntegrityError:
            logger.warning(
                f"Outcome ID {outcome_id} already exists for bet {bet.bet_id}"
            )
            return False

        except Exception as error:
            logger.error(f"Error while creating outcomes data: {error}")

    @classmethod
    def is_exists(cls, outcome_id: str) -> bool:
        return cls.select().where(cls.outcome_id == outcome_id).exists()
