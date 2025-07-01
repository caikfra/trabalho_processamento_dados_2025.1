import socket  # Importa o módulo para comunicação de rede (sockets)
import smart_city_pb2  # Importa o módulo gerado pelo Protocol Buffers (smart_city.proto)
import time  # Importa o módulo para lidar com tempo (e.g., pausas)
import random  # Importa o módulo para gerar números aleatórios
import threading  # Importa o módulo para criar threads (execução paralela)

MCAST_GRP = '224.1.1.1'  # Define o endereço multicast para descoberta de dispositivos
MCAST_PORT = 5007  # Define a porta multicast
GATEWAY_IP = '127.0.0.1'  # Define o endereço IP do Gateway
TEMP_SENSOR_PORT = 5000  # Define a porta para enviar dados do sensor de temperatura
AIR_SENSOR_PORT = 5002  # Define a porta para enviar dados do sensor de qualidade do ar

def send_discovery_message(device_type, port):
    """
    Envia uma mensagem multicast para anunciar a presença do sensor na rede.

    Args:
        device_type: O tipo de dispositivo ("TEMPERATURE_SENSOR" ou "AIR_QUALITY_SENSOR").
        port: A porta para onde o Gateway deve enviar comandos para o dispositivo.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Cria um socket UDP
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)  # Define o TTL para o multicast

    discovery_message = smart_city_pb2.DiscoveryMessage()  # Cria uma instância da mensagem DiscoveryMessage
    discovery_message.device_type = device_type  # Define o tipo de dispositivo
    discovery_message.ip_address = "127.0.0.1"  # Define o endereço IP do sensor
    discovery_message.port = port  # Define a porta do sensor

    message = discovery_message.SerializeToString()  # Serializa a mensagem para enviar pela rede

    try:
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))  # Envia a mensagem para o grupo multicast
        print(f"Mensagem de descoberta enviada para {MCAST_GRP}:{MCAST_PORT} ({device_type})")  # Exibe mensagem de sucesso
    except Exception as e:
        print(f"Erro ao enviar mensagem multicast: {e}")  # Exibe mensagem de erro ao enviar multicast
    finally:
        sock.close()  # Fecha o socket

def send_temperature_data():
    """
    Envia dados de temperatura aleatórios para o Gateway periodicamente.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP

    while True:  # Loop infinito para enviar dados periodicamente
        temperature_data = smart_city_pb2.TemperatureSensorData()  # Cria uma instância da mensagem TemperatureSensorData
        temperature_data.sensor_id = "temp_sensor123"  # Define o ID do sensor
        temperature_data.temperature = round(random.uniform(20.0, 30.0), 1)  # Gera uma temperatura aleatória entre 20 e 30 graus
        temperature_data.timestamp = int(time.time())  # Define o timestamp atual

        message = temperature_data.SerializeToString()  # Converte a mensagem para uma string de bytes

        try:
            sock.sendto(message, (GATEWAY_IP, TEMP_SENSOR_PORT))  # Envia a string de bytes para o Gateway
            print(f"Temperatura enviada: {temperature_data.temperature}")  # Exibe a temperatura enviada
        except Exception as e:  # Captura qualquer exceção que ocorra durante o envio
            print(f"Erro ao enviar dados de temperatura: {e}")  # Exibe mensagem de erro ao enviar dados

        time.sleep(5)  # Espera 5 segundos antes de enviar o próximo dado

def send_air_quality_data():
    """
    Envia dados de qualidade do ar aleatórios para o Gateway periodicamente.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP

    while True:  # Loop infinito para enviar dados periodicamente
        air_quality_data = smart_city_pb2.AirQualitySensorData()  # Cria uma instância da mensagem AirQualitySensorData
        air_quality_data.sensor_id = "air_sensor456"  # Define o ID do sensor
        air_quality_data.carbon_monoxide = round(random.uniform(0.0, 5.0), 2)  # Gera um valor aleatório para o monóxido de carbono
        air_quality_data.particulate_matter = round(random.uniform(0.0, 100.0), 2)  # Gera um valor aleatório para o material particulado
        air_quality_data.timestamp = int(time.time())  # Define o timestamp atual

        message = air_quality_data.SerializeToString()  # Converte a mensagem para uma string de bytes

        try:
            sock.sendto(message, (GATEWAY_IP, AIR_SENSOR_PORT))  # Envia a string de bytes para o Gateway
            print(f"Qualidade do ar enviada: CO={air_quality_data.carbon_monoxide}, PM={air_quality_data.particulate_matter}")  # Exibe os dados enviados
        except Exception as e:  # Captura qualquer exceção que ocorra durante o envio
            print(f"Erro ao enviar dados de qualidade do ar: {e}")  # Exibe mensagem de erro ao enviar dados

        time.sleep(7)  # Espera 7 segundos antes de enviar o próximo dado

if __name__ == "__main__":
    """Função principal do programa."""
    # envia a mensagem de descoberta para cada tipo de sensor
    send_discovery_message("TEMPERATURE_SENSOR", TEMP_SENSOR_PORT)  # Envia mensagem de descoberta para o sensor de temperatura
    send_discovery_message("AIR_QUALITY_SENSOR", AIR_SENSOR_PORT)  # Envia mensagem de descoberta para o sensor de qualidade do ar

    # inicia as threads dos sensores
    threading.Thread(target=send_temperature_data).start()  # Inicia a thread para enviar dados de temperatura
    threading.Thread(target=send_air_quality_data).start()  # Inicia a thread para enviar dados de qualidade do ar