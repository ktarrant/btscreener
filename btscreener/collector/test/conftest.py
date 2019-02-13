import pytest
import os

def pytest_addoption(parser):
    parser.addoption(
        "--pickle",
        action="store_true",
        help="save the results of tests as pickles",
    )
