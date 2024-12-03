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
    EXPECTED_CLIENTS = 5 # Number of Connection Requests Which Can Be in Backlog
    def __init__(self, window: Tk, host: str = "127.0.0.1", serverPort: int = 3234, buffersize: int = 1024):
        # Data Fields for Server-Client Communication Configuration
        self.host, self.serverPort = host, serverPort

        # TCP Server Setup
        self.serverSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
        self.serverSocket.bind((host, serverPort))

        # Tkinter Window Setup
        self.window = window
        self.window.geometry("400x400")
        self.window.title(f"Chat Server @PORT #{self.serverPort}") # Identify Server in Window Title

        # Define Label Widgets
        self.server_label = Label(self.window, text = "Chat Server", font = ("Helvetica", 12, "normal"))
        self.history_label = Label(self.window, text = "Chat History:", font = ("Helvetica", 12, "normal"))

        # Define Chat History With Scrollbar
        self.scrollbar = Scrollbar(window, orient = VERTICAL)
        self.chat_history = Text(self.window, yscrollcommand = self.scrollbar.set, state = DISABLED) # User Has Read-Only Access
        self.scrollbar.config(command = self.chat_history.yview)

        # Place Widgets with Grid Manager
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
        self.window.grid_columnconfigure(3, weight = 1) # Will Grow Proportionally
        self.window.grid_columnconfigure(4, weight = 0) # Won't Grow

        # Establish Client Connection(s) in New Thread.
        self.lock = threading.Lock()
        self.socketInfo: list[dict] = []
        self.msg_threads: list[threading.Thread] = []
        self.handshake_thread = threading.Thread(
            target = self.accept_clients,
            args = (buffersize, ),
            daemon = True # Kill Thread When Spawning Thread (i.e. Main Thread) Exits
        )
        self.handshake_thread.start()

        # Intercept the Close Button (Documented at "https://tkdocs.com/tutorial/windows.html")
        self.window.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self) -> None:
        """
        This method is invoked when the close button is clicked.
        """

        self.lock.acquire() # Critical Section (Start)
        readInfo: list[dict] = self.socketInfo.copy() # Copy List of Sockets for Sending
        self.lock.release() # Critical Section (End)

        staleInfo: list[dict] = []
        for info in readInfo:
            try:
                info["socket"].send(f"Server @PORT #{self.serverPort} Offline...".encode())
                info["socket"].close() # Close Sockets When Tkinter Window Closed.
            except socket.error:
                staleInfo.append(info) # Remove Info
            finally:
                self.display_msg(f"""Client @PORT{info["addr"][1]} Closed""")

        for info in staleInfo:
            self.lock.acquire() # Critical Section (Start)
            if info in self.socketInfo:
                self.socketInfo.remove(info) # Remove Stale Socket Info
            self.lock.release() # Critical Section (End)

        #TODO -> Determine if Need to Close Client and Server Sockets.
        self.window.destroy()
        self.serverSocket.close() # Close Socket When Tkinter Window Closed.

    def accept_clients(self, buffersize) -> None:
        """
        Accepts new client sockets which wish to connect to the server port.
        Spawns a thread for receiving messages if connection successfully established, otherwise exits.
        """

        # Enable Server to Accept Connection Requests.
        self.serverSocket.listen(ChatServer.EXPECTED_CLIENTS)
        # print("Server Listening for Incoming Connection Request(s) ...")

        while True: # Infinite Loop Until Server Cannot Accept New Clients
            clientSocket: dict = {}
            try:
                clientSocket["socket"], clientSocket["addr"] = self.serverSocket.accept()
            except socket.error:
                self.display_msg(msg = f"""Could Not Establish Client Connection!""")
                break
            else:
                self.display_msg(msg = f"""Client @PORT #{clientSocket["addr"][1]} Has Connected!""")

                self.lock.acquire() # Critical Section (Start)
                self.socketInfo.append(clientSocket) # Append to List of Open Sockets
                self.lock.release() # Critical Section (End)

                client_thread = threading.Thread(
                    target = self.handle_msgs,
                    kwargs = {
                        "recvInfo" : clientSocket,
                        "max_bytes" : buffersize,
                    },  name = f"""Handle Messages : Client @PORT #{clientSocket["addr"][1]}""",
                    daemon = True # Kill Thread When Spawning Thread Exits
                )
                client_thread.start()
                self.msg_threads.append(client_thread) # For Expansions : If Threads Need to be Accounted for.
        return

    def display_msg(self, msg: str) -> None:
        """
        This displays the msg in the self.chat_history widget.
        """
        self.chat_history.config(state = NORMAL) # Enable Widget to Insert Message
        self.chat_history.insert(END, f"{msg}\n")
        self.chat_history.config(state = DISABLED) # Disable Widget (i.e. User Has Read-Only State)

    def handle_msgs(self, recvInfo: dict, max_bytes: int) -> None:
        """
        This receives messages from the specified client socket. The number of bytes to be received is indicated.
        """
        while True: # Check if New Data Received.
            try:
                recv_stream: bytes = recvInfo["socket"].recv(max_bytes) # Receive Byte Stream
            except socket.error:
                self.display_msg(msg = f"""Could Not Receive from Client @PORT #{recvInfo["addr"][1]}...""")
                break
            else:
                if recv_stream:
                    new_msg: str = recv_stream.decode() # Decode to String
                    self.__send_tcp(new_msg)
        return

    def __send_tcp(self, msg: str) -> None:
        """
        Default send function via TCP.
        """

        #TODO -> Ask Professor about Writer/Reader Implementation
        self.lock.acquire() # Critical Section (Start)
        readInfo: list[dict] = self.socketInfo.copy() # Copy List of Sockets for Sending
        self.lock.release() # Critical Section (End)

        staleInfo: list[dict] = []
        for info in readInfo:
            try:
                info["socket"].send(msg.encode()) # Send Encoded Byte Stream
            except socket.error:
                staleInfo.append(info) # Remove Info
        self.display_msg(msg)

        for info in staleInfo:
            self.lock.acquire() # Critical Section (Start)
            if info in self.socketInfo:
                self.socketInfo.remove(info) # Remove Stale Socket Info
            self.lock.release() # Critical Section (End)
def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()