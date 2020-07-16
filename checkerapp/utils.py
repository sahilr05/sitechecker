import socket


def is_open(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except socket.error:
        return False
    finally:
        s.close()


def check_tcp(ip, port):
    if is_open(ip, port):
        return True
    else:
        return False
    return True
