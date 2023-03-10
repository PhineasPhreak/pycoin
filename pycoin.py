#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
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
    Liste de tous les Tokens pris en charge : prix, capitalisation boursière,
    volume, et les données relatives au marché.
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

    # La conversion du format brute JSON en DataFrame avec pandas
    pd_markets = pd.read_json(
        cg_markets,
        orient="records",
        encoding="utf-8",
        dtype="objet"
        )

    # Sélection de chaque colonne avec pandas, si la colonne n'est pas citée
    # ci-dessous alors, elle ne sera pas présente dans le DataFrame
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

    # Définit la colonne 'market_cap_rank' comme index du DataFrame
    pd_markets_df_rank = pd_markets.set_index("market_cap_rank")

    # Supprimer la colonne "image" dans le DataFrame.
    # Si besoin de supprimer une colonne...
    # pd_markets_df_rank.drop('image', axis=1, inplace=True)

    return pd_markets_df_rank


progress = Progress(
    TextColumn("Downloading...", table_column=Column(ratio=1)),
    BarColumn(table_column=Column(ratio=2)),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(binary_units=False)
)

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="""Use of the CoinGecko API by generating a *.csv file,
with the non-exhaustive list of Cryptocurrency."""
)

# Définition de la commande --page pour personnaliser le nombre de pages dans
# le fichier data.csv final. Nombre de pages par défaut 10.
num_page = parser.add_argument_group()
num_page.add_argument(
    "-p",
    "--page",
    default=10,
    type=int,
    metavar="Number",
    help="""Customization of the number of pages to generate in the data.csv,
do not exceed 15 for the page generation value, file default value 10"""
)

args = parser.parse_args()


if __name__ == '__main__':
    dfs = []
    if args.page:
        with progress:
            try:
                for num_page in progress.track(range(1, args.page + 1)):
                    df_market = markets(page=num_page)
                    dfs.append(df_market)

                # Concaténer plusieurs tableaux pandas ensemble
                # https://www.geeksforgeeks.org/convert-multiple-json-files-to-csv-python/
                # https://towardsdatascience.com/concatenate-multiple-and-messy-dataframes-efficiently-80847b4da12b
                df_concat = pd.concat(dfs)
                df_concat.to_csv("data.csv", index=False)
                df_concat.to_html("data.html", index=False)

            except urllib.error.HTTPError as HTTPError:
                print(HTTPError)
