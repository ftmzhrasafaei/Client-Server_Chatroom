import socket
import threading
import time
from queue import Queue
import os
import random

IP = socket.gethostbyname(socket.gethostname())
PORT = 1237
SIZE = 1024
HEADERSZIE = 16
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "exit"
LISTEN_MODE = "listen"
CONNECTION = [True]
def Main():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP , PORT))
    print(f"[CONNECTED]: This client at connected to the server at {IP}:{PORT}")
    thread1 = threading.Thread(target = HandleMessage , args = (client,))
    thread2 = threading.Thread(target = Send , args = (client,))
    #thread1.daemon = True
    #thread2.daemon = True
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


def HandleMessage(client):
    while CONNECTION[0]:
        #print(CONNECTION)
        message = Receive(client)
        #if message:
        #    print(f"{message['data']} with length {message['header']}")

def Send(client_socket):
    cond = True
    while True:
        msg = input()
        #filemod = False
        #m1 = msg.split()
        #if len(m1)>=3:
        #    if m1[0]=='send' and m1[1]=='file':
        #        filemod = True
        #        SendFile(m1[4],client_socket,m1[3])
        #if not filemod:
        smsg = f"{len(msg):<{HEADERSZIE}}" + msg
        client_socket.send(smsg.encode(FORMAT))
        if msg == DISCONNECT_MESSAGE:
            CONNECTION[0] = False
                #client_socket.close()
            break




def Receive(client_socket):
    try:
        fullmsg = ''
        newmsg = True
        #filemod = False
        while True:
            #if filemod:
        #        msg = client_socket.recv(SIZE)
        #        name = SetFileName('received_file')

        #    else:
            msg = client_socket.recv(SIZE).decode(FORMAT)
            if newmsg:
                #x = msg[:HEADERSZIE]
                #y = x.split()
                #if len(y)>=3:
                #    if y[0] == 'file':
                #        port = m[2]
                #        filemod = True
                #        f = open(name,'wb')
                #print('message:   ' , msg)
                #print(f"[NEW MESSAGE LENGTH]: {msg[:HEADERSZIE]}")
                msglen = int(msg[:HEADERSZIE].strip())
                #if filemod:
                #    msglen = mlen
                #    msg=''
                #else:
                #    msglen = mlen
                newmsg = False


            #if filemod:
            #    if msg:
            #        f.write(msg)
                #if len(fullmsg) == msglen:
                #    print(f"[RECEIVING FILE FINISHED]")
                #    rmsg = fullmsg
                #    url = os.path.join(os.getcwd(), name)
                #    rmsg = url
                #    rmsg = 'send file to '+port+' '+url
                #    f.close()
                #    newmsg = True
                #    fullmsg = ''
                #    break
            #else:
            fullmsg = fullmsg + msg
            if len(fullmsg) - HEADERSZIE == msglen:
                print(f"[NEW MESSAGE]: {fullmsg[HEADERSZIE:]}")
                rmsg = fullmsg[HEADERSZIE:]
                newmsg = True
                fullmsg = ''
                break

        #x = 'send file to'
        #print(x[0:9])

        return {"header":msglen , "data":rmsg}
    except Exception as e:
        print(f"[ERROR] {e}" )
        return False


def SetFileName(name):
    if os.path.isfile(name):
        ind = 1
        while os.path.isfile(name+str(ind)):
            ind = ind + 1
        return name+str(ind)
        #print ("File exist")
    else:
        return name
        #print ("File not exist")


def SendFile(url , c , port):
    filename = url
    print(filename)
    f = open(filename,'rb')
    lenf = file_size(url)
    f1 = 'send file to'+port
    smsg = f"{lenf:<{HEADERSZIE}}" + f1
    c.send(smsg.encode(FORMAT))

    l = f.read(SIZE)
    while(l):
        c.send(l)
        print('Sent ',repr(l))
        l = f.read(SIZE)
    f.close()
    print('Done sending')

def file_size(fname):
        statinfo = os.stat(fname)
        return statinfo.st_size



if __name__ == "__main__":
    Main()
