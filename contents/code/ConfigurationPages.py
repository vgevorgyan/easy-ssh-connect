from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from ConnectionDialog import *

from const import *

class ServerListPage(QWidget):
	def __init__(self, applet, parent=None):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.applet = applet
		self.init()
		
	def init(self):
		self.layout = QHBoxLayout()

		self.serversList = KListWidget(self.parent)
		QObject.connect(self.serversList, SIGNAL("itemSelectionChanged()"), self.serverSelected)
		QObject.connect(self.serversList, SIGNAL("doubleClicked(QListWidgetItem*, const QPoint&)"), self.showEditDialog)
		
		self.refreshServersList()
		self.buttonsLayout = QVBoxLayout()
		self.buttonsLayout.setAlignment(Qt.AlignTop)

		self.addButton = KPushButton("Add")
		QObject.connect(self.addButton, SIGNAL("clicked()"), self.showAddDialog)

		self.editButton = KPushButton("Edit")
		self.editButton.setEnabled (False)
		QObject.connect(self.editButton, SIGNAL("clicked()"), self.showEditDialog)

		self.removeButton = KPushButton("Remove")
		self.removeButton.setEnabled (False)
		QObject.connect(self.removeButton, SIGNAL("clicked()"), self.removeServer)

		self.buttonsLayout.addWidget(self.addButton)
		self.buttonsLayout.addWidget(self.editButton)
		self.buttonsLayout.addWidget(self.removeButton)

		self.layout.addWidget(self.serversList)
		self.layout.addLayout(self.buttonsLayout)

		self.setLayout(self.layout)
	
	def refreshServersList(self):
		self.serversList.clear()
		for name, server in self.applet.servers.iteritems():
			self.serversList.addItem(name)
		
	def removeServer(self):
		self.applet.removeServer(self.serversList.currentItem().text())
		self.refreshServersList()

	def serverSelected(self):
		self.editButton.setEnabled(True)
		self.removeButton.setEnabled(True)
		
	def showAddDialog(self):
		addDialog = ConnectionDialog(self, False)
		addDialog.setCaption(NEW_DIALOG)
		addDialog.show()
		
	def showEditDialog(self, item, pos):
		self.showEditDialog()
	
	def showEditDialog(self):
		server = self.applet.servers[self.serversList.currentItem().text()]
		editDialog = ConnectionDialog(self, True)
		editDialog.setCaption(EDIT_DIALOG)
		editDialog.name.setText(server.name)
		editDialog.oldName = server.name
		if not server.port == "":
			editDialog.port.setValue(int(server.port))
		editDialog.login.setText(server.login)
		editDialog.switches.setText(server.switches)
		editDialog.hostIP.setText(server.hostIP)
		if server.authenticationType == AUTH_TYPE_PASSWORD:
			editDialog.passCheckbox.setCheckState(Qt.Checked)
			editDialog.password.setText(server.password)
		elif server.authenticationType == AUTH_TYPE_PRIVATE_KEY:
			editDialog.keyCheckbox.setCheckState(Qt.Checked)
			editDialog.keyFilePath.setText(server.keyPath)
		editDialog.enableButtonOk(True)
		editDialog.show()
	
	def addServer(self, server):
		self.applet.addServer(server)
		self.refreshServersList()
	
	def saveServer(self, name, server):
		self.applet.saveServer(name, server)
		self.refreshServersList()
		
