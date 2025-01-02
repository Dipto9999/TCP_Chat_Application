# Group#: G6
# Student Names: Muntakim Rahman, Tomaz Zlindra

#Content of client.py; to complete/implement

from tkinter import *
import socket
import threading
from multiprocessing import current_process #only needed for getting the current process name

class ChatClient:
    """
    This class implements the chat client.
    It uses the socket module to create a TCP socket and to connect to the server.
    It uses the tkinter module to create the GUI for the chat client.
    """
    MIN_WIDTH_TAB = 400 # Min Width of Tkinter Window for Additional Tabs
    MAX_BYTES = 1024 # Max Byte Count Which can be Sent
    def __init__(self, window: Tk, window_width: int = 650, host: str = "127.0.0.1", serverPort: int = 3234):

        # Data Fields for Server-Client Communication Configuration
        self.host, self.serverPort = host, serverPort
        self.process_name: str = current_process().name

        # Tkinter Window Setup
        self.window = window
        self.window.geometry(f"{window_width}x400")

        # Define and Configure Widgets

        # Connect/Reconnect Button
        self.conn_btn = Button(self.window, text = "Server\nConnect", command = self.conn_tcp)

        # Define Label Widgets
        self.msg_label = Label(self.window, text = "Chat Message: ", font = ("Helvetica", 12, "normal"))
        self.history_label = Label(self.window, text = "Chat History:", font = ("Helvetica", 12, "normal"))

        # Define Entry Widget and Bind to "Enter" Key
        self.msg_entry = Entry(self.window)
        self.msg_entry.bind("<Return>", self.send_msg)

        # Define Chat History With Scrollbar
        self.scrollbar = Scrollbar(window, orient = VERTICAL)
        self.chat_history = Text(self.window, yscrollcommand = self.scrollbar.set, state = DISABLED) # User Has Read-Only Access
        self.scrollbar.config(command = self.chat_history.yview)

        # Place Widgets with Grid Manager
        self.conn_btn.grid(row = 1, column = 3, sticky = E, padx = 5, pady = 5)
        self.msg_label.grid(row = 1, column = 1, sticky = W)
        self.msg_entry.grid(row = 1, column = 2, sticky = EW)
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

        self.msg_offset: str = "\t\t" # Default Offset for Messages from This Client
        self.window.update_idletasks() # Update Displays of Windows
        if (self.window.winfo_width() >= ChatClient.MIN_WIDTH_TAB): # Tabs Should be Relative to Initial Window Width
            self.msg_offset = "\t" * (self.window.winfo_width() // ChatClient.MIN_WIDTH_TAB + 2)

        self.conn_tcp() # Establish TCP Server-Client Connection.

        # Intercept the Close Button (Documented at "https://tkdocs.com/tutorial/windows.html")
        self.window.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self) -> None:
        """
        This method is invoked when the close button is clicked.
        """
        self.__send_tcp(f"{self.process_name} Disconnected!")
        self.clientSocket.close() # Close Socket When Tkinter Window Closed.
        self.window.destroy()

    def conn_tcp(self) -> None:
        """
        This method tries to establish TCP connection with Server Port. Display Connection status and server port #.
        """
        try: # Try to Establish TCP Connection with Server Port
            self.clientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
            self.clientSocket.connect((self.host, self.serverPort))
        except OSError: # Notify User When Connection Failed and Enable Ability to Reconnect.
            self.conn_btn.config(state = NORMAL) # Enable Button When Connection has Failed
            self.display_msg("Connection Failed!")
            self.window.title(f"{self.process_name} Disconnected From Server @PORT #{self.serverPort}!") # Display State in Window Title
        else: # Continue With Expected Functionality
            self.conn_btn.config(state = DISABLED) # Disable Button When Connection has Succeeded
            self.display_msg(f"Connection Successful With Server @PORT #{self.serverPort}!")
            self.window.title(f"{self.process_name} @PORT #{self.clientSocket.getsockname()[1]}") # Display Process Name in Window Title

            # Create New Thread to Receive Messages from Server.
            self.receive_msgs_thread = threading.Thread(
                target = self.receive_msgs,
                name = f"Receive Messages",
                daemon = True # Kill Thread When Spawning Thread (i.e. Main Thread) Exits
            )
            self.receive_msgs_thread.start()

    def send_msg(self, event) -> None:
        """
        This callback function sends the self.msg_entry widget message to the server.
        """
        new_msg: str = f"{self.process_name}: {self.msg_entry.get()}"
        self.msg_entry.delete(0, END) # Flush Text from Entry Widget
        self.__send_tcp(new_msg)

    def display_msg(self, msg: str, sentByMe: bool = False) -> None:
        """
        This displays the msg in the self.chat_history widget. If it was sent from this client, there
        is a predetermined offset used to highlight this.
        """
        self.chat_history.config(state = NORMAL) # Enable Widget to Insert Message
        if sentByMe:
            self.chat_history.insert(END, f"{self.msg_offset}{msg}\n")
        else:
            self.chat_history.insert(END, f"{msg}\n")
        self.chat_history.config(state = DISABLED) # Disable Widget (i.e. User Has Read-Only State)

    def receive_msgs(self) -> None:
        """
        Receives message stream from the server of specified size. Decodes byte stream into string
        and displays in application.
        """
        while True: # Check if New Data Received.
            try:
                recv_stream: bytes = self.clientSocket.recv(ChatClient.MAX_BYTES) # Receive New Message Stream
            except OSError:
                self.conn_btn.config(state = NORMAL)
                break # New Data Cannot Be Received
            else:
                if recv_stream:
                    new_msg: str = recv_stream.decode() # Decode to String
                    self.display_msg(msg = new_msg, sentByMe = self.process_name in new_msg)
        # self.display_msg(msg = f"Recv Failed from Server @PORT #{self.serverPort}!", sentByMe = False)
        self.window.title(f"{self.process_name} Disconnected") # Display State in Window Title
        return

    def __send_tcp(self, msg: str) -> None:
        """
        Default send method via TCP.
        """
        try:
            self.clientSocket.send(msg.encode()) # Send New Message Stream
        except OSError:
            self.conn_btn.config(state = NORMAL) # Enable Button When Connection has Failed
            self.display_msg(msg = f"Lost Connection with Server @PORT #{self.serverPort}!", sentByMe = False)

def main(): #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()