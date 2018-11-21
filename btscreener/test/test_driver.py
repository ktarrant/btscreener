#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Methods for loading, caching, and saving IEX finance data

"""
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

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging
import pytest
import unittest.mock as mock

# Third-party imports -----------------------------------------------
import backtrader as bt

# Our own imports ---------------------------------------------------


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# LOCAL UTILITIES
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------

@pytest.fixture(scope="function")
def strategy_mock(request):
    return mock.MagicMock()

@pytest.fixture(scope="function")
def trend_stop_driver(request, strategy_mock):
    driver = mock.MagicMock()
    driver.strategy = strategy_mock
    strategy_mock.driver = driver
    return driver

# -----------------------------------------------------------------------------
# TESTS
# -----------------------------------------------------------------------------
def test_long_entry(strategy_mock, trend_stop_driver):
    trend_stop_driver.start(price=100.0, breakout=110.0, stop=90.0)
    strategy_mock.buy.assert_called_with(price=110.0)