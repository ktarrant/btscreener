# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # -----------------------------------------------------------------------------
# # Copyright (c) 2018, Kevin Tarrant (@ktarrant)
# #
# # Distributed under the terms of the MIT License.
# #
# # The full license is in the file LICENSE.txt, distributed with this software.
# #
# # REFERENCES:
# # http://ipython.org/ipython-doc/rel-0.13.2/development/coding_guide.html
# # https://www.python.org/dev/peps/pep-0008/
# # -----------------------------------------------------------------------------
# """
# Runs backtrader on many symbols and collects the relevant outputs from each
# run into a combined data table keyed on symbol.
# """
#
# # -----------------------------------------------------------------------------
# # Imports
# # -----------------------------------------------------------------------------
#
# # stdlib imports -------------------------------------------------------
# import logging
# from multiprocessing import Pool
#
# # Third-party imports -----------------------------------------------
# import pandas as pd
# from bs4 import BeautifulSoup
#
# # Our own imports ---------------------------------------------------
# from btscreener.chart import run_backtest, SCAN_RANGE
# from btscreener.iex import load_calendar, load_historical
#

#
# # -----------------------------------------------------------------------------
# # LOCAL UTILITIES
# # -----------------------------------------------------------------------------
# logger = logging.getLogger(__name__)
#
# # -----------------------------------------------------------------------------
# # EXCEPTIONS
# # -----------------------------------------------------------------------------
#
# # -----------------------------------------------------------------------------
# # CLASSES
# # -----------------------------------------------------------------------------
#
# # -----------------------------------------------------------------------------
# # FUNCTIONS
# # -----------------------------------------------------------------------------
#
#
# # COLLECTION GENERATOR -----------------------------------------

#
# # ARGPARSE CONFIGURATION  -----------------------------------------
# def load_symbol_list(groups=["faves"], symbols=[]):
#     if "faves" in groups:
#         symbols += load_faves()
#     elif "dji" in groups:
#         symbols += dji_components
#     elif "sp" in groups:
#         weights = load_sp500_weights()
#         symbols += list(weights.Symbol)
#     if len(symbols) == 0:
#         raise ValueError("No symbols or groups provided")
#     # make sure it's unique
#     return list(set(symbols))
#
# def add_subparser_collect(subparsers):
#     """
#     Loads historical data from IEX Finance
#
#     Args:
#         subparsers: subparsers to add to
#
#     Returns:
#         Created subparser object
#     """
#     def cmd_collect(args):
#         groups = args.group if args.group else []
#         groups += ["{}s".format(len(args.symbol))] if args.symbol else []
#         args.group_label = "-".join(groups)
#         symbols = load_symbol_list(groups=args.group if args.group else [],
#                                    symbols=args.symbol if args.symbol else [])
#         return run_collection(symbols, pool_size=args.poolsize)
#
#     parser = subparsers.add_parser("collect", description="""
#     collects summary technical and event data for a group of stock tickers
#     """)
#     parser.add_argument("-s", "--symbol", action="append")
#     parser.add_argument("-g", "--group", action="append",
#                         choices=["faves", "dji", "sp"])
#     parser.add_argument("-p", "--poolsize", type=int, default=0,
#                         help="Pool size. If 0, multithreading is not used.")
#
#     parser.set_defaults(func=cmd_collect,
#                         output="{today}_[{group_label}].csv")
#     return parser
#
# # -----------------------------------------------------------------------------
# # RUNTIME PROCEDURE
# # -----------------------------------------------------------------------------
# if __name__ == '__main__':
#     import argparse
#     import datetime
#
#     parser = argparse.ArgumentParser(description="""
#     Complete description of the runtime of the script, what it does and how it
#     should be used
#     """)
#
#     parser.add_argument("-v", "--verbose", action="store_true",
#                         help="use verbose logging")
#
#     subparsers = parser.add_subparsers()
#     scan_parser = add_subparser_collect(subparsers)
#
#     args = parser.parse_args()
#     args.today = datetime.date.today()
#
#     # configure logging
#     logLevel = logging.DEBUG if args.verbose else logging.INFO
#     logging.basicConfig(level=logLevel)
#
#     # execute the function
#     table = args.func(args)
#
#     # print and save the result for the user
#     print(table)
#     table.to_csv(args.output.format(**vars(args)))
