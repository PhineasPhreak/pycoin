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


# Liste des Requêtes URL avec aucune modification (Statique)
API_URL_BASE = "https://api.coingecko.com/api/v3/"

API_PING = f"{API_URL_BASE}ping"
GLOBAL_DATA = f"{API_URL_BASE}global"
GLOBAL_DATA_DEFI = f"{API_URL_BASE}global/decentralized_finance_defi"

# Variables pour les erreurs de "timeout" pour les requêtes
# INFO:
# - ConnectTimeout: The connect timeout is the number of seconds Requests will wait for your client to establish a connection to a remote machine call on the socket.
# - ReadTimeout: The read timeout is the number of seconds the client will wait for the server to send a response.
REQ_CONNECT_TIMEOUT = 25
REQ_READ_TIMEOUT = 100

# Variable static pour la version de Pycoin
PYCOIN_VERSION = "1.3.0"


def tmp_action():
    """Compteur pour le temps d'exécution d'une commande"""
    tmp_execution = timeit() * 60
    tmp_second = "{:,.2f}secs".format(tmp_execution)
    reponse = {"tmp_second": tmp_second, "tmp_execution": tmp_execution}

    # return tmp_second, tmp_execution
    return reponse


def check_api(visibility: str = "standard"):
    """
    Affiche le status du server de l'API de CoinGecko
    :param visibility: Determine si le résultat doit être affiché en Verbose ou pas
    :return: Affiche le résultat de la réponse du server plus le temps en seconde
    """

    try:
        answer_ping_raw = requests.get(API_PING).json()
        answer_ping = requests.get(API_PING).status_code

        if visibility == "standard":
            return print(f"Status Server : {answer_ping} in {tmp_action()['tmp_second']}")
        elif visibility == "verbose":
            return print(
                f"Reply Gecko : {answer_ping_raw['gecko_says']} "
                f"Status Server : {answer_ping} "
                f"in {tmp_action()['tmp_execution']}"
            )

    except requests.exceptions.ConnectionError as req_error:
        return f"Failed to establish a connection\n\n" f"{req_error.args}"


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
    Documentation de l'API de CoinGecko :
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
        pd_markets = requests.get(
            cg_markets,
            timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json()

        # Capture du status code 429 (TooManyRequests)
        # Trop d'erreurs 429, cela rend le programme inutilisable, à voir sur le long terme si des problèmes de donner qui du coup ne sont pas récupérés par les requêtes.
        # status_code = requests.get(
        #     cg_markets,
        #     timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).status_code
        # if status_code == 429:
        #     print("HTTPS Error 429: Too Many Requests")
        #     exit(1)

    except requests.ConnectTimeout as error_connect_timeout:
        print("Connect Time Error {0}", error_connect_timeout)

    except requests.ReadTimeout as error_read_timeout:
        print("Read Time Error {0}", error_read_timeout)

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
            "last_updated"
        ]
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
    name: str = "market",
    pd_index: bool = False,
    time_wait: int = 25
    ):
    """
    Création de la fonction pour la génération des fichiers...
    :param extension: Gestion des extensions du fichier de donner,
    les deux principales sont CSV, HTML.
    :param name: Nom du fichier de donner, par défaut "market"
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

                elif ext == "json":
                    df_concat.to_json(f"{name}.{ext}", orient="columns")

            return print(f"Successful creation of {name}.{extension} files")

        except urllib.error.HTTPError as HTTPError:
            return print("Code: ", HTTPError.code, HTTPError.reason)

        except urllib.error.URLError as URLError:
            return print(URLError.reason)


def global_data_market(
        extension: list,
        name: str = "global",
        type_data: list = ["default", "defi"]
        ):
    """
    Création de la fonction pour la génération des fichiers "global" et
    "global_defi".
    :param extension: Gestion des extensions du fichier de donner,
    les deux principales sont CSV, HTML.
    :param name: Nom du fichier de donner, par défaut "global", "global_defi"
    :param type_data: Liste des possibilités pour la génération des fichiers de sortie :
    default: global et defi: global_defi
    """

    # Affiche le DataFrame pandas dans le terminal avec les options ci-dessous
    # pas utile si pas d'affichage dans le terminal.
    # pd.options.display.max_rows = None
    # pd.options.display.max_columns = None
    # pd.options.display.max_colwidth = None
    # pd.options.display.width = 1000
    # pd.options.display.float_format = '{:,.2f}'.format
    # pd.options.display.precision = 2

    df_stack = []
    match type_data:
        case "default":
            # Raw date for JSON file
            raw_global_data_json_data = requests.get(
                GLOBAL_DATA,
                timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json()

            # Raw data for DataFrame
            global_data_json = requests.get(
                GLOBAL_DATA,
                timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json()
            pd_global_data_df_data = pd.DataFrame(
                data=global_data_json,
                index=[
                "active_cryptocurrencies",
                "upcoming_icos",
                "ongoing_icos",
                "ended_icos",
                "markets",
                "market_cap_change_percentage_24h_usd",
                "updated_at"
            ])
            # pd_global_data_df_data.to_csv("raw_data.csv")
            df_stack.append(pd_global_data_df_data)


            # total_market_cap
            global_data_json_total_market_cap = requests.get(
                GLOBAL_DATA,
                timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json() \
                ["data"]["total_market_cap"]
            pd_global_data_df_total_market_cap = pd.DataFrame(
                data=global_data_json_total_market_cap,
                index=["total_market_cap"])
            # pd_global_data_df_total_market_cap.to_csv("total_market_cap.csv")
            df_stack.append(pd_global_data_df_total_market_cap)


            # total_volume
            global_data_json_total_volume = requests.get(
                GLOBAL_DATA,
                timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json() \
                ["data"]["total_volume"]
            pd_global_data_df_total_volume = pd.DataFrame(
                data=global_data_json_total_volume,
                index=["total_volume"])
            # pd_global_data_df_total_volume.to_csv("total_volume.csv")
            df_stack.append(pd_global_data_df_total_volume)


            # market_cap_percentage
            global_data_json_market_cap_percentage = requests.get(
                GLOBAL_DATA,
                timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json() \
                ["data"]["market_cap_percentage"]
            pd_global_data_df_market_cap_percentage = pd.DataFrame(
                data=global_data_json_market_cap_percentage,
                index=["market_cap_percentage"])
            # pd_global_data_df_market_cap_percentage.to_csv("market_cap_percentage.csv")
            df_stack.append(pd_global_data_df_market_cap_percentage)

            # Concaténer les différents DataFrame en un seul au format CSV.
            df_concat = pd.concat(df_stack)
            # df_concat.to_csv("all_data.csv")
            # df_concat.to_html("all_data.html")

            for ext in extension:
                if ext == "csv":
                    df_concat.to_csv(f"{name}.{ext}")

                elif ext == "html":
                    df_concat.to_html(f"{name}.{ext}")

                elif ext == "json":
                    with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                        json_file.write(str(raw_global_data_json_data))

            return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")

        case "defi":
            global_data_json = requests.get(
                GLOBAL_DATA_DEFI,
                timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT)).json()
            pd_global_data_df = pd.DataFrame(data=global_data_json, columns=["data"])

            for ext in extension:
                if ext == "csv":
                    pd_global_data_df.to_csv(f"{name}.{ext}", header=False)

                elif ext == "html":
                    pd_global_data_df.to_html(f"{name}.{ext}", header=False)

                elif ext == "json":
                    with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                        json_file.write(str(global_data_json))

            return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")

        case _:
            return print(f"Error <{type_data}> is not a valid argument.")


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
    description="""Use of the CoinGecko API by generating a *.csv file (or html with verbose option),
with the non-exhaustive list of Cryptocurrency.""",
    epilog="""Pycoin home page: <https://github.com/PhineasPhreak/pycoin>"""
)

# Définition de la commande --name qui est une commande commune pour choisir le nom de fichier
# de sortie que vous souhaitez, mais attention pas son extension.
# La valeur par défaut comme nom de fichier est "market".
name_default = parser.add_argument_group()
name_default.add_argument(
    "-n",
    "--name",
    default="market",
    type=str,
    metavar="str",
    help="""Define output file name. default 'market'."""
)

extension_default = parser.add_argument_group()
extension_default.add_argument(
    "-e",
    "--extension",
    default="csv",
    choices=["csv", "html", "json"],
    metavar="str",
    help="""Selects CSV, HTML and JSON output file extensions"""
)

# Affiche les messages du serveur de CoinGecko
ping = parser.add_argument_group("Status Server")
ping.add_argument(
    "-P",
    "--ping",
    action="store_true",
    help="check API server status"
)

# Définition de la commande --page pour personnaliser le nombre de pages dans
# le fichier data.csv final. Nombre de pages par défaut 10.
market_data = parser.add_argument_group("Options market")
market_data.add_argument(
    "-p",
    "--page",
    # Si cette option <default=5> et de commenter le fichier python lancera automatiquement
    # la génération d'un fichier CSV avec 5 page, même sans argument donner au fichier python.
    # default=5,
    type=int,
    metavar="int",
    help="""Customization of the number of pages to generate in the *.csv,
do not exceed 15 for the page generation value"""
)

# La commande 'time' permet de préciser le temps d'attente en seconde entre les requêtes
market_data.add_argument(
    "-t",
    "--time",
    default="25",
    type=int,
    metavar="int",
    help="""Define waiting time in seconds between each request,
Avoid values below 5 seconds (default is 25 seconds)"""
)

# market_data.add_argument(
#     "-n",
#     "--name",
#     default="market",
#     type=str,
#     metavar="str",
#     help="""Define output file name. default 'market'."""
# )

# Définition de la commande --currency pour choisir le type de
# devise que nous voulons, USD étant la devise par défaut.
market_data.add_argument(
    "-c",
    "--currency",
    default="usd",
    type=str,
    metavar="str",
    help="""Choose the type of currency we want,
USD being the default currency. Choice: usd, eur, cad, gbp, etc"""
)

# CODE BLOCK - SI UTILISATION D'UN SUBPARSER...
# sub_parsers_global = parser.add_subparsers(title="Get cryptocurrency global data", dest="global_cmd")
# global_data = sub_parsers_global.add_parser("global", help="Get global data and for defi")
# global_data.add_argument(
#     "-g",
#     "--global",
#     type=str,
#     metavar="default, defi",
#     dest="global_data",
#     help="""Get global data: total_volume, total_market_cap, ongoing icos etc"""
# )
#
# global_data.add_argument(
#     "-n",
#     "--name",
#     default="global",
#     type=str,
#     metavar="str",
#     help="""okay"""
# )

# Création du groupe global_data pour "global"
global_data = parser.add_argument_group("Get cryptocurrency global data")
global_data.add_argument(
    "-g",
    "--global",
    action="store_true",
    dest="global_data",
    help="""Get global data - total_volume, total_market_cap, ongoing icos etc"""
)

# Ajout au groupe global_data pour "decentralized_finance_defi"
global_data.add_argument(
    "-G",
    "--global_defi",
    action="store_true",
    dest="global_defi",
    help="""Get Top 100 Cryptocurrency Global Eecentralized Finance(defi) data"""
)

# Affiche la version du programme
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=f"%(prog)s version {PYCOIN_VERSION}"
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
    # TODO: Développer davantage le "argparse"...
    # TODO: Ajouter davantage d'option disponible de l'API coingecko...
    # TODO: Avoir le choix de l'extension pour le fichier de sortie "json", "csv", "html" et voir pour d'autres extensions si possible.
    # À voir pour des ajouts comme 'exchange', 'global' (voir API coingecko)

    try:
        if args.verbose:
            if args.ping:
                check_api(visibility="verbose")

            elif args.page and args.currency:
                generate(extension=["csv", "html", "json"], name=args.name, time_wait=args.time)

        else:
            if args.ping:
                check_api(visibility="standard")

            elif args.page and args.currency:
                generate(extension=[args.extension], name=args.name, time_wait=args.time)


            elif args.global_data:
                if args.name == "market":
                    global_data_market(extension=[args.extension], name="global_data", type_data="default")
                else:
                    global_data_market(extension=[args.extension], name=args.name, type_data="default")

            elif args.global_defi:
                if args.name == "market":
                    global_data_market(extension=[args.extension], name="global_defi", type_data="defi")
                else:
                    global_data_market(extension=[args.extension], name=args.name, type_data="defi")

            # CODE BLOCK - SI UTILISATION D'UN SUBPARSER...
            # elif args.global_cmd == "global":
            #     global_data_market(extension=["csv"], name=args.name, type_data=args.global_data)

            else:
                # Si aucun argument saisi, afficher l'aide par défaut.
                print("No arguments entered, display default help.")
                args = parser.parse_args(["--help"])

    except KeyboardInterrupt as KeyboardError:
        print("Keyboard Interrupt")
