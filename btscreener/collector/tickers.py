import pandas as pd
from bs4 import BeautifulSoup

dji_components = ["v", "xom", "wmt", "cat", "cvx", "aapl", "gs", "axp",
                  "ibm", "mcd", "mmm", "jpm", "ba", "trv", "msft", "dwdp",
                  "pg", "nke", "ko", "mrk", "dis", "csco", "intc", "jnj",
                  "pfe", "unh", "hd", "wba", "vz", "utx"]
"""list(str): List of Dow Jones Industrial Index component tickers."""

default_faves = [
    # start with a base of liquid, optionable stocks
    "VXX", "GE", "F", "EEM", "USO", "BAC", "XLF", "JNK", "GGB", "FXI",
    "EFA", "SLV", "HYG", "GDX", "XOP", "SPY", "AKS", "TVPT", "QQQ", "T", "CHK",
    "FCX", "SWN", "VALE", "AAPL", "ESV", "IWM", "GLD", "AGI", "CVE", "CPE",
    "BBD", "WFT", "AMD", "WFC", "IBN", "MSFT", "NIO", "SAN", "BB", "NVAX", "JD",
    "SIRI", "INTC", "GSAT", "QEP", "VZ", "CMCSA", "GIS", "JPM", "EWZ", "SNAP",
    "C", "MU", "QCOM", "BCS", "NGD", "XLU", "FB", "RIG", "KNX", "JCP", "RF",
    "NOK", "ENPH", "PACB", "GPRO", "NOG", "PBR", "FITB", "DNR", "AMBC", "APHA",
    "SLB", "PE", "KMI", "UNIT", "FIT", "XLP", "SQQQ", "ZNGA", "PSEC", "PFE",
    "MS", "LEN", "EVRI", "DIS", "UXIN", "ITUB", "SBUX", "PVG", "PLUG", "AUY",
    "GM", "CZR", "KHC", "TWTR", "GFI", "ET", "TEVA", "RAD", "NIHD", "M", "TXT",
    "ZAYO", "UUP", "DB", "KO", "TTOO", "FHN", "EBAY", "FCAU", "KRE", "SID",
    "ACRX", "HAL", "TLT", "WPM", "IQ", "XHB", "ERIC", "IAG", "AAL", "NLSN", "X",
    "HL", "SQ", "NWL", "GLNG", "XME", "AGNC", "DF", "MRK", "CSCO", "OIH", "NEM",
    "CLNE", "MEET", "HPQ", "PCG", "GOLD", "FEZ", "PEGI", "HBAN", "CLF", "BKS",
    "SNH", "EWW", "NEPT", "XLE", "LVS", "XLRE", "BMY", "USB", "SAND", "WMT",
    "MRVL", "VNQ", "BABA", "ADMP", "TRQ", "FSM", "DBD", "SPWR", "GERN", "CRNT",
    "CS", "V", "TGT", "CAG", "RESI", "GNW", "ACB", "ARCC", "XLK", "EQT", "DAL",
    "GORO", "HST", "ORCL", "XBI", "AMRS", "GDXJ", "XLI", "MGM", "GEL", "NVDA",
    "PG", "CY", "JNJ", "GNC", "AMAT", "USAT", "AVEO", "DXC", "XOM", "PDD",
    "MTG", "SMH", "TXMD", "IMMR", "MRO", "IBM", "WATT", "CLDR", "BBBY",
    "NBR", "BRFS", "TROX", "NE", "CNQ", "TSM", "PEG", "BTI", "MET", "EWJ",
    "CYH", "FEYE", "CNX", "KGC", "SFUN", "PSO", "XRT", "AEZS", "IEF", "STM",
    "NUGT", "BP", "VSTM", "CX",
    # throw in some high-average-volume stocks
    "SNAP", "EWZ", "CZR", "CRON", "EA", "ZNGA", "ACB", "MGNX", "NOK",
    # throw in some that I like
    "GOOG", "AMZN", "NFLX", "IRBT", "XLNX", "SPOT", "EB", "UVXY",
    "CAT", "DE", "X", "LUV", "TSLA", "STM", "BA",
    "TLRY", "STZ", "BJ", "MCD", "CPB", "RH",
]
"""list(str): List of liquid, optionable, and well-known tickers according
to the author """


# SYMBOL LOADERS -----------------------------------------
def load_sp500_weights():
    """
    Loads a list of the S&P500 components and their weight in the index.
    :return: table containing information about S&P500 components
    :type: pd.DataFrame
    """
    cache_fn = "sp500_weights.csv"
    try:
        sp500_weights = pd.read_csv(cache_fn)
    except IOError:
        # "spx_page.html" is an html page manually saved from the source of
        # https://www.slickcharts.com/sp500
        with open("spx_page.html") as fobj:
            soup = BeautifulSoup(fobj.read())

        columns = [th.text.strip() for th in soup.thead.find_all('th')]
        rows = [[td.text.strip() for td in tr.find_all("td")]
                for tr in soup.tbody.find_all("tr")]
        df = pd.DataFrame(rows, columns=columns)
        df.Change = df.Change.apply(lambda s: float(s.split("  ")[0]))
        df.Price = df.Price.apply(lambda s: float(s.replace(",", "")))
        df.Weight = df.Weight.apply(float)
        df.to_csv(cache_fn)
        sp500_weights = df

    return sp500_weights

def load_tastyworks_screener(fn):
    """
    loads a tastyworks screener exported as a CSV file, and returns the list
    of symbols in the screener.
    note that the exported files from tastyworks often need some doctoring
    tickers are added that have been long bought out or bankrupt
    and other tickers are for indices, which IEX won't have
    :param fn: CSV file path
    :return: list of str
    """
    screener = pd.read_csv(fn)
    return list(screener.Symbol)