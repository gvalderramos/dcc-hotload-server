import argparse

from dcc_hotload_server.server import DccServer


def _parser():
    """Creates the argument parser for the DCC Hotload Server.
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser("DCC Hotload Server", description="TCP Server to run a DCC in batch mode.")

    parser.add_argument(
        "--dcc",
        choices=["mayapy", "hython"],
        required=True,
        help="The dcc name to choose for",
    )

    parser.add_argument(
        "--version",
        "-v",
        required=True,
        help="The DCC version string. E.g. for Maya2024 -> 2024",
    )
    parser.add_argument("--custom-path", "-cp", help="DCC custom root path.")
    return parser.parse_args()


def main():
    """Main entry point for the DCC Hotload Server."""
    parser = _parser()
    server = DccServer(dcc_name=parser.dcc, version=parser.version)

    server.start()


if __name__ == "__main__":
    main()
