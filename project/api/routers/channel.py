from fastapi import APIRouter
from starlette.responses import JSONResponse
from database import *
from models import *
from dependencies import process_verify_channel
from bot import send_bet_to_channel

router = APIRouter(
    prefix="/channel",
    tags=["channel"],
)



@router.post("/verify", status_code=200)
async def check_channel(data: CheckChannelData) -> JSONResponse:
    result = await process_verify_channel(data)
    return JSONResponse(result)



@router.post("/send_message", status_code=200)
async def send_message(data: SendMessageData) -> JSONResponse:
    await send_bet_to_channel(data.channel_id, data.text)
    return JSONResponse(
        {
            'status': 'ok',
            "message": "Message sent successfully",
            "result": None
        }
    )



@router.post("/get_filters", status_code=200)
async def get_channel_filters(data: CheckChannelData) -> JSONResponse:
    filters = Filter.get_channel_data(data.channel_id)
    sports_filters = FilterSports.get_sports_filters(data.channel_id)

    return JSONResponse(
        {
            'status': 'ok',
            "message": "Success",
            "result": {
                "filters": filters,
                "sports_filters": sports_filters
            }
        }
    )



@router.post("/update_filters", status_code=200)
async def update_channel_filters(data: UpdateChannelFiltersData) -> JSONResponse:
    Filter.update_channel_filters(
        channel_id=data.channel_id,
        filters=data.filters.model_dump()
    )
    return JSONResponse(
        {
            'status': 'ok',
            "message": "Success",
            "result": None
        }
    )


@router.post("/update_sports_filters", status_code=200)
async def update_sports_filters(data: UpdateSportsFilterData) -> JSONResponse:
    FilterSports.update_sports_filter(data)
    return JSONResponse(
        {
            'status': 'ok',
            "message": "Success",
            "result": None
        }
    )



@router.post("/delete", status_code=200)
async def delete_channel(data: CheckChannelData) -> JSONResponse:
    if all(
        [
            Filter.delete_filters(data.channel_id),
            FilterSports.delete_sports_filters(data.channel_id),
            TelegramChannel.delete_channel(data.channel_id)
        ]
    ):
        return JSONResponse(
            {
                'status': 'ok',
                "message": "Channel deleted successfully",
                "result": None
            }
    )

    return JSONResponse(
        {
            'status': 'error',
            "message": "Failed to delete channel",
            "result": None
        }
    )
