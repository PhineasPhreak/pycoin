#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import urllib.error
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn


# With this is that all errors will be ignored, therefore it is not ideal.
# import warnings

# RuntimeWarning: invalid value encountered in cast values = values.astype(str)
# warnings.filterwarnings("ignore")

def markets(
    vs_currencies="usd",
    order="market_cap_desc",
    per_page=250,
    page=1,
    sparkline=False,
):
    """
    List all supported coins price, market cap, volume,
    and market related data
    https://www.delftstack.com/howto/python-pandas/
    """

    cg_markets = (
        f"https://api.coingecko.com/api/v3/coins/"
        f"markets?vs_currency={vs_currencies}&"
        f"order={order}&"
        f"per_page={per_page}&"
        f"page={page}&"
        f"sparkline={sparkline}"
    )

    # Source all data in terminal
    # answer_markets = requests.get(cg_markets).json()

    # Convert json format on DataFrame in pandas
    pd_markets = pd.read_json(
        cg_markets,
        orient="records",
        encoding="utf-8",
        dtype="objet"
        )

    # For delete column in DataFrame
    # https://stackoverflow.com/questions/13411544/delete-a-column-from-a-pandas-dataframe
    pd_markets = pd.DataFrame(
        data=pd_markets,
        columns=[
            "id",
            "symbol",
            "name",
            "current_price",
            "market_cap",
            "market_cap_rank",
            "fully_diluted_valuation",
            "total_volume",
            "high_24h",
            "low_24h",
            "price_change_24h",
            "price_change_percentage_24h",
            "market_cap_change_24h",
            "market_cap_change_percentage_24h",
            "circulating_supply",
            "total_supply",
            "max_supply",
            "last_updated",
        ],
    )

    # Sets the 'market_cap_rank' column as an index of the my_df DataFrame
    pd_markets_df_rank = pd_markets.set_index("market_cap_rank")

    # pd_markets_df_rank.to_csv("data.csv", encoding="utf-8", index=False)

    # Delete 'image' column in the data Frame
    # pd_markets_df_rank.drop('image', axis=1, inplace=True)

    return pd_markets_df_rank

# Exemple sans boucle FOR
# df1 = markets(category=False, page=1)
# df2 = markets(category=False, page=2)

# df_concat = pd.concat([df1, df2])
# print(df_concat)
# df_concat.to_csv("data.csv", index=False)


# Concaténer plusieurs tableaux pandas ensemble
# https://www.geeksforgeeks.org/convert-multiple-json-files-to-csv-python/
# https://towardsdatascience.com/concatenate-multiple-and-messy-dataframes-efficiently-80847b4da12b
number_of_page = 10
dfs = []

progress = Progress(
    TextColumn("Downloading...", table_column=Column(ratio=1)),
    BarColumn(table_column=Column(ratio=2)),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(binary_units=False)
)

with progress:
    try:
        for num_page in progress.track(range(1, number_of_page + 1)):
            df_market = markets(page=num_page)
            dfs.append(df_market)

        df_concat = pd.concat(dfs)
        df_concat.to_csv("data.csv", index=False)

    except urllib.error.HTTPError as httpError:
        print(httpError)
