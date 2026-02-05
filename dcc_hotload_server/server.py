import base64
import os
import pickle
import signal
import subprocess

from dcc_hotload_server.hooks.base_hook import BaseHookServer
from dcc_hotload_server.hooks.hython import HythonServer
from dcc_hotload_server.hooks.mayapy import MayaPyServer

_DCC_SERVER = {
    "mayapy": MayaPyServer,
    "hython": HythonServer,
}

_SERVER_SCRIPT = """
import pickle
import sys
import base64
try:
    pickled_instance = base64.b64decode(sys.argv[1].encode('utf-8'))
    server=pickle.loads(pickled_instance)
    server.listen()
except KeyboardInterrupt:
    print("Stopping server...")
    server.stop()
except Exception as e:
    print("Failed to start server: " + str(e))
"""


class DccServer:
    """DCC Hotload Server to run a DCC in batch mode."""

    def __init__(self, dcc_name, version):
        """Initializes the DCC Hotload Server.

        Args:
            dcc_name (str): Name of the DCC application (e.g., "mayapy", "hython").
            version (str): Version of the DCC application.
        """
        _hook_cls = self._get_server(name=dcc_name)
        self._hook = _hook_cls(version)

    @staticmethod
    def _get_server(name) -> BaseHookServer:
        """Dynamically loads and returns the server hook class for the specified DCC.
        Args:
            name (str): Name of the DCC application.
        Returns:
            BaseHookServer: The server hook class for the specified DCC.
        Raises:
            RuntimeError: If the module cannot be loaded.
        """
        module = _DCC_SERVER.get(name)
        if module:
            return module
        raise NotImplementedError(f"Hook '{name}' not implemented.")

    def start(self) -> None:
        """Starts the DCC Hotload Server."""
        app_path = self._hook.app_path
        encoded_data = base64.b64encode(pickle.dumps(self._hook)).decode("utf-8")
        args = [
            str(app_path),
            "-c",
            _SERVER_SCRIPT,
            encoded_data,
        ]

        popen_kwargs = {}
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        proc = subprocess.Popen(args, **popen_kwargs)
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("Stopping server...")
            try:
                if os.name == "nt":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    proc.send_signal(signal.SIGINT)
            except Exception:
                proc.terminate()
            proc.wait()
