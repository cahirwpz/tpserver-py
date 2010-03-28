"""Version of the requirements which is quiet unless there is an error."""
import cStringIO as StringIO
import sys

sys_stdout = sys.stdout
sys.stdout = StringIO.StringIO()
sys_stderr = sys.stderr
sys.stderr = sys.stdout

try:
	import requirements
except:
	stdout = sys.stdout.getvalue()
	sys.stdout = sys_stdout
	print stdout
	raise
	
sys.stdout = sys_stdout
sys.stderr = sys_stderr
