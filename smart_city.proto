syntax = "proto3";

package smart_city;

message TemperatureSensorData {
  string sensor_id = 1;
  float temperature = 2;
  int64 timestamp = 3;
}

message AirQualitySensorData {
  string sensor_id = 1;
  float carbon_monoxide = 2;
  float particulate_matter = 3;
  int64 timestamp = 4;
}

message ActuatorCommand {
  string device_id = 1;
  string command = 2; // "ON", "OFF", "SET_VALUE"
  string value = 3; // Valor para SET_VALUE
}

message DeviceStatus {
    string device_id = 1;
    string status = 2; //"ON", "OFF", "IDLE", "ERROR"
}

message DiscoveryMessage {
    string device_type = 1; // "TEMPERATURE_SENSOR", "AIR_QUALITY_SENSOR", "LAMP", etc.
    string ip_address = 2;
    int32 port = 3;
}