import logging
import argparse
import pickle
import os
import datetime
from collections import OrderedDict

import pandas as pd

from btscreener.collector.tickers import default_faves, dji_components
from btscreener.collector.collect import run_collection
from btscreener.report.screener import make_screener_table

logger = logging.getLogger(__name__)


def get_collection_dir(args):
    date = datetime.date.today()
    dest = "collections/{date}".format(date=date)
    os.makedirs(dest, exist_ok=True)
    return dest

def get_symbols(group_name):
    if group_name == "faves":
        return default_faves
    elif group_name == "dji":
        return dji_components
    else:
        raise KeyError("No group '{}'".format(group_name))


def yield_collections(collection_dir):
    for root, dirs, files in os.walk(collection_dir):
        for file in files:
            if file.endswith("_collection.pickle"):
                date, group, suffix = file.split("_")
                fn = os.path.join(root, file)
                logger.info("Loading collection: {}".format(fn))
                with open(fn, "rb") as fobj:
                    yield (date, group, pickle.load(fobj))

parser = argparse.ArgumentParser(description="""
Runs a full technical screening process to produce one or more reports and/or
data artifacts.

The process has two stages:

I. Collection
1. Create an output directory to put log files and data artifacts
2. Find a list of tickers, either hardcoded or from an index
3. For each ticker, collect historical price data and other miscellaneous data.
3. a. TODO: Allow user to pickle the price data and misc data as well
4. Run indicators against the price data using backtrader
5. Collect all available data into a big table
6. Pickle the data table into the output directory

II. Reporting
1. Load a collection table from an collection output directory
2. Perform preprocessing and summarization of the data for the visualization
3. Pass the data off to plotly or another service to report the information
""")

parser.add_argument('-v', '--verbose', action='count', default=0,
                    help="Logging verbosity level")
parser.add_argument("--cache",
                    choices=["collection"],
                    action="append")
parser.add_argument("--group",
                    choices=["faves", "dji"],
                    default="faves",
                    help="symbol group to collect")
parser.add_argument("--pool-size",
                    default=4,
                    help="pool size for multiprocessing")
parser.add_argument("--format-file",
                    default="{date}_{group}_collection.{ext}")
parser.add_argument("--csv",
                    action="store_true",
                    help="enable csv output")
parser.add_argument("--report",
                    action="append",
                    choices=["screener"],
                    help="generate a report from the collection")

if __name__ == "__main__":
    import sys

    # Set up the root logger to log everything, we will filter with handlers
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(logging.Formatter())

    args = parser.parse_args()

    v_count = args.verbose if args.verbose < 3 else 3
    # set the error level for the console handler
    # 0 - ERROR, 1 - WARNING, 2 - INFO, 3 - DEBUG
    logLevel = logging.ERROR - (10 * v_count)
    consoleHandler.setLevel(logLevel)
    rootLogger.addHandler(consoleHandler)

    today = datetime.date.today()

    if args.cache:
        collection_dir = get_collection_dir(args)
        logger.debug("Using collection dir: {}".format(collection_dir))

        collection_fn = args.format_file.format(date=today, ext="pickle",
                                                **vars(args))
        collection_path = os.path.join(collection_dir, collection_fn)

    symbols = get_symbols(args.group)

    if args.cache and "collection" in args.cache and (
            os.path.exists(collection_path)):
        # we are using caching and we found a cached collection for today
        with open(collection_path, mode="rb") as fobj:
            collection = pickle.load(fobj)

    else:
        # run_collection downloads symbol data and runs backtests
        collection = run_collection(symbols, pool_size=args.pool_size)

        # if we are using caching, update the cache with the new collection
        if args.cache and "collection" in args.cache:
            with open(collection_path, mode="wb") as fobj:
                logger.debug("Saving pickle: {}".format(collection_path))
                pickle.dump(collection, fobj)

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        logger.info(collection)

    if args.csv:
        csv_fn = args.format_csv.format(date=today, ext="csv", **vars(args))
        csv_path = os.path.join(collection_dir, csv_fn)
        logger.info("Saving csv: {}".format(csv_path))
        collection.to_csv(csv_path)

    if args.report and "screener" in args.report:
        url = make_screener_table(args.group, collection)
