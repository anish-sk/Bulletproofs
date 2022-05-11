import argparse
from Crypto.Util.number import inverse
from group import *
import random
import secrets
import socket
from time import sleep

#parsing arguments
parser = argparse.ArgumentParser(description='Range Proof Prover')

#Required Verifier Address Argument
parser.add_argument('-a', type=str, help = 'IP Address of the verifier', required=True)

#Required Verifier Port Argument
parser.add_argument('-p', type=int, help = 'Port in which the verifier is listening', required=True)

#Required Transaction Amount Argument
parser.add_argument('-v', type=int, help = 'The transaction amount', required=True)

#Required Randomness Argument
parser.add_argument('-g', type=int, help = 'The randomness value used in pedersen commitment to v', required=True)

#Required Seed Argument
parser.add_argument('-s', type=int, help = 'The seed used while generating the generators in the proof', required=True)

args = parser.parse_args()

#Setting the seed for the random library
random.seed(args.s)

#Create socket and connect to verifier
s = socket.socket()
s.connect((args.a, args.p))
print("Connected to Verifier")

#n - The goal is to prove that v lies in the range [0, 2^n -1] 
n = 32

#Let G denote a cyclic group of prime order p, and let Zp denote the ring of integers modulo p
G = Elliptic

#Getting the generators required in the proof
g = G.get_generators(1)
h = G.get_generators(1)
g_vec = Vector(G.get_generators(n))
h_vec = Vector(G.get_generators(n))

#The order of the group G (should be changed based on the chosen group)
p = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

#v and gamma belong to Zp and are inputs to the prover. v represents the transaction amount
v = args.v
alpha = secrets.randbelow(p)
gamma = args.g

#Commitment to aL and aR 
aL = Vector(list(bin(v)[2:].zfill(n)))
aR = Vector([(i-1) for i in aL]) 
alpha = secrets.randbelow(p)

h_alpha = h.exp(alpha)
g_aL = g_vec.exp(aL)
h_aR = h_vec.exp(aR)

A = h_alpha.mult(g_aL).mult(h_aR)

#Send A to verifier
s.send(A.serialize())
sleep(0.1)

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
sleep(0.1)

#Receiving challenge points y and z
y = int(s.recv(1024).decode())
z = int(s.recv(1024).decode())

#Function for returning the vector x^y where x belongs to Zp
def vector_gen(x,y,p):
	result = [1]
	ans = 1
	for i in range(y-1):
		ans = (ans * x)% p
		result.append(ans)
	return Vector(result)

#Calculate t1 and t2
ones = vector_gen(1,n,p)
twos = vector_gen(2,n,p)
yn = vector_gen(y,n,p)
y_invn = vector_gen(inverse(y,p), n, p)
tmp1 = yn.mult(aR.add(ones.mult(z)))
tmp1 = tmp1.add(twos.mult(z*z))
tmp1 = sL.inner_prod(tmp1)

tmp2 = aL.add(ones.mult(-z))
tmp2 = tmp2.inner_prod(yn.mult(sR))

t1 = tmp1 + tmp2

t2 = sL.add(yn.mult(sR))

#Calculate T1
tau1 = secrets.randbelow(p)

h_tau1 = h.exp(tau1)
g_t1 = g.exp(t1)

T1 = h_tau1.mult(g_t1)

#Send T1 to verifier
s.send(T1.serialize())
sleep(0.1)

#Calculate T2
tau2 = secrets.randbelow(p)

h_tau2 = h.exp(tau2)
g_t2 = g.exp(t2)

T2 = h_tau2.mult(g_t2)

#Send T2 to verifier
s.send(T2.serialize())
sleep(0.1)

#Receiving a challenge point x
x = int(s.recv(1024).decode())

#Compute l(x)
tmp = aL.add(ones.mult(-z))
lx = tmp.add(sL.mult(x))

#Compute r(x)
tmp2 = aR.add(ones.mult(z))
tmp2 = tmp2.add(sR.mult(x))
tmp2 = yn.mult(tmp2)
rx = tmp2.add(twos.mult(z*z))

#Compute t_hat, taux and mu
t_hat = lx.inner_prod(rx)
taux = (tau2*x*x + tau1*x + z*z*gamma)%p
mu = (alpha + rho*x)%p

#Send taux, mu and t_hat to verifier
s.send(taux.encode())
sleep(0.1)

s.send(mu.encode())
sleep(0.1)

s.send(t_hat.encode())
sleep(0.1)

#Use the inner product prover and verifier to complete the rest of the proof based on l and r.

#Calculate hdash
hdash = []
for i in range(n):
	hdash.append(h_vec.v[i].exp(y_invn.v[i]))
hdash = Vector(hdash)