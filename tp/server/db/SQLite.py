

import sqlite
import time

import config

connection = None
def connect():
	global connection
	
	connection = sqlite.connect(config.database).db

def query(query, kw1=None, **kw2):
	global connection

	if kw1:
		kw2.update(kw1)

	for key,value in kw2.items():
		# How do I escape string in sqlite?
		# kw2[key] = connection.escape_string(str(value))
		pass

	sql = query % kw2
	print sql
	result = connection.execute(sql)
	
	if not result.:
		return

	returns = []
	while True:
		row = result.fetch_row(how=1)
		if len(row) == 0:
			break
		else:
			returns.append(row[0])
	return returns

if __name__ == "__main__":
	connect()
	print connection
	print query("select * from user;")
	print query("describe user;")	
