#coding:utf-8
import time
import socket

host = "localhost"
port = 8500
tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcp.bind(("localhost", port))
tcp.listen(1)
while True:
    con, addr = tcp.accept()
    print "client", addr
    while True:
        try:
            con.sendall("1;23,45,67,89;1234567890,11035678\n")
        except socket.error:
            break
        time.sleep(10)
