import json
import time
import zmq
import bson

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:16840")
i = 0

while True:
    #  Wait for next request from client
    # message = socket.recv()
    # print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)
    d = bson.dumps({'a':i})
    print(d)
    #  Send reply back to client
    socket.send_multipart([b'test', d])
    i+=1