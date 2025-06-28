import socket
import smart_city_pb2
import time
import threading

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
LAMP_PORT = 5001  # Porta para o lamp
GATEWAY_IP = '127.0.0.1' #IP do Gateway
LAMP_STATUS = False #Status inicial da lampada

def send_discovery_message():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    discovery_message = smart_city_pb2.DiscoveryMessage()
    discovery_message.device_type = "LAMP"
    discovery_message.ip_address = "127.0.0.1"  # Substitua pelo IP real se não for localhost
    discovery_message.port = LAMP_PORT

    message = discovery_message.SerializeToString()

    try:
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        print(f"Mensagem de descoberta enviada para {MCAST_GRP}:{MCAST_PORT} (LAMP)")
    except Exception as e:
        print(f"Erro ao enviar mensagem multicast: {e}")
    finally:
        sock.close()

def command_listener():
    global LAMP_STATUS
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((GATEWAY_IP, LAMP_PORT))  # Use o IP do Gateway e a porta da LAMP
    print(f"Lamp ouvindo comandos na porta {LAMP_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            command = smart_city_pb2.ActuatorCommand()
            command.ParseFromString(data)

            if command.device_id == "LAMP":
                if command.command == "ON":
                    LAMP_STATUS = True
                    print("Lampada ligada")
                elif command.command == "OFF":
                    LAMP_STATUS = False
                    print("Lampada desligada")
        except Exception as e:
            print(f"Erro ao processar comando: {e}")

if __name__ == "__main__":
    send_discovery_message()

    # Iniciar thread para ouvir comandos
    threading.Thread(target=command_listener).start()