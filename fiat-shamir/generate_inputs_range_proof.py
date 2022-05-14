#Generate v, gamma and V given p and n
from group import *
import random
import secrets

#Take p, n and seed as input
n = int(input())
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
v = secrets.randbelow(1<<n)
gamma = secrets.randbelow(p)
V = h.exp(gamma).mult(g.exp(v))

#Writing v, gamma and V to respective files
with open("v", "w") as f:
	f.write(str(v))
with open("gamma", "w") as f:
	f.write(str(gamma))
with open("V", "w") as f:
	f.write(V.serialize().decode())