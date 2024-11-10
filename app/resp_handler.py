import time


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
expiry_store = {}


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

    elif args[0].upper() == "SET" and (len(args) == 3 or len(args) == 5):
        key = args[1]
        value = args[2]
        data_store[key] = value
        if len(args) == 5 and args[3].upper() == "PX":
            expiry_value = args[4]
            expiry_store[key] = time.time() * 1000 + int(expiry_value)
        return b"+OK\r\n"

    elif args[0].upper() == "GET" and len(args) == 2:
        key = args[1]
        response = data_store.get(key)

        if response is None:
            return b"$-1\r\n"

        if key in expiry_store:
            if time.time() * 1000 > expiry_store[key]:
                del data_store[key]
                del expiry_store[key]
                return b"$-1\r\n"

        return f"${len(response)}\r\n{response}\r\n".encode()

    return b"-ERR unknown command\r\n"
