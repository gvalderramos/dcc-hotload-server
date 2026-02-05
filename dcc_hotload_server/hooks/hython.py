from dcc_hotload_server.hooks import base_hook


class HythonServer(base_hook.BaseHookServer):
    """Server hook for Houdini's hython executable."""
    def __init__(self, version, host="127.0.0.1", port=5000):
        """Initializes the Hython server hook.

        Args:
            version (str): Version of Houdini.
            host (str, optional): Host address to bind the server. Defaults to "127.0.0.1".
            port (int, optional): Port number to bind the server. Defaults to 5000.
        """
        super().__init__("hython", host, port)

        self._version = version

    def hints(self, version: str = None) -> base_hook.SoftwareHint:
        """Provides path hints for locating the hython executable.
        Args:
            version (str, optional): Version of Houdini. Defaults to None.
        Returns:
            SoftwareHint: Hints for locating the hython executable.
        """
        version = version if version else self._version
        return base_hook.SoftwareHint(
            windows=[
                f"C:/Program Files/Side Effects Software/Houdini {version}",
            ],
            darwin=[
                f"/Applications/Houdini/Houdini {version}/Frameworks/Houdini.framework/Resources"
            ],
            linux=[
                f"/opt/hfs{version}",
            ],
        )

    def initialize(self):
        """Initializes the Houdini environment."""
        pass

    def uninitialize(self):
        """Uninitializes the Houdini environment."""
        pass
