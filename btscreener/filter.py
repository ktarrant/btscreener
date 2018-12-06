#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018, Kevin Tarrant (@ktarrant)
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#
# REFERENCES:
# http://ipython.org/ipython-doc/rel-0.13.2/development/coding_guide.html
# https://www.python.org/dev/peps/pep-0008/
# -----------------------------------------------------------------------------
""" Filters a collected data set for key events or conditions to help highlight
potential opportunities or insights.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging

# Third-party imports -----------------------------------------------
import pandas as pd

# Our own imports ---------------------------------------------------


# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# LOCAL UTILITIES
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# EXCEPTIONS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

# BREAKOUT ALERTS -----------------------------------------
def check_ad_breakout(superad_row):
    """
    Checks a row of a Super AD scan to see if it has a breakout condition and
    returns the condition if it does, or None if no condition is present.

    Args:
        superad_row: DataFrame row object

    Returns:
        Alert string, or None
    """
    was_below_resistance = superad_row.prev_close < superad_row.resistance
    was_above_support = superad_row.prev_close > superad_row.support
    is_above_resistance = superad_row.close > superad_row.resistance
    is_below_support = superad_row.close < superad_row.support
    was_in_zone = was_below_resistance and was_above_support
    is_long = is_above_resistance and was_in_zone
    is_short = is_below_support and was_in_zone
    return "long" if is_long else ("short" if is_short else None)

def add_ad_breakout(superad_scan):
    """
    Uses the results of a Super AD scan to create AD breakout alerts. A copy
    of the provided results will be returned with the new 'breakout' column.

    Args:
        superad_scan (pd.DataFrame): The Super AD scan results

    Returns:
        pd.DataFrame: A copy of the provided DataFrame with a 'breakout'
            column added with alert information
    """
    rv = superad_scan.copy()
    rv["breakout"] = superad_scan.apply(check_ad_breakout, axis=1)
    return rv[~pd.isnull(rv["breakout"])]

# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import os
    import argparse
    import datetime
    from collections import OrderedDict

    from collector import DEFAULT_FILE_FORMAT as COLLECTOR_FILE_FORMAT

    DEFAULT_INPUT_FILE = COLLECTOR_FILE_FORMAT.format(
        date=datetime.date.today())
    DEFAULT_FILE_FORMAT = "{date}_filtered_{mode}.csv"

    modes = OrderedDict([
        ("breakout", add_ad_breakout),
    ])

    parser = argparse.ArgumentParser(description="""
    Filters a collected data set for key events or conditions to help highlight
    potential opportunities or insights.
    """)
    parser.add_argument("-i", "--infile", default=DEFAULT_INPUT_FILE,
                        type=os.path.abspath,
                        help="Path to scan results. default: {}".format(
                            DEFAULT_INPUT_FILE))
    parser.add_argument("-m", "--mode", action="append",
                        default=["breakout"], choices=list(modes.keys()))
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")
    parser.add_argument("-o", "--outfile", default=DEFAULT_FILE_FORMAT,
                        type=os.path.abspath,
                        help="output file format. default: {}".format(
                            DEFAULT_FILE_FORMAT))

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # load the scan and perform any filtering requested in the modes
    scan = pd.read_csv(args.infile)
    # TODO: Add more modes and "or" the results together
    for mode in modes:
        if mode in args.mode:
            scan = add_ad_breakout(scan)

    # Save to file
    modeStr = ",".join(args.mode)
    fn = args.outfile.format(date=datetime.date.today(), mode=modeStr)
    print("Saving to: {}".format(fn))
    scan.to_csv(fn)