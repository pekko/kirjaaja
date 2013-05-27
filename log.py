from datetime import datetime

today = datetime.today()
fn = "/rdata/www/speksi/var/script/kirjaaja/log/%04d-%02d-%02d.log" % (today.year, today.month, today.day)

class Message(object):
	def __init__(self, msg, level="INFO"):
		self.msg = msg
		self.level = level
		self.timestamp = datetime.now()

	def __str__(self):
		return "[%s] [%s] %s" % (self.timestamp, self.level, self.msg)

def msg(msg, level="INFO"):
	logfile = open(fn, 'a')
	message = Message(msg, level)
	msg_str = str(message)
	logfile.write(msg_str+"\n")
	logfile.close()
