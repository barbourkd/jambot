#!/usr/bin/env python
import irc.client
import irc.bot
import configparser
import traceback
import importlib
import ssl

# Swampbot modular IRC bot
# by ice at irc.kickinrad.tv


config_file = "swampbot.cfg"

class botModule():
	def _load_settings(self):
		self.config = configparser.ConfigParser()
		self.config.read(config_file)
		if self.name in self.config.sections():
			for key in self.config[self.name]:
				self.settings[key] = self.config[self.name][key]

	def __init__(self, name): 
		self.name = name
		self.settings = {}
		self._load_settings()
		self.initialize()

	def initialize(self):
		pass
	def on_join(self, c, e):
		pass
	def on_kick(self, c, e):
		pass
	def on_mode(self, c, e):
		pass
	def on_welcome(self, c, e):
		pass
	def on_part(self, c, e):
		pass
	def on_ping(self, c, e):
		pass
	def on_privmsg(self, c, e):
		pass
	def on_privnotice(self, c, e):
		pass
	def do_command(self, c, e, command, args, admin):
		pass
	def on_pubmsg(self, c, e):
		pass
	def on_pubnotice(self, c, e):
		pass
	def on_quit(self, c, e):
		pass
	def on_invite(self, c, e):
		pass
	def on_pong(self, c, e):
		pass
	def on_action(self, c, e):
		pass
	def on_topic(self, c, e):
		pass
	def on_nick(self, c, e):
		pass

class botMain(irc.bot.SingleServerIRCBot):
	def _load_settings(self):
		self.config = configparser.ConfigParser()
		self.config.read(config_file)
		self.settings["modules"] = self.config["settings"]["modules"].split()
		self.settings["channels"] = self.config["settings"]["channels"].split()
		self.settings["nickname"] = self.config["settings"]["nickname"]
		self.settings["realname"] = self.config["settings"]["realname"]
		self.settings["serverhost"] = self.config["settings"]["serverhost"]
		self.settings["serverport"] = int(self.config["settings"]["serverport"])
		self.settings["serverpass"] = self.config["settings"]["serverpass"]
		self.settings["server"] = [ irc.bot.ServerSpec(self.settings["serverhost"], self.settings["serverport"], self.settings["serverpass"]) ]
		self.settings["ssl"] = False
		if self.config["settings"]["ssl"]=="True":
			self.settings["ssl"] = True
		self.settings["command_prefix"] = self.config["settings"]["command_prefix"][0]
		self.settings["owner_hosts"] = self.config["settings"]["owner_hosts"].split()
		self.settings["version"] = self.config["settings"]["version"]
		
	def _load_modules(self):
		for module in self.settings["modules"]:
			moduleClass = getattr(importlib.import_module(module), 'moduleClass')
			self.modules.append(moduleClass(module))
			print("Loaded " + module)

	def __init__(self): 
		self.settings = {}
		self.modules = []
		self._load_settings()
		self._load_modules()

	def initialize(self):
		print("Connecting...")
		reactor = irc.connection.Factory()
		if self.settings["ssl"]:
			reactor = irc.connection.Factory(wrapper=ssl.wrap_socket)
		irc.bot.SingleServerIRCBot.__init__(self,self.settings["server"], self.settings["nickname"], self.settings["realname"], connect_factory=reactor)
		print("Connected!")
		self.start()

	def on_error(self, c, e):
		for module in self.modules:
			module.on_error(c, e)

	def on_join(self, c, e):
		for module in self.modules:
			module.on_join(c, e)

	def on_kick(self, c, e):
		for module in self.modules:
			module.on_kick(c, e)

	def on_mode(self, c, e):
		for module in self.modules:
			module.on_mode(c, e)

	def on_welcome(self, c, e):
		for channel in self.settings["channels"]:
			c.join(channel)
		for module in self.modules:
			module.on_welcome(c, e)

	def on_part(self, c, e):
		for module in self.modules:
			module.on_part(c, e)

	def on_ping(self, c, e):
		for module in self.modules:
			module.on_ping(c, e)

	def on_privmsg(self, c, e):
		for module in self.modules:
			module.on_privmsg(c, e)

	def on_privnotice(self, c, e):
		for module in self.modules:
			module.on_privnotice(c, e)

	def on_command(self, c, e):
		command = e.arguments[0].split()[0].split(self.settings["command_prefix"])[1]
		args = e.arguments[0].split()[1:]
		admin = False
		for host in self.settings["owner_hosts"]:
			if e.source.split("@")[1]==host:
				admin = True
		while admin:
			if command=="join":
				for arg in args:
					if arg[0]!="#":
						c.privmsg(e.target, "Invalid channel name")
					else:
						c.privmsg(e.target, "Joining " + arg)
						c.join(arg)
			elif command=="part":
				if len(args)==0:
					c.part(e.target)
				else:
					for arg in args:
						if arg[0]!="#":
							c.privmsg(e.target, "Invalid channel name")
						else:
							c.privmsg(e.target, "Parting " + arg)
							c.part(arg)
			elif command=="nick":
				if args[0].isalnum():
					c.privmsg(e.target, "Setting nick to " + args[0])
					c.nick(args[0])
					self.settings["nickname"]=args[0]
				else:
					c.privmsg(e.target, "Invalid nick (" + args[0]+ ")")
			elif command=="setprefix":
				c.privmsg(e.target, "Setting command prefix to " + args[0][0])
				self.settings["command_prefix"]=args[0][0]
			elif command=="addowner":
				for arg in args:
					if "@" not in arg:
						c.privmsg(e.target, "Invalid host")
					else:
						c.privmsg(e.target, "Adding " + arg + "to owners")
						self.settings["owners"] += " " + arg
			elif command=="quit":
				c.privmsg(e.target, "Quitting...")
				self.shutdown()
			else:
				break
			return
		if command=="version":
			c.privmsg(e.target, "Version: " + self.settings["version"])
		elif command=="say":
			msg = ""
			for arg in args:
				msg += arg + " "
			c.privmsg(e.target, msg)
		else:
			for module in self.modules:
				module.do_command(c, e, command, args, admin)

	def on_pubmsg(self, c, e):
		if e.arguments[0][0]==self.settings["command_prefix"]:
			self.on_command(c, e)
		for module in self.modules:
			module.on_pubmsg(c, e)

	def on_pubnotice(self, c, e):
		for module in self.modules:
			module.on_pubmsg(c, e)

	def on_quit(self, c, e):
		for module in self.modules:
			module.on_quit(c, e)

	def on_invite(self, c, e):
		for module in self.modules:
			module.on_invite(c, e)

	def on_pong(self, c, e):
		for module in self.modules:
			module.on_pong(c, e)

	def on_action(self, c, e):
		for module in self.modules:
			module.on_action(c, e)

	def on_topic(self, c, e):
		for module in self.modules:
			module.on_topic(c, e)

	def on_nick(self, c, e):
		for module in self.modules:
			module.on_nick(c, e)

	def shutdown(self):
		print("Disconnecting...")
		self.die()

if __name__ == "__main__":
	bot = botMain()
	try:
		bot.initialize()
	except KeyboardInterrupt as e:
		bot.shutdown()
	except SystemExit as e:
		bot.shutdown()
	except:
		traceback.print_exc()
	bot.shutdown()


