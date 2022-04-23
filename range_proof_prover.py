import argparse
from group import *
import secrets
import socket

#parsing arguments
parser = argparse.ArgumentParser(description='Range Proof Prover')

#Required Verifier Address Argument
parser.add_argument('-a', type=str, help = 'IP Address of the verifier', required=True)

#Required Verifier Port Argument
parser.add_argument('-p', type=int, help = 'Port in which the verifier is listening', required=True)

args = parser.parse_args()

s = socket.socket()
s.connect((args.a, args.p))
print("Connected to Verifier")

# n - The goal is to prove that v lies in the range [0, 2^n -1] 
n = 32

# Let G denote a cyclic group of prime order p, and let Zp denote the ring of integers modulo p
G = NIST_P256
g = G.get_generators(1)
h = G.get_generators(1)
g_vec = Vector(G.get_generators(n))
h_vec = Vector(G.get_generators(n))

#The order of the group G (should be changed based on the chosen group)
p = 1000000007

#v and gamma belong to Zp and are inputs to the prover. v represents the transaction amoun
v = 10000
alpha = secrets.randbelow(p)

#Commitment to aL and aR 
aL = Vector(list(bin(v)[2:]))
aR = Vector([(i-1) for i in aL]) 
alpha = secrets.randbelow(p)

h_alpha = h.exp(alpha)
g_aL = g_vec.exp(aL)
h_aR = h_vec.exp(aR)

A = h_alpha.mult(g_aL).mult(h_aR)

#Send A to verifier
s.send(A.serialize())
s.sleep(0.1)

#Choosing blinding factors sL and sR
sL = []
for i in range(n):
	sL.append(secrets.randbelow(p))
sL = Vector(sL)

sR = []
for i in range(n):
	sR.append(secrets.randbelow(p))
sR = Vector(sL)

rho = secrets.randbelow(p)

h_rho = h.exp(rho)
g_sL = g_vec.exp(sL)
h_sR = h_vec.exp(sR)

S = h_rho.mult(g_sL).mult(h_sR)

#Send S to verifier
s.send(S.serialize())
s.sleep(0.1)

# Receiving challenge points
y = int(s.recv(1024).decode())
z = int(s.recv(1024).decode())


