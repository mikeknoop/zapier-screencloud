import json
import requests
import ScreenCloud

from PythonQt.QtCore import QFile, QSettings, QBuffer, QIODevice, QByteArray
from PythonQt.QtUiTools import QUiLoader


class ZapierUploader():

    def __init__(self):
        self.uil = QUiLoader()
        self.loadSettings()

    def isConfigured(self):
        self.loadSettings()
        return bool(self.zapier_url.strip())

    def getFilename(self):
        return ScreenCloud.formatFilename("screenshot")

    def showSettingsUI(self, parentWidget):
        self.parent_widget = parentWidget
        self.settings_widget = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
        self.settings_widget.connect("accepted()", self.saveSettings)
        self.settings_widget.setWindowTitle("Zapier settings")
        self.settings_widget.group_url.widget_url.input_url.setText(self.zapier_url)
        self.settings_widget.adjustSize()
        self.settings_widget.open()

    def upload(self, screenshot, name):
        q_byte_array = QByteArray()
        q_buffer = QBuffer(q_byte_array)
        q_buffer.open(QIODevice.WriteOnly)
        screenshot.save(q_buffer, ScreenCloud.getScreenshotFormat()) # writes image to byte array
        q_buffer.close()

        json_data = json.dumps({'image': str(q_byte_array.toBase64())})
        #f = open('/tmp/zapier', 'w')
        #f.write("{}\n{}\n\n".format(self.zapier_url, json_data))
        #f.close()
        response = requests.post(url=self.zapier_url,
                                 data=json_data,
                                 headers={'Content-Type': 'application/json'})

        try:
            response.raise_for_status()
        except Exception as e:
            ScreenCloud.setError("Could not upload to: " + self.zapier_url + "\n" + e.message)
            return False

        try:
            ScreenCloud.setUrl(response.json()['link'])
        except Exception as e:
            ScreenCloud.setError("Upload to {} worked, but response was invalid: {}\n{}".format(self.zapier_url, response.content, e.message))
            return False

        return True

    def loadSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("zapier")
        self.zapier_url = settings.value("url", "")
        settings.endGroup()
        settings.endGroup()

    def saveSettings(self):
        self.zapier_url = self.settings_widget.group_url.widget_url.input_url.text
        settings = QSettings()

        settings.beginGroup("uploaders")
        settings.beginGroup("zapier")
        settings.setValue("url", self.zapier_url)
        settings.endGroup()
        settings.endGroup()
