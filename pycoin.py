#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import time
import pandas as pd
import requests
from timeit import timeit
import urllib.error
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn


# With this is that all errors will be ignored, therefore it is not ideal.
# import warnings

# RuntimeWarning: invalid value encountered in cast values = values.astype(str)
# warnings.filterwarnings("ignore")

API_PING = "https://api.coingecko.com/api/v3/ping"


def check_api(visibility: str = "standard"):
    """
    Affiche le status du server de l'API de CoinGecko
    :param visibility: Determine si le résultat doit être affiché en Verbose ou pas
    :return: Affiche le résultat de la réponse du server plus le temps en seconde
    """

    try:
        answer_ping_raw = requests.get(API_PING).json()
        answer_ping = requests.get(API_PING).status_code

        tmp_execution = timeit() * 60
        tmp_second = "{:,.2f}secs".format(tmp_execution)

        if visibility == "standard":
            return print(f"Status Server : {answer_ping} in {tmp_second}")
        elif visibility == "verbose":
            return print(
                f"Reply Gecko : {answer_ping_raw['gecko_says']} "
                f"Status Server : {answer_ping} "
                f"in {tmp_execution}"
            )

    except requests.exceptions.ConnectionError as req_error:
        return f"Failed to establish a connection\n\n" f"{req_error.args}"


def markets(
    vs_currencies: str = "usd",
    order: str = "market_cap_desc",
    per_page: int = 250,
    page: int = 1,
    sparkline: bool = False,
    connect_timeout: int = 25,
    read_timeout: int = 100
):
    """
    Liste de tous les Tokens pris en charge : prix, capitalisation boursière,
    volume et les données relatives au marché.
    Documentation de l'API de CoinGecko :
    https://www.coingecko.com/en/api/documentation
    :param vs_currencies: Définir la monnaie cible des données de marché
    :param order: Valeurs valides : (market_cap_asc, market_cap_desc,
    volume_asc, volume_desc, id_asc, id_desc) trier les résultats par champ.
    :param per_page: Valeurs valables : 1[...]250 Total des résultats par page
    :param page: Parcourir les nombres de page demandé
    :param sparkline: Inclure les données du sparkline des 7 derniers jours
    :param connect_timeout: The connect timeout is the number of seconds
    Requests will wait for your client to establish a connection to a remote
    machine call on the socket.
    :param read_timeout: The read timeout is the number of seconds the client
    will wait for the server to send a response.
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
    # pd_markets = pd.read_json(
    #     cg_markets,
    #     orient="records",
    #     encoding="utf-8",
    #     dtype="objet"
    #     )

    # Utilisation de requests pour la récupération d'un format JSON
    # Info :
    # https://reqbin.com/code/python/3zdpeao1/python-requests-timeout-example
    # Read docs :
    # https://requests.readthedocs.io/en/stable/user/advanced/#timeouts
    try:
        pd_markets = requests.get(cg_markets, timeout=(connect_timeout,
                                                       read_timeout)).json()

    except requests.ConnectTimeout as e:
        print("Connect Time Error {}", e)

    except requests.ReadTimeout as e:
        print("Read Time Error {}", e)

    # Sélection de chaque colonne avec pandas, si la colonne n'est pas citée
    # ci-dessous alors, elle ne sera pas présente dans le DataFrame
    # https://www.delftstack.com/howto/python-pandas/
    # https://stackoverflow.com/questions/13411544/delete-a-column-from-a-pandas-dataframe
    dt_markets = pd.DataFrame(
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
    pd_markets_df_sort_rank = dt_markets.sort_values("market_cap_rank")

    # Supprimer la colonne "image" dans le DataFrame.
    # Si besoin de supprimer une colonne...
    # pd_markets_df_rank.drop('image', axis=1, inplace=True)

    return pd_markets_df_sort_rank


def generate(
    extension: list,
    name: str = "data",
    pd_index: bool = False,
    time_wait: int = 25,
):
    """
    Création de la fonction pour la génération des fichiers...
    :param extension: Gestion des extensions du fichier de donner,
    les deux principales sont CSV, HTML.
    :param name: Nom du fichier de donner, par défaut "data"
    :param pd_index: Détermine si l'index du tableau doit être présent ou pas
    :param time_wait: Définition du temps d'attente en seconde entre chaque requête
    :return: Les résultats des différents fichiers CSV ou HTML ou les erreurs.
    """
    dfs = []
    with progress:
        try:
            for num_pages in progress.track(range(1, args.page + 1)):
                if args.currency:
                    # Juste un message entre chaque génération des pages
                    # print(f"Generate pages {num_pages}/{args.page},"
                    #       f"wait 25 Secs for the next one.")
                    time.sleep(time_wait)
                    df_market = markets(vs_currencies=args.currency,
                                        page=num_pages)
                else:
                    time.sleep(time_wait)
                    df_market = markets(page=num_pages)
                dfs.append(df_market)

            # Concaténer plusieurs tableaux pandas ensemble
            # https://www.geeksforgeeks.org/convert-multiple-json-files-to-csv-python/
            # https://towardsdatascience.com/concatenate-multiple-and-messy-dataframes-efficiently-80847b4da12b
            df_concat = pd.concat(dfs)

            for ext in extension:
                if ext == "csv":
                    df_concat.to_csv(f"{name}.{ext}", index=pd_index)

                elif ext == "html":
                    df_concat.to_html(f"{name}.{ext}", index=pd_index)

            return None

        except urllib.error.HTTPError as HTTPError:
            return print("Code: ", HTTPError.code, HTTPError.reason)

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

# Affiche les messages du serveur de CoinGecko
ping = parser.add_argument_group()
ping.add_argument(
    "-P",
    "--ping",
    action="store_true",
    help="check API server status"
)

# Définition de la commande --page pour personnaliser le nombre de pages dans
# le fichier data.csv final. Nombre de pages par défaut 10.
num_page = parser.add_argument_group()
num_page.add_argument(
    "-p",
    "--page",
    default=5,
    type=int,
    metavar="int",
    help="""customization of the number of pages to generate in the *.csv,
do not exceed 15 for the page generation value, file default value 5"""
)

time_to_wait = parser.add_argument_group()
time_to_wait.add_argument(
    "-t",
    "--time",
    default="25",
    type=int,
    metavar="int",
    help="""Define waiting time in seconds between each request,
Avoid values below 5 seconds (default is 25 seconds)"""
)

# Définition de la commande --currency pour choisir le type de
# devise que nous voulons, USD étant la devise par défaut.
choice_currency = parser.add_argument_group()
choice_currency.add_argument(
    "-c",
    "--currency",
    default="usd",
    type=str,
    metavar="str",
    help="""Choose the type of currency we want,
USD being the default currency. Choice: usd, eur, cad, gbp, etc"""
)

# Affiche la version du programme
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version="%(prog)s version 0.2"
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
    # TODO: Parser pour le temps d'attente entre les requests
    # TODO: Modifier le parser pour la sortie des fichier CSV/HTML
    # Faire une possible modification pour la sélection des extensions

    try:
        if args.verbose:
            if args.ping:
                check_api(visibility="verbose")

            elif args.page:
                generate(extension=["csv", "html"], time_wait=args.time)

        else:
            if args.ping:
                check_api(visibility="standard")

            elif args.page:
                generate(extension=["csv"], time_wait=args.time)

            elif args.currency:
                generate(extension=["csv"], time_wait=args.time)

    except KeyboardInterrupt as KeyboardError:
        print("Keyboard Interrupt")
