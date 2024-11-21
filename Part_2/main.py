#Content of main.py; use as is
from tkinter import *
import multiprocessing
import time

import Part_2.client_part2 as client_part2
import Part_2.server_part2 as server_part2

if __name__ == "__main__":
    server_part2 = multiprocessing.Process(target=server_part2.main)
    server_part2.start()
    time.sleep(1)  #to ensure server is up and running; may be commented out or changed

    numberOfClients = 2  #Change this value for a different number of clients
    for count in range(1, numberOfClients+1):
        multiprocessing.Process(target=client_part2.main, name=f"Client{count}").start()