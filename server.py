import socket
import threading
import select
import time
import copy


MAX_CONNECTIONS = 5
IP = socket.gethostbyname(socket.gethostname())
PORT = 1237
SIZE = 1024
HEADERSZIE = 16
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "exit"
LISTEN_MODE = "listen"






class ClienT:
    def __init__(self , connection ,port):
        self.connection = connection
        self.port = port

class Group:
    def __init__(self , name ,owner, members=[]):
        self.name = name
        self.owner = owner
        self.members = members
        if len(members)==0:
            self.members.append(owner)
    def AddMember(self,m):
        self.members.append(m)
    def removeMember(self,m):
        self.members.remove(m)
    def GroupName(self):
        return self.name
    def GroupMembers(self):
        return self.members



def SendFile(url , c , port):
    filename = url
    f = open(filename,'rb')
    lenf = file_size(url)
    f1 = 'file from '+str(port)
    smsg = f"{lenf:<{HEADERSZIE}}" + f1
    c.send(smsg.encode(FORMAT))

    l = f.read(SIZE)
    while(l):
        c.send(l.decode())
     #  print('Sent ',repr(l))
        l = f.read(SIZE)
    f.close()
    print('Done sending')

def file_size(fname):
        statinfo = os.stat(fname)
        return statinfo.st_size


def HandleClient(cin, socketList , client, grp):
    conn = cin.connection
    addr = cin.port
    connected  =True
    print(f"[THREAD STARTING]: {addr}")
    while connected:

        message = Receive(conn,addr)
        if message is False:
            print(f"[CLOSED CONNECTION]: from {addr}")
            break

        rmsg = message['data']
        msglen = message['header']

        m = rmsg.split()
        endl= '\n'
        if len(m)==1:

            if m[0] == 'getAllPorts':
                st = 'ports> '
                el = '\n'
                for clin in client:
                    if clin.port != addr:
                        st = st + str(clin.port)+ el
                st = f"{len(st):<{HEADERSZIE}}" + st
                conn.send(st.encode(FORMAT))

            if m[0] == 'exit':
                for g in grp:
                    if cin in g.GroupMembers():
                        g.removeMember(cin)
                    if len(g.GroupMembers()) == 0:
                        grp.remove(g)
                        del g


            if m[0] == 'getAllGroups':
                st = 'groups> '
                el = '\n'
                for gr in grp:
                    st = st + str(gr.GroupName())+el
                st = f"{len(st):<{HEADERSZIE}}" + st
                conn.send(st.encode(FORMAT))


        else:
            if len(m)>=3:
                if m[0]== 'send' and m[1]=='message' and m[2]=='to':
                    if m[3]!= 'group':
                        #send message to $port $message
                        p = int(m[3])
                        mes = m[4:]
                        mts = ' '.join(mes)
                        clint= None
                        for clin in client:
                            if clin.port == p:
                                clint = clin
                                break
                        if clint:
                            #message from $port: $message
                            mts = 'message from '+ str(addr)+': '+mts
                            mts = f"{len(mts):<{HEADERSZIE}}" + mts
                            clint.connection.send(mts.encode(FORMAT))
                        else:
                            msg = 'There is no such client name!'
                            msg = f"{len(msg):<{HEADERSZIE}}" + msg
                            conn.send(msg.encode(FORMAT))
                    else:
                        if m[0]=='send' and m[1]=='file':
                            pass
                            #p = int(m[3])
                            #mfile = m[4]
                            #clint= None
                            #for clin in client:
                            #    if clin.port == p:
                            #        clint = clin
                            #        break
                            #if clint:
                                # file from $port: $message
                            #    SendFile(mfile , clin.connection ,addr)



                        else:
                            #send message to group $groupName $message
                            g = None
                            gn = m[4]
                            for gr in grp:
                                if gr.GroupName() == gn:
                                    g = gr
                                    break

                            if g:
                                if cin in g.GroupMembers():
                                    msg = ' '.join(m[5:])
                                    msg = 'message from '+ str(addr)+' in '+ gn + ' : '+msg
                                    msg = f"{len(msg):<{HEADERSZIE}}" + msg
                                    #message from $port in $groupName: $message
                                    for mem in g.GroupMembers():
                                        mem.connection.send(msg.encode(FORMAT))
                                else:
                                    msg = 'You are not in '+gn
                                    msg = f"{len(msg):<{HEADERSZIE}}" + msg
                                    conn.send(msg.encode(FORMAT))
                            else:
                                msg = 'There is no such group name!'
                                msg = f"{len(msg):<{HEADERSZIE}}" + msg
                                conn.send(msg.encode(FORMAT))

            if m[0] == 'create':
                #create group $groupName
                gn = m[2]
                statment = True
                for g in grp:
                    if g.GroupName() == gn:
                        statment = False
                        break
                if statment:
                    newg = Group(gn , cin , [cin])
                    grp.append(newg)
                else:
                    st = 'This name is already taken!'
                    st = f"{len(st):<{HEADERSZIE}}" + st
                    conn.send(st.encode(FORMAT))

            if m[0] == 'add':
                #add $port to $groupName
                p = int(m[1])
                gn = m[3]
                g = None
                clint = None

                for gr in grp:
                    if gr.GroupName()==gn:
                        g = gr
                        break
                for clin in client:
                    if clin.port == p:
                        clint = clin
                        break

                if clint and g:
                    if clint in g.GroupMembers():
                        msg = str(clint.port) + ' is aleady in '+gn
                        msg = f"{len(msg):<{HEADERSZIE}}" + msg
                        conn.send(msg.encode(FORMAT))
                    else:
                        g.AddMember(clint)
                        msg = str(addr) + ' added you in '+gn
                        msg = f"{len(msg):<{HEADERSZIE}}" + msg
                        clint.connection.send(msg.encode(FORMAT))
                else:
                    if not clint:
                        msg = 'There is no such client name!'
                        msg = f"{len(msg):<{HEADERSZIE}}" + msg
                        conn.send(msg.encode(FORMAT))
                    if not g:
                        msg = 'There is no such group name!'
                        msg = f"{len(msg):<{HEADERSZIE}}" + msg
                        conn.send(msg.encode(FORMAT))


            if m[0] == 'join':
                #join $groupName
                g = None
                gn = m[1]
                for gr in grp:
                    if gr.GroupName()==gn:
                        g = gr
                        break
                if g:
                    if cin in g.GroupMembers():
                        msg = 'You are aleady in '+gn
                        msg = f"{len(msg):<{HEADERSZIE}}" + msg
                        conn.send(msg.encode(FORMAT))
                    else:
                        g.AddMember(cin)
                else:
                    msg = 'There is no such group name!'
                    msg = f"{len(msg):<{HEADERSZIE}}" + msg
                    conn.send(msg.encode(FORMAT))
                #cl.connection.send(bytes('', 'UTF-8'))


            if m[0] == 'leave':
                #leave $groupName
                gn = m[1]
                g = None
                for gr in grp:
                    if gr.GroupName()==gn:
                        g = gr
                        break
                if g:
                    if cin in g.GroupMembers():
                        g.removeMember(cin)
                        if len(g.GroupMembers()) == 0:
                            grp.remove(g)
                            del g
                    else:
                        msg = 'You are not in '+gn
                        msg = f"{len(msg):<{HEADERSZIE}}" + msg
                        conn.send(msg.encode(FORMAT))
                else:
                    msg = 'There is no such group name!'
                    msg = f"{len(msg):<{HEADERSZIE}}" + msg
                    conn.send(msg.encode(FORMAT))
                #cl.connection.send(bytes('', 'UTF-8'))

            if m[0] == 'get':
                #get members $groupName
                gn = m[2]
                g = None
                for gr in grp:
                    if gr.GroupName()==gn:
                        g = gr
                        break
                mem = 'members in '+gn+'> '
                if g:
                    for memb in g.GroupMembers():
                        mem = mem + str(memb.port)+endl
                    mem = f"{len(mem):<{HEADERSZIE}}" + mem
                    conn.send(mem.encode(FORMAT))
                else:
                    msg = 'There is no such group name!'
                    msg = f"{len(msg):<{HEADERSZIE}}" + msg
                    conn.send(msg.encode(FORMAT))

        if rmsg == DISCONNECT_MESSAGE:
            connected = False
            
        print(f"[NEW MESSAGE]: The client at {addr} has sent :  {rmsg} with length {msglen}")
        rmsg = rmsg + f" : [RECEIVED]"
        msg = f"{len(rmsg):<{HEADERSZIE}}" + rmsg
        conn.send(msg.encode(FORMAT))



    socketList.remove(conn)
    client.remove(cin)
    conn.close()
    del cin
    print(f"[DISCONNECTING]: The connection at {addr} has been closed")

def Receive(client_socket,addr):
    try:
        fullmsg = ''
        newmsg = True
    #    filemod = False

        while True:
    #        if filemod:
    #            msg = client_socket.recv(SIZE)


    #        else:
            msg = client_socket.recv(SIZE).decode(FORMAT)
            if newmsg:
                #x = msg[:HEADERSZIE]
                #y = x.split()
                #if len(y)>=3:

                #    if y[0] == 'send' and y[1] == 'file':
                #        port = m[3]
                #        filemod = True
                #        name = SetFileName('server_file')
                #        f = open(name,'wb')
                #print('message:   ' , msg)
                print(f"[NEW MESSAGE LENGTH]: {msg[:HEADERSZIE]} from {addr}")
                msglen = int(msg[:HEADERSZIE].strip())
                #if filemod:
                #    msglen = mlen
                #    msg=''
                #    print('first step')
                #else:
                #    msglen = mlen
                newmsg = False


            #if filemod:
            #    if msg:
            #        print(repr(msg))
            #        f.write(msg)
            #    if len(file_size(f)) == msglen:
            #        print(f"[RECEIVING FILE FINISHED]")
            #        rmsg = fullmsg
            #        url = os.path.join(os.getcwd(), name)
            #        rmsg = url
            #        rmsg = 'send file to '+port+' '+url
            #        f.close
            #        newmsg = True
            #        fullmsg = ''
            #        break
            #else:
            fullmsg = fullmsg + msg
            if len(fullmsg) - HEADERSZIE == msglen:
                print(f"[RECEIVING FINISHED]: {fullmsg[HEADERSZIE:]}")
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

def Time(cin , cl):
    while True:
        if cin in cl:
            t = str(time.time())
            msg = f"{len(t):<{HEADERSZIE}}" + t
            cin.connection.send(msg.encode(FORMAT))
            time.sleep(5)
        else:
            break





def Main():
    print(f"[STARTING]: This server is able to listen on {IP}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP , PORT))
    server.listen(MAX_CONNECTIONS)
    socketList = [server]
    client = []
    groups = []
    print(f"[LISTENING]: Server is listening on {IP}:{PORT}")

    while True:
        try:
            read_sockets, _, exception_sockets = select.select(socketList , [], socketList)
            for notified_socket in read_sockets :
                if notified_socket == server:
                    conn , addr = server.accept()
                    socketList.append(conn)
                    c = ClienT(conn , addr[1])
                    client.append(c)
                    print(f"[CONNECTING]: {addr[1]} connected to the server")
                    thread1 = threading.Thread(target = HandleClient , args = (c , socketList,client, groups))
                    thread1.start()
                    #print(f"[ACTIVE GROUPS]: {len(groups)}")
                    #for g in groups:
                    #    print(g.GroupName())
                    ##thread2 = threading.Thread(target = Time , args = (c,client))
                    #thread2.start()
                    print(f"[ACTIVE CONNECTIONS]: {int(threading.activeCount() - 1)}")

        except KeyboardInterrupt:
            print('[SHUTING DOWN]: Server is turing off.')
            break

if __name__ == "__main__":
    Main()
