import socket  # Importa o módulo para comunicação de rede (sockets)
import time  # Importa o módulo para lidar com tempo (e.g., pausas)
import smart_city_pb2  # Importa o módulo gerado pelo Protocol Buffers (smart_city.proto), que contém as definições das mensagens

HOST = '127.0.0.1'  # Define o endereço IP do servidor (Gateway). '127.0.0.1' é o localhost (a própria máquina)
PORT = 65432  # Define a porta do servidor (Gateway)
RECONNECT_DELAY = 5  # Define o tempo (em segundos) para esperar antes de tentar reconectar ao servidor

def send_command(command_value):
    """
    Envia um comando para o Gateway para ligar ou desligar a lâmpada.

    Args:
        command_value: Uma string, "ON" para ligar a lâmpada ou "OFF" para desligar.
    """
    while True:  # Loop infinito para tentar reconectar em caso de falha
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # Cria um socket TCP (confiável)
                try:
                    s.connect((HOST, PORT))  # Tenta conectar ao Gateway
                    print(f"Conectado ao Gateway em {HOST}:{PORT}")  # Exibe uma mensagem de sucesso

                    # Criar um comando
                    command = smart_city_pb2.ActuatorCommand()  # Cria uma instância da mensagem ActuatorCommand
                    command.device_id = "LAMP"  # Define o ID do dispositivo como "LAMP" (lâmpada)
                    command.command = command_value  # Define o comando como "ON" ou "OFF" (ligar ou desligar)
                    command.value = ""  # Define o valor (não usado neste caso, poderia ser usado para definir a intensidade da luz)

                    # Serializar o comando
                    serialized_command = command.SerializeToString()  # Converte a mensagem para uma string de bytes (para enviar pela rede)

                    # Enviar o comando
                    s.sendall(serialized_command)  # Envia a string de bytes para o Gateway
                    print(f"Comando enviado: {command.command}")  # Exibe uma mensagem de sucesso
                    break  # Sai do loop se a conexão e o envio forem bem-sucedidos

                except Exception as e:  # Captura qualquer exceção que ocorra durante a conexão ou envio
                    print(f"Erro ao conectar/enviar comando: {e}. Tentando novamente em {RECONNECT_DELAY} segundos...")  # Exibe uma mensagem de erro
                    time.sleep(RECONNECT_DELAY)  # Espera um tempo antes de tentar novamente

        except Exception as e:  # Captura qualquer exceção que ocorra fora do bloco 'with'
            print(f"Erro geral na função send_command: {e}")  # Exibe uma mensagem de erro

    print("Conexão fechada")  # Exibe uma mensagem quando a conexão é fechada

if __name__ == "__main__":
    """
    Função principal do programa.
    Loop infinito para receber comandos do usuário e enviá-los para o Gateway.
    """
    while True:  # Loop infinito para receber comandos do usuário
        try:
            comando = input("Digite 'ON' para ligar a lâmpada ou 'OFF' para desligar: ").upper()  # Solicita um comando ao usuário e converte para maiúsculas
            if comando == "ON" or comando == "OFF":  # Verifica se o comando é válido
                send_command(comando)  # Envia o comando para o Gateway
            else:
                print("Comando inválido. Digite 'ON' ou 'OFF'.")  # Exibe uma mensagem de erro se o comando for inválido
        except KeyboardInterrupt:  # Captura a interrupção do teclado (Ctrl+C)
            print("\nSaindo...")  # Exibe uma mensagem de saída
            break  # Sai do loop