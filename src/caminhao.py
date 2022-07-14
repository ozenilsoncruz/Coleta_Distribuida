import json
from random import randint
from threading import Thread
from time import sleep
from client import Cliente
from flask import Flask, render_template


class Caminhao(Cliente):

    def __init__(self, latitude, longitude, id):
        self.__latitude = latitude
        self.__longitude = longitude
        self.__capacidade = 10000 #m³
        self.__lixeiras_coletar = []
        self._msg = {'acao': '', 'dados':{'caminhao': '', 'lixeiras': ''}}
        Cliente.__init__(self, id, "caminhao", f"setor/{id}")
     
    def getLixeiras(self) -> list:
        """Retorna todas as lixeiras no sistema
        
        Resturns:
            list: lista de lixeiras
        """
        return self.__lixeiras_coletar
   
    def getLixeirasByNumber(self, number: int) -> list:
        """Retorna a quantidade de lixeiras exigida
        Args:
            number (int): numero de lixeiras a ser retornado
        Returns:
            list: lista de lixeiras
        """
        number = int(number)
        # after subscribed, retrieve data from topic /lixeiras and limit by number
        if  number >= 0 and number <= len(self.__lixeiras_coletar):
            return self.__lixeiras_coletar[:number]
        return self.__lixeiras_coletar
    
    def getLixeiraByID(self, id: str) -> dict:
        """Busca uma lixera pelo id
        Args:
            id (str): id da lixera
        Returns:
            dict: dicionario contendo as informacoes de determinada lixeira 
        """
        # after subscribed, retrieve data from topic /lixeiras/id and return
        for l in self.__lixeiras_coletar:
            if id in l['id']:
                return l
        return {}
    
    def dadosCaminhao(self) -> dict:
        """Informacoes da lixeira

        Returns:
            dict: informacoes da lixeira
        """
        return {
            "id": self._client_id,
            "latitude": self.__latitude, 
            "longitude": self.__longitude
        }
    
    def enviarDadosSetor(self):
        """Envia dados para o setor que pertence solicitando mais lixeiras
        """
        self._msg['acao'] = 'REQUEST'
        self._msg['dados']['caminhao'] = self.dadosCaminhao()
        
        idSetor = self._client_id.split('/')
        idSetor = idSetor[1]
        self.enviarDadosTopic(f'setor/{idSetor}/{self._client_id}')
        
    def coletarLixeira(self):
        """
        Esvazia a lixeira
            @param lixeira: Lixera
                lixeira a ser esvaziada
        """ 
        for lixeira in self.__lixeiras_coletar:            
            print(f"O Caminhão {self._client_id} está coletando a lixeira {lixeira['id']}")
            
            if self.__capacidade - lixeira.get('qtd_lixo') < 0:
                print("Caminhão cheio! Esvaziando caminhao..")
                sleep(5)  
                self.__capacidade = 10000
            self.__capacidade -= lixeira.get('qtd_lixo')
            
            #enviando msg para a lixeira
            idSetor = self._client_id.split('/')
            idSetor = idSetor[1]

            self._msg['acao'] = 'esvaziar'
            self.enviarDadosTopic(f"setor/{idSetor}/caminhao/{lixeira.get('id')}")
            
            #altera a localizacao do caminhao
            self.__latitude = lixeira.get('latitude')
            self.__longitude = lixeira.get('longitude')
            #aguarda 5 segundos ate coletar uma nova lixeira
            sleep(2)
        
        self.enviarDadosSetor()
    
    def receberDados(self):
        """Recebe a mensagem do servidor e realiza ações
        """
        while True:
            try:
                super().receberDados()
                if self._msg.get('dados') != None and self._msg.get('dados') != '' and self._msg.get('dados').get('lixeiras') != None and self._msg.get('dados').get('lixeiras') != '':
                    self.__lixeiras_coletar = self._msg.get('dados').get('lixeiras')
                    if self.__lixeiras_coletar != None and len(self.__lixeiras_coletar) > 0:
                        self.coletarLixeira()
                if len(self.__lixeiras_coletar) == 0:
                    self.enviarDadosSetor()
                    
            except Exception as ex:
                print("Erro ao receber dados => ", ex)
                break
            
    def run(self):
        """"Metodo que inicia o servidor MQTT
        """
        super().run()
        
        idSetor = self._client_id.split('/')
        idSetor = idSetor[1]
        
        self._client_mqtt.subscribe(f'setor/{idSetor}/{self._client_id}listaColeta')
 
listaCaminhoes = []        
for i in range (1):    
    listaCaminhoes.append(Caminhao(latitude=(i+1)*randint(1, 2000), longitude=(i+1)*randint(1, 2000), id=i+1))
    listaCaminhoes[i].run()


app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
    return 'Tudo ok'

########## ROTAS LIXEIRA ##########
# @app.route('Caminhao/<idCaminhao>/lixeiras/<number>', methods=['GET'])
# def getLixeirasByNumber(idCaminhao: int,number: int):
#     try:
#         c = listaCaminhoes[idCaminhao-1]
#         lixeiras = c.getLixeirasByNumber(number)
#         return str(lixeiras)
#     except Exception as ex:
#         return f"Erro: {ex}"

# @app.route('Caminhao/<idCaminhao>/lixeira/<id>', methods=['GET'])
# def getLixeiraByID(idCaminhao: int, id):
#     try:
#         c = listaCaminhoes[idCaminhao-1]
#         lixeiras = c.getLixeiraByID(id)
#         return str(lixeiras)
#     except Exception as ex:
#         return f"Erro: {ex}"
# ########## ROTAS LIXEIRA ##########

# app.run()
