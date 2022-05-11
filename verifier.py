#!/usr/bin/env python3
import secrets
import socket
from group import *


def one_round(g_vec,h_vec,u,P,conn,p,Grp):
	n = len(g_vec)
	#Base case
	if n==1:
		msg = conn.recv(1024)
		a,b = msg.split(b'*')
		a = Vector.deserialize(p,a,Zmod)
		b = Vector.deserialize(p,b,Zmod)
		c = a.inner_prod(b)
		P_n = g_vec.exp(a).mult(h_vec.exp(b)).mult(u.exp(c))
		if P_n==P:
			print("Verification successfull!!")
		else:
			print("Verification failed")

		return None,None,None,None
		
	#Recursion part

	n1 = n//2
	g_vec1 = Vector(g_vec[:n1],p)
	g_vec2 = Vector(g_vec[n1:],p)
	h_vec1 = Vector(h_vec[:n1],p)
	h_vec2 = Vector(h_vec[n1:],p)
	msg = conn.recv(1024)
	L,R = msg.split(b'*')
	L = Grp.deserialize(p,L)
	R = Grp.deserialize(p,R)
	x = secrets.randbelow(p)
	x = Zmod(p,x)
	c.send(x.serialize())

	x_inv = x.inverse()
	gd = g_vec1.exp(x_inv.v).mult(g_vec2.exp(x.v))
	hd = h_vec1.exp(x.v).mult(h_vec2.exp(x_inv.v))
	Pd = L.exp(x.exp(2).v).mult(P).mult(R.exp(x.exp(-2)))

	return gd,hd,u,Pd

def verifier(port,p,g,h,u,P,Grp):
	'''
	port - verifier port
	p - group order
	g - vector of generators
	h - vector of generators
	u - group element
	P - commitment
  Grp - Group class
	'''
	s = socket.socket()
	s.bind(('', port))
	s.listen(5)
	c, addr = s.accept()
	print ('Prover ip,port : ', addr )

	while g is not None:
		g,h,u,P = one_round(g,h,u,P,c,p,Grp)

