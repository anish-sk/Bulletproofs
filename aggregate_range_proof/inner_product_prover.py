#!/usr/bin/env python3
import secrets
import socket
import sys
import os
import time
from group import *


def one_round(g_vec,h_vec,u,P,a_vec,b_vec,server_s,p):
	'''
	implements one round of the inner product proof
	'''
	n = len(g_vec)
	if n==1:
		server_s.send(a_vec.serialize()+b'*'+b_vec.serialize())
		return None,None,None,None,None,None


	n1 = n//2
	g_vec1 = Vector(g_vec.v[:n1],p)
	g_vec2 = Vector(g_vec.v[n1:],p)
	h_vec1 = Vector(h_vec.v[:n1],p)
	h_vec2 = Vector(h_vec.v[n1:],p)
	a_vec1 = Vector(a_vec.v[:n1],p)
	a_vec2 = Vector(a_vec.v[n1:],p)
	b_vec1 = Vector(b_vec.v[:n1],p)
	b_vec2 = Vector(b_vec.v[n1:],p)

	cL = a_vec1.inner_prod(b_vec2)
	cR = a_vec2.inner_prod(b_vec1)

	L = g_vec2.exp(a_vec1).mult(h_vec1.exp(b_vec2)).mult(u.exp(cL))
	R = g_vec1.exp(a_vec2).mult(h_vec2.exp(b_vec1)).mult(u.exp(cR))

	server_s.send(L.serialize()+b'*'+R.serialize())

	msg = server_s.recv(1024)
	x = Zmod.deserialize(p,msg)
	x_inv = x.inverse()

	gd = g_vec1.exp(x_inv.v).mult(g_vec2.exp(x.v))
	hd = h_vec1.exp(x.v).mult(h_vec2.exp(x_inv.v))
	Pd = L.exp(x.exp(2).v).mult(P).mult(R.exp(x.exp(-2).v))

	ad = a_vec1.mult(x.v).add(a_vec2.mult(x_inv.v))
	bd = b_vec1.mult(x_inv.v).add(b_vec2.mult(x.v))

	return gd,hd,u,Pd,ad,bd



def prover(conn,p,g,h,u,P,a,b):
	'''
	conn - prover socket
	p - group order
	g - vector of generators
	h - vector of generators
	u - group element
	P - commitment
	a - Vector of Zp group elements
	b - Vector of Zp group elements
	'''

	#Opening socket to connect with the verifier

	while g is not None:
		g,h,u,P,a,b = one_round(g,h,u,P,a,b,conn,p)

