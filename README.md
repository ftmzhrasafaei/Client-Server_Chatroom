# Client-Server_Chatroom
This is a client-server chatroom in Python

##Overview of files
There are two .py files named "server.py" and "client.py".
Run "server.py": Server will listen on port "1237" of the localhost.
The sever use multithreading to handle each client; therefore, there will be #client + 1(for listening) threats
Then run "client.py" as many times you wish to have clients. Each client will bind on the server with a random port.
The client use three threads: 1- the main thread, 2- listening to the server, 3- sending data to the server: using 2rd and 3rd threads, the client can listen and send data simultaneously.

##Overview of functionality
The client can send any message to the server, but there are some special messages that the server handles in a specific way.
1- "getAllPorts": as the result of sending this message to the server, the server sends the ports of all other clients connected to it.
2- "create group $groupName": the client can create a group using this command
3- "add $port to $groupName": the client can add another client to a group using this command
4- "join $groupName": having had the group name, the client can join the group with this command
5- "leave $groupName": same as 4
6- "get members $groupName": the client can get the ports of the other clients in a group
7- "send message to group $groupName $message": this command is for sending messages to a group
8- "send message to $port $message": the client can send a message to a specific client using the destination client's port

The server sends messages to clients using this format: "message from $port: $message"

Each message between the server and the clients contains two parts: header and data (I used this format to handle files as well as text message)
The size of the message is stored in the header
The message itself is stored in the data
