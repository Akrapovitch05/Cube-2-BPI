#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "SparkFunHTU21D.h"
#include <ArduinoJson.h>

const char* ssid = "alex";
const char* password = "alex1409";
const char* mqtt_server = "192.168.32.58"; // MQTT server IP
const int mqtt_port = 1883; // MQTT server port
const char* flask_server = "192.168.32.58"; // Flask server IP
const int flask_port = 5000; // Flask server port
const String flask_endpoint = "/raspberrypi/temperature"; // Flask endpoint
const String contentType = "application/json";

WiFiClient wifiClient;
PubSubClient client(wifiClient);
HTU21D myHumidity;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(9600);
  Wire.begin(2, 0); // Specify I2C pins
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  myHumidity.begin();
  Serial.println("HTU21D initialized");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  const int numReadings = 5; // Number of readings to average
  float humiditySum = 0.0;
  float temperatureSum = 0.0;

  for (int i = 0; i < numReadings; ++i) {
    float humidity = myHumidity.readHumidity();
    float temperature = myHumidity.readTemperature();
    humiditySum += humidity;
    temperatureSum += temperature;
    delay(1000); // Adjust delay as needed between readings
  }

  float humidityAverage = humiditySum / numReadings;
  float temperatureAverage = temperatureSum / numReadings;

  Serial.print("Average Humidity: ");
  Serial.print(humidityAverage);
  Serial.print(" %\t Average Temperature: ");
  Serial.print(temperatureAverage);
  Serial.println(" *C");

  // Publish data to MQTT server
  client.publish("sensor/temperature", String(temperatureAverage).c_str());
  client.publish("sensor/humidity", String(humidityAverage).c_str());

  // Prepare JSON payload
  StaticJsonDocument<200> jsonPayload;
  jsonPayload["temperature"] = temperatureAverage;
  jsonPayload["humidity"] = humidityAverage;

  // Convert JSON to string
  String jsonString;
  serializeJson(jsonPayload, jsonString);

  // Send HTTP POST request to Flask server
  sendHttpPostRequest(flask_server, flask_port, flask_endpoint, jsonString);

  delay(1000); // Adjust delay as needed
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void sendHttpPostRequest(const String& server, int port, const String& endpoint, const String& payload) {
  WiFiClient client;

  if (!client.connect(server, port)) {
    Serial.println("Connection to server failed");
    return;
  }

  // Send POST request with Content-Type header
  client.print(String("POST ") + endpoint + " HTTP/1.1\r\n" +
               "Host: " + server + "\r\n" +
               "Content-Type: application/json\r\n" + // Specify JSON content type
               "Content-Length: " + payload.length() + "\r\n" +
               "\r\n" +
               payload);

  Serial.println("Request sent to server");
}
