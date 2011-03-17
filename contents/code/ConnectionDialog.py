from PyQt4.Qt import SIGNAL, QObject, Qt
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from Server import *

from const import *

class ConnectionDialog(KDialog):
	def __init__(self, parent, isEdit):
		KDialog.__init__(self, parent)
		self.parent = parent
		self.isEdit = isEdit
		
		layout = QVBoxLayout(self.mainWidget())
		
		informationBox = KButtonGroup(self)
		informationBox.setTitle("Server information")
		if self.isEdit:
			self.oldName = ""
		self.name = KLineEdit()
		QObject.connect(self.name, SIGNAL("editingFinished()"), self.nameFinished)
		self.hostIP = KLineEdit()
		self.port = KIntNumInput(22)
		self.login = KLineEdit()
		self.switches = KLineEdit()
		self.passCheckbox = QCheckBox("Password")
		QObject.connect(self.passCheckbox, SIGNAL("stateChanged(int)"), self.passwordChecked)
		self.keyCheckbox = QCheckBox("Private Key")
		QObject.connect(self.keyCheckbox, SIGNAL("stateChanged(int)"), self.keyChecked)
		self.password = KLineEdit()
		self.password.setPasswordMode(True)
		self.password.setEnabled(False)
		self.keyFilePath = KLineEdit()
		self.keyFilePath.setEnabled(False)
		self.browseButton = KPushButton("Browse")
		self.browseButton.setEnabled(False)
		QObject.connect(self.browseButton, SIGNAL("clicked()"), self.openFileDialog)
		
		informationBoxLayout = QGridLayout(informationBox)
		informationBoxLayout.addWidget(QLabel("Name:"), 0, 0)
		informationBoxLayout.addWidget(self.name, 0, 1)
		
		informationBoxLayout.addWidget(QLabel("Host/IP:"), 1, 0)
		informationBoxLayout.addWidget(self.hostIP, 1, 1)
		
		informationBoxLayout.addWidget(QLabel("Port:"), 2, 0)
		informationBoxLayout.addWidget(self.port, 2, 1)
		
		informationBoxLayout.addWidget(QLabel("Login:"), 3, 0)
		informationBoxLayout.addWidget(self.login, 3, 1)
		
		informationBoxLayout.addWidget(QLabel("SSH command line:"), 4, 0)
		informationBoxLayout.addWidget(self.switches, 4, 1)
		
		authenticationBox = KButtonGroup(self)
		authenticationBox.setTitle("Authentication")
		authenticationBoxLayout = QGridLayout(authenticationBox)
		authenticationBoxLayout.addWidget(self.passCheckbox, 0, 0)
		authenticationBoxLayout.addWidget(self.password, 0, 1)
		authenticationBoxLayout.addWidget(self.keyCheckbox, 1, 0)
		authenticationBoxLayout.addWidget(self.keyFilePath, 1, 1)
		authenticationBoxLayout.addWidget(self.browseButton, 1, 2)
		
		layout.addWidget(informationBox)
		layout.addWidget(authenticationBox)
		
		self.enableButtonOk(False)
		QObject.connect(self, SIGNAL("okClicked()"), self.saveSettings)
		
	def nameFinished(self):
		try:
			self.parent.applet.servers.keys().index(self.name.originalText())
			self.enableButtonOk(False)
		except ValueError:
			self.enableButtonOk(True)
		
	def passwordChecked(self, state):
		if (state == Qt.Checked):
			self.password.setEnabled(True)
			self.keyCheckbox.setCheckState(Qt.Unchecked)
		else:
			self.password.setEnabled(False)
	
	def keyChecked(self, state):
		if (state == Qt.Checked):
			self.keyFilePath.setEnabled(True)
			self.browseButton.setEnabled(True)
			self.passCheckbox.setCheckState(Qt.Unchecked)
		else:
			self.keyFilePath.setEnabled(False)
			self.browseButton.setEnabled(False)
	
	def openFileDialog(self):
		self.keyFilePath.setText(QFileDialog.getOpenFileName(self, "Select private key"))
	
	def saveSettings(self):
		server = Server()
		server.setName(self.name.originalText())
		server.setHostIP(self.hostIP.originalText())
		server.setPort(str(self.port.value()))
		server.setSwitches(str(self.switches.originalText()))
		server.setLogin(self.login.originalText())
		if (Qt.Checked == self.passCheckbox.checkState()):
			server.setAuthenticationType(AUTH_TYPE_PASSWORD)
			server.setPassword(self.password.originalText())
		elif (Qt.Checked == self.keyCheckbox.checkState()):
			server.setAuthenticationType(AUTH_TYPE_PRIVATE_KEY)
			server.setKeyPath(self.keyFilePath.originalText())
		else:
			server.setAuthenticationType(AUTH_TYPE_NONE)
			
		if self.isEdit:
			self.parent.saveServer(self.oldName, server)
		else:
			self.parent.addServer(server)
