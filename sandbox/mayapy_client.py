import socket

_SCRIPT = b"""
import maya.cmds as cmds

sphere = cmds.polySphere()
print(f'Sphere created in Maya via mayapy client: {sphere}')

__SHUTDOWN__
"""


def create_mayapy_client_socket(host: str = "localhost", port: int = 5000) -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket


def close_mayapy_client_socket(client_socket: socket.socket) -> None:
    client_socket.close()


def main():
    client_socket = create_mayapy_client_socket()
    print("Connected to mayapy server.")

    client_socket.sendall(_SCRIPT)
    data = client_socket.recv(1024)
    print(f"Received from server: {data}")

    close_mayapy_client_socket(client_socket)
    print("Connection closed.")


if __name__ == "__main__":
    main()
