

import MySQLdb
import time

connection = None
def connect():
	global connection
	
	connection = MySQLdb.connect("localhost", "tp", "tp-password", "tp")

def query(query, kw1=None, **kw2):
	global connection

	if kw1:
		kw2.update(kw1)

	for key,value in kw2.items():
		kw2[key] = connection.escape_string(str(value))

	connection.ping()
	sql = query % kw2
	print sql
	connection.query(sql)
	
	result = connection.use_result()
	if not result:
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
