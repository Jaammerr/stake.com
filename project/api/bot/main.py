from pyrogram import Client
from configuration import config

# api_id = 17429549
# api_hash = "ebec90693311b8385a711785751d2e81"
# bot_token = "6195999019:AAHYZ8woCKxK-H1KU3ZklIOyzIZgvnFd4IM"


bot = Client("my_bot", api_id=config["tg_api_id"], api_hash=config["tg_api_hash"], bot_token=config["tg_bot_token"])


async def send_bet_to_channel(channel_id: int, text: str | list[str]):
    if isinstance(text, str):
        await bot.send_message(
            chat_id=channel_id, text=text, disable_web_page_preview=True
        )

    else:
        for message in text:
            await bot.send_message(
                chat_id=channel_id, text=message, disable_web_page_preview=True
            )
