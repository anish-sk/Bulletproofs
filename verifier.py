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




parser = argparse.ArgumentParser()
parser.add_argument('-n', type=str, required=True)
parser.add_argument('-m', type=str, required=True)
parser.add_argument('-q', type=int, required=True)

args = parser.parse_args()



serv_name = args.n
s = socket.socket()
port = args.q
s.bind(('', port))

s.listen(5)

c, addr = s.accept()

print ('Prover ip,port : ', addr )

x = Zmod(p).random()

c.send(str(x).encode())

