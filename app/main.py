import socket
import select


def parse_redis_message(data):
    parts = data.split(b"\r\n")
    if not parts[0].startswith(b"*"):
        return None

    # Skip the first line which has the number of arguments
    args = []
    i = 1
    while i < len(parts):
        if parts[i].startswith(b"$"):
            length = int(parts[i][1:])
            arg = parts[i + 1][:length]
            args.append(arg.decode("utf-8"))
            i += 2
        else:
            i += 1
    return args


def handle_conn(data):
    args = parse_redis_message(data)
    if not args:
        return None

    # Check for ECHO command
    if args[0].upper() == "ECHO" and len(args) == 2:
        response = args[1]
        return f"${len(response)}\r\n{response}\r\n".encode()

    elif args[0].upper() == "PING" and len(args) == 1:
        return b"+PONG\r\n"

    return b"-ERR unknown command\r\n"


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    server_socket.setblocking(False)  # Make it non-blocking

    sockets_to_monitor = [server_socket]

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
                        response = handle_conn(data)
                        if response:
                            sock.send(response)
                    else:
                        # Client has disconnected
                        print("Client disconnected")
                        sockets_to_monitor.remove(sock)
                        sock.close()

                except (ConnectionResetError, BrokenPipeError):
                    print("Client disconnected")
                    sockets_to_monitor.remove(sock)
                    sock.close()


if __name__ == "__main__":
    main()
