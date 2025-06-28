import socket
import smart_city_pb2
import time
import random
import threading

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
GATEWAY_IP = '127.0.0.1'
TEMP_SENSOR_PORT = 5000  # Porta para mandar as informações do sensor de temperatura
AIR_SENSOR_PORT = 5002  # Porta para mandar as informações do sensor de qualidade do ar

def send_discovery_message(device_type, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    discovery_message = smart_city_pb2.DiscoveryMessage()
    discovery_message.device_type = device_type
    discovery_message.ip_address = "127.0.0.1"  # Substitua pelo IP real se não for localhost
    discovery_message.port = port

    message = discovery_message.SerializeToString()

    try:
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        print(f"Mensagem de descoberta enviada para {MCAST_GRP}:{MCAST_PORT} ({device_type})")
    except Exception as e:
        print(f"Erro ao enviar mensagem multicast: {e}")
    finally:
        sock.close()

def send_temperature_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        temperature_data = smart_city_pb2.TemperatureSensorData()
        temperature_data.sensor_id = "temp_sensor123"
        temperature_data.temperature = round(random.uniform(20.0, 30.0), 1)
        temperature_data.timestamp = int(time.time())

        message = temperature_data.SerializeToString()

        try:
            sock.sendto(message, (GATEWAY_IP, TEMP_SENSOR_PORT))
            print(f"Temperatura enviada: {temperature_data.temperature}")
        except Exception as e:
            print(f"Erro ao enviar dados de temperatura: {e}")

        time.sleep(5)

def send_air_quality_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        air_quality_data = smart_city_pb2.AirQualitySensorData()
        air_quality_data.sensor_id = "air_sensor456"
        air_quality_data.carbon_monoxide = round(random.uniform(0.0, 5.0), 2)
        air_quality_data.particulate_matter = round(random.uniform(0.0, 100.0), 2)
        air_quality_data.timestamp = int(time.time())

        message = air_quality_data.SerializeToString()

        try:
            sock.sendto(message, (GATEWAY_IP, AIR_SENSOR_PORT))
            print(f"Qualidade do ar enviada: CO={air_quality_data.carbon_monoxide}, PM={air_quality_data.particulate_matter}")
        except Exception as e:
            print(f"Erro ao enviar dados de qualidade do ar: {e}")

        time.sleep(7)  # Intervalo diferente para não coincidir com a temperatura

if __name__ == "__main__":
    #envia a mensagem de descoberta para cada tipo de sensor
    send_discovery_message("TEMPERATURE_SENSOR", TEMP_SENSOR_PORT)
    send_discovery_message("AIR_QUALITY_SENSOR", AIR_SENSOR_PORT)

    #inicia as threads dos sensores
    threading.Thread(target=send_temperature_data).start()
    threading.Thread(target=send_air_quality_data).start()