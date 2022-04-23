#!/usr/bin/env python3
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import cryptography.hazmat.primitives.padding as symmetric_padding
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
import secrets
import socket
import sys
import base64
import os
import argparse
import threading
import time
from group import *


#parsing arguments
parser = argparse.ArgumentParser(description='TLS Client')

#Required Name Argument
parser.add_argument('-n', type=str, help = 'Name of the client', required=True)

#Required Mode Argument
parser.add_argument('-m', type=str, help = 'Mode of the client - Sender(S)/Receiver(R)', required=True)

#Required Server IP Argument
parser.add_argument('-d', type=str, help = 'Server IP denotes the IP address of the server', required=True)

#Required Server Port Argument
parser.add_argument('-q', type=int, help = 'Port on which the Server process listens', required=True)

args = parser.parse_args()

#sanity checks
if args.m != 'R':
	print("client.py has to be run only with mode = R")
	sys.exit()

my_name = args.n
server_ip = args.d
server_port = args.q
p = 
g_vec = 
h_vec = 
u = 
P = 
a_vec = 
b_vec = 
n = len(g_vec)
n1 = n//2

def vector_gen(g,x):
	result = []
	if x<0:
		g = g.inverse()
		x = -x

	for i in range(x):
		result.append(g.exp(i))

	return Vector(result)

#Opening socket to connect with the server
server_s = socket.socket()
server_s.connect((server_ip, server_port))
print("Connected to server")

msg = server_s.recv(1024)

x_value = int(msg.decode())

x = Zmod(p,x_value)

g_vec1 = g_vec[:n1]
g_vec2 = g_vec[n1:]
a_vec1 = a_vec[:n1] 
a_vec2 = a_vec[n1:]
b_vec1 = b_vec[:n1] 
b_vec2 = b_vec[n1:]









