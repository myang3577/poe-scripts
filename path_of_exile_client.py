import logging
import os
import time

import requests

from constants import SLEEP_TIME

LOG = logging.getLogger(__name__)


class PathOfExileClient:
    TRADE_SEARCH_URL = "https://www.pathofexile.com/api/trade/search/Crucible"  # initial search request
    TRADE_FETCH_URL = "https://www.pathofexile.com/api/trade/fetch/"  # get the actual items in the trade
    WHISPER_URL = "https://www.pathofexile.com/api/trade/whisper"
    TRADE_FETCH_BATCH_SIZE = 10

    def __init__(self, posessid, username):
        self.session = requests.Session()
        self.session.cookies.set("POESESSID", posessid)
        self.session.headers = {
            "User-Agent": username,
            "referer": "https://www.pathofexile.com/trade/search/Crucible/VGgdqKwfp",
        }

    def query_trade(self, payload, result_count=TRADE_FETCH_BATCH_SIZE, item_name=None):
        LOG.info("Querying trade site.")

        if item_name:
            payload["query"]["term"] = item_name

        res = self.session.post(PathOfExileClient.TRADE_SEARCH_URL, json=payload)
        res.raise_for_status()

        if not res.ok:
            print(res.json())
            return None

        search_res = res.json()

        if item_name:
            item_link = (
                f"https://www.pathofexile.com/trade/search/Crucible/{search_res['id']}"
            )
            LOG.info(
                f"Searched for [{item_name}] in trade site. Opening link: [{item_link}]."
            )

            time.sleep(SLEEP_TIME)
            os.system(f"cmd.exe /C start {item_link}")
            time.sleep(SLEEP_TIME)
            return

        return self.__fetch_trade_items(
            search_res=search_res, result_count=result_count
        )

    def __fetch_trade_items(self, search_res, result_count):
        results = []

        if len(search_res["result"]) < result_count:
            result_count = len(search_res["result"])

        LOG.info(f"Fetching [{result_count}] items from trade site.")

        for i in range(0, result_count, PathOfExileClient.TRADE_FETCH_BATCH_SIZE):
            LOG.info(
                f"Fetching items [{i}] to [{i + PathOfExileClient.TRADE_FETCH_BATCH_SIZE}] from trade site."
            )
            item_ids = ",".join(
                search_res["result"][i : i + PathOfExileClient.TRADE_FETCH_BATCH_SIZE]
            )

            fetch_url = f"{PathOfExileClient.TRADE_FETCH_URL}{item_ids}?query={search_res['id']}"

            res = self.session.get(fetch_url)
            res.raise_for_status()

            if not res.ok:
                print(res.json())
                return None

            results += res.json()["result"]

            LOG.info(
                f"Sleeping for {SLEEP_TIME} second(s) to not overload the trade site."
            )
            time.sleep(SLEEP_TIME)

        return results
