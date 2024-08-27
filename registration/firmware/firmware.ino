#include <ArduinoJson.h>
#include <CertStoreBearSSL.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServerSecure.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266mDNS.h>
#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>

#include <time.h>

#ifndef STASSID
#define APSSID "VioletOxygen"
#define APPSK "enterthenetlab"
#endif

#define INFLUXDB_URL "<Put IP addr here>"
#define INFLUXDB_TOKEN                                                                             \
    "<Put token here>"
#define INFLUXDB_ORG "<Put org here>"
#define INFLUXDB_BUCKET "<Put bucket here>"
#define TZ_INFO "MST7MDT,M3.2.0,M11.1.0"

const char DEVICE_ID[] = "banana";
static String STA_SSID;
static String STA_PASSWD;
static String sesh_id;
static String pub_IP;
InfluxDBClient *db_client;
Point sensor("wifi_status");
const char *ssid = APSSID;
const char *password = APPSK;

BearSSL::ESP8266WebServerSecure serverHTTPS(443);
ESP8266WebServer server(80);

const int led = LED_BUILTIN;

const String postForms = "<html>\
  <head>\
    <title>VioletOxygen Setup</title>\
    <style>\
      body { background-color: #f0d6ff; font-family: Arial, Helvetica, Sans-Serif; Color: #000088; }\
    </style>\
  </head>\
  <body>\
    <h1>VioletOxygen</h1><br>\
    <p> To connect to the Internet, please enter your WiFi credentials </p>\
    <form method=\"post\" enctype=\"application/json\" action=\"/setup/\">\
      <input type=\"text\" name=\"ssid\" placeholder=\"WiFi Network\"><br>\
      <input type=\"password\" name=\"pass\" placeholder=\"Password\"><br>\
      <button type=\"submit\">Submit</button>\
    </form>\
  </body>\
</html>";

const String reg_complete = "<html>\
  <head>\
    <title>VioletOxygen Setup</title>\
    <style>\
      body { background-color: #f0d6ff; font-family: Arial, Helvetica, Sans-Serif; Color: #000088; }\
    </style>\
  </head>\
  <body>\
    <h1>Registration Complete</h1><br>\
    <p> Your device is now submitting info to the VioletOxygen Map! Any time you unplug your VioletOxygen device, you will need to re-register it again. You may now close this window. </p>\
  </body>\
</html>";

const char cert_le1[] PROGMEM = R"CERT(
<Put cert here>
)CERT";

const char cert_le2[] PROGMEM = R"CERT(
<Put cert here>
)CERT";

static const char serverCert[] PROGMEM = R"EOF(
<Put cert here>
)EOF";

static const char serverKey[] PROGMEM = R"EOF(
<Put cert here>
)EOF";

String getDeviceURI() {
    // DEVICE_ID will most likely be stored in flash or EEPROM memory to make it more secure
    // For the meantime it is a global const

    // code to fetch DEVICE_ID from FS

    String prefix = "/location_verification/register/";
    return prefix + DEVICE_ID;
}

// Set time via NTP, as required for x.509 validation
void setClock() {
    configTime(3 * 3600, 0, "pool.ntp.org", "time.nist.gov");

    Serial.print("Waiting for NTP time sync: ");
    time_t now = time(nullptr);
    while (now < 8 * 3600 * 2) {
        delay(500);
        Serial.print(".");
        now = time(nullptr);
    }
    Serial.println("");
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    Serial.print("Current time: ");
    Serial.print(asctime(&timeinfo));
}

void GetExternalIP() {
    WiFiClient client;
    if (!client.connect("api.ipify.org", 80)) {
        Serial.println("Failed to connect with 'api.ipify.org' !");
    } else {
        int timeout = millis() + 5000;
        client.print("GET /?format=text HTTP/1.1\r\nHost: api.ipify.org\r\n\r\n");
        while (client.available() == 0) {
            if (timeout - millis() < 0) {
                Serial.println(">>> Client Timeout !");
                client.stop();
                return;
            }
        }
        // end of ipify inquiry

        int nbytes; // number of characters waiting from Ipify
        int ii;     // just counter for char read

        while ((nbytes = client.available()) > 0) {
            char *IpifyReply = (char *)malloc(nbytes + 1); // allocate memory for reply string
            for (ii = 0; ii < nbytes; ii++)                // read char by char from reply
            {
                IpifyReply[ii] = client.read();
            }
            IpifyReply[ii] = 0; // add end of string

            while (IpifyReply[--nbytes] != 10) {
            }

            // assign new (moved) pointer to new global ptr pointing last string from input.
            // PublIP has been declared anywhere outside function/procedure to be global as
            // String PublIP; // pointer to global externalIP string
            pub_IP = IpifyReply + nbytes +
                     1; // +1 beacuse when found points to LF an should for next char
            free(IpifyReply);
        }
    }
}

void handleRoot() {
    digitalWrite(led, 1);
    server.send(200, "text/html", postForms);
    digitalWrite(led, 0);
}

void handleForm() {

    if (server.method() != HTTP_POST) {
        digitalWrite(led, 1);
        server.send(405, "text/plain", "Method Not Allowed");
        digitalWrite(led, 0);
    } else {
        digitalWrite(led, 1);
        String message = "POST form was:\n";
        for (uint8_t i = 0; i < server.args(); i++) {
            message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
            Serial.print("Name: ");
            Serial.println(server.argName(i));
            Serial.print("Arg: ");
            Serial.println(server.arg(i));
            if (server.argName(i) == "ssid") {
                Serial.print("SSID: ");
                Serial.println(server.arg(i));
                STA_SSID = server.arg(i);
            }
            if (server.argName(i) == "pass") {
                Serial.print("Password: ");
                Serial.println(server.arg(i));
                STA_PASSWD = server.arg(i);
            }
        }
        // WiFi.disconnect(true);
        WiFi.begin(STA_SSID, STA_PASSWD);
        while (WiFi.status() != WL_CONNECTED) {
            delay(100);
            Serial.print(".");
        }
        Serial.println("Connected");

        setClock();

        BearSSL::WiFiClientSecure *clientSec = new BearSSL::WiFiClientSecure();
        BearSSL::X509List trustedRoots;

        trustedRoots.append(cert_le1);
        trustedRoots.append(cert_le2);
        clientSec->setTrustAnchors(&trustedRoots);

        Serial.println(WiFi.localIP());

        HTTPClient http;
        http.begin(*clientSec, "aq.byu.edu", 443, getDeviceURI().c_str(), true);
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");
        http.POST("id=" + sesh_id);

        String res = http.getString();

        if (res == "Registration complete!") {
            server.send(200, "text/html", reg_complete);
            db_client = new InfluxDBClient(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET,
                                           INFLUXDB_TOKEN, InfluxDbCloud2CACert);
            sensor.addTag("device", DEVICE_ID);
            sensor.addTag("SSID", WiFi.SSID());
            timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");

            // Check server connection
            if (db_client->validateConnection()) {
                Serial.print("Connected to InfluxDB: ");
                Serial.println(db_client->getServerUrl());
            } else {
                Serial.print("InfluxDB connection failed: ");
                Serial.println(db_client->getLastErrorMessage());
            }
        } else {
            server.send(200, "text/html", res);
        }
    }
}

void handleNotFound() {
    Serial.println("not found");
    if (server.method() == HTTP_OPTIONS) {
        server.sendHeader("Access-Control-Allow-Origin", "*");
        server.sendHeader("Access-Control-Max-Age", "10000");
        server.sendHeader("Access-Control-Allow-Methods", "PUT,POST,GET,OPTIONS");
        server.sendHeader("Access-Control-Allow-Headers", "*");
        server.send(204);
    } else {
        server.send(404, "text/plain", "");
    }
    digitalWrite(led, 1);
    String message = "File Not Found\n\n";
    message += "URI: ";
    message += server.uri();
    message += "\nMethod: ";
    message += (server.method() == HTTP_GET) ? "GET" : "POST";
    message += "\nArguments: ";
    message += server.args();
    message += "\n";
    for (uint8_t i = 0; i < server.args(); i++) {
        message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
    }
    server.send(404, "text/plain", message);
    digitalWrite(led, 0);
}

void handleDiscover() {
    Serial.println("DISCOVER");
    Serial.println("########");
    // StaticJsonDocument<200> jsonBuffer;
    // deserializeJson(jsonBuffer, server.arg("plain"));
    // String sesh_id = jsonBuffer["geo_id"];
    // banana = sesh_id;
    // Serial.println(banana);
    sesh_id = server.arg("geo_id");
    Serial.println(sesh_id);
    digitalWrite(led, 1);
    server.sendHeader("Discover", "1");
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.sendHeader("Access-Control-Max-Age", "10000");
    server.sendHeader("Access-Control-Allow-Methods", "PUT,POST,GET,OPTIONS");
    server.sendHeader("Access-Control-Allow-Headers", "*");
    // server.send(200, "text/plain", "{\"status\": \"0\"}");
    // digitalWrite(led, 0);
    handleRoot();
}

void showWebpage() {
    Serial.println("Pong!");
    serverHTTPS.send(200, "text/plain", "");
}

void setup(void) {
    pinMode(led, OUTPUT);
    digitalWrite(led, 0);
    Serial.begin(115200);

    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.println("");

    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(IP);

    if (MDNS.begin("esp8266")) {
        Serial.println("MDNS responder started");
    }

    configTime(3 * 3600, 0, "pool.ntp.org", "time.nist.gov");

    server.on("/", handleRoot);

    server.on("/setup/", handleForm);

    server.on("/discoverDevice", handleDiscover);

    server.onNotFound(handleNotFound);

    server.begin();

    serverHTTPS.getServer().setRSACert(new BearSSL::X509List(serverCert),
                                       new BearSSL::PrivateKey(serverKey));
    serverHTTPS.on("/", showWebpage);

    serverHTTPS.begin();

    Serial.println("HTTP server started");
}

void getStats() {
    Serial.print("ESP.getBootMode(); ");
    Serial.println(ESP.getBootMode());
    Serial.print("ESP.getSdkVersion(); ");
    Serial.println(ESP.getSdkVersion());
    Serial.print("ESP.getBootVersion(); ");
    Serial.println(ESP.getBootVersion());
    Serial.print("ESP.getChipId(); ");
    Serial.println(ESP.getChipId());
    Serial.print("ESP.getFlashChipSize(); ");
    Serial.println(ESP.getFlashChipSize());
    Serial.print("ESP.getFlashChipRealSize(); ");
    Serial.println(ESP.getFlashChipRealSize());
    Serial.print("ESP.getFlashChipSizeByChipId(); ");
    Serial.println(ESP.getFlashChipSizeByChipId());
    Serial.print("ESP.getFlashChipId(); ");
    Serial.println(ESP.getFlashChipId());
    uint32 heap = ESP.getFreeHeap();
    Serial.print("Heap: ");
    Serial.println(heap);
}

void loop(void) {
    server.handleClient();
    serverHTTPS.handleClient();
    MDNS.update();

    if (db_client != NULL) {

        GetExternalIP();
        Serial.println("PUB IP:" + pub_IP);
        // getStats();

        // Store measured value into point
        sensor.clearFields();
        // Report RSSI of currently connected network
        sensor.addField("rssi", WiFi.RSSI());
        sensor.addField("pub_ip", pub_IP);
        // Print what are we exactly writing
        Serial.print("Writing: ");
        Serial.println(db_client->pointToLineProtocol(sensor));

        // Write point
        if (!db_client->writePoint(sensor)) {
            Serial.print("InfluxDB write failed: ");
            Serial.println(db_client->getLastErrorMessage());
        }

        delay(10000);
    }
}
