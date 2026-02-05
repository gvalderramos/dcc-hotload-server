import base64
import importlib
import inspect
import os
import pickle
import signal
import subprocess

from dcc_hotload_server.hooks.base_hook import BaseHookServer

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
        module_name = f"dcc_hotload_server.hooks.{name}"
        try:
            module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError) as e:
            raise RuntimeError(f"Unable to import module '{module_name}': {e}") from e

        # Find classes defined in the module that subclass BaseHookServer.
        for _, obj in inspect.getmembers(module, inspect.isclass):
            # skip the base class itself and classes not defined in the module
            if obj is BaseHookServer:
                continue
            if getattr(obj, "__module__", None) != module.__name__:
                continue
            try:
                if issubclass(obj, BaseHookServer):
                    return obj
            except TypeError:
                # obj is not a class that can be checked with issubclass
                continue

        raise NotImplementedError(f"Hook '{name}' not implemented in module '{module_name}'.")

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
