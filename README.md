# Chat Application with Concurrency

## Contents

* [Overview](#Overview)
* [Program Design](#Program-Design)
    * [Disconnections](#Disconnections)
* [Demonstration](#Demonstration)
* [Credit](#Credit)


## Overview
We developed a chat application in **Python** to implement a **Client-Server Model** via **Transmission Control Protocol (TCP)**. We developed this with the following base requirement :

<b>The chat service provider (i.e. server) must be able to manage multiple clients in the system without a significant drop in performance.</b>

## Program Design

The server and clients are managed via `multiprocessing` as these represent seperate entities (i.e. each have their own code section and **Global Interpreter Lock (GIL)**).

Handshakes are performed and messages are handled (i.e. received/sent from client to server) via `multithreading` for concurrency.

### Disconnections

There has been error handling implemented for both the chat server and clients to appropriately handle disconnections, including a client leaving the system, as well as server shutdown.

We have implemented this, such that the same client can attempt reconnection and communicate via a reestablished server application.

## Demonstration

We have uploaded our Final Demo on <a href="https://www.youtube.com/watch?v=xPEcu-LOH6w" target="_blank">Youtube</a>.

## Credit

This was completed as part of the <b>CPEN 333 - Software Design</b> course in the <b>The University of British Columbia Electrical and Computer Engineering</b> undergraduate program. We received tremendous support and guidance from Dr. Farshid Agharebparast.