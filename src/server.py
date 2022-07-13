import json
from threading import Thread
from datetime import datetime

from paho.mqtt.client import Client


class Server():
    
    def __init__(self, topic: str, topics: list = []):
        self._broker = 'broker.emqx.io'
        self._port = 1883
        self._server_id = topic
        self._topics = topics
        self._server = Client(self._server_id)
        self.timestamp = datetime.now().timestamp()
        self.isRequesting = False
    
    def getTimestamp(self):
        return self.timestamp
    
    def connect_mqtt(self) -> Client:
        """Conecta o servidor mqtt, publica e se inscreve nos topicos iniciais

        Returns:
            Client: Cliente MQTT
        """
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Servidor iniciado! {self._server_id}")
            else:
                print("Falha ao se conectar, codigo de retorno: ", rc)
        
        self._server.on_connect = on_connect
        self._server.connect(self._broker, self._port)
        self._server.publish(self._server_id)
        for topic in self._topics:
            print("Inscreveu-se no topico: ", topic+"#")
            self._server.subscribe(topic+"#") #se inscreve numa lista de topicos
        return self._server
    
    def enviarDados(self, topic: str, msg: dict):
        """Envia mensagens no formato json para determinado topico

        Args:
            topic (str): topico de destino
            msg (dict): mensagem a convertida em json e enviada

        Raises:
            Exception: Retorna um erro para o caso do envio falhar
        """
        try:
            msg = json.dumps(msg).encode("utf-8")
            result = self._server.publish(topic, msg)
            if result[0] != 0:
                raise Exception("Mensagem não enviada para o topico "+"'"+topic+"'")
        except Exception as ex:
            print(ex)
            
    def run(self):
        """"Metodo que inicia o servidor MQTT
        """
        self._server = self.connect_mqtt()
        Thread(target=self.receberDados).start()