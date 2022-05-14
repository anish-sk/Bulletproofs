#!/usr/bin/env python3
import secrets
import socket
import sys
import os
import time
import random
from group import *


def one_round(g_vec,h_vec,u,P,transcript,p,Grp,transcript_prover):
	n = len(g_vec)
	if n==1:
		a,b = transcript_prover['a'],transcript_prover['b']
		a = Vector.deserialize(p,a.encode(),Zmod)
		b = Vector.deserialize(p,b.encode(),Zmod)
		c = a.inner_prod(b)
		P_n = g_vec.exp(a).mult(h_vec.exp(b)).mult(u.exp(c))

		if P_n==P:
			print("Verification successfull!!")
		else:
			print("Verification failed")

		return None,None,None,None,None

	n1 = n//2
	g_vec1 = Vector(g_vec.v[:n1],p)
	g_vec2 = Vector(g_vec.v[n1:],p)
	h_vec1 = Vector(h_vec.v[:n1],p)
	h_vec2 = Vector(h_vec.v[n1:],p)
	
	i = len(transcript.get('L',[]))
	L,R = transcript_prover['L'][i],transcript_prover['R'][i]

	L = Grp.deserialize(p,L.encode())
	R = Grp.deserialize(p,R.encode())

	if i!=0:
		transcript['L'].append(str(L))
		transcript['R'].append(str(R))

	else :
		transcript['L']=[str(L)]
		transcript['R']=[str(R)]

	x = fiatshamir(str(transcript),p)
	if str(x)!= transcript_prover['IPx'][i]:
		print(f"Error verifying.. challenge IPx{i} mismatch!!")
		exit()

	if i!=0:
		transcript['IPx'].append(str(x))
	else :
		transcript['IPx'] = [str(x)]

	x = Zmod(p,x)

	x_inv = x.inverse()
	gd = g_vec1.exp(x_inv.v).mult(g_vec2.exp(x.v))
	hd = h_vec1.exp(x.v).mult(h_vec2.exp(x_inv.v))
	Pd = L.exp(x.exp(2).v).mult(P).mult(R.exp(x.exp(-2).v))


	return gd,hd,u,Pd,transcript

def verifier(transcript_prover,transcript,p,g,h,u,P,Grp):
	'''
	transcript_prover - transcript of prover which has all values
	transcript - current transcript, to check if challenges are generated with fiatshamir
	p - group order
	g - vector of generators
	h - vector of generators
	u - group element
	P - commitment
	Grp - Group class
	'''

	while g is not None:
		g,h,u,P,transcript = one_round(g,h,u,P,transcript,p,Grp,transcript_prover)


