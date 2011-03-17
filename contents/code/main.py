from PyKDE4.plasma import Plasma
from PyQt4.Qt import QObject
from PyKDE4 import plasmascript
from PyKDE4.kdecore import *
from ConfigurationPages import *
from Server import *
import subprocess

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
		self.selectedServer = ""
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
					
					self.servers[server.name] = server

	def showPopup(self):
		self.generateServerList().exec_(QCursor.pos())

	def generateServerList(self):
		menu = QMenu()
		self.actionGroup = QActionGroup(self)
		QObject.connect(self.actionGroup, SIGNAL("triggered(QAction*)"), self.openSubMenu)
		slist = self.servers.keys()
		slist.sort()
		for s in slist:
			server = self.servers[s]
			action = QAction(server.name, self)
			action.setData(server.name)
			menu.addAction(action)
			self.actionGroup.addAction(action)

		return menu

	def openSubMenu(self, action):
		self.selectedServer = action.data().toString()
		subMenu = QMenu()
		subActionGroup = QActionGroup(self)
		QObject.connect(subActionGroup, SIGNAL("triggered(QAction*)"), self.openSSHConnection)

		action = QAction("new tab", self)
		action.setData(0)
		subMenu.addAction(action)
		subActionGroup.addAction(action)

		action = QAction("new window", self)
		action.setData(1)
		subMenu.addAction(action)
		subActionGroup.addAction(action)

		subMenu.exec_(QCursor.pos())

	def openSSHConnection(self, action):
		newTab = "--new-tab"
		if bool(int(action.data().toString())):
			newTab = ""
		
		server = self.servers[self.selectedServer]
		if server.authenticationType == AUTH_TYPE_PASSWORD:
			self.openWallet()
			passwd = self.wallet.readPassword(server.name)
			if passwd[0] == 0:
				server.setPassword(passwd[1])

		command = "ssh " + server.switches + " -p " + str(server.port) + " " + server.hostIP
		if server.login != "":
			command += " -l " + server.login
		if server.authenticationType == AUTH_TYPE_PASSWORD and server.password != "":
			subprocess.Popen(str("konsole " + newTab + " -e python " + str(self.package().filePath("scripts", "runPassword.py")) + " '"+command+"' '"+server.password+"'"), shell=True)
		elif server.authenticationType == AUTH_TYPE_PRIVATE_KEY:
			command += " -i " + server.keyPath
			subprocess.Popen(str("konsole " + newTab + " -e " + command), shell=True)
		else:
			subprocess.Popen(str("konsole " + newTab + " -e " + command), shell=True)

	def getConfig(self):
		return KConfig(self.package().filePath("config", "main.rc"), KConfig.SimpleConfig)

	def showConfigurationInterface(self):
		self.dlg = KDialog()
		self.dlg.setCaption(SETTINGS_DIALOG)
		self.page = ServerListPage(self, self.dlg)
		self.dlg.setMainWidget(self.page)
		self.dlg.show()

	def openWallet(self):
		if not self.wallet.isOpen():
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
				self.openWallet()
				self.wallet.writePassword(server.name.replace(" ", "_"), str(server.password))
			elif server.authenticationType == AUTH_TYPE_PRIVATE_KEY:
				servers1.writeEntry(SERVER_DATA_KEY_PATH,  server.keyPath)

def CreateApplet(parent):
	return EasySSHConnection(parent)
