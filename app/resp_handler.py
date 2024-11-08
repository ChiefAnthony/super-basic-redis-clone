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


data_store = {}


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

    elif args[0].upper() == "SET" and len(args) == 3:
        key = args[1]
        value = args[2]
        data_store[key] = value
        return b"+OK\r\n"

    elif args[0].upper() == "GET" and len(args) == 2:
        response = data_store.get(args[1])
        if response is None:
            return "$-1\r\n"
        return f"${len(response)}\r\n{response}\r\n".encode()

    return b"-ERR unknown command\r\n"
