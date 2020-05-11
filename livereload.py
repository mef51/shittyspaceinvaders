import os
import time
import _thread

file = 'spaceinvaders.py'

def startgame(t, file):
	exec(open(file).read())
	return 0

if __name__ == '__main__':
	print('yo')
	if os.path.exists(file):
		print('yoo')
		moddate = os.stat(file)[8]
		_thread.start_new_thread(startgame, ('Thread 1', file))





