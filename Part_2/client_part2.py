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
    def __init__(self, window: Tk, window_width: int = 650, host: str = "127.0.0.1", serverPort: int = 3234, buffersize: int = 1024):
        # Establish TCP Server-Client Connection.
        self.clientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
        self.clientSocket.connect((host, serverPort))

        self.process_name: str = current_process().name

        # Tkinter Window Setup
        self.window = window
        self.window.geometry(f"{window_width}x400")
        self.window.title(f"{self.process_name} @PORT #{self.clientSocket.getsockname()[1]}")

        # Define and Configure Widgets
        self.message_label = Label(self.window, text = "Chat Message: ", font = ("Helvetica", 12, "normal"))
        self.history_label = Label(self.window, text = "Chat History:", font = ("Helvetica", 12, "normal"))

        self.new_msg = Entry(self.window)
        self.new_msg.bind("<Return>", self.send_msg)

        self.scrollbar = Scrollbar(window, orient = VERTICAL)
        self.chat_history = Text(self.window, yscrollcommand = self.scrollbar.set, state = DISABLED) # User Has Read-Only Access
        self.scrollbar.config(command = self.chat_history.yview)

        # Indicate Messages From This Client
        self.msg_offset: str = "\t"
        if (window_width >= ChatClient.MIN_WIDTH_TAB): # Tabs Should be Relative to Window Width
            self.msg_offset *= (window_width // ChatClient.MIN_WIDTH_TAB + 2)

        # Place Widgets with Grid Manager
        self.message_label.grid(row = 1, column = 1, sticky = W)
        self.history_label.grid(row = 2, column = 1, sticky = W)
        self.new_msg.grid(row = 1, column = 2, sticky = "w", padx = 5, pady = 5)
        self.chat_history.grid(row = 3, column = 1, columnspan = 2, sticky = NSEW)
        self.scrollbar.grid(row = 3, column = 4, sticky = NS)

        # Configure Rows and Columns for Window Resizing.
        self.window.grid_rowconfigure(1, weight = 0) # Won't Grow
        self.window.grid_rowconfigure(2, weight = 0) # Won't Grow
        self.window.grid_rowconfigure(3, weight = 1) # Will Grow Proportionally

        self.window.grid_columnconfigure(1, weight = 0) # Won't Grow
        self.window.grid_columnconfigure(2, weight = 1) # Will Grow Proportionally
        self.window.grid_columnconfigure(2, weight = 1) # Will Grow Proportionally

        receive_msgs_thread = threading.Thread(
            target = self.receive_msgs,
            args = (buffersize, ),
            name = f"Receive Messages",
            daemon = True # Kill Thread When Spawning Thread (i.e. Main Thread) Exits
        )
        receive_msgs_thread.start()

        #TODO -> Ask Professor if Code Sample is Alright to Include.
        self.window.protocol("WM_DELETE_WINDOW", self.exit) # Close Socket After Tkinter Window Closed.

    def exit(self) -> None:
        self.__send_tcp(f"{self.process_name} Disconnected!")
        self.window.destroy()
        self.clientSocket.close()

    def send_msg(self, event) -> None:
        new_msg: str = f"{self.process_name}: {self.new_msg.get()}"
        self.new_msg.delete(0, END) # Flush Text from Entry Widget
        self.__send_tcp(new_msg)

    def display_msg(self, msg: str, fromSelf: bool = False) -> None:
        self.chat_history.config(state = NORMAL)
        if fromSelf:
            self.chat_history.insert(END, f"{self.msg_offset}{msg}\n")
        else:
            self.chat_history.insert(END, f"{msg}\n")
        self.chat_history.config(state = DISABLED)

    def receive_msgs(self, max_bytes) -> None:
        open: bool = True
        while open: # Check if New Data Received.
            try:
                new_msg: str = self.clientSocket.recv(max_bytes).decode() # Receive New Message
                self.display_msg(msg = new_msg, fromSelf = self.process_name in new_msg)
            except Exception:
                open = False
                self.display_msg(msg = "Could Not Receive from Server...", fromSelf = True)

    def __send_tcp(self, msg: str) -> None:
        try: #TODO -> Check if Connection Available
            self.clientSocket.send(msg.encode()) # Send New Message
        except Exception:
            self.display_msg(msg = "Lost Connection to Server!", fromSelf = True)


def main(): #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()