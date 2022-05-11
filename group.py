from Crypto.Util.number import inverse
from Crypto.PublicKey.ECC import EccPoint
import secrets
import random

def byte_len(x):
	return (len(bin(x))+5)//8


class Group:
	def __init__(self) :
		pass

	def exp(self,a) :
		pass

	def mult(self,a) :
		pass

	def inverse(self):
		pass

	def serialize(self):
		pass

	@staticmethod
	def deserialize(p,val):
		pass

	@staticmethod
	def get_generators(n):
		pass

class Zmod:
	def __init__(self, p,v=None) :
		self.p = p
		self.v = v

	def exp(self,a:int) :
		if a<0:
			return Zmod(self.p,pow(inverse(self.v,self.p),-a,self.p))

		else :
			return Zmod(self.p,pow(self.v,a,self.p))


	def mult(self,a) :
		return Zmod(self.p,(a.v*self.v)%self.p)

	def inverse(self) :
		return Zmod(self.p,inverse(self.v,self.p))


	def serialize(self):
		return str(self.v).encode()

	def __str__(self):
		return str(self.v)

	@staticmethod
	def deserialize(p, val):
		return Zmod(p, int(val.decode()))

class Zmod_Group(Group):
	'''
	Group of order 500

	Group is defined as mod 625

	'''
	def __init__(self, v) :
		self.p = 500
		self.mod = 625
		self.v = v

	def exp(self,a:int) :
		if a<0:
			v = inverse(self.v,self.p)
			if v*self.v % self.p != 1:
				assert 1==0
			return Zmod_Group(pow(inverse(self.v,self.p),-a,self.mod))

		else :
			return Zmod_Group(pow(self.v,a,self.mod))


	def mult(self,a) :
		return Zmod_Group((a.v*self.v)%self.mod)

	def inverse(self) :
		v = inverse(self.v,self.p)
		if v*self.v % self.p != 1:
			assert 1==0
		return Zmod_Group(inverse(self.v,self.p))


	def serialize(self):
		return str(self.v).encode()

	def __eq__(self, other):
	    if isinstance(other, Zmod_Group):
	        return self.v == other.v
	    return False

	def __str__(self):
		return str(self.v)

	@staticmethod
	def deserialize(p, val):
		return Zmod_Group(int(val.decode()))

	@staticmethod
	def get_generators(n):
		p = 500
		G_b = 3
		mod = 625
		result = []
		for i in range(n):
			v = 10
			while v%5==0 or v%2==0:
				v = random.randint(1,p)
			result.append(Zmod_Group(pow(G_b,v,mod)))

		if n==1:
			return result[0]

		return result

class Elliptic:
	'''
	NIST P-256 Elliptic Curve
	'''
	def __init__(self,x,y):
		# by default, curve is nist p-256
		self.point = EccPoint(x,y)

	def exp(self,a:int) :
		if a<0:
			print('here')
			pt = -self.point*(-a)

		else :
			pt = self.point*a

		x,y = pt.x,pt.y
		return Elliptic(x,y)

	def mult(self,point):
		pt = self.point+point.point
		x,y = pt.x,pt.y
		return Elliptic(x,y)

	def serialize(self):
		return f'({self.point.x},{self.point.y})'.encode()

	def __eq__(self, other):
	    if isinstance(other, Elliptic):
	        return self.point == other.point
	    return False

	def __str__(self):
		return self.serialize().decode()


	@staticmethod
	def deserialize(p, val):
		val = val.decode()
		x,y = val.strip()[1:-1].split(',')
		x = int(x)
		y = int(y)
		return Elliptic(x,y)

	@staticmethod
	def get_generators(n):
		Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
		Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
		G_b = EccPoint(Gx,Gy)
		p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
		result = []
		for i in range(n):
			v = random.randint(1,p)
			pt = v*G_b
			x,y = pt.x,pt.y
			result.append(Elliptic(x,y))

		if n==1:
			return result[0]

		return result



class Vector:
	'''
	Vector of Group objects
	'''
	def __init__(self,v,p):
		if type(v)!=list:
			v = [v]

		self.v = v
		self.p = p

	def inner_prod(self,V):
		result = 0
		for val1,val2 in zip(self.v,V.v):
			result += val1.mult(val2).v

		result = result%self.p
		return result

	def __len__(self):
		return len(self.v)


	def exp(self,V):
		if type(V)==Vector :
			assert len(V)==len(self.v)
			result = None
			for val1,val2 in zip(self.v,V.v):
				result_t = val1.exp(val2.v)
				if result is not None:
					result = result.mult(result_t)
				else :
					result = result_t

			return result

		else :
			# type(V)==int
			result = []
			for val in self.v:
				result.append(val.exp(V))

			return Vector(result,self.p)

	def mult(self,V):
		if type(V)==Vector :
			assert len(V.v)==len(self.v)
			result = []
			for val1,val2 in zip(self.v,V.v):
				result.append(val1.mult(val2))
	
			return Vector(result,self.p)
		else:
			# type(V)==int
			# defined only if Vector of Zmods
			result = [] 
			for val in self.v:
				result.append(val.mult(Zmod(self.p,V)))
			return Vector(result,self.p)

	def add(self,V):
		assert len(V.v)==len(self.v)
		result = []
		for val1,val2 in zip(self.v,V.v):
			result.append(Zmod(self.p,(val1.v+val2.v)%self.p))

		return Vector(result,self.p)


	def serialize(self):
		val = b'['
		for v in self.v :
			try:
				temp = v.serialize()

			except :
				temp = str(v).encode()

			val += temp + b','

		if len(val)>=2:
			val = val[:-1]
		val += b']'
		return val

	def __str__(self):
		return self.serialize().decode()

	@staticmethod
	def deserialize(p,val,Grp=None):
		val = val[1:-1]
		val = val.split(b',')
		result = []
		for v in val :
			if Grp is not None:
				result.append(Grp.deserialize(p,v))
			else:
				result.append(int(v.decode()))

		return Vector(result,p)