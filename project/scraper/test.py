import random

import pyuseragents
import websocket

from curl_cffi import requests
from curl_cffi.requests import BrowserType


def create_session():
    session = requests.Session()
    session.impersonate = random.choice(BrowserType.__dict__["_member_names_"])
    session.headers = {
        'authority': 'stake.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'access-control-allow-origin': '*',
        'content-type': 'application/json',
        'origin': 'https://stake.com',
        'referer': 'https://stake.com/',
        'user-agent': pyuseragents.random(),
        'x-language': 'en',
    }

    session.proxies = {
        "http": "http://yy53kafked:71tdd1zomt_country-de@premium.proxywing.com:12321",
        "https": "http://yy53kafked:71tdd1zomt_country-de@premium.proxywing.com:12321"
    }
    session.timeout = 5
    return session



session = create_session()
response = session.get("https://stake.com/sports/home")
print(response.status_code)
cookies = dict(session.cookies)
print(cookies)



def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("Opened connection")


ws = websocket.WebSocketApp("wss://stake.com/_api/websockets", on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close,
                            header=session.headers,
                            cookie="; ".join(["%s=%s" %(i, j) for i, j in cookies.items()])
                            )
ws.run_forever()