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
    MIN_WIDTH_TAB = 400
    MAX_BYTES = 1024
    def __init__(self, window: Tk, window_width: int = 650, host: str = "127.0.0.1", serverPort: int = 3234):
        self.host, self.serverPort = host, serverPort
        self.process_name: str = current_process().name

        # Tkinter Window Setup
        self.window = window
        self.window.geometry(f"{window_width}x400")

        # Define and Configure Widgets
        self.conn_btn = Button(self.window, text = "Server\nConnect", command = self.conn_tcp)

        self.msg_label = Label(self.window, text = "Chat Message: ", font = ("Helvetica", 12, "normal"))
        self.history_label = Label(self.window, text = "Chat History:", font = ("Helvetica", 12, "normal"))

        self.msg_entry = Entry(self.window)
        self.msg_entry.bind("<Return>", self.send_msg)

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

        self.window.grid_columnconfigure(1, weight = 0) # Will Grow Proportionally
        self.window.grid_columnconfigure(2, weight = 1) # Won't Grow
        self.window.grid_columnconfigure(3, weight = 1) # Will Grow Proportionally
        self.window.grid_columnconfigure(4, weight = 0) # Won't Grow

        self.window.update_idletasks() # Update Displays of Windows

        # Indicate Messages From Client
        self.msg_offset: str = "\t\t"
        if (self.window.winfo_width() >= ChatClient.MIN_WIDTH_TAB): # Tabs Should be Relative to Initial Window Width
            self.msg_offset = "\t" * (self.window.winfo_width() // ChatClient.MIN_WIDTH_TAB + 2)

        self.conn_tcp() # Establish TCP Server-Client Connection.

        #TODO -> Document Exit Conditions
        self.window.protocol("WM_DELETE_WINDOW", self.exit) # Close Socket After Tkinter Window Closed.

    def exit(self) -> None:
        self.__send_tcp(f"{self.process_name} Disconnected!")
        self.clientSocket.close()
        self.window.destroy()

    def conn_tcp(self) -> None:
        try:
            self.clientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
            self.clientSocket.connect((self.host, self.serverPort))
        except socket.error:
            self.conn_btn.config(state = NORMAL)
            self.display_msg("Connection Failed!")
            self.window.title(f"{self.process_name} Disconnected")
        else:
            self.conn_btn.config(state = DISABLED)
            self.display_msg("Connection Successful!")
            self.window.title(f"{self.process_name} @PORT #{self.clientSocket.getsockname()[1]}")

            self.receive_msgs_thread = threading.Thread(
                target = self.receive_msgs,
                name = f"Receive Messages",
                daemon = True # Kill Thread When Spawning Thread (i.e. Main Thread) Exits
            )
            self.receive_msgs_thread.start()

    def send_msg(self, event) -> None:
        new_msg: str = f"{self.process_name}: {self.msg_entry.get()}"
        self.msg_entry.delete(0, END) # Flush Text from Entry Widget
        self.__send_tcp(new_msg)

    def display_msg(self, msg: str, sentByMe: bool = False) -> None:
        self.chat_history.config(state = NORMAL)
        if sentByMe:
            self.chat_history.insert(END, f"{self.msg_offset}{msg}\n")
        else:
            self.chat_history.insert(END, f"{msg}\n")
        self.chat_history.config(state = DISABLED)

    def receive_msgs(self) -> None:
        while True: # Check if New Data Received.
            try:
                recv_stream: bytes = self.clientSocket.recv(ChatClient.MAX_BYTES) # Receive New Message
            except socket.error:
                self.conn_btn.config(state = NORMAL)
                break # New Data Cannot Be Received
            else:
                if recv_stream:
                    new_msg: str = recv_stream.decode() # Decode to String
                    self.display_msg(msg = new_msg, sentByMe = self.process_name in new_msg)
        self.display_msg(msg = "Could Not Receive from Server...", sentByMe = False)
        self.window.title(f"{self.process_name} Disconnected")
        return

    def __send_tcp(self, msg: str) -> None:
        try:
            self.clientSocket.send(msg.encode()) # Send New Message
        except socket.error:
            self.conn_btn.config(state = NORMAL)
            self.display_msg(msg = "Lost Connection to Server!", sentByMe = False)

def main(): #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()