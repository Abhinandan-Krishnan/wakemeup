class A:
	def __init__(self):
		self.var="class A"

	def change(self,text):
		self.var=text

class B(A):
	def __init__(self):
		super().__init__()

		self.change("Overide")

	def func(self):
		print(self.var)


c=B()
c.func()