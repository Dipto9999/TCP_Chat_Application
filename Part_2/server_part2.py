# Group#: G6
# Student Names: Muntakim Rahman, Tomaz Zlindra

#Content of server.py; To complete/implement

from tkinter import *
import socket
import threading

class ChatServer:
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When
    the server receives a message, it displays it in its own GUI and also sents
    the message to the other client.
    It uses the tkinter module to create the GUI for the server client.
    See the project info/video for the specs.
    """
    EXPECTED_CLIENTS = 5
    def __init__(self, window: Tk, host: str = "127.0.0.1", serverPort: int = 3234, buffersize: int = 1024):
        # TCP Server Setup
        self.serverSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
        self.serverSocket.bind((host, serverPort))

        # Tkinter Window Setup
        self.window = window
        self.window.title("Chat Server")

        # Define and Configure Widgets
        self.server_label = Label(self.window, text = "Chat Server", font = ("Helvetica", 12, "normal"))
        self.history_label = Label(self.window, text = "Chat History:", font = ("Helvetica", 12, "normal"))

        self.scrollbar = Scrollbar(window, orient = VERTICAL)
        self.chat_history = Text(self.window, yscrollcommand = self.scrollbar.set, state = DISABLED) # User Has Read-Only Access
        self.scrollbar.config(command = self.chat_history.yview)

        self.server_label.grid(row = 1, column = 1, sticky = W)
        self.history_label.grid(row = 2, column = 1, sticky = W)
        self.chat_history.grid(row = 3, column = 1, columnspan = 3, sticky = NSEW)
        self.scrollbar.grid(row = 3, column = 4, sticky = NS)

        # Configure Rows and Columns for Window Resizing.
        self.window.grid_rowconfigure(1, weight = 0) # Won't Grow
        self.window.grid_rowconfigure(2, weight = 0) # Won't Grow
        self.window.grid_rowconfigure(3, weight = 1) # Will Grow Proportionally

        self.window.grid_columnconfigure(1, weight = 0) # Won't Grow
        self.window.grid_columnconfigure(2, weight = 1) # Will Grow Proportionally
        self.window.grid_columnconfigure(2, weight = 1) # Will Grow Proportionally

        # Establish Client Connection(s)
        self.client_lock = threading.Lock()
        self.clientSockets: list[dict] = []
        self.msg_threads: list[threading.Thread] = []
        self.handshake_thread = threading.Thread(
            target = self.accept_clients,
            args = (buffersize, ),
            daemon = True # Kill Thread When Spawning Thread (i.e. Main Thread) Exits
        )
        self.handshake_thread.start()
        # self.exit()

    #TODO -> Implement Exit
    def exit(self):
        for clientSocket in self.clientSockets:
            try:
                clientSocket["socket"].close()
            except Exception as e:
                print(e)
        self.serverSocket.close()

    def accept_clients(self, buffersize):
        # Enable Server to Accept Connections.
        self.serverSocket.listen(ChatServer.EXPECTED_CLIENTS)
        print("Server Listening for Incoming Connection Request(s) ...")
        while True: # Infinite Loop, Checking for New Clients
            connSocket, addr = self.serverSocket.accept()
            self.client_lock.acquire() # Critical Section (Start)
            self.clientSockets.append({"socket" : connSocket, "addr" : addr})
            self.client_lock.release() # Critical Section (End)

            client_thread = threading.Thread(
                target = self.handle_msgs,
                kwargs = {
                    "max_bytes" : buffersize,
                    "rcvSocket" : connSocket,
                    "rcv_addr" : addr,
                },  name = f"Handle Messages : Client @PORT{addr[1]}",
                daemon = True # Kill Thread When Spawning Thread Exits
            )
            client_thread.start()
            self.msg_threads.append(client_thread)

    def handle_msgs(self, max_bytes: int, rcvSocket: socket.socket, rcv_addr: tuple) -> None:
        while True: # Check if New Data Received.
            try:
                new_msg = rcvSocket.recv(max_bytes).decode()

                self.client_lock.acquire() # Critical Section (Start)
                for clientSocket in self.clientSockets:
                    try:
                        clientSocket["socket"].send(new_msg.encode())
                    except:
                        self.clientSockets.remove(clientSocket) # Remove Client Socket
                self.client_lock.release() # Critical Section (End)

                self.chat_history.config(state = NORMAL)
                self.chat_history.insert(END, f"{new_msg}\n")
                self.chat_history.config(state = DISABLED)
            except:
                return # New Data Cannot Be Received

def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    # window.geometry("400x400")
    server = ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()