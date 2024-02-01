from fastapi import FastAPI
from pyrogram import Client
from starlette.responses import JSONResponse

from database import *
from routers.channel import router as channel_router
from routers.data import router as data_router
from bot import bot


app = FastAPI()
app.include_router(channel_router)
app.include_router(data_router)



@app.on_event("startup")
async def on_startup():
    db.connect()
    db.create_tables([TelegramChannel, Filter, FilterSports, BetData, OutComes])

    try:
        await bot.start()
    except Exception as error:
        raise Exception(f"Error while starting bot: {error}")




@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        {
            'status': 'error',
            "message": f"Error: {exc}"
        }
    )


# @app.get("/start_bot", status_code=200)
# async def start_bot():
#     try:
#         await bot.start()
#         return JSONResponse(
#             {
#                 'status': 'ok',
#                 "message": "Bot started"
#             }
#         )
#
#     except Exception as error:
#         return JSONResponse(
#             {
#                 'status': 'error',
#                 "message": f"Error: {error}"
#             }
#         )




# if __name__ == '__main__':
#     db.connect()
#     db.create_tables([TelegramChannel, Filter, FilterSports, BetData, OutComes])
#     uvicorn.run(app, host="0.0.0.0", port=8002)

