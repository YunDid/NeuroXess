#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import bson
import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.SUB)
# socket.connect("tcp://localhost:16480")
socket.connect("tcp://localhost:16480") # tcp://localhost:16480
#  Do 10 requests, waiting each time for a response
# for request in range(10):
#     print("Sending request %s …" % request)
#     socket.send(b"Hello")
#
#     #  Get the reply.
#     message = socket.recv()
#     print("Received reply %s [ %s ]" % (request, message)) cc-hs-data
socket.setsockopt(zmq.SUBSCRIBE, "cc-hs-data".encode('utf-8'))
print("dddd")
while True:
    topic, *msg, meta = socket.recv_multipart()
    print(topic, meta)