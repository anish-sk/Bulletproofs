from prover import prover
from verifier import verifier
from group import *
import random
import sys

random.seed(0xdeadbeef)
# p = 500
# G = Zmod_Group

p = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G= Elliptic


n = 2
u = G.get_generators(1)
print('u: ', u.serialize())
g_vec = Vector(G.get_generators(n),p)
print('g_vec: ',g_vec)
h_vec = Vector(G.get_generators(n),p)
print('h_vec: ',h_vec)



a = []
for i in range(n):
    a.append(Zmod(p,random.randint(0,p)))
b = []
for i in range(n):
    b.append(Zmod(p,random.randint(0,p)))

a = Vector(a,p)
b = Vector(b,p)
print('a:',a)
print('b:',b)
c = a.inner_prod(b)
P = g_vec.exp(a).mult(h_vec.exp(b)).mult(u.exp(c))
print(P)
port = 1234
if sys.argv[1]=='1':
    prover(port,p,g_vec,h_vec,u,P,a,b)
else :
    verifier('127.0.0.1',port,p,g_vec,h_vec,u,P,G)