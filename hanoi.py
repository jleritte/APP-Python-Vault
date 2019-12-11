
def move(f,t):
	print "Move disc from {} to {}!".format(f,t)

def hanoi(n,f,h,t):
	if n == 0:
		pass
	else:
		hanoi(n-1,f,t,h)
		move(f,t)
		hanoi(n-1,h,f,t)

hanoi(1,"A","B","C")
hanoi(2,"A","B","C")
hanoi(3,"A","B","C")
hanoi(4,"A","B","C")
hanoi(5,"A","B","C")
hanoi(6,"A","B","C")
hanoi(7,"A","B","C")
hanoi(8,"A","B","C")
hanoi(9,"A","B","C")
hanoi(10,"A","B","C")