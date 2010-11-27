from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from ConfigurationPages import *
from Server import *
import subprocess
import os

from const import *

class EasySSHConnection(plasmascript.Applet):

	def __init__(self, parent, args=None):
		plasmascript.Applet.__init__(self, parent)
		
	def init(self):
		self.wallet = KWallet.Wallet(0,  KWALLET_NAME)
		
		self.setHasConfigurationInterface(True)
		
		self.svg = Plasma.IconWidget()
		self.svg.setSvg(self.package().filePath("images", "ssh.svg"))
		
		self.layout = QGraphicsLinearLayout(Qt.Horizontal, self.applet)
		
		QObject.connect(self.svg, SIGNAL("clicked()"), self.showPopup)
		
		self.layout.addItem(self.svg)
		self.applet.setLayout(self.layout)
		self.resize(32, 32)
		
		self.servers = {}
		self.readServersData()
	
	def readServersData(self):
		config = self.getConfig()
		if config.hasGroupImpl(CONFIG_SERVERS):
			configServers = config.groupImpl(CONFIG_SERVERS)
			list = configServers.groupList()
			if (list.count() > 0):
				for i in range(list.count()):
					serverData = KConfigGroup(configServers, list.__getitem__(i))
					
					server = Server()
					server.setName(list.__getitem__(i))
					server.setHostIP(serverData.readEntry(SERVER_DATA_HOST_IP))
					server.setPort(serverData.readEntry(SERVER_DATA_PORT))
					server.setLogin(serverData.readEntry(SERVER_DATA_LOGIN))
					server.setSwitches(serverData.readEntry(SERVER_DATA_SWITCHES))
					server.setAuthenticationType(serverData.readEntry(SERVER_DATA_AUTHENTICATION_TYPE))
					if server.authenticationType == AUTH_TYPE_PRIVATE_KEY:
						server.setKeyPath(serverData.readEntry(AUTH_TYPE_PRIVATE_KEY))
					elif server.authenticationType == AUTH_TYPE_PASSWORD:
						if not self.wallet.isOpen():
							self.openWallet()
						passwd = self.wallet.readPassword(server.name)
						if passwd[0] == 0:
							server.setPassword(passwd[1])
					
					self.addServer(server)
	
	def showPopup(self):
		self.generateServerList().exec_(QCursor.pos())
		
	def generateServerList(self):
		menu = QMenu()
		self.actionGroup = QActionGroup(self)
		QObject.connect(self.actionGroup, SIGNAL("triggered(QAction*)"), self.openSSHConnection)
		for name, server in self.servers.iteritems():
			action = QAction(name, self)
			action.setData(name)
			menu.addAction(action)
			self.actionGroup.addAction(action)
		
		return menu
	
	def openSSHConnection(self, action):
		server = self.servers[action.data().toString()]
		command = "ssh " + server.switches + " -p " + str(server.port) + " " + server.hostIP
		if server.login != "":
			command += " -l " + server.login
		if server.authenticationType == AUTH_TYPE_PASSWORD and server.password != "":
			subprocess.Popen(str("konsole --new-tab -e python " + str(self.package().filePath("scripts", "runPassword.py")) + " '"+command+"' '"+server.password+"'"), shell=True)
		elif server.authenticationType == AUTH_TYPE_PRIVATE_KEY:
			command += " -i " + server.keyPath
			subprocess.Popen(str("konsole --new-tab -e " + command), shell=True)
		else:
			subprocess.Popen(str("konsole --new-tab -e " + command), shell=True)
	
	def getConfig(self):
		return KConfig(self.package().filePath("config", "main.rc"), KConfig.SimpleConfig)
	
	def showConfigurationInterface(self):
		self.dlg = KDialog()
		self.dlg.setCaption("Easy SSH Connection Settings")
		self.page = ServerListPage(self, self.dlg)
		self.dlg.setMainWidget(self.page)
		self.dlg.show()
        
        def openWallet(self):
		list = KWallet.Wallet.walletList()
		walletName = list.first()
		if list.count() == 0:
			walletName = KWALLET_NAME
		self.wallet = KWallet.Wallet.openWallet(walletName, 0)
		if not self.wallet.hasFolder(KWALLET_FOLDER):
			self.wallet.createFolder(KWALLET_FOLDER)
		self.wallet.setFolder(KWALLET_FOLDER)
        	
	def addServer(self, server):
		self.servers[server.name] = server
		self.saveServers()
	
	def removeServer(self, name):
		if self.servers[name].authenticationType == AUTH_TYPE_PASSWORD:
			self.removePasswordFromWallet(name)
		del self.servers[name]
		self.saveServers()
		
	def saveServer(self, name, server):
		if self.servers[name].authenticationType == AUTH_TYPE_PASSWORD:
			self.removePasswordFromWallet(name)
		del self.servers[name]
		self.addServer(server)
	
	def removePasswordFromWallet(self, name):
		if not self.wallet.isOpen():
			self.openWallet()
		self.wallet.removeEntry(name)
	
	def saveServers(self):
		config = self.getConfig()
		if config.hasGroupImpl(CONFIG_SERVERS):
			config.groupImpl(CONFIG_SERVERS).deleteGroup()
		for name, server in self.servers.iteritems():
			serversConfig = config.groupImpl(CONFIG_SERVERS)
			servers1 = KConfigGroup(serversConfig, name)
			servers1.writeEntry(SERVER_DATA_HOST_IP, server.hostIP)
			servers1.writeEntry(SERVER_DATA_PORT,  server.port)
			servers1.writeEntry(SERVER_DATA_LOGIN,  server.login)
			servers1.writeEntry(SERVER_DATA_SWITCHES,  server.switches)
			servers1.writeEntry(SERVER_DATA_AUTHENTICATION_TYPE,  server.authenticationType)
			if server.authenticationType == AUTH_TYPE_PASSWORD:
				if not self.wallet.isOpen():
					self.openWallet()
				self.wallet.writePassword(server.name.replace(" ", "_"), str(server.password))
			elif server.authenticationType == AUTH_TYPE_PRIVATE_KEY:
				servers1.writeEntry(SERVER_DATA_KEY_PATH,  server.keyPath)

def CreateApplet(parent):
	return EasySSHConnection(parent)
