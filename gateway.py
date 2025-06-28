import socket
import threading
import smart_city_pb2
import struct

HOST = '127.0.0.1'
PORT = 65432
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
TEMP_SENSOR_PORT = 5000  # Porta para mandar as informações do sensor de temperatura
AIR_SENSOR_PORT = 5002  # Porta para mandar as informações do sensor de qualidade do ar

# Dicionário para armazenar informações sobre os dispositivos descobertos
devices = {}

class ClientThread(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        print(f"Nova conexão de: {addr}")

    def run(self):
        while True:
            data = self.conn.recv(1024)
            if not data:
                print(f"Conexão com {self.addr} fechada")
                break

            # Desserializar o comando
            try:
                command = smart_city_pb2.ActuatorCommand()
                command.ParseFromString(data)
                print(f"Comando recebido de {self.addr}: {command}")

                # Enviar comando para a lampada
                if command.device_id == "LAMP":
                    send_command_to_lamp(command)

            except Exception as e:
                print(f"Erro ao desserializar o comando: {e}")

        self.conn.close()

def send_command_to_lamp(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        lamp_ip = devices["LAMP"]["ip_address"]
        lamp_port = devices["LAMP"]["port"]

        message = command.SerializeToString()
        sock.sendto(message, (lamp_ip, lamp_port))
        print(f"Comando enviado para a lamp: {command.command}")
    except Exception as e:
        print(f"Erro ao enviar comando para a lamp: {e}")

def multicast_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MCAST_GRP, MCAST_PORT))

    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Ouvindo multicast em {MCAST_GRP}:{MCAST_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            discovery_message = smart_city_pb2.DiscoveryMessage()
            discovery_message.ParseFromString(data)
            print(f"Dispositivo descoberto: {discovery_message} de {addr}")

            # Armazenar informações sobre o dispositivo
            devices[discovery_message.device_type] = {
                "ip_address": discovery_message.ip_address,
                "port": discovery_message.port
            }

        except Exception as e:
            print(f"Erro ao processar mensagem multicast: {e}")

def temp_udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, TEMP_SENSOR_PORT))
    print(f"Ouvindo dados de temperatura na porta {TEMP_SENSOR_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            temperature_data = smart_city_pb2.TemperatureSensorData()
            temperature_data.ParseFromString(data)
            print(f"Temperatura recebida: {temperature_data.temperature} de {addr}")
        except Exception as e:
            print(f"Erro ao processar dados de temperatura: {e}")

def air_udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, AIR_SENSOR_PORT))
    print(f"Ouvindo dados de qualidade do ar na porta {AIR_SENSOR_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            air_quality_data = smart_city_pb2.AirQualitySensorData()
            air_quality_data.ParseFromString(data)
            print(f"Qualidade do ar recebida: CO={air_quality_data.carbon_monoxide}, PM={air_quality_data.particulate_matter} de {addr}")
        except Exception as e:
            print(f"Erro ao processar dados de qualidade do ar: {e}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Gateway ouvindo em {HOST}:{PORT}")

    # Iniciar thread para ouvir o multicast
    multicast_thread = threading.Thread(target=multicast_listener)
    multicast_thread.start()

    # Iniciar threads para ouvir os dados dos sensores via UDP
    threading.Thread(target=temp_udp_listener).start()
    threading.Thread(target=air_udp_listener).start()

    while True:
        conn, addr = s.accept()
        thread = ClientThread(conn, addr)
        thread.start()