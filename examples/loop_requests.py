#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from timeit import timeit

vs_currencies = "usd"
order = "market_cap_desc"
per_page = 250
page = 1
sparkline = False
connect_timeout = 30
read_timeout = 100

cg_markets = (
    f"https://api.coingecko.com/api/v3/coins/"
    f"markets?vs_currency={vs_currencies}&"
    f"order={order}&"
    f"per_page={per_page}&"
    f"page={page}&"
    f"sparkline={sparkline}"
)

tmp_execution = timeit() * 60
tmp_second = "{:,.2f}sec".format(tmp_execution)

for _ in range(1, 3):
    try:
        print("Wait, 25 secs")
        time.sleep(15)
        response = requests.get(url=cg_markets, timeout=60).json()

    except requests.exceptions.TooManyRedirects as e:
        print(e)
    except requests.exceptions.ConnectTimeout as e:
        print(e)
    except requests.exceptions.ReadTimeout as e:
        print(e)

print(response, tmp_second)
