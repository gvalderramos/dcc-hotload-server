import socket

_SCRIPT = b"""
import hou

node = hou.node("/obj").createNode("geo", "my_geo")
print(f'Geometry node created in Houdini via hython client: {node.path()}')

__SHUTDOWN__
"""


def create_hython_client_socket(
    host: str = "localhost", port: int = 5000
) -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket


def close_hython_client_socket(client_socket: socket.socket) -> None:
    client_socket.close()


def main():
    client_socket = create_hython_client_socket()
    print("Connected to hython server.")

    client_socket.sendall(_SCRIPT)
    data = client_socket.recv(1024)
    print(f"Received from server: {data}")

    close_hython_client_socket(client_socket)
    print("Connection closed.")


if __name__ == "__main__":
    main()
