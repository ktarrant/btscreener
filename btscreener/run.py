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
    if group_name is "faves":
        return default_faves
    elif group_name is "dji":
        return dji_components
    else:
        raise KeyError("No group '{}'".format(group_name))

def do_collection(args):
    dest = get_collection_dir(args)
    logger.debug("Using collection dir: {}".format(dest))
    symbols = get_symbols(args.group)
    backtest = run_collection(symbols, pool_size=args.pool_size)
    # print and save the result for the user
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        logger.info(backtest)
    last_datetime = backtest.datetime.iloc[-1]
    last_date = last_datetime.date()
    fn = args.format_file.format(date=last_date, ext="pickle", **vars(args))
    path = os.path.join(dest, fn)
    with open(path, mode="wb") as fobj:
        logger.debug("Saving pickle: {}".format(path))
        pickle.dump(backtest, fobj)

    if args.csv:
        fn = args.format_csv.format(date=last_date, ext="csv", **vars(args))
        path = os.path.join(dest, fn)
        logger.info("Saving csv: {}".format(path))
        backtest.to_csv(path)

def yield_collections(collection_dir):
    for root, dirs, files in os.walk(collection_dir):
        for file in files:
            if file.endswith("_collection.pickle"):
                date, group, suffix = file.split("_")
                fn = os.path.join(root, file)
                logger.info("Loading collection: {}".format(fn))
                with open(fn, "rb") as fobj:
                    yield (date, group, pickle.load(fobj))

def do_report(args):
    dest = get_collection_dir(args)
    logger.debug("Using collection dir: {}".format(dest))
    # TODO: allow the user to specify which collection and pass that to y_c
    for date, group, collection in yield_collections(collection_dir=dest):
        # TODO: Support processing more than one collection (?)
        return make_screener_table(group, collection)

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

parser.add_argument('-v', '--verbose', action='count', default=0)

subparsers = parser.add_subparsers()

collect_parser = subparsers.add_parser("collect")
collect_parser.set_defaults(func=do_collection)
collect_parser.add_argument("--group",
                            choices=["faves", "dji"],
                            default="faves",
                            help="symbol group to collect")
collect_parser.add_argument("--pool-size",
                            default=4,
                            help="pool size for multiprocessing")
collect_parser.add_argument("--format-file",
                            default="{date}_{group}_collection.{ext}")
collect_parser.add_argument("--csv",
                            action="store_true",
                            help="enable csv output")

report_parser = subparsers.add_parser("report")
report_parser.set_defaults(func=do_report)

if __name__ == "__main__":
    import sys

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(logging.Formatter())

    args = parser.parse_args()

    v_count = args.verbose if args.verbose < 3 else 3
    # 0 - ERROR, 1 - WARNING, 2 - INFO, 3 - DEBUG
    logLevel = logging.ERROR - (10 * v_count)
    consoleHandler.setLevel(logLevel)
    rootLogger.addHandler(consoleHandler)

    args.func(args)


