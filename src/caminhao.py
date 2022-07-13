from time import sleep
from client import Cliente

class Caminhao(Cliente):

    def __init__(self, latitude, longitude, setor):
        self.__latitude = latitude
        self.__longitude = longitude
        self.__capacidade = 10000 #m³
        self.__setor = setor
        self.__lixeiras_coletar = []
        Cliente.__init__(self, "caminhao", "setor")
    
    def getSetor(self):
        return self.__setor
    
    def getLixeirasColetar(self):
        return self.__lixeiras_coletar
    
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
    
    def coletarLixeira(self):
        """
        Esvazia a lixeira
            @param lixeira: Lixera
                lixeira a ser esvaziada
        """ 
        lixeira = self.__lixeiras_coletar.pop(0)
        
        print(f"O Caminhão {self._client_id} está coletando a lixeira {lixeira['id']}")
        
        if self.__capacidade - lixeira.get('qtd_lixo') < 0:
            print("Caminhão cheio! Esvaziando caminhao..")
            sleep(5)  
            self.__capacidade = 10000
        self.__capacidade -= lixeira.get('qtd_lixo')
        self._msg['acao'] = f"{lixeira.get('id')}"

        sleep(5)
        self.enviarDadosTopic('caminhao/')
        self.__latitude = lixeira.get('latitude')
        self.__latitude = lixeira.get('longetude')
        self._msg['acao'] = ''
        self.enviarDadosTopic('caminhao/')
    
    def receberDados(self):
        """Recebe a mensagem do servidor e realiza ações
        """
        while True:
            try:
                super().receberDados()
                self.__lixeiras_coletar = self._msg.get('dados')
                if len(self.__lixeiras_coletar) > 0:
                    self.coletarLixeira()
            except Exception as ex:
                print("Erro ao receber dados => ", ex)
                break

    def run(self):
        """"Metodo que inicia o servidor MQTT
        """
        super().run()
        self._client_mqtt.subscribe('setor/caminhao/listaColeta')
