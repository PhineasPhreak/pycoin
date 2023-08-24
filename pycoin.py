#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PIP3 install : pandas, rich, requests, openpyxl


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

# *** OPTION PANDAS ***
# Affiche le DataFrame pandas dans le terminal avec les options ci-dessous:
# pd.options.display.max_rows = None
# pd.options.display.max_columns = None
# pd.options.display.max_colwidth = None
# pd.options.display.width = 1000
# pd.options.display.float_format = '{:,.2f}'.format
# pd.options.display.precision = 2

# Liste des Requêtes URL avec aucune modification (Statique)
API_URL_BASE = "https://api.coingecko.com/api/v3/"

API_PING = f"{API_URL_BASE}ping"
GLOBAL_DATA = f"{API_URL_BASE}global"
GLOBAL_DATA_DEFI = f"{API_URL_BASE}global/decentralized_finance_defi"
TRENDING_TOP7 = f"{API_URL_BASE}search/trending"

# Variables pour les erreurs de "timeout" pour les requêtes
# INFO:
# - ConnectTimeout: The connect timeout is the number of seconds Requests will wait for your client to establish a connection to a remote machine call on the socket.
# - ReadTimeout: The read timeout is the number of seconds the client will wait for the server to send a response.
REQ_CONNECT_TIMEOUT = 25
REQ_READ_TIMEOUT = 100

# Variable static pour la version de Pycoin
PYCOIN_VERSION = "1.8.2"


def tmp_action():
    """Compteur pour le temps d'exécution d'une commande"""
    tmp_execution = timeit() * 60
    tmp_second = "{:,.2f}secs".format(tmp_execution)
    reponse = {"tmp_second": tmp_second, "tmp_execution": tmp_execution}

    return reponse


def check_api(visibility: str = "standard"):
    """
    Affiche le status du server de l'API de CoinGecko
    :param visibility: Determine si le résultat doit être affiché en Verbose ou pas
    :return: Affiche le résultat de la réponse du server plus le temps en seconde
    """

    try:
        requests_ping = requests.get(API_PING)
        answer_ping_json = requests_ping.json()
        answer_ping_headers = requests_ping.headers
        answer_ping_status = requests_ping.status_code

        if visibility == "standard":
            return print(f"Status Server : {answer_ping_status} "
                         f"in {tmp_action()['tmp_second']}")
        elif visibility == "verbose":
            return print(
                f"{answer_ping_headers['Date']}\n"
                f"Reply Gecko : {answer_ping_json['gecko_says']} "
                f"Status Server : {answer_ping_status} "
                f"in {tmp_action()['tmp_execution']}"
            )

    except requests.exceptions.ConnectionError as req_error:
        return f"Failed to establish a connection\n\n" f"{req_error.args}"


def coins_list(
        extension: list,
        name: str = "coins_list",
        include_platform: bool = False
):
    """
    Liste de toutes les cryptos prises en charge (id, name et symbol)
    :param extension: Gestion des extensions du fichier de donner, les possibilités sont sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "coins_list"
    :param: include_platform: pour inclure les adresses des contrats de plateforme (par exemple, 0x.... pour les jetons basés sur Ethereum).
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
    """

    cg_coins_list = (
        f"{API_URL_BASE}coins/"
        f"list?include_platform={include_platform}"
    )

    requests_coins_list = requests.get(cg_coins_list, timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT))
    coins_list_json = requests_coins_list.json()
    pd_coins_list_df = pd.DataFrame(data=coins_list_json)

    for ext in extension:
        if ext == "csv":
            pd_coins_list_df.to_csv(f"{name}.{ext}", index=False)

        elif ext == "html":
            pd_coins_list_df.to_html(f"{name}.{ext}", index=False)

        elif ext == "json":
            with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                json_file.write(str(coins_list_json))

        elif ext == "xlsx":
            pd_coins_list_df.to_excel(f"{name}.{ext}", sheet_name="COINS_LIST", index=False)

    return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")


def markets(
        vs_currencies: str = "usd",
        order: str = "market_cap_desc",
        per_page: int = 250,
        page: int = 1,
        sparkline: bool = False
):
    """
    Liste de tous les Tokens pris en charge : prix, capitalisation boursière, volume et les données relatives au marché.
    Documentation de l'API de CoinGecko :
    https://www.coingecko.com/en/api/documentation
    :param vs_currencies: Définir la monnaie cible des données de marché
    :param order: Valeurs valides : (market_cap_asc, market_cap_desc, volume_asc, volume_desc, id_asc, id_desc) trier les résultats par champ.
    :param per_page: Valeurs valables : 1[...]250 Total des résultats par page
    :param page: Parcourir les nombres de page demandé
    :param sparkline: Inclure les données du sparkline des 7 derniers jours
    :return: Retourne un tableau (DataFrame)
    """

    cg_market = (
        f"{API_URL_BASE}coins/"
        f"markets?vs_currency={vs_currencies}&"
        f"order={order}&"
        f"per_page={per_page}&"
        f"page={page}&"
        f"sparkline={sparkline}"
    )

    # La conversion du format brute JSON en DataFrame avec pandas
    # pd_markets = pd.read_json(
    #     cg_market,
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
        request_market = requests.get(cg_market, timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT))
        market_json = request_market.json()

        # Capture du status code 429 (TooManyRequests)
        # Trop d'erreurs 429, cela rend le programme inutilisable, à voir sur le long terme si des problèmes de manque de donner.
        # status_code = request_market.status_code
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
        data=market_json,
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
    # pd_markets_df_rank = market_json.set_index("market_cap_rank")

    # Trie la colonne "market_cap_rank dans l'ordre croissant
    pd_markets_df_sort_rank = dt_markets.sort_values("market_cap_rank")

    # Supprimer la colonne "image" dans le DataFrame.
    # Si besoin de supprimer une colonne...
    # pd_markets_df_rank.drop('image', axis=1, inplace=True)

    return pd_markets_df_sort_rank


def generate(
        extension: list,
        name: str = "markets",
        pd_index: bool = False,
        time_wait: int = 25
):
    """
    Création de la fonction pour la génération des fichiers...
    :param extension: Gestion des extensions du fichier de donner, les possibilités sont sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "markets"
    :param pd_index: Détermine si l'index du tableau doit être présent ou pas
    :param time_wait: Définition du temps d'attente en seconde entre chaque requête
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
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

                elif ext == "xlsx":
                    df_concat.to_excel(f"{name}.{ext}", sheet_name="MARKETS", index=pd_index)

            return print(f"Successful creation of {name}.{extension} files")

        except urllib.error.HTTPError as HTTPError:
            return print("Code: ", HTTPError.code, HTTPError.reason)

        except urllib.error.URLError as URLError:
            return print(URLError.reason)


def exchanges(
        extension: str,
        name: str = "exchanges",
        per_page: int = 250,
        page: int = 1
):
    """
    :param extension: Gestion des extensions du fichier de donner, les possibilités sont sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "exchanges"
    :param per_page: Valeurs valables : 1[...]250 Total des résultats par page
    :param page: Parcourir les nombres de page demandé, ici seulement une
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
    """
    cg_exchanges = (
        f"{API_URL_BASE}exchanges"
        f"?per_page={per_page}&"
        f"page={page}"
    )

    try:
        requests_exchanges = requests.get(cg_exchanges, timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT))
        exchanges_json = requests_exchanges.json()

    except requests.ConnectTimeout as error_connect_timeout:
        print("Connect Time Error {0}", error_connect_timeout)

    except requests.ReadTimeout as error_read_timeout:
        print("Read Time Error {0}", error_read_timeout)

    dt_exchanges = pd.DataFrame(
        data=exchanges_json,
        columns=[
            "id",
            "name",
            "year_established",
            "country",
            "has_trading_incentive",
            "trust_score",
            "trust_score_rank",
            "trade_volume_24h_btc",
            "trade_volume_24h_btc_normalized"
        ]
    )

    for ext in extension:
        if ext == "csv":
            dt_exchanges.to_csv(f"{name}.{ext}", index=False)

        elif ext == "html":
            dt_exchanges.to_html(f"{name}.{ext}", index=False)

        elif ext == "json":
            dt_exchanges.to_json(f"{name}.{ext}", orient="columns")

        elif ext == "xlsx":
            dt_exchanges.to_excel(f"{name}.{ext}", sheet_name="EXCHANGES", index=False)

    return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")


def global_data_market(
        extension: list,
        name: str = "global"
):
    """
    Création de la fonction pour la génération du fichier "global"
    :param extension: Gestion des extensions du fichier de donner, les deux principales sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "global"
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
    """

    df_stack = []
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

    for ext in extension:
        if ext == "csv":
            df_concat.to_csv(f"{name}.{ext}")

        elif ext == "html":
            df_concat.to_html(f"{name}.{ext}")

        elif ext == "json":
            with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                json_file.write(str(raw_global_data_json_data))

        elif ext == "xlsx":
            df_concat.to_excel(f"{name}.{ext}", sheet_name="GLOBAL")

    return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")


def global_defi_market(
        extension: list,
        name: str = "global_defi"
):
    """
    Création de la fonction pour la génération du fichier "global_defi"
    :param extension: Gestion des extensions du fichier de donner, les deux principales sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "global_defi"
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
    """

    requests_global_defi = requests.get(GLOBAL_DATA_DEFI, timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT))
    global_defi_json = requests_global_defi.json()
    pd_global_data_df = pd.DataFrame(data=global_defi_json, columns=["data"])

    for ext in extension:
        if ext == "csv":
            pd_global_data_df.to_csv(f"{name}.{ext}", header=False)

        elif ext == "html":
            pd_global_data_df.to_html(f"{name}.{ext}", header=False)

        elif ext == "json":
            with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                json_file.write(str(global_defi_json))

        elif ext == "xlsx":
            pd_global_data_df.to_excel(f"{name}.{ext}", sheet_name="GLOBAL_DEFI", header=False)

    return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")


def trending_top7(
        extension: list,
        name: str = "trending_top7"
):
    """
    Création de la fonction pour la génération du fichier "trending_top7"
    :param extension: Gestion des extensions du fichier de donner, les deux principales sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "trending_top7"
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
    """

    dfs = []
    request_trending = requests.get(TRENDING_TOP7, timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT))
    trending_data_json = request_trending.json()

    for top_trending in range(0, len(trending_data_json["coins"])):
        trending_data = trending_data_json["coins"][top_trending]
        pd_trending_data = pd.DataFrame(data=trending_data)
        dfs.append(pd_trending_data)

    df_concat = pd.concat(dfs)

    for ext in extension:
        if ext == "csv":
            df_concat.to_csv(f"{name}.{ext}", header=False)

        elif ext == "html":
            df_concat.to_html(f"{name}.{ext}", header=False)

        elif ext == "json":
            with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                json_file.write(str(trending_data_json))

        elif ext == "xlsx":
            df_concat.to_excel(f"{name}.{ext}", sheet_name="TRENDING_TOP7", header=False)

    return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")


def companies(
        extension: list,
        name: str = "companies",
        coin_id: list = ["bitcoin", "ethereum"]
):
    """
    Obtenir les avoirs en bitcoins ou en ethereum des entreprises publiques (classés par ordre décroissant du nombre total d'avoirs)
    :param extension: Gestion des extensions du fichier de donner, les possibilités sont sont CSV, HTML et JSON.
    :param name: Nom du fichier de donner, par défaut "companies"
    :return: Les résultats des différents fichiers CSV ou HTML et JSON ou les erreurs.
    """

    dfs = []
    cg_companies = (
        f"{API_URL_BASE}companies/public_treasury/{coin_id}"
    )

    requests_companies = requests.get(cg_companies, timeout=(REQ_CONNECT_TIMEOUT, REQ_READ_TIMEOUT))
    companies_json = requests_companies.json()
    companies_json_only_companies = companies_json["companies"]

    pd_companies_df = pd.DataFrame(data=companies_json, columns=["total_holdings", "total_value_usd", "market_cap_dominance"], index=[""])
    pd_companies_df_only_companies = pd.DataFrame(data=companies_json_only_companies)
    dfs.append(pd_companies_df)
    dfs.append(pd_companies_df_only_companies)

    df_concat = pd.concat(dfs)

    for ext in extension:
        if ext == "csv":
            df_concat.to_csv(f"{name}.{ext}")

        elif ext == "html":
            df_concat.to_html(f"{name}.{ext}")

        elif ext == "json":
            with open(file=f"{name}.{ext}", mode="w", encoding="utf-8") as json_file:
                json_file.write(str(companies_json))

        elif ext == "xlsx":
            df_concat.to_excel(f"{name}.{ext}", sheet_name="COMPANIES")

    return print(f"Create {name}.{extension} in {tmp_action()['tmp_second']}")


# Personnalisation de la progress bar.
progress = Progress(
    TextColumn(text_format="Downloading..."),
    BarColumn(bar_width=50),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn()
)

parser = argparse.ArgumentParser(
    # Maintient un espace blanc pour toutes sortes de textes d'aide
    # https://docs.python.org/3/library/argparse.html#argparse.RawTextHelpFormatter
    # formatter_class=argparse.RawTextHelpFormatter,

    # Indique que la description et l'épilogue sont déjà correctement formatés et ne doivent pas être entourés de lignes
    # https://docs.python.org/3/library/argparse.html#argparse.RawDescriptionHelpFormatter
    # formatter_class=argparse.RawDescriptionHelpFormatter,
    description="""Use of the CoinGecko API by generating a CSV, HTML AND JSON file,
    with the non-exhaustive list of Cryptocurrency.""",
    epilog="""Pycoin home page: <https://github.com/PhineasPhreak/pycoin>"""
)

# Définition de la commande --name qui est une commande commune pour choisir le nom de fichier de sortie que vous souhaitez, mais attention pas son extension. La valeur par défaut comme nom de fichier est "markets".
name_default = parser.add_argument_group()
name_default.add_argument(
    "-n",
    "--name",
    type=str,
    metavar="str",
    help="""Define output file name. default 'markets'"""
)

# Définition de la commande --extension qui est une commande commune pour choisir l'extension du fichier de sortie, les formats possibles sont CSV, HTML, JSON
# nargs="+": Tous les arguments présents sur la ligne de commande sont capturés dans une liste. De plus, un message d'erreur est produit s'il n'y a pas au moins un argument présent sur la ligne de commande.
extension_default = parser.add_argument_group()
extension_default.add_argument(
    "-e",
    "--extension",
    default=["csv"],
    choices=["csv", "html", "json", "xlsx"],
    nargs="+",
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

# Définition de la commande --coins_list pour afficher la liste des cryptos
coins_list_arg = parser.add_argument_group("Coins List")
coins_list_arg.add_argument(
    "-C",
    "--coins_list",
    action="store_true",
    help="""List all coins with id, name, and symbol.
    All the coins that show up on this /coins/list endpoint are Active coins that listed by CoinGecko team on CoinGecko.com.
    If a coin is inactive or deactivated, it will be removed from /coins/list"""
)

# Définition de la commande --page pour personnaliser le nombre de pages dans le fichier final. Nombre de pages par défaut 10.
market_data = parser.add_argument_group("Options Markets")
market_data.add_argument(
    "-p",
    "--page",
    # Si cette option <default=5> et de commenter le fichier python lancera automatiquement la génération d'un fichier CSV avec 5 page, même sans argument donner au fichier python.
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

# Définition de la commande --currency pour choisir le type de devise que nous voulons, USD étant la devise par défaut.
market_data.add_argument(
    "-c",
    "--currency",
    default="usd",
    type=str,
    metavar="str",
    help="""Choose the type of currency we want,
    USD being the default currency. Choice: usd, eur, cad, gbp, etc"""
)

# Définition de la commande --exchanges pour lister tous les exchanges actif
exchanges_data = parser.add_argument_group("Options Exchanges")
exchanges_data.add_argument(
    "-E",
    "--exchanges",
    action="store_true",
    help="""List all exchanges (Active with trading volumes)"""
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
    help="""Get Top 100 Cryptocurrency Global Eecentralized Finance(defi) data"""
)

# Génération des tendances de coingecko sur les dernières 24h
trending_data = parser.add_argument_group("Get Top-7 trending coins")
trending_data.add_argument(
    "-T",
    "--trending",
    action="store_true",
    help="""Top-7 trending coins on CoinGecko as searched by users in the last 24 hours (Ordered by most popular first)."""
)

# Obtenir les avoirs en bitcoins ou en ethereum des entreprises publiques
companies_arg = parser.add_argument_group("Get public companies data (beta)")
companies_arg.add_argument(
    "-H",
    "--companies",
    choices=["bitcoin", "ethereum"],
    default="bitcoin",
    metavar="bitcoin, ethereum",
    help="""Get public companies bitcoin or ethereum holdings (Ordered by total holdings descending)"""
)

# Affiche la version du programme
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=f"%(prog)s version {PYCOIN_VERSION}"
)

# Groupe pour verbose ou quiet, groupe mutuellement exclusif soit verbose ou quiet, mais pas les deux.
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
    # TODO: Ajouter les fonctionnalités API suivantes: tickers, exchange/tickers.

    try:
        if args.verbose:
            # API: /ping (verbose)
            if args.ping:
                check_api(visibility="verbose")

        else:
            # API: /ping
            if args.ping:
                check_api()

            # API: /coins/list
            elif args.coins_list:
                if args.name is None:
                    coins_list(extension=args.extension)
                else:
                    coins_list(extension=args.extension, name=args.name)

            # API: /coins/markets
            elif args.page and args.currency:
                if args.name is None:
                    generate(extension=args.extension, time_wait=args.time)
                else:
                    generate(extension=args.extension, name=args.name, time_wait=args.time)

            # API: /exchanges
            elif args.exchanges:
                if args.name is None:
                    exchanges(extension=args.extension)
                else:
                    exchanges(extension=args.extension, name=args.name)

            # API: /global
            elif args.global_data:
                if args.name is None:
                    global_data_market(extension=args.extension)
                else:
                    global_data_market(extension=args.extension, name=args.name)

            # API: /global/decentralized_finance_defi
            elif args.global_defi:
                if args.name is None:
                    global_defi_market(extension=args.extension)
                else:
                    global_defi_market(extension=args.extension, name=args.name)

            # API: /search/trending
            elif args.trending:
                if args.name is None:
                    trending_top7(extension=args.extension)
                else:
                    trending_top7(extension=args.extension, name=args.name)

            # API: /companies/public_treasury/{coin_id}
            elif args.companies:
                if args.name is None:
                    companies(extension=args.extension, coin_id=args.companies)
                else:
                    companies(extension=args.extension, name=args.name, coin_id=args.companies)

            # CODE BLOCK - SI UTILISATION D'UN SUBPARSER...
            # elif args.global_cmd == "global":
            #     global_data_market(extension=["csv"], name=args.name, type_data=args.global_data)

            else:
                # Si aucun argument saisi, afficher l'aide par défaut.
                print("No arguments entered, display default help.")
                args = parser.parse_args(["--help"])

    except KeyboardInterrupt as KeyboardError:
        print("Keyboard Interrupt")
