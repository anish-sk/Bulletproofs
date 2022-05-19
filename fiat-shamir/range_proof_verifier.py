import argparse
from Crypto.Util.number import inverse
from group import *
from inner_product_verifier import verifier
import random
import secrets
import socket
import sys
from time import sleep

#parsing arguments
parser = argparse.ArgumentParser(description='Range Proof Verifier')

#Required Transaction Commitment Argument
parser.add_argument('-V', type=str, help = 'The transaction commitment value of the amount v', required=True)

#Required Seed Argument
parser.add_argument('-s', type=int, help = 'The seed used while generating the generators in the proof', required=True)

args = parser.parse_args()

#Setting the seed for the random library
random.seed(args.s)

transcript_prover = LoadTranscript('transcript')

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


#Get V by deserializing the corresponding argument
V = G.deserialize(p, (args.V).encode())
if str(V)!=transcript_prover['V']:
	print("Error verifying.. V mismatch!!")
	exit()

#Receiving A, S from prover
A,S = transcript_prover['A'],transcript_prover['S']
A = G.deserialize(p, A.encode())
S = G.deserialize(p, S.encode())
transcript = {}
transcript['V'] = str(V)
transcript['n'] = str(n)
transcript['A'] = str(A)
transcript['S'] = str(S)


#Generate and send challenge points y and z to prover
y = fiatshamir(str(transcript),p)
if str(y) != transcript_prover['y']:
	print("Error verifying.. challenge y mismatch!!")
	exit()
transcript['y'] = str(y)
z = fiatshamir(str(transcript),p)
if str(z) != transcript_prover['z']:
	print("Error verifying.. challenge z mismatch!!")
	exit()
transcript['z'] = str(z)


#Receiving T1, T2 from prover
T1,T2 = transcript_prover['T1'],transcript_prover['T2']
T1 = G.deserialize(p, T1.encode())
T2 = G.deserialize(p, T2.encode())

transcript['T1']=str(T1)
transcript['T2']=str(T2)

#Generate and send challenge point x to prover
x = fiatshamir(str(transcript),p)
if str(x) != transcript_prover['x']:
	print("Error verifying.. challenge x mismatch!!")
	exit()
transcript['x'] = str(x)


#Receiving taux, mu and t_hat from receiver
taux,mu,t_hat = transcript_prover['taux'],transcript_prover['mu'],transcript_prover['t_hat']
taux = int(taux)
mu = int(mu)
t_hat = int(t_hat)

transcript['taux']=str(taux)
transcript['mu']=str(mu)
transcript['t_hat']=str(t_hat)


#Function for returning the vector x^y where x belongs to Zp
def vector_gen(x,y,p):
	result = [Zmod(p,1)]
	ans = 1
	for i in range(y-1):
		ans = (ans * x)% p
		result.append(Zmod(p,ans))
	return Vector(result,p)

#Generating required vectors
ones = vector_gen(1,n,p)
twos = vector_gen(2,n,p)
yn = vector_gen(y,n,p)
y_invn = vector_gen(inverse(y,p), n, p)

#Calculate hdash
hdash = []
for i in range(n):
	hdash.append(h_vec.v[i].exp(y_invn.v[i].v))
hdash = Vector(hdash,p)

#First check
#check that t_hat = t(x) =  t0 + t1*x + t2*x*x

#LHS
g_t_hat = g.exp(t_hat)
h_taux = h.exp(taux)

lhs1 = g_t_hat.mult(h_taux)

#RHS
#calculate delta(y,z)
def delta(yn,z):
	tmp1 = ones.inner_prod(yn)
	tmp1 = tmp1*(z - z*z)
	tmp2 = ones.inner_prod(twos)
	tmp2 = tmp2*(z*z*z)
	return (tmp1 - tmp2)%p

Vz2 = V.exp(z*z)
g_delta = g.exp(delta(yn,z))
T1x = T1.exp(x)
T2x2 = T2.exp(x*x)

rhs1 = Vz2.mult(g_delta).mult(T1x).mult(T2x2)

#Compare lhs and rhs
if lhs1 == rhs1:
	print("Verified that t_hat = t(x) =  t0 + t1*x + t2*x*x")
else:
	print("Verification failed: t_hat != t0 + t1*x + t2*x*x")
	sys.exit()

#Calculate P and Pdash
tmp0 = ones.mult(-z)
tmp1 = A.mult(S.exp(x)).mult(g_vec.exp(tmp0))
tmp2 = yn.mult(z).add(twos.mult(z*z))
tmp2 = hdash.exp(tmp2)
P = tmp1.mult(tmp2)
Ph_mu = P.mult(h.exp(-mu))
Pdash = Ph_mu.mult(u.exp(t_hat))


#Call inner product verifier
verifier(transcript_prover, transcript, p, g_vec, hdash, u, Pdash, Elliptic)


