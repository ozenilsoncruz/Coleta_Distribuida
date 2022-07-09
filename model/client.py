import json
import random
import string
from threading import Thread

from paho.mqtt.client import Client

_BROKER = 'test.mosquitto.org'
_PORT = 1883

class Cliente: 
    
    def __init__(self, type: str, topic: str ="", topicPublish: list = []):
        self._client_id = f'{type}/'+"".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))+'/'
        self._topic = topic+'/'+self._client_id
        self._topicsPublish = topicPublish
        self._msg = {'dados': '', 'acao': ''}
        self._client_mqtt = Client(self._client_id)
    
    def connect_mqtt(self) -> Client:
        """Conecta o servidor mqtt, publica e se inscreve nos topicos iniciais

        Returns:
            Client: Cliente MQTT
        """
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Conectado ao Broker!")
            else:
                print("Falha ao se conectar, código de erro: %d\n", rc)
        self._client_mqtt.on_connect = on_connect
        self._client_mqtt.connect(_BROKER, _PORT)
        print("Increveu-se no topico", self._topic)
        self._client_mqtt.subscribe(self._topic)
        self._client_mqtt.publish(self._topic)
        # for topic in self._topicsPublish:
        #     self._client_mqtt.publish(topic)
            
        return self._client_mqtt

    def receberDados(self):
        """Recebe as mensagens para atualizar dos topicos para o qual se inscreveu
        """
        def on_message(client, userdata, msg):
            mensagem = msg.payload
            if mensagem:
                self._msg = json.loads(mensagem)
                return mensagem
            
        self._client_mqtt.on_message = on_message
        self._client_mqtt.loop_start()
    
    def enviarDadosTopic(self, topic):
        """Envia mensagens no formato json para determinado topico

        Args:
            topic (str): topico de destino
            msg (dict): mensagem a convertida em json e enviada

        Raises:
            Exception: Retorna um erro para o caso do envio falhar
        """
        try:
            msg = json.dumps(self._msg).encode("utf-8")
            result = self._client_mqtt.publish(topic, msg)
            if result[0] != 0:
                raise Exception("Mensagem não enviada para o topico "+"'"+topic+"'")
        except Exception as ex:
            print(ex)
            
    def enviarDados(self):
        """Envia mensagens no formato json para determinado topico
        
        Raises:
            Exception: Retorna um erro para o caso do envio falhar
        """
        try:
            msg = json.dumps(self._msg).encode("utf-8")
            print("Enviando mensagem para", self._topic)
            result = self._client_mqtt.publish(self._topic, msg)
            if result[0] != 0:
                raise Exception("Mensagem não enviada para o topico "+"'"+self._topic+"'")
        except Exception as ex:
            print(ex)

    def run(self):
        """"Metodo que inicia o servidor MQTT
        """
        self._client_mqtt = self.connect_mqtt()
        Thread(target=self.receberDados).start()
        
