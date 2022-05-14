import argparse
from group import *
from inner_product_prover import prover
import random
import secrets
import socket
import sys
from time import sleep

#parsing arguments
parser = argparse.ArgumentParser(description='Range Proof Prover')

#Required Prover Port Argument
parser.add_argument('-p', type=int, help = 'Port in which the prover is listening', required=True)

#Required Transaction Amount Argument
parser.add_argument('-v', type=int, help = 'The transaction amount', required=True)

#Required Randomness Argument
parser.add_argument('-g', type=int, help = 'The randomness value used in pedersen commitment to v', required=True)

#Required Seed Argument
parser.add_argument('-s', type=int, help = 'The seed used while generating the generators in the proof', required=True)

args = parser.parse_args()

#Setting the seed for the random library
random.seed(args.s)

#Create socket
c = socket.socket()

#Bind socket to required port
port = args.p
c.bind(('', port))

c.listen(5)

#Accept connection from client
s, addr = c.accept()
print(f"Connected to Verifier: {addr}")

#n - The goal is to prove that v lies in the range [0, 2^n -1] 
n = 32

#Let G denote a cyclic group of prime order p, and let Zp denote the ring of integers modulo p
G = Elliptic
#The order of the group G (should be changed based on the chosen group)
p = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551


#Getting the generators required in the proof
g = G.get_generators(1)
h = G.get_generators(1)
g_vec = Vector(G.get_generators(n),p)
h_vec = Vector(G.get_generators(n),p)
u = G.get_generators(1)

#v and gamma belong to Zp and are inputs to the prover. v represents the transaction amount
v = args.v
alpha = secrets.randbelow(p)
gamma = args.g
V = h.exp(gamma).mult(g.exp(v))

#Commitment to aL and aR 
aL = Vector([Zmod(p,int(i)) for i in list(bin(v)[2:].zfill(n))[::-1]],p)
aR = Vector([Zmod(p,int(i)-1) for i in list(bin(v)[2:].zfill(n))[::-1]],p) 
alpha = secrets.randbelow(p)

h_alpha = h.exp(alpha)
g_aL = g_vec.exp(aL)
h_aR = h_vec.exp(aR)

A = h_alpha.mult(g_aL).mult(h_aR)

#Choosing blinding factors sL and sR
sL = []
for i in range(n):
	sL.append(Zmod(p,secrets.randbelow(p)))
sL = Vector(sL,p)

sR = []
for i in range(n):
	sR.append(Zmod(p,secrets.randbelow(p)))
sR = Vector(sR,p)

rho = secrets.randbelow(p)

h_rho = h.exp(rho)
g_sL = g_vec.exp(sL)
h_sR = h_vec.exp(sR)

S = h_rho.mult(g_sL).mult(h_sR)

#Send A,S to verifier
s.send(A.serialize()+b'*'+S.serialize())

#Receiving challenge points y and z
msg = s.recv(1024)
y,z = msg.split(b'*')
y = int(y.decode())
z = int(z.decode())

#Function for returning the vector x^y where x belongs to Zp
def vector_gen(x,y,p):
	result = [Zmod(p,1)]
	ans = 1
	for i in range(y-1):
		ans = (ans * x)% p
		result.append(Zmod(p,ans))
	return Vector(result,p)

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

t2 = sL.inner_prod(yn.mult(sR))


#Calculate T1
tau1 = secrets.randbelow(p)

h_tau1 = h.exp(tau1)
g_t1 = g.exp(t1)

T1 = h_tau1.mult(g_t1)

#Calculate T2
tau2 = secrets.randbelow(p)

h_tau2 = h.exp(tau2)
g_t2 = g.exp(t2)

T2 = h_tau2.mult(g_t2)

#Send T1,T2 to verifier
s.send(T1.serialize()+b'*'+T2.serialize())

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
s.send(str(taux).encode()+b'*'+str(mu).encode()+b'*'+str(t_hat).encode())

#Use the inner product prover and verifier to complete the rest of the proof based on l and r.

#Calculate hdash
hdash = []
for i in range(n):
	hdash.append(h_vec.v[i].exp(y_invn.v[i].v))
hdash = Vector(hdash,p)

#Calculate P*h^(-mu) and P' to send to inner product prover
Ph_mu = g_vec.exp(lx).mult(hdash.exp(rx))
Pdash = Ph_mu.mult(u.exp(t_hat))

#Wait for confirmation message from verifier
msg = s.recv(1024).decode()
if msg[:3] == "400":
	print("Verification Failed")
	s.close()
	sys.exit()
elif msg[:3]=="200":
	print("Verified that t_hat = t(x) =  t0 + t1*x t2*x*x")
else :
	print("Error!!")

#Call inner product prover
prover(s, p, g_vec, hdash, u, Pdash, lx, rx)

#Finishing
s.close()
c.close()