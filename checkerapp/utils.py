import socket
import time

timeout = 2
delay = 2


def is_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    finally:
        s.close()


def check_tcp(ip, port):
    if is_open(ip, port):
        return True
    else:
        time.sleep(delay)
    return True


# if checkHost(ip, port):
#         print(ip + " is UP")
