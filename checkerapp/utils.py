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


# def socket_to_me():
#     try:
#         s = socket.socket()
#         s.settimeout(2)
#         s.connect(("192.168.95.148",21))
#         ans = s.recv(1024)
#         print(ans)
#         s.shutdown(1) # By convention, but not actually necessary
#         s.close()     # Remember to close sockets after use!
#     except socket.error as socketerror:
#         print("Error: ", socketerror)


# if checkHost(ip, port):
#         print(ip + " is UP")
