import argparse
from Crypto.Util.number import inverse
from group import *
import random
import secrets
import socket
from time import sleep

#parsing arguments
parser = argparse.ArgumentParser(description='Range Proof Verifier')

#Required Verifier Port Argument
parser.add_argument('-p', type=int, help = 'Port in which the verifier is listening', required=True)

#Required Transaction Commitment Argument
parser.add_argument('-V', type=str, help = 'The transaction commitment value of the amount v', required=True)

#Required Seed Argument
parser.add_argument('-s', type=int, help = 'The seed used while generating the generators in the proof', required=True)

args = parser.parse_args()

#Setting the seed for the random library
random.seed(args.s)

#Create socket
s = socket.socket()

#Bind socket to required port
port = args.p
s.bind(('', port))

s.listen(5)

#Accept connection from client
c, addr = s.accept()
print(f"Connected to Prover: {addr}")

#Let G denote a cyclic group of prime order p, and let Zp denote the ring of integers modulo p
G = Elliptic

#Getting the generators required in the proof
g = G.get_generators(1)
h = G.get_generators(1)
g_vec = Vector(G.get_generators(n))
h_vec = Vector(G.get_generators(n))

#The order of the group G (should be changed based on the chosen group)
p = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

#n - The goal is to prove that v lies in the range [0, 2^n -1] 
n = 32

#Get V by deserializing the corresponding argument
V = G.deserialize(p, args.V)

#Receiving A, S from prover
A = G.deserialize(p, c.recv(1024).decode())
S = G.deserialize(p, c.recv(1024).decode())

#Generate and send challenge points y and z to prover
y = secrets.randbelow(p)
c.send(y.encode())
sleep(0.1)

z = secrets.randbelow(p)
c.send(z.encode())
sleep(0.1) 

#Receiving T1, T2 from prover
T1 = G.deserialize(p, c.recv(1024).decode())
T2 = G.deserialize(p, c.recv(1024).decode())

#Generate and send challenge point x to prover
x = secrets.randbelow(p)
c.send(x.encode())
sleep(0.1)

#Receiving taux, mu and t_hat from receiver
taux = int(c.recv(1024).decode())
mu = int(c.recv(1024).decode())
t_hat = int(c.recv(1024).decode())

#Function for returning the vector x^y where x belongs to Zp
def vector_gen(x,y,p):
	result = [1]
	ans = 1
	for i in range(y-1):
		ans = (ans * x)% p
		result.append(ans)
	return Vector(result)

#Generating required vectors
ones = vector_gen(1,n,p)
twos = vector_gen(2,n,p)
yn = vector_gen(y,n,p)
y_invn = vector_gen(inverse(y,p), n, p)

#Calculate hdash
hdash = []
for i in range(n):
	hdash.append(h_vec.v[i].exp(y_invn.v[i]))
hdash = Vector(hdash)

#First check
#check that t_hat = t(x) =  t0 + t1*x t2*x*x

#LHS
g_t_hat = g.exp(t_hat)
h_taux = h.exp(taux)

lhs1 = g_t_hat.mult(h_taux)

#RHS
