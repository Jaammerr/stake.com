from fastapi import APIRouter
from starlette.responses import JSONResponse
from database import *
from models import *
from worker import *


router = APIRouter(
    prefix="/data",
    tags=["data"],
)


@router.post("/process_bet", status_code=200)
async def process_bet(data: ProcessBetData):
    task = process_bet_data.delay(data.model_dump())
    return JSONResponse(
        {
            'status': 'ok',
            "message": "Success",
            "result": {
                "task_id": task.id,
                "task_status": task.status,
                "task_result": task.result,
                "bet_url": data.url,
            }
        }
    )


@router.get("/channels", status_code=200)
async def get_channels():
    channels = TelegramChannel.get_all_channels()
    return JSONResponse(
        {
            'status': 'ok',
            "message": "Success",
            "result": channels
        }
    )