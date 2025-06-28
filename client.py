import socket
import smart_city_pb2

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Conectado ao Gateway em {HOST}:{PORT}")

    # Criar um comando
    command = smart_city_pb2.ActuatorCommand()
    command.device_id = "lamp123"
    command.command = "ON"
    command.value = ""

    # Serializar o comando
    serialized_command = command.SerializeToString()

    # Enviar o comando
    s.sendall(serialized_command)
    print(f"Comando enviado: {command}")

    # Receber uma resposta (opcional)
    # data = s.recv(1024)
    # print(f"Resposta recebida: {data.decode()}")

print("Conexão fechada")