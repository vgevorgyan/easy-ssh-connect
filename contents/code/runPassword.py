try:
	import pexpect
	import sys
	
	command = sys.argv[1]
	password = sys.argv[2]
	child = pexpect.spawn(command)
	child.expect("assword:")
	child.sendline(password)
	child.interact()
except ImportError:
	print "Module pexpect not found, please install pexpect package."
