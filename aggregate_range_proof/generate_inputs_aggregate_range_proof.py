#Generate v, gamma and V given p and n
from group import *
import random
import secrets

#Take p, n, m and seed as input
n = int(input())
m = int(input())
p = int(input(), 16)
s = int(input())

#Setting the seed for the random library
random.seed(s)

#Let G denote a cyclic group of prime order p, and let Zp denote the ring of integers modulo p
G = Elliptic

#Getting the generators required for the commitment
g = G.get_generators(1)
h = G.get_generators(1)

#Generate v, gamma and V
v = []
for i in range(m):
	v.append(secrets.randbelow(1<<n))
v = Vector(v, p)
gamma = []
for i in range(m):
	gamma.append(secrets.randbelow(p))
gamma = Vector(gamma, p)
V = []
for i in range(m):
	V.append(h.exp(gamma.v[i]).mult(g.exp(v.v[i])))
V = Vector(V, p)

#Writing v, gamma and V to respective files
with open("v", "wb") as f:
	f.write(v.serialize())
with open("gamma", "wb") as f:
	f.write(gamma.serialize())
with open("V", "wb") as f:
	f.write(V.serialize())