#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import urllib.error
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn


# With this is that all errors will be ignored, therefore it is not ideal.
# import warnings

# RuntimeWarning: invalid value encountered in cast values = values.astype(str)
# warnings.filterwarnings("ignore")

def markets(
    vs_currencies: str = "usd",
    order: str = "market_cap_desc",
    per_page: int = 250,
    page: int = 1,
    sparkline: bool = False
):
    """
    Liste de tous les Tokens pris en charge : prix, capitalisation boursière,
    volume et les données relatives au marché.
    https://www.coingecko.com/en/api/documentation
    :param vs_currencies: Définir la monnaie cible des données de marché
    :param order: Valeurs valides : (market_cap_asc, market_cap_desc,
    volume_asc, volume_desc, id_asc, id_desc) trier les résultats par champ.
    :param per_page: Valeurs valables : 1[...]250 Total des résultats par page
    :param page: Parcourir les nombres de page demandé
    :param sparkline: Inclure les données du sparkline des 7 derniers jours
    :return: Retourne un tableau (DataFrame)
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
    # https://www.delftstack.com/howto/python-pandas/
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
    # pd_markets_df_rank = pd_markets.set_index("market_cap_rank")

    # Trie la colonne "market_cap_rank dans l'ordre croissant
    pd_markets_df_sort_rank = pd_markets.sort_values("market_cap_rank")

    # Supprimer la colonne "image" dans le DataFrame.
    # Si besoin de supprimer une colonne...
    # pd_markets_df_rank.drop('image', axis=1, inplace=True)

    return pd_markets_df_sort_rank


def generate(
    extension: list = ("csv", "html"),
    name: str = "data",
    pd_index: bool = False
):
    """
    Création de la fonction pour la génération des fichiers...
    :param extension: Gestion des extensions du fichier de donner,
    les deux principales sont CSV, HTML.
    :param name: Nom du fichier de donner, par défaut "data"
    :param pd_index: Détermine si l'index du tableau doit être présent ou pas
    :return: Les résultats des différents fichiers CSV ou HTML ou les erreurs.
    """
    dfs = []
    with progress:
        try:
            for num_pages in progress.track(range(1, args.page + 1)):
                df_market = markets(page=num_pages)
                dfs.append(df_market)

            # Concaténer plusieurs tableaux pandas ensemble
            # https://www.geeksforgeeks.org/convert-multiple-json-files-to-csv-python/
            # https://towardsdatascience.com/concatenate-multiple-and-messy-dataframes-efficiently-80847b4da12b
            df_concat = pd.concat(dfs)

            for exe in extension:
                if exe == "csv":
                    df_concat.to_csv(f"{name}.{exe}", index=pd_index)

                elif exe == "html":
                    df_concat.to_html(f"{name}.{exe}", index=pd_index)

            return None

        except urllib.error.HTTPError as HTTPError:
            return print(HTTPError.reason)

        except urllib.error.URLError as URLError:
            return print(URLError.reason)


# Personnalisation de la progress bar.
progress = Progress(
    TextColumn(text_format="Downloading..."),
    BarColumn(bar_width=50),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn()
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
    help="""customization of the number of pages to generate in the *.csv,
do not exceed 15 for the page generation value, file default value 10"""
)

# Groupe pour verbose ou quiet, groupe mutuellement exclusif
# soit verbose ou quiet, mais pas les deux.
output = parser.add_mutually_exclusive_group()

# output.add_argument('-q', '--quiet', action='store_true', help='print quiet')
output.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="increase output visibility"
)

args = parser.parse_args()


if __name__ == '__main__':
    # TODO: Développer davantage le "argparse"
    # Implémenter davantage de fonctions par défaut essentiel,
    # et plus d'option avec l'option verbose...

    # TODO: Ajouter la fonction ping sur l'API de CoinGecko.

    if args.verbose:
        if args.page:
            pass

    else:
        if args.page:
            generate(name="data", extension=["csv"], pd_index=False)

# Surement utile plus tard pour les options
# cols_df = list(df_concat.columns.values)
# print(cols_df)
#
# df_concat_print = df_concat.drop(
#     [
#         "name",
#         "market_cap",
#         "fully_diluted_valuation",
#         "total_volume",
#         "high_24h",
#         "low_24h",
#         "price_change_24h",
#         "price_change_percentage_24h",
#         "market_cap_change_24h",
#         "market_cap_change_percentage_24h",
#         "max_supply"
#     ],
#     axis=1)
# pd.set_option('expand_frame_repr', False)
# pd.set_option('display.max_columns', 999)
# pd.set_option('display.max_rows', 999)
# print(df_concat_print)
