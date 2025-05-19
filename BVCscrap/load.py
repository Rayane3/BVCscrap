import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import json
import datetime
from .utils import *

def loadata(name, start=None, end=None, decode="utf-8"):
    # 1) load your long-term CSV
    local_df = load_local_history(name)

    # 2) decide the scrape window: last 5 years
    if not (start and end):
        # default: scrape the last 5 years
        today = datetime.date.today()
        five_years_ago = today.replace(year=today.year - 5)
        scrape_start = five_years_ago.isoformat()
        scrape_end   = today.isoformat()
    else:
        scrape_start, scrape_end = start, end

    # 3) run the existing scraper logic, but only for [scrape_start:scrape_end]
    code = get_code(name)
    if not code and name not in ["MASI", "MSI20"]:
        raise ValueError(f"Unknown name or missing ISIN for: {name}")

    if name not in ["MASI", "MSI20"]:
        link = f"https://medias24.com/content/api?method=getPriceHistory&ISIN={code}"
        link += f"&format=json&from={scrape_start}&to={scrape_end}"
    else:
        # index logic unchanged…
        if name == "MASI":
            link = "https://medias24.com/content/api?method=getMasiHistory&periode=5y&format=json"
        else:
            link = "https://medias24.com/content/api?method=getIndexHistory&ISIN=msi20&periode=5y&format=json"

    # cloudscraper call as before…
    scraper = cloudscraper.create_scraper()
    resp    = scraper.get(link)
    if resp.status_code != 200 or not resp.text.strip().startswith('{'):
        raise ValueError(f"Bad API response for {name}: {resp.status_code}")

    web_df = get_data(resp.text, decode)
    web_df.index = pd.to_datetime(web_df.index, errors='coerce')

    # 4) Merge local CSV + scraped
    # 4) Merge CSV + scrape, but drop any overlapping dates from the CSV
    if local_df is not None:
        if not web_df.empty:
            # drop from the CSV any dates we actually scraped
            overlap = local_df.index.intersection(web_df.index)
            if not overlap.empty:
                local_df = local_df.drop(overlap)
        df = pd.concat([local_df, web_df]).sort_index()
    else:
        df = web_df

    # 4.a) Special-case: scrape was empty but we have local CSV → just use CSV
    if web_df.empty and local_df is not None:
        return produce_data(local_df, start, end)

    # 5) Otherwise, apply the usual slice on the combined frame
    if start and end:
        return produce_data(df, start, end)
    return df


def loadata_patch(name, start=None, end=None, decode="utf-8"):
    """
    Patch de bvc.loadata() qui gère le cas MASI/MSI20 avec dates en epoch ms.
    """
    code = get_code(name)
    # 1) Construire l'URL
    if name not in ["MASI", "MSI20"]:
        if not (start and end):
            start = '2011-09-18'
            end   = str(datetime.date.today())
        link = (
            f"https://medias24.com/content/api?"
            f"method=getPriceHistory&ISIN={code}"
            f"&format=json&from={start}&to={end}"
        )
    else:
        if name == "MASI":
            link = (
                "https://medias24.com/content/api?"
                "method=getMasiHistory&periode=10y&format=json"
            )
        else:  # MSI20
            link = (
                "https://medias24.com/content/api?"
                "method=getIndexHistory&ISIN=msi20&periode=10y&format=json"
            )

    # 2) Requête HTTP
    resp = cloudscraper.create_scraper().get(link)
    if resp.status_code != 200 or not resp.text.strip().startswith('{'):
        raise ValueError(f"Bad API response for {name}: {resp.status_code}")

    # 3) Charger le JSON en DataFrame « brut »
    table = json.loads(resp.text.encode().decode(decode))
    df    = pd.DataFrame(table["result"])

    # 4) Renommer selon nombre de colonnes
    if name in ["MASI", "MSI20"] and df.shape[1] == 2:
        df.columns = ["Date", "Value"]
    else:
        df.columns = ["Date", "Value", "Min", "Max", "Variation", "Volume"]

    # 5) Conversion de la colonne Date
    if pd.api.types.is_numeric_dtype(df["Date"]):
        # MASI renvoie un timestamp en ms
        df["Date"] = pd.to_datetime(df["Date"], unit="s", errors="coerce")
    else:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # 6) Indexer et retourner
    return df.set_index("Date")



def getIntraday(name,decode="utf-8"):
    """
    Load intraday data
    Inputs: 
        -Name: stock,index 
        -decode: default value is "utf-8", if it is not working use : "utf-8-sig"
    
    """
    if name != "MASI" and name != "MSI20":
        code=get_code(name)
        link="https://medias24.com/content/api?method=getStockIntraday&ISIN="+code+"&format=json"
    elif name == "MASI":
            link="https://medias24.com/content/api?method=getMarketIntraday&format=json"
    else :
            link="https://medias24.com/content/api?method=getIndexIntraday&ISIN=msi20&format=json"
    request_data = requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(request_data.text,features="lxml")
    data=intradata(soup,decode)
    return data
