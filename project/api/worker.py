from celery import Celery
from models import ProcessBetData
from database import BetData, OutComes, Filter, FilterSports
from utils import create_message_and_send
from configuration import config

celery = Celery()
celery.conf.broker_url = config["redis_broker_url"]
celery.conf.result_backend = config["redis_backend_url"]


@celery.task(time_limit=20)
def process_bet_data(data: dict):
    data = ProcessBetData(**data)
    if BetData.is_exists(data.bet_id):
        return

    print(
        f"""
        Processing bet data:
        {data}
        """
    )

    bet_data_instance = BetData.add_new_bet(
        bet_type=data.bet_type,
        bet_id=data.bet_id,
        url=data.url,
        user=data.user,
        amount=data.amount,
        amount_usd=data.amount_usd,
        currency=data.currency,
        total_multiplier=data.total_multiplier,
        created_at=data.created_at,
    )

    if bet_data_instance:
        for outcome in data.outcomes:
            OutComes.add_new_outcome(
                bet=bet_data_instance,
                outcome_id=outcome.outcome_id,
                sport=outcome.sport,
                market=outcome.market,
                odds=outcome.odds,
                outcome_name=outcome.outcome_name,
                start_time=outcome.start_time,
                is_live=outcome.is_live,
                live_score=outcome.live_score,
                live_status=outcome.live_status,
                home=outcome.home,
                league=outcome.league,
                bet_type_v1=outcome.bet_type_v1,
                away=outcome.away,
            )

    channels = get_channels_with_correct_filters(data)
    for channel in channels:
        create_message_and_send(channel, data)


def validate_outcomes(channel_filter: dict, data: ProcessBetData):
    sports_filters = FilterSports.get_sports_filters(channel_filter["channel_id"])
    print(f"Sports filters for bet {data.bet_id}")
    valid_commands = channel_filter["valid_commands"].get("values", [])
    valid_leagues = channel_filter["valid_leagues"].get("values", [])
    invalid_commands = channel_filter["invalid_commands"].get("values", [])
    invalid_leagues = channel_filter["invalid_leagues"].get("values", [])
    types_of_bet = channel_filter["types_of_bet"].get("values", [])

    # if (
    #         channel_filter["type_of_bet"] != "All"
    #         and channel_filter["type_of_bet"] != data.bet_type
    # ):
    #     return

    if "All" not in types_of_bet and data.bet_type not in types_of_bet:
        print(f"return because of type_of_bet: {data.bet_id}")
        return

    # type_of_bet_v1 (All, Live, Prematch)
    if channel_filter["type_of_bet_v1"] != "All":
        if not all(
                outcome.bet_type_v1 == channel_filter["type_of_bet_v1"]
                for outcome in data.outcomes
        ):
            print(f"return because of type_of_bet_v1 {data.bet_id}")
            return

    # if not all(sports_filters and valid_commands and valid_leagues and invalid_commands and invalid_leagues):
    #     print(f"return because of no sports filters1")
    #     return channel_filter["channel_id"]

    bet_commands = [
        command for outcome in data.outcomes for command in [outcome.home, outcome.away]
    ]
    bet_leagues = [outcome.league for outcome in data.outcomes]

    if valid_commands and "All" not in valid_commands:
        if channel_filter["include_commands"]:
            if not all(command in valid_commands for command in bet_commands):
                print(f"return because of valid commands {data.bet_id}")
                return

        else:
            if not any(command in valid_commands for command in bet_commands):
                print(f"return because of valid1 commands {data.bet_id}")
                return

    if valid_leagues and "All" not in valid_leagues:
        if channel_filter["include_leagues"]:
            if not all(league in valid_leagues for league in bet_leagues):
                print(f"return because of valid leagues {data.bet_id}")
                return

        else:
            if not any(league in valid_leagues for league in bet_leagues):
                print(f"return because of valid1 leagues {data.bet_id}")
                return

    if invalid_commands and "All" not in invalid_commands:
        if any(
                any(command in invalid_commands for command in [outcome.home, outcome.away])
                for outcome in data.outcomes
        ):
            print(f"return because of invalid commands {data.bet_id}")
            return

    if invalid_leagues and "All" not in invalid_leagues:
        if any(
                any(league in invalid_leagues for league in [outcome.league])
                for outcome in data.outcomes
        ):
            print(f"return because of invalid leagues {data.bet_id}")
            return

    if not sports_filters:
        print(f"return because of no sports filters {data.bet_id}")
        return channel_filter["channel_id"]

    print(f"filtering sports filters for bet {data.bet_id}")
    # if channel_filter["type_of_bet"] == "Multiple":
    if any(type_of_bet.startswith("Multiple") for type_of_bet in types_of_bet):
        for sport_filter in sports_filters:
            if not sport_filter.get("sport"):
                return channel_filter["channel_id"]

            if channel_filter["include_sports"]:
                if not all(
                        outcome.sport == sport_filter["sport"] for outcome in data.outcomes
                ):
                    continue

                if not all(
                        sport_filter["min_multiplier"]
                        <= outcome.odds
                        <= sport_filter["max_multiplier"]
                        for outcome in data.outcomes
                ):
                    continue

                if (
                        not sport_filter["min_amount"]
                            <= data.amount_usd
                            <= sport_filter["max_amount"]
                ):
                    continue

                return channel_filter["channel_id"]

            else:
                # check if sport is in outcomes
                # if sport_filter["sport"] in [outcome.sport for outcome in data.outcomes]:
                #     # check if selected sport has correct multiplier and amount
                #     outcomes = [outcome for outcome in data.outcomes if outcome.sport == sport_filter["sport"]]
                #
                #     if all([
                #         True for outcome in outcomes if sport_filter["min_multiplier"] <= outcome.odds <= sport_filter["max_multiplier"]
                #     ]):
                #         if sport_filter["min_amount"] <= data.amount_usd <= sport_filter["max_amount"]:
                #             return channel_filter["channel_id"]

                if sport_filter["sport"] in [
                    outcome.sport for outcome in data.outcomes
                ]:
                    # check if selected sport has correct multiplier and amount
                    filtered_outcomes = [
                        outcome
                        for outcome in data.outcomes
                        if outcome.sport == sport_filter["sport"]
                    ]

                    if all(
                            sport_filter["min_multiplier"]
                            <= outcome.odds
                            <= sport_filter["max_multiplier"]
                            for outcome in filtered_outcomes
                    ):

                        if (
                                sport_filter["min_amount"]
                                <= data.amount_usd
                                <= sport_filter["max_amount"]
                        ):
                            return channel_filter["channel_id"]

    else:
        outcome = data.outcomes[0]
        for sport_filter in sports_filters:
            if sport_filter["sport"] == outcome.sport:
                if (
                        sport_filter["min_multiplier"]
                        <= outcome.odds
                        <= sport_filter["max_multiplier"]
                ):
                    if (
                            sport_filter["min_amount"]
                            <= data.amount_usd
                            <= sport_filter["max_amount"]
                    ):
                        return channel_filter["channel_id"]




def get_channels_with_correct_filters(data: ProcessBetData):
    # Получаем все фильтры для каналов и фильтры для спортов
    channel_filters = Filter.get_all_filters()

    # Список для хранения подходящих результатов
    channels_to_send = []

    # Итерируем по фильтрам для каналов
    for channel_filter in channel_filters:
        types_of_bet = channel_filter["types_of_bet"].get("values", [])
        # Проверяем, соответствуют ли данные ставки фильтру для канала

        # if channel_filter["type_of_bet"] != "All":
        if "All" not in types_of_bet:
            # if channel_filter["type_of_bet"] == "Multiple":
            if "Multiple | x4+" in types_of_bet and len(data.outcomes) >= 4:
                # if channel_filter["count_of_outcomes"] == 4 and len(data.outcomes) >= 4:
                channel_users = channel_filter["users"].get("values", [])

                if channel_users:
                    if data.user in channel_users:

                        # Итерируем по фильтрам для спортов
                        channel = validate_outcomes(channel_filter, data)
                        if channel:
                            channels_to_send.append(channel)

                    else:
                        # не подходит
                        continue

                else:
                    # Итерируем по фильтрам для спортов
                    channel = validate_outcomes(channel_filter, data)
                    if channel:
                        channels_to_send.append(channel)

            elif "Multiple | x3" in types_of_bet and len(data.outcomes) == 3 or "Multiple | x2" in types_of_bet and len(data.outcomes) == 2:
                # if channel_filter["count_of_outcomes"] != 4:
                # if len(data.outcomes) == channel_filter["count_of_outcomes"]:
                channel_users = channel_filter["users"].get("values", [])
                if channel_users:
                    if data.user in channel_users:

                        # Итерируем по фильтрам для спортов
                        channel = validate_outcomes(channel_filter, data)
                        if channel:
                            channels_to_send.append(channel)

                    else:
                        # не подходит
                        continue

                else:
                    # Итерируем по фильтрам для спортов
                    channel = validate_outcomes(channel_filter, data)
                    if channel:
                        channels_to_send.append(channel)

            # elif channel_filter["type_of_bet"] == "Single":
            elif "Single" in types_of_bet and len(data.outcomes) == 1:
                channel_users = channel_filter["users"].get("values", [])
                if channel_users:
                    if data.user in channel_users:
                        # Итерируем по фильтрам для спортов
                        channel = validate_outcomes(channel_filter, data)
                        if channel:
                            channels_to_send.append(channel)

                    else:
                        # не подходит
                        continue

                else:
                    # Итерируем по фильтрам для спортов
                    channel = validate_outcomes(channel_filter, data)
                    if channel:
                        channels_to_send.append(channel)

        else:
            # Итерируем по фильтрам для спортов
            channel = validate_outcomes(channel_filter, data)
            if channel:
                channels_to_send.append(channel)

    print(f"Channels to send bet {data.bet_id}:", channels_to_send)
    return channels_to_send
