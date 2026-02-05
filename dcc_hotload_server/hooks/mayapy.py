from dcc_hotload_server.hooks import base_hook


class MayaPyServer(base_hook.BaseHookServer):
    """Server hook for Maya's mayapy executable."""
    def __init__(self, version, host="127.0.0.1", port=5000):
        """Initializes the MayaPy server hook.

        Args:
            version (str): Version of Maya.
            host (str, optional): Host address to bind the server. Defaults to "127.0.0.1".
            port (int, optional): Port number to bind the server. Defaults to 5000.
        """
        super().__init__("mayapy", host, port)

        self._version = version

    def hints(self, version: str = None) -> base_hook.SoftwareHint:
        """Provides path hints for locating the mayapy executable.
        Args:
            version (str, optional): Version of Maya. Defaults to None.
        Returns:
            SoftwareHint: Hints for locating the mayapy executable.
        """
        version = version if version else self._version
        return base_hook.SoftwareHint(
            windows=[
                f"C:/Program Files/Autodesk/Maya{version}",
            ],
            darwin=[f"/Applications/Autodesk/maya{version}"],
            linux=[
                f"/usr/autodesk/maya{version}",
                f"/opt/autodesk/maya{version}" f"/opt/maya{version}",
            ],
        )

    def initialize(self):
        """Initializes the Maya standalone environment."""
        import maya.standalone

        maya.standalone.initialize(name="python")

    def uninitialize(self):
        """Uninitializes the Maya standalone environment."""
        import maya.standalone

        maya.standalone.uninitialize()
