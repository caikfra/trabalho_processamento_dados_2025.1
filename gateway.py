import socket  # Importa o módulo para comunicação de rede (sockets)
import threading  # Importa o módulo para trabalhar com threads (execução paralela)
import smart_city_pb2  # Importa o módulo gerado pelo Protocol Buffers, que contém as definições das mensagens
import struct  # Importa o módulo para trabalhar com estruturas de dados binárias
import time  # Importa o módulo para trabalhar com tempo

HOST = '127.0.0.1'  # Define o endereço IP do servidor (Gateway). '127.0.0.1' é o localhost (a própria máquina)
PORT = 65432  # Define a porta do servidor TCP
MCAST_GRP = '224.1.1.1'  # Define o endereço multicast para descoberta de dispositivos
MCAST_PORT = 5007  # Define a porta multicast
TEMP_SENSOR_PORT = 5000  # Define a porta para receber dados do sensor de temperatura
AIR_SENSOR_PORT = 5002  # Define a porta para receber dados do sensor de qualidade do ar
RECONNECT_DELAY = 5  # Tempo para tentar reconectar (segundos)

# Dicionário para armazenar informações sobre os dispositivos descobertos
devices = {}

class ClientThread(threading.Thread):
    """
    Classe para lidar com a conexão de um cliente TCP em uma thread separada.
    """
    def __init__(self, conn, addr):
        """
        Inicializa a thread do cliente.

        Args:
            conn: O socket da conexão.
            addr: O endereço do cliente.
        """
        threading.Thread.__init__(self)
        self.conn = conn  # Salva o socket da conexão
        self.addr = addr  # Salva o endereço do cliente
        print(f"Nova conexão de: {addr}")  # Exibe uma mensagem de nova conexão

    def run(self):
        """
        Executa a thread do cliente.
        Recebe dados do cliente, desserializa o comando e envia para a lâmpada (se for o caso).
        """
        try:
            while True:  # Loop infinito para receber dados do cliente
                data = self.conn.recv(1024)  # Recebe até 1024 bytes de dados do cliente
                if not data:  # Se não houver dados, a conexão foi fechada
                    print(f"Conexão com {self.addr} fechada")  # Exibe uma mensagem de conexão fechada
                    break  # Sai do loop

                # Desserializar o comando
                try:
                    command = smart_city_pb2.ActuatorCommand()  # Cria uma instância da mensagem ActuatorCommand
                    command.ParseFromString(data)  # Desserializa a string de bytes para a mensagem
                    print(f"Comando recebido de {self.addr}: {command}")  # Exibe o comando recebido

                    # Enviar comando para a lampada
                    if command.device_id == "LAMP":  # Se o comando for para a lâmpada
                        send_command_to_lamp(command)  # Envia o comando para a lâmpada

                except Exception as e:  # Captura qualquer exceção que ocorra durante a desserialização ou envio
                    print(f"Erro ao desserializar o comando: {e}")  # Exibe uma mensagem de erro

        except Exception as e:  # Captura qualquer exceção que ocorra na thread do cliente
            print(f"Erro na thread do cliente: {e}")  # Exibe uma mensagem de erro
        finally:
            self.conn.close()  # Fecha a conexão

def send_command_to_lamp(command):
    """
    Envia um comando para a lâmpada usando UDP.

    Args:
        command: A mensagem ActuatorCommand a ser enviada.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP

    try:
        lamp_ip = devices["LAMP"]["ip_address"]  # Obtém o endereço IP da lâmpada do dicionário
        lamp_port = devices["LAMP"]["port"]  # Obtém a porta da lâmpada do dicionário

        message = command.SerializeToString()  # Serializa o comando para enviar pela rede
        sock.sendto(message, (lamp_ip, lamp_port))  # Envia a string de bytes para a lâmpada
        print(f"Comando enviado para a lamp: {command.command}")  # Exibe uma mensagem de sucesso
    except Exception as e:  # Captura qualquer exceção que ocorra durante o envio
        print(f"Erro ao enviar comando para a lamp: {e}")  # Exibe uma mensagem de erro

def multicast_listener():
    """
    Ouve por mensagens multicast para descobrir dispositivos na rede.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Cria um socket UDP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar o endereço
        sock.bind((MCAST_GRP, MCAST_PORT))  # Associa o socket ao endereço multicast

        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)  # Cria uma estrutura para o endereço multicast
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)  # Adiciona o socket ao grupo multicast

        print(f"Ouvindo multicast em {MCAST_GRP}:{MCAST_PORT}")  # Exibe uma mensagem de que está ouvindo

        while True:  # Loop infinito para receber mensagens multicast
            try:
                data, addr = sock.recvfrom(1024)  # Recebe até 1024 bytes de dados
                try:
                    discovery_message = smart_city_pb2.DiscoveryMessage()  # Cria uma instância da mensagem DiscoveryMessage
                    discovery_message.ParseFromString(data)  # Desserializa a string de bytes para a mensagem
                    print(f"Dispositivo descoberto: {discovery_message} de {addr}")  # Exibe a mensagem de descoberta

                    # Armazenar informações sobre o dispositivo
                    devices[discovery_message.device_type] = {  # Armazena as informações do dispositivo no dicionário
                        "ip_address": discovery_message.ip_address,  # Salva o endereço IP
                        "port": discovery_message.port  # Salva a porta
                    }

                except Exception as e:  # Captura qualquer exceção que ocorra durante a desserialização
                    print(f"Erro ao processar mensagem multicast: {e}")  # Exibe uma mensagem de erro
            except Exception as e:  # Captura qualquer exceção que ocorra ao receber a mensagem
                print(f"Erro ao receber mensagem multicast: {e}")  # Exibe uma mensagem de erro
    except Exception as e:  # Captura qualquer exceção que ocorra ao iniciar o listener multicast
        print(f"Erro ao iniciar multicast listener: {e}")  # Exibe uma mensagem de erro
    finally:
        sock.close()  # Fecha o socket

def temp_udp_listener():
    """
    Ouve por dados do sensor de temperatura via UDP.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        sock.bind((HOST, TEMP_SENSOR_PORT))  # Associa o socket ao endereço e porta do sensor de temperatura
        print(f"Ouvindo dados de temperatura na porta {TEMP_SENSOR_PORT}")  # Exibe uma mensagem de que está ouvindo

        while True:  # Loop infinito para receber dados
            try:
                data, addr = sock.recvfrom(1024)  # Recebe até 1024 bytes de dados
                temperature_data = smart_city_pb2.TemperatureSensorData()  # Cria uma instância da mensagem TemperatureSensorData
                temperature_data.ParseFromString(data)  # Desserializa a string de bytes para a mensagem
                print(f"Temperatura recebida: {temperature_data.temperature} de {addr}")  # Exibe a temperatura recebida
            except Exception as e:  # Captura qualquer exceção que ocorra durante o recebimento ou processamento dos dados
                print(f"Erro ao processar dados de temperatura: {e}")  # Exibe uma mensagem de erro
    except Exception as e:  # Captura qualquer exceção que ocorra ao iniciar o listener
        print(f"Erro ao iniciar o temp udp listener: {e}")  # Exibe uma mensagem de erro

def air_udp_listener():
    """
    Ouve por dados do sensor de qualidade do ar via UDP.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        sock.bind((HOST, AIR_SENSOR_PORT))  # Associa o socket ao endereço e porta do sensor de qualidade do ar
        print(f"Ouvindo dados de qualidade do ar na porta {AIR_SENSOR_PORT}")  # Exibe uma mensagem de que está ouvindo

        while True:  # Loop infinito para receber dados
            try:
                data, addr = sock.recvfrom(1024)  # Recebe até 1024 bytes de dados
                air_quality_data = smart_city_pb2.AirQualitySensorData()  # Cria uma instância da mensagem AirQualitySensorData
                air_quality_data.ParseFromString(data)  # Desserializa a string de bytes para a mensagem
                print(f"Qualidade do ar recebida: CO={air_quality_data.carbon_monoxide}, PM={air_quality_data.particulate_matter} de {addr}")  # Exibe a qualidade do ar recebida
            except Exception as e:  # Captura qualquer exceção que ocorra durante o recebimento ou processamento dos dados
                print(f"Erro ao processar dados de qualidade do ar: {e}")  # Exibe uma mensagem de erro
    except Exception as e:  # Captura qualquer exceção que ocorra ao iniciar o listener
        print(f"Erro ao iniciar o air udp listener: {e}")  # Exibe uma mensagem de erro

def start_tcp_server():
    """Inicia o servidor TCP para receber comandos dos clientes."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # Cria um socket TCP
            s.bind((HOST, PORT))  # Associa o socket ao endereço e porta
            s.listen()  # Coloca o socket em modo de escuta
            print(f"Gateway ouvindo em {HOST}:{PORT}")  # Exibe uma mensagem de que está ouvindo

            while True:
                try:
                    conn, addr = s.accept()  # Aceita uma nova conexão
                    thread = ClientThread(conn, addr)  # Cria uma thread para lidar com o cliente
                    thread.daemon = True  # Define a thread como daemon (termina quando o programa principal termina)
                    thread.start()  # Inicia a thread
                except Exception as e:  # Captura qualquer exceção que ocorra ao aceitar a conexão
                    print(f"Erro ao aceitar conexão TCP: {e}")  # Exibe uma mensagem de erro
    except Exception as e:  # Captura qualquer exceção que ocorra ao iniciar o servidor TCP
        print(f"Erro ao iniciar o servidor TCP: {e}")  # Exibe uma mensagem de erro

if __name__ == "__main__":
    """Função principal do programa."""
    # Iniciar thread para ouvir o multicast
    multicast_thread = threading.Thread(target=multicast_listener)  # Cria uma thread para o multicast listener
    multicast_thread.daemon = True  # Define a thread como daemon
    multicast_thread.start()  # Inicia a thread

    # Iniciar threads para ouvir os dados dos sensores via UDP
    threading.Thread(target=temp_udp_listener).start()  # Inicia a thread para o sensor de temperatura
    threading.Thread(target=air_udp_listener).start()  # Inicia a thread para o sensor de qualidade do ar

    # Iniciar o servidor TCP
    start_tcp_server()  # Inicia o servidor TCP