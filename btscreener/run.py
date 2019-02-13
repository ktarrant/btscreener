import argparse
import pickle
import os
import datetime
from collections import OrderedDict

from btscreener.collector.tickers import default_faves, dji_components
from btscreener.collector.collect import run_collection

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
    symbols = get_symbols(args.group)
    backtest = run_collection(symbols, pool_size=args.pool_size)
    last_datetime = backtest.datetime.iloc[0]
    fn = args.format_out.format(date=last_datetime, group=args.group)
    path = os.path.join(dest, fn)
    with open(path, mode="wb") as fobj:
        pickle.dump(backtest, fobj)

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

subparsers = parser.add_subparsers()

collect_parser = subparsers.add_parser("collect")
collect_parser.add_argument("--group", choices=["faves", "dji"],
                            default="faves",
                            help="symbol group to collect")
collect_parser.add_argument("--pool-size", default=4,
                            help="pool size for multiprocessing")
collect_parser.add_argument("--format-out",
                            default="{date}_{group}_collection.pickle")
collect_parser.set_defaults(func=do_collection)

args = parser.parse_args()
args.func(args)
