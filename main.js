loadQtBindings("qt.core", "qt.gui","qt.network");
include("json2.js");

var settingsWidget = loadUiFile("settings.ui");
settingsWidget.accepted.connect(saveSettings);

function init()
{
    settings.beginGroup("uploaders");
    settings.beginGroup("zapier");
    ScreenCloud.setConfigured(JSON.parse(settings.value("configured", false)));
    zapier_url = settings.value("url", "");
    settings.endGroup();
    settings.endGroup();
}
function loadSettings()
{
    settings.beginGroup("uploaders");
    settings.beginGroup("zapier");
    ScreenCloud.setConfigured(JSON.parse(settings.value("configured", false)));
    zapier_url = settings.value("url", "");
    settings.endGroup();
    settings.endGroup();

    if(isBlankOrEmpty(zapier_url))
    {
        configured = false;
    }else
    {
        configured = true;
    }

    ScreenCloud.setConfigured(configured);
    ScreenCloud.setFilename("screenshot.png");

}
function saveSettings()
{
    zapier_url = settingsWidget.group_url.widget_url.input_url.text
    configured = !isBlankOrEmpty(zapier_url);

    settings.beginGroup("uploaders");
    settings.beginGroup("zapier");
    settings.setValue("configured", configured);
    ScreenCloud.setConfigured(configured);
    settings.setValue("url", zapier_url);
    settings.endGroup();
    settings.endGroup();
}
function setupSettingsUi(preferencesDialog)
{
    loadSettings();
    settingsWidget.setWindowTitle("Zapier settings");
    updateSettingsUi();
    settingsWidget.exec();
}
function updateSettingsUi()
{
    settingsWidget.group_url.widget_url.input_url.setText(zapier_url);
}
function qb2String(qbytearray) {
  var result = "";
  for (var i = 0; i < qbytearray.length(); i++) {
    result += String.fromCharCode(qbytearray.at(i));
  }
  return result;
}
function isBlank(str) {
    return (!str || /^\s*$/.test(str));
}
function isEmpty(str) {
    return (!str || 0 === str.length);
}
function isBlankOrEmpty(str)
{
    return isBlank(str) || isEmpty(str);
}
function upload(screenshot)
{
    var net = new QNetworkAccessManager();

    var ba = new QByteArray();
    var buffer = new QBuffer( ba );
    buffer.open(QIODevice.WriteOnly);
    screenshot.save( buffer, format ); // writes image into ba
    buffer.close();

    var url = new QUrl(zapier_url);
    var request = new QNetworkRequest(url);
    var json = new QByteArray(JSON.stringify({image: qb2String(ba.toBase64())}));
    request.setRawHeader("Content-Type", "application/json");
    request.setRawHeader("Content-Length", json.length);
    var reply = net.post(request, json);

    reply.error.connect(function(networkError) { queryError = true; });
    reply.finished.connect(function(reply) { queryFinished = true; });

    queryFinished = false;
    queryError = false;
    var eventLoop = new QEventLoop();
    while (!queryFinished) {
       eventLoop.processEvents(QEventLoop.WaitForMoreEvents);
    }
    var replyText = qb2String(reply.readAll());
    if(queryError)
    {
        return ScreenCloud.error("Could not upload to: "+zapier_url);
    }
    try
    {
        var json = JSON.parse(replyText);
        link = json.link;
        ScreenCloud.finished(link);
    }
    catch(e)
    {
        ScreenCloud.finished("");
    }
}
