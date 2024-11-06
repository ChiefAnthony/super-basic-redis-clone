import socket
import select


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    server_socket.setblocking(False)  # Make it non-blocking

    sockets_to_monitor = [server_socket]

    print("Server is ready to accept connections...")

    while True:
        ready_to_read, _, _ = select.select(sockets_to_monitor, [], [])

        for sock in ready_to_read:
            if sock == server_socket:
                client_socket, address = server_socket.accept()
                client_socket.setblocking(False)
                sockets_to_monitor.append(client_socket)
                print(f"New connection from {address}")

            else:
                try:
                    data = sock.recv(1024)
                    if data:
                        sock.send(b"+PONG\r\n")
                    else:
                        raise ConnectionResetError

                except (ConnectionResetError, BrokenPipeError):
                    print("Client disconnected")
                    sockets_to_monitor.remove(sock)
                    sock.close()


if __name__ == "__main__":
    main()
