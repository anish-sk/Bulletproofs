from Crypto.Util.number import inverse,bytes_to_long
import secrets

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

	def random(self):
		pass

	def serialize(self):
		pass

	@staticmethod
	def deserialize(self):
		pass

	@staticmethod
	def get_generators(n):
		pass

class Zmod(Group):
	def __init__(self, p,v=None) :
		self.p = p
		self.v = v

	def exp(self,a:int) :
		if a<0:
			return Zmod(self.p,pow(inverse(self.v,self.p),-a,self.p))

		else :
			return Zmod(self.p,pow(self.v,a,self.p))


	def mult(self,a) :
		return Zmod(self.p,(a.v*self.v)%p)

	def inverse(self) :
		return Zmod(self.p,inverse(self.v,self.p))

	def random(self):
		return secrets.randbelow(self.p)

	def serialize(self):
		return str(self.v).encode()

	@staticmethod
	def deserialize(self, p, val):
		return Zmod(p, int(val.decode()))

class Point:
	def __init__(self,x:int,y:int):
		self.x = x
		self.y = y

class Elliptic:
	def __init__(self,p:int,a:int,b:int) :
		self.p = p
		self.a = a
		self.b = b


# @dispatch(Group,Group)
# def mult(a,b):

class Vector:
	def __init__(self,v,p):
		assert type(v)==list
		self.v = v
		self.p = p

	def inner_prod(self,V):
		result = 0
		for val1,val2 in zip(self.v,V.v):
			result += val1.mult(val2).v

		result = result%p

	def __len__(self):
		return len(self.v)


	def exp(self,V):
		if type(V)==Vector :
			assert len(V)==len(self.v)
			result = None
			for val1,val2 in zip(self.v,V.v):
				result_t = val1.exp(val2)
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
		# type(V)==int
		result = [] 
		for val in self.v:
			result.append(val.mult(V))
    	return Vector(result,self.p)