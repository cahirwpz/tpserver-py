
import sys, string, traceback

lasts = {}

def do_traceback():
	global lasts
	
	type, val, tb = sys.exc_info()
	sys.stderr.write(string.join(traceback.format_exception(type, val, tb), ''))
	lasts = (type, val, tb)
	

def send_traceback(server, dest):
	global lasts
	
	#print "Sending traceback to ", dest
	type, val, tb = sys.exc_info()

	if type==None:
		type, val, tb = lasts[0], lasts[1], lasts[2]

	#print type, val, tb
	
	bits = traceback.format_exception(type, val, tb)
		
	for i in bits:
		server.privmsg(dest, i)

	lasts = (type, val, tb)


def event_mangle(event):

	if event.eventtype() == "privmsg":
		
		#print "making target the source"

		#print event.target()
		event.target = event.source
		#print event.target()


import os
import cPickle as pickle

def load_data(file):
	f = open(os.path.join("data", file), "r")
	return pickle.load(f)

def save_data(file, data):
	f = open(os.path.join("data", file), "w")
	pickle.dump(data, f)

def load_conf(file):

	returns = {}

	f = open(os.path.join("conf", file))
	data = string.split(f.read(), '\n')

	bits = None
	for i in data:
		try:
			#print i
			if i[0] == '#':
				continue
			if i[0] == '/':
				if bits:
					if type(bits[1]) == type([]):
						bits[1] = string.join(bits[1], " ")
					bits[1] = bits[1] + "\n" + i[1:]
					returns[bits[0]] = bits[1]
				else:
					continue
			else:
				bits = string.split(i,"=",1)
				bits = [string.strip(bits[0]), string.strip(bits[1])]
				
				if len(string.split(bits[1])) > 1:
					bits[1] = string.split(bits[1])
			
				returns[bits[0]] = bits[1]
		except:
			do_traceback()

	return returns
	
