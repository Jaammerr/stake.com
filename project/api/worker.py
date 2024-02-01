from celery import Celery
from models import ProcessBetData
from database import BetData, OutComes, Filter, FilterSports
from utils import create_message_and_send



celery = Celery()
celery.conf.broker_url = "redis://localhost:6379"
celery.conf.result_backend = "redis://localhost:6379"




@celery.task(time_limit=20)
def process_bet_data(data: dict):
    data = ProcessBetData(**data)

    if BetData.is_exists(data.bet_id):
        return

    bet_data_instance = BetData.add_new_bet(
        bet_type=data.bet_type,
        bet_id=data.bet_id,
        url=data.url,
        user=data.user,
        amount=data.amount,
        amount_usd=data.amount_usd,
        currency=data.currency,
        total_multiplier=data.total_multiplier,
        created_at=data.created_at
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
                away=outcome.away
            )


    channels = get_channels_with_correct_filters(data)
    for channel in channels:
        create_message_and_send(channel, data)




def validate_outcomes(channel_filter: dict, data: ProcessBetData):
    sports_filters = FilterSports.get_sports_filters(channel_filter["channel_id"])

    if channel_filter["type_of_bet"] != "All" and channel_filter["type_of_bet"] != data.bet_type:
        return

    if not sports_filters:
        return channel_filter["channel_id"]

    if channel_filter["type_of_bet"] == "Multiple":
        for sport_filter in sports_filters:
            if not sport_filter.get("sport"):
                return channel_filter["channel_id"]

            if channel_filter["include_sports"]:
                if not all(outcome.sport == sport_filter["sport"] for outcome in data.outcomes):
                    continue

                if not all(sport_filter["min_multiplier"] <= outcome.odds <= sport_filter["max_multiplier"] for outcome in data.outcomes):
                    continue

                if not sport_filter["min_amount"] <= data.amount_usd <= sport_filter["max_amount"]:
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

                if sport_filter["sport"] in [outcome.sport for outcome in data.outcomes]:
                    # check if selected sport has correct multiplier and amount
                    filtered_outcomes = [outcome for outcome in data.outcomes if outcome.sport == sport_filter["sport"]]

                    if all(sport_filter["min_multiplier"] <= outcome.odds <= sport_filter["max_multiplier"] for outcome in filtered_outcomes):

                        if sport_filter["min_amount"] <= data.amount_usd <= sport_filter["max_amount"]:
                            return channel_filter["channel_id"]



    else:
        outcome = data.outcomes[0]
        for sport_filter in sports_filters:
            if sport_filter["sport"] == outcome.sport:
                if sport_filter["min_multiplier"] <= outcome.odds <= sport_filter["max_multiplier"]:
                    if sport_filter["min_amount"] <= data.amount_usd <= sport_filter["max_amount"]:
                        return channel_filter["channel_id"]




def get_channels_with_correct_filters(data: ProcessBetData):
    # Получаем все фильтры для каналов и фильтры для спортов
    channel_filters = Filter.get_all_filters()

    # Список для хранения подходящих результатов
    channels_to_send = []

    print(f"""
    bet_type = {data.bet_type}
    count_of_outcomes = {len(data.outcomes)}
    amount = {data.amount}
    outcomes_sports = {[outcome.sport for outcome in data.outcomes]}
    outcomes_odds = {[outcome.odds for outcome in data.outcomes]}
    """)

    # Итерируем по фильтрам для каналов
    for channel_filter in channel_filters:
        # Проверяем, соответствуют ли данные ставки фильтру для канала

        if channel_filter["type_of_bet"] != "All":
            if channel_filter["type_of_bet"] == "Multiple":
                if channel_filter["count_of_outcomes"] == 4 and len(data.outcomes) >= 4:
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
                    if channel_filter["count_of_outcomes"] != 4:
                        if len(data.outcomes) == channel_filter["count_of_outcomes"]:
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

            elif channel_filter["type_of_bet"] == "Single":
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



    print("channels to send bet", channels_to_send)
    return channels_to_send
