
def pytest_addoption(parser):
    parser.addoption(
        "--plot",
        action="store_true",
        help="plot the results of backtests",
    )
