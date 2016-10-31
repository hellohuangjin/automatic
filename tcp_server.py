#coding:utf-8
import time
import socket

host = "localhost"
port = 9990
tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcp.bind(("localhost", port))
tcp.listen(1)
while True:
    con, addr = tcp.accept()
    print "client", addr
    while True:
        try:
            con.sendall("from socket")
        except socket.error:
            break
        time.sleep(10)
