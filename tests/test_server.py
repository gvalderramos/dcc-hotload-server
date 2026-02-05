import socket
import threading
import time

import pytest

from dcc_hotload_server.server import DccServer
from dcc_hotload_server.hooks.base_hook import BaseHookServer, SoftwareHint


def get_free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_get_server_returns_hook_class():
    cls = DccServer._get_server("mayapy")
    assert issubclass(cls, BaseHookServer)


def test_get_server_raises_on_missing():
    with pytest.raises(RuntimeError):
        DccServer._get_server("this_module_does_not_exist")


class MockHook(BaseHookServer):
    def __init__(self, host, port):
        super().__init__("testapp", host, port)
        self.uninitialized = False

    def hints(self, version: str = None) -> SoftwareHint:
        return SoftwareHint()

    def initialize(self) -> None:
        # no-op initialize for test
        pass

    def uninitialize(self) -> None:
        # mark that uninitialize was called
        self.uninitialized = True


def test_shutdown_command_stops_server():
    port = get_free_port()
    hook = MockHook("127.0.0.1", port)

    thread = threading.Thread(target=hook.listen, daemon=True)
    thread.start()

    # give server a moment to bind
    time.sleep(0.1)

    # connect and send shutdown command
    s = socket.create_connection(("127.0.0.1", port))
    s.sendall(b"__SHUTDOWN__")
    s.recv(1024)
    s.close()

    thread.join(timeout=2)

    assert not thread.is_alive()
    assert hook.uninitialized is True
