import os
import uuid

import requests

from bot import send_bet_to_channel
from loguru import logger
from models import ProcessBetData
from bot import bot



def create_message_and_send(channel_id: int, data: ProcessBetData):
    messages = (
        f"🆕   <b><strong>Одиночна ставка ➖ 🆔 <b><a href={data.url}>{data.bet_id.split(':')[1]}</a><strong></b>:"
        f"\n\n📃   <b>Загальний коеф. = {round(data.total_multiplier, 2)}</b>"
        f"\n💵   <b>Оригінальна сума = {round(data.amount, 3)} {data.currency.upper()}</b>"
        f"\n💸   <b>Сума в USD = {round(data.amount_usd, 1)} $</b>"
        f"\n\n{'🔥   <u>Live</u>' if data.outcomes[0].is_live else ''}"
        f"\n\n🖥   {f'<i>{data.outcomes[0].home} - {data.outcomes[0].away}</i>'}"
        f"\n🔮   <b><strong>Спорт = {f'{data.outcomes[0].sport}'}"
        f"\n🪧   Ринок = {f'{data.outcomes[0].market}'}"
        f"\n📎   Вибір = {f'{data.outcomes[0].outcome_name}'}"
        f"\n🫲   Коеф. = {f'{data.outcomes[0].odds}'}<strong></b>"
        f"\n\n{f'<u>  🧾 Актуальний рахунок = {data.outcomes[0].live_score}</u>' if data.outcomes[0].is_live else ''}"
        f"\n{f'<u>  📆 Час початку = {data.outcomes[0].start_time}</u>' if not data.outcomes[0].is_live else ''}"
    ) if data.bet_type == "Single" else (
        f"🆕   <b><strong>Експрес ставка ➖ 🆔 <b><a href={data.url}>{data.bet_id.split(':')[1]}</a><strong></b>:"
        f"\n\n📃   <b>Загальний коеф. = {round(data.total_multiplier, 2)}</b>"
        f"\n💵   <b>Оригінальна сума = {round(data.amount, 3)} {data.currency.upper()}</b>"
        f"\n💸   <b>Сума в USD = {round(data.amount_usd, 1)} $</b>"
        f"\n\n📖  <b>Кількість подій = {len(data.outcomes)}</b>"
    )

    # if data.bet_type == "Single":
    #     messages = f"""
    #         🆕   <b><strong>Одиночна ставка ➖ 🆔 <b><a href={data.url}>{data.bet_id.split(":")[1]}</a><strong></b>:
    #
    #         📃   <b>Загальний коеф. = {data.total_multiplier}</b>
    #         💵   <b>Оригінальна сума = {round(data.amount, 3)} {data.currency.upper()}</b>
    #         💸   <b>Сума в USD = {data.amount_usd.split(".")[1] if "." in str(data.amount_usd) else data.amount_usd} $</b>
    #
    #         {"🔥   <u>Live</u>" if data.outcomes[0].is_live else ""}
    #         🖥   {f"<i>{data.outcomes[0].home} - {data.outcomes[0].away}</i>"}
    #
    #         🔮   <b><strong>Спорт = {f"{data.outcomes[0].sport}"}
    #         🪧   Ринок = {f"{data.outcomes[0].market}"}
    #         📎   Вибір = {f"{data.outcomes[0].outcome_name}"}
    #         🫲   Коеф. = {f"{data.outcomes[0].odds}"}<strong></b>
    #
    #         {f"<u>  🧾 Актуальний рахунок = {data.outcomes[0].live_score}</u>" if data.outcomes[0].is_live else ""}
    #         {f'<u>  📆 Час початку = {f"{data.outcomes[0].start_time}"}</u>' if not data.outcomes[0].is_live else ""}
    #
    #     """
    #
    # else:
    #     messages = f"""
    #         🆕   <b><strong>Експрес ставка ➖ 🆔 <b><a href={data.url}>{data.bet_id.split(":")[1]}</a><strong></b>:
    #
    #         📃   <b>Загальний коеф. = {data.total_multiplier}</b>
    #         💵   <b>Оригінальна сума = {round(data.amount, 3)} {data.currency.upper()}</b>
    #         💸   <b>Сума в USD = {data.amount_usd.split(".")[1] if "." in str(data.amount_usd) else data.amount_usd} $</b>
    #
    #         📖  <b>Кількість подій = {len(data.outcomes)}</b>
    #     """

    # messages = [message]
    # for i in range(0, len(data.outcomes), 4):
    #     chunk = data.outcomes[i:i + 4]
    #     outcome_messages = []
    #     for outcome in chunk:
    #         outcome_message = f"""
    #             {"🔥   <u>Live</u>" if outcome.is_live else ""}
    #             🖥   {f"<i>{outcome.home} - {outcome.away}</i>"}
    #
    #             🔮   <b><strong>Спорт = {f"{outcome.sport}"}
    #             🪧   Ринок = {f"{outcome.market}"}
    #             📎   Вибір = {f"{outcome.outcome_name}"}
    #             🫲   Коеф. = {f"{outcome.odds}"}<strong></b>
    #
    #             {f'<u>  📆 Час початку = {f"{outcome.start_time}"}</u>' if not outcome.is_live else ""}
    #
    #
    #         """
    #         outcome_messages.append(outcome_message)
    #     messages.extend(outcome_messages)



    response = requests.post(
        "http://api:8000/channel/send_message",
        json={
            "channel_id": channel_id,
            "text": messages,
        }
    )

    if response.json()["status"] == "ok":
        logger.debug(f"New bet sent to channel {channel_id}")

    else:
        logger.error(f"Error while sending bet to channel {channel_id} | {response.json()['message']}")
