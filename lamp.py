import socket  # Importa o módulo para comunicação de rede (sockets)
import smart_city_pb2  # Importa o módulo gerado pelo Protocol Buffers (smart_city.proto)
import time  # Importa o módulo para lidar com tempo (e.g., pausas)
import threading  # Importa o módulo para criar threads (execução paralela)

MCAST_GRP = '224.1.1.1'  # Define o endereço multicast para descoberta de dispositivos
MCAST_PORT = 5007  # Define a porta multicast
LAMP_PORT = 5001  # Define a porta para receber comandos na lâmpada
GATEWAY_IP = '127.0.0.1'  # Define o endereço IP do Gateway - localhost
LAMP_STATUS = False  # Define o estado inicial da lâmpada (desligada)

def send_discovery_message():
    """
    Envia uma mensagem multicast para anunciar a presença da lâmpada na rede.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Cria um socket UDP
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)  # Define o TTL para o multicast

        discovery_message = smart_city_pb2.DiscoveryMessage()  # Cria uma instância da mensagem DiscoveryMessage
        discovery_message.device_type = "LAMP"  # Define o tipo de dispositivo como "LAMP"
        discovery_message.ip_address = "127.0.0.1"  # Define o endereço IP da lâmpada
        discovery_message.port = LAMP_PORT  # Define a porta da lâmpada

        message = discovery_message.SerializeToString()  # Converte a mensagem para uma string de bytes

        try:
            sock.sendto(message, (MCAST_GRP, MCAST_PORT))  # Envia a string de bytes para o endereço multicast
            print(f"Mensagem de descoberta enviada para {MCAST_GRP}:{MCAST_PORT} (LAMP)")  # Exibe uma mensagem de sucesso
        except Exception as e:  # Captura qualquer exceção que ocorra durante o envio
            print(f"Erro ao enviar mensagem multicast: {e}")  # Exibe uma mensagem de erro
        finally:
            sock.close()  # Fecha o socket
    except Exception as e:  # Captura qualquer exceção que ocorra ao criar o socket ou preparar a mensagem
        print(f"Erro ao enviar mensagem de descoberta: {e}")  # Exibe uma mensagem de erro

def command_listener():
    """Ouve os comandos enviados pelo Gateway."""
    global LAMP_STATUS  # Permite modificar a variável global LAMP_STATUS
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        sock.bind((GATEWAY_IP, LAMP_PORT))  # Associa o socket ao endereço IP do Gateway e à porta da lâmpada
        print(f"Lamp ouvindo comandos na porta {LAMP_PORT}")  # Exibe uma mensagem de que está ouvindo

        while True:  # Loop infinito para receber comandos
            try:
                data, addr = sock.recvfrom(1024)  # Recebe até 1024 bytes de dados
                command = smart_city_pb2.ActuatorCommand()  # Cria uma mensagem ActuatorCommand (Protocol Buffers)
                command.ParseFromString(data)  # Desserializa os dados recebidos

                if command.device_id == "LAMP":  # Se o comando for para a lâmpada
                    if command.command == "ON":  # Se o comando for para ligar
                        LAMP_STATUS = True  # Define o estado da lâmpada como ligada
                        print("Lampada ligada")  # Exibe mensagem de lâmpada ligada
                    elif command.command == "OFF":  # Se o comando for para desligar
                        LAMP_STATUS = False  # Define o estado da lâmpada como desligada
                        print("Lampada desligada")  # Exibe mensagem de lâmpada desligada
            except Exception as e:  # Captura qualquer exceção que ocorra durante a desserialização ou processamento do comando
                print(f"Erro ao processar comando: {e}")  # Exibe uma mensagem de erro
    except Exception as e:  # Captura qualquer exceção que ocorra ao iniciar o listener de comandos
        print(f"Erro ao iniciar o listener de comandos: {e}")  # Exibe uma mensagem de erro

if __name__ == "__main__":
    """Função principal do programa."""
    send_discovery_message()  # Envia a mensagem de descoberta multicast

    # Iniciar thread para ouvir comandos
    threading.Thread(target=command_listener).start()  # Inicia uma thread para ouvir os comandos