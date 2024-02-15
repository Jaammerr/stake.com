from pyrogram.errors import PeerIdInvalid

from bot import bot
from models import CheckChannelData
from database import TelegramChannel


async def process_verify_channel(data: CheckChannelData) -> dict:
    try:
        print(f"Verifying channel: {data.channel_id}")
        # member_info = await bot.get_chat_member(
        #     chat_id=data.channel_id,
        #     user_id=6195999019
        # )
        # print(f"Member status: {member_info.status}")

        # if member_info.status == ChatMemberStatus.ADMINISTRATOR:
        channel_data = await bot.get_chat(data.channel_id)
        if not TelegramChannel.add_new_channel(
            channel_id=data.channel_id, channel_title=channel_data.title
        ):
            return {
                "status": "error",
                "message": "Error: Channel already exists",
                "result": None,
            }

        return {
            "status": "ok",
            "message": "Success: Channel added",
            "result": {
                "channel_id": data.channel_id,
                "channel_title": channel_data.title,
            },
        }

        # return {
        #     "status": "error",
        #     "message": "Error: Bot is not admin in channel",
        #     "result": None
        # }

    except PeerIdInvalid as error:
        print(f"PerrIdInvalid: {error}")
        return {
            "status": "error",
            "message": "Error: Invalid channel ID",
            "result": None,
        }

    except Exception as error:
        return {"status": "error", "message": f"Error: {error}", "result": None}
