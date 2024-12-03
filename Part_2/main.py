#Content of main.py; use as is
from tkinter import *
import multiprocessing
import time

import client_part2 as client
import server_part2 as server

if __name__ == "__main__":
    server = multiprocessing.Process(target=server.main)
    server.start()
    # time.sleep(1)  #to ensure server is up and running; may be commented out or changed

    numberOfClients = 3  #Change this value for a different number of clients
    for count in range(1, numberOfClients+1):
        multiprocessing.Process(target=client.main, name=f"Client{count}").start()