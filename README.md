# Smart City Simulator

## Descrição

Este projeto foi desenvolvido como parte da disciplina de Sistemas Distribuídos/Distribuição de Processos e Dados da Universidade Federal do Ceará (UFC). O objetivo principal é consolidar os conhecimentos sobre sistemas distribuídos, explorando conceitos como comunicação entre processos (sockets TCP e UDP), serialização de dados (Protocol Buffers) e descoberta de serviços (Multicast UDP).

O sistema simula uma cidade inteligente, composta por um Gateway central, dispositivos inteligentes (sensores de temperatura e qualidade do ar, e uma lâmpada) e um Cliente para controle e monitoramento.

## Arquitetura

O sistema é composto pelos seguintes componentes principais:

* **Gateway:** Atua como o ponto central da cidade inteligente. Recebe dados dos sensores, controla os atuadores e se comunica com o Cliente.
* **Sensores (Temperatura e Qualidade do Ar):** Simulam dispositivos que coletam dados do ambiente e enviam para o Gateway.
* **Lâmpada:** Simula um atuador que pode ser controlado pelo Cliente através do Gateway.
* **Cliente:** Permite ao usuário monitorar os sensores e controlar a lâmpada.

## Arquivos

O projeto é composto pelos seguintes arquivos:

* `client.py`: Implementa o cliente que permite interagir com o Gateway e controlar a lâmpada.
* `gateway.py`: Implementa o Gateway, que recebe dados dos sensores, controla a lâmpada e se comunica com o cliente.
* `lamp.py`: Simula o comportamento da lâmpada, recebendo comandos do Gateway.
* `sensor.py`: Simula os sensores de temperatura e qualidade do ar, enviando dados para o Gateway.
* `smart_city.proto`: Define as mensagens Protocol Buffers usadas para a comunicação entre os componentes.
* `requirements.txt`: Lista as dependências do projeto (pacotes Python).

## Tecnologias Utilizadas

* **Python:** Linguagem de programação utilizada para implementar todos os componentes.
* **Sockets (TCP e UDP):** Mecanismos para comunicação entre processos.
* **Protocol Buffers:** Formato para serialização e troca de mensagens.
* **Multicast UDP:** Protocolo para descoberta de serviços na rede.

## Execução

Para executar o sistema, siga os seguintes passos:

Observação: sistema linux Ubuntu.

1. **Clone o repositório:**
    ```bash
    git clone [URL do seu repositório]
    ```

2. **Crie um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    ```

3. **Ative o ambiente virtual:**
    ```bash
    source .venv/bin/activate
    ```

4. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5. **Execute os componentes (em terminais separados):**

    * Gateway: `python gateway.py`
    * Sensor: `python sensor.py`
    * Lampada: `python lamp.py`
    * Cliente: `python client.py`

## Contribuições

* Caik Franco
* Adílio Juvêncio
* Maria Karoline
