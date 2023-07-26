class WriteLog:
	def write(self, s):
		f = open("log", "a")
		f.write(s)
		f.close()

	def debug(self, s):
		f = open("debug", "a")
		f.write(s)
		f.close()
	

