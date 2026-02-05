import sys

import pytest

from dcc_hotload_server import main


def test_parser_valid(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--dcc", "mayapy", "--version", "2024"])
    args = main._parser()
    assert args.dcc == "mayapy"
    assert args.version == "2024"


def test_parser_missing_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):
        main._parser()
