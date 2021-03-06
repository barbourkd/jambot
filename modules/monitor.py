from jambot import botModule
#Monitor Module
class moduleClass(botModule):
	def on_start(self, c, e):
		pass

	def on_pubmsg(self, c, e):
		print("Public msg:")
		print(vars(e))

	def on_send(self, chan, msg, modulename):
		print("Sent msg to " + chan + " from " + modulename + ":")
		print(msg)

	def on_event(self, c, e):
		print("Channel Event:")
		print(vars(e))

	def do_command(self, c, e, command, args, admin):
		pass

	def on_privmsg(self, c, e):
		print("Private Event:")
		print(vars(e))

	def on_shutdown(self):
		print("Shutting down...")
