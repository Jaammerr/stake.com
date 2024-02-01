import random
import time
import queue

from datetime import datetime
from threading import Thread

import pyuseragents

from curl_cffi import requests
from curl_cffi.requests import BrowserType
from loguru import logger


from utils.json_queries import JsonQueries


class Scraper:
    API_URL = "https://stake.com/_api/graphql"

    def __init__(self):
        self.session = requests.Session(timeout=3)
        self.server = requests.Session()
        self.queue = queue.Queue()
        self.crypto_rates = []
        # self.proxies: list[dict] = get_proxies()
        # self.proxy_cycle = cycle(self.proxies)


    def create_session(self) -> None:
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
        self.session = session


    def api_request(self, json_data: dict) -> dict:
        while True:
            try:
                response = self.session.post(self.API_URL, json=json_data, verify=False)
                if "errors" in response.text:
                    error_type = response.json()["errors"][0]["errorType"]
                    error_message = response.json()["errors"][0]["message"]

                    if error_type == "rateLimit":
                        logger.error(f"Rate limit error: {error_message} | Waiting 1m..")
                        time.sleep(60)
                        continue

                    else:
                        logger.error(f"Error: {error_type} | {error_message}")
                        time.sleep(0.1)
                        self.create_session()
                        continue

                response.raise_for_status()
                return response.json()

            except requests.errors.RequestsError as error:
                logger.error(f"Request error: {error.args}")
                time.sleep(0.1)
                self.create_session()


    def get_all_bets(self, limit: int = 40) -> dict:
        json_data = JsonQueries.all_sport_bets(limit)
        return self.api_request(json_data)

    @staticmethod
    def extract_bets_ids(data: dict) -> list[str]:
        print(len(data['data']['highrollerSportBets']), "BETS")
        return [bet["iid"] for bet in data["data"]["highrollerSportBets"]]

    def get_bet_data(self, iid: str) -> dict:
        json_data = JsonQueries.bet_lookup(iid)
        return self.api_request(json_data)


    @staticmethod
    def reformat_bet_data(data: dict) -> dict:
        data = data["data"]["bet"]
        _bet_data = {}


        try:
            if data["bet"]["__typename"] == "SportBet":
                # print(f"Amount {data['bet']['amount']} {data['bet']['currency']}")
                _bet_data = {
                    "bet_type": "Multiple" if len(data["bet"]["outcomes"]) > 1 else "Single",
                    "bet_id": data["iid"],
                    "url": f"https://stake.com/sports/home?iid={data['iid']}&modal=bet",
                    "user": data["bet"]["user"]["name"] if data["bet"]["user"] is not None else None,
                    "amount": float(data["bet"]["amount"]),
                    "currency": data["bet"]["currency"],
                    "total_multiplier": float(data["bet"]["potentialMultiplier"]),
                    "created_at": str(datetime.strptime(data["bet"]["createdAt"], "%a, %d %b %Y %H:%M:%S GMT")),
                    "outcomes": [
                        {
                            "outcome_id": outcome["outcome"]["id"],
                            "sport": outcome["fixture"]["tournament"]["category"]["sport"]["name"],
                            "market": outcome["market"]["name"],
                            "odds": float(outcome["odds"]),
                            "outcome_name": outcome["outcome"]["name"],
                            "start_time": str(datetime.strptime(outcome["fixture"]["data"]["startTime"], "%a, %d %b %Y %H:%M:%S GMT")),
                            "is_live": outcome["fixture"]["eventStatus"]["matchStatus"] != "Not started",
                            "live_score": None if outcome["fixture"]["eventStatus"]["matchStatus"] == "Not started" else f'{outcome["fixture"]["eventStatus"]["homeScore"]}-{outcome["fixture"]["eventStatus"]["awayScore"]}',
                            "live_status": None if outcome["fixture"]["eventStatus"]["matchStatus"] == "Not started" else outcome["fixture"]["eventStatus"]["matchStatus"],
                            "home": outcome["fixture"]["data"]["competitors"][0]["name"],
                            "away": outcome["fixture"]["data"]["competitors"][1]["name"],
                        }
                        for outcome in data["bet"]["outcomes"]
                    ]
                }

        except (KeyError, ValueError):
            pass

        return _bet_data


    def get_crypto_rates(self) -> None:
        while True:
            json_data = JsonQueries.currency_conversion_rate()
            data = self.api_request(json_data=json_data)

            currencies = data.get("data").get("info").get("currencies")
            if not currencies:
                logger.warning("Crypto rates not found")

            else:
                self.crypto_rates = currencies

            time.sleep(60)

    # @cachetools.func.ttl_cache(ttl=60)
    def convert_crypto_to_usd(self, currency: str, amount: float) -> float | None:
        while not self.crypto_rates:
            time.sleep(0.1)

        for _currency in self.crypto_rates:
            if _currency["name"] == currency:
                return amount * float(_currency["usd"])

        return None



    def add_bet_data_to_db(self, reformatted_data: dict) -> None:
        try:
            if reformatted_data["currency"] not in ("usd", "usdt"):
                amount_usd = self.convert_crypto_to_usd(reformatted_data["currency"].lower(), reformatted_data["amount"])
            else:
                amount_usd = float(reformatted_data["amount"])

            reformatted_data["amount_usd"] = amount_usd
            response = self.server.post("http://34.16.93.103:8004/data/process_bet", json=reformatted_data)
            logger.debug(response.text)

        except Exception as error:
            logger.error(f"Error while adding bet data to DB: {error}")


    def monitor_queue(self) -> None:
        while True:
            try:
                if self.queue.empty():
                    time.sleep(0.1)
                    continue

                data = self.queue.get()
                reformatted_data = self.reformat_bet_data(data)
                if reformatted_data:
                    Thread(target=self.add_bet_data_to_db, args=(reformatted_data,)).start()

            except Exception as error:
                logger.error(f"Error while monitoring queue: {error}")


    def process_bets(self) -> None:
        try:
            data = self.get_all_bets()
            ids = self.extract_bets_ids(data)

            for iid in ids:
                # if BetData.is_exists(iid):
                #     logger.warning(f"Bet with ID {iid} already exists")
                #     continue

                try:
                    _bet_data = self.get_bet_data(iid)
                    if _bet_data:
                        self.queue.put(_bet_data)

                except Exception as error:
                    logger.error(f"Error while processing bet with ID {iid}: {error}")

                # time.sleep(1)

        except Exception as error:
            logger.error(f"Error while processing bets cycle: {error}")


    def start(self):
        logger.info("Scraper started..")
        self.create_session()
        Thread(target=self.monitor_queue).start()
        Thread(target=self.get_crypto_rates).start()

        while True:
            self.process_bets()
            logger.debug("Waiting 40s..")
            time.sleep(40)


if __name__ == "__main__":
    scraper = Scraper()
    scraper.start()
