import ScreenCloud, json, urllib2
from PythonQt.QtCore import QSettings, QByteArray, QBuffer, QIODevice, QFile
from PythonQt.QtGui import QWidget, QDialog
from PythonQt.QtUiTools import QUiLoader

class ZapierUploader():
	def __init__(self):
		self.uil = QUiLoader()
		self.loadSettings()

	def loadSettings(self):
		settings = QSettings()
		settings.beginGroup("uploaders")
		settings.beginGroup("zapier")
		self.zapier_url = settings.value("url", "")
		settings.endGroup()
		settings.endGroup()

	def saveSettings(self):
		self.zapier_url = self.settingsDialog.group_url.widget_url.input_url.text
		settings = QSettings()
		settings.beginGroup("uploaders")
		settings.beginGroup("zapier")
		settings.setValue("url", self.zapier_url)
		settings.endGroup()
		settings.endGroup()

	def isConfigured(self):
		return bool(self.zapier_url.strip())

	def getFilename(self):
		return ScreenCloud.formatFilename("screenshot")

	def showSettingsUI(self, parentWidget):
		self.settingsDialog = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
		self.settingsDialog.connect("accepted()", self.saveSettings)
		self.settingsDialog.setWindowTitle("Zapier settings");
		self.settingsDialog.group_url.widget_url.input_url.setText(self.zapier_url)
		self.settingsDialog.adjustSize()
		self.settingsDialog.open()

	def upload(self, screenshot, name):
		ba = QByteArray()
		buf = QBuffer(ba)
		buf.open(QIODevice.WriteOnly)
		screenshot.save( buf, ScreenCloud.getScreenshotFormat() ) #writes image into ba
		buf.close()

		json_data = json.dumps({'image': ba.toBase64().data()})
		request = urllib2.Request(self.zapier_url, json_data, {"Content-Type": "application/json"})
		try:
			reply = urllib2.urlopen(request)
		except Exception as e:
			ScreenCloud.setError("Could not upload to: "+ self.zapier_url + "\n" + e.message)
			return False
		try:
			replyText = reply.read()
			ScreenCloud.setUrl(json.loads(replyText).link)
		except Exception as e:
			ScreenCloud.setError("Could not upload to: "+ self.zapier_url + "\n" + e.message)
			return False
		return True