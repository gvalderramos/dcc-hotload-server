import socket
import sys
import contextlib

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3

import logging
from typing import Generator
from dataclasses import dataclass, field, asdict
import platform
from pathlib import Path


@dataclass
class SoftwareHint:
    """Dataclass to hold software path hints for different operating systems."""
    windows: list[str] = field(default_factory=[])
    darwin: list[str] = field(default_factory=[])
    linux: list[str] = field(default_factory=[])

    def get(self) -> list[str]:
        """Returns the hints for the current operating system.
        
        Returns:
            list[str]: List of path hints for the current OS.
        """
        current_os = platform.system().lower()
        return asdict(self).get(current_os, [])


# Helper to capture stdout/stderr to send back to client
@contextlib.contextmanager
def _capture_output() -> Generator[tuple[StringIO, StringIO], None, None]:
    """"Context manager to capture stdout and stderr.

    Yields:
        tuple[StringIO, StringIO]: Captured stdout and stderr streams.
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class BaseHookServer:
    """Base class for DCC hotload server hooks."""
    _SHUTDOWN_COMMAND = "__SHUTDOWN__"

    def __init__(self, app_name: str, host="127.0.0.1", port=5000):
        """Initializes the base hook server.

        Args:
            app_name (str): Name of the DCC application executable.
            host (str, optional): Host address to bind the server. Defaults to "127.0.0.1".
            port (int, optional): Port number to bind the server. Defaults to 5000.
        """
        self._host = host
        self._port = port
        self._app_name = app_name

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def log(self) -> logging.Logger:
        """Returns the logger for the server."""
        return self._logger

    @property
    def app_path(self) -> Path:
        """Finds and returns the path to the DCC application executable.
        
        Returns:
            Path: The path to the DCC application executable.

        Raises:
            RuntimeError: If the application executable cannot be found.
        """
        hints = self.hints().get()
        app_path = None
        app_name = (
            self._app_name
            if platform.system().lower() != "windows"
            else f"{self._app_name}.exe"
        )
        for hint in hints:
            paths = list(Path(hint).rglob(app_name))
            if paths:
                app_path = paths[0]
                break
            else:
                self.log.exception(f"Unable to find the app {self._app_name}")
                raise RuntimeError(f"Unable to find the app {self._app_name}")
        return app_path

    def hints(self, version: str = None) -> SoftwareHint:
        """Provides path hints for locating the DCC application.

        Args:
            version (str, optional): Version of the DCC application. Defaults to None.
        Returns:
            SoftwareHint: Hints for locating the DCC application.
        """
        raise NotImplementedError("This method might be implemented by the subclass.")

    def initialize(self) -> None:
        """Initializes the DCC application environment."""
        raise NotImplementedError("This method might be implemented by the subclass.")

    def uninitialize(self) -> None:
        """Uninitializes the DCC application environment."""
        raise NotImplementedError("This method might be implemented by the subclass.")

    def listen(self) -> None:
        """Starts the server to listen for incoming connections."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.initialize()
        try:
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(5)
            self.log.info(f"Server listening on {self._host}:{self._port}")

            while True:
                conn, add = self._server_socket.accept()
                self.log.info(f"Connection from {add}")

                data = conn.recv(4096).decode("utf-8")

                if not data:
                    break

                # Support a special shutdown command so external controllers
                # can ask this server to stop cleanly.
                should_shutdown = False
                if self._SHUTDOWN_COMMAND in data.strip():
                    self.log.info(
                        "Shutdown command received, it will stop after processing the current request."
                    )
                    should_shutdown = True
                    data = data.replace(self._SHUTDOWN_COMMAND, "").strip()

                response = ""
                try:
                    with _capture_output() as (out, err):
                        exec(data, globals())

                    output = out.getvalue()
                    error_output = err.getvalue()

                    if output:
                        response += f"OUTPUT: \n{output}"
                    if error_output:
                        response += f"ERRORS: \n{error_output}"
                    if not response:
                        response = "Script executed (no output)."
                except Exception as e:
                    response = f"EXECUTION ERROR: {str(e)}"

                self.log.info(f"Sending response to client: {response}")
                conn.sendall(response.encode("utf-8"))
                conn.close()
                if should_shutdown:
                    self.log.info("Shutting down server as requested.")
                    break
        except KeyboardInterrupt:
            self.log.info("Stopping server...")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stops the server and uninitializes the environment."""
        self.log.info("Closing server socket.")
        self._server_socket.close()
        self.uninitialize()
