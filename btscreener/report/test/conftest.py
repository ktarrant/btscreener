import pytest
import os

def pytest_addoption(parser):
    my_dir = os.path.dirname(__file__)
    default_collection = os.path.join(my_dir, "collection.pickle")
    parser.addoption(
        "--collection",
        default=default_collection,
        help="sample collection data to use for test, default: {}".format(
            default_collection)
    )
