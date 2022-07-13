from src.client import Cliente


class Adm(Cliente):

    def __init__(self):
        Cliente.__init__(self, "adm", "setor")
        self.__lixeiras = []
   
    def getLixeiras(self) -> list:
        """Retorna todas as lixeiras no sistema
        
        Resturns:
            list: lista de lixeiras
        """
        return self.__lixeiras
   
    def getLixeirasByNumber(self, number: int) -> list:
        """Retorna a quantidade de lixeiras exigida
        Args:
            number (int): numero de lixeiras a ser retornado
        Returns:
            list: lista de lixeiras
        """
        number = int(number)
        # after subscribed, retrieve data from topic /lixeiras and limit by number
        if  number >= 0 and number <= len(self.__lixeiras):
            return self.__lixeiras[:number]
        return self.__lixeiras
    
    def getLixeiraByID(self, id: str) -> dict:
        """Busca uma lixera pelo id
        Args:
            id (str): id da lixera
        Returns:
            dict: dicionario contendo as informacoes de determinada lixeira 
        """
        # after subscribed, retrieve data from topic /lixeiras/id and return
        for l in self.__lixeiras:
            if id in l['id']:
                return l
        return {}
        
    def receberDados(self):
        """Recebe a mensagem do servidor e realiza ações
        """
        while True:
            try:
                super().receberDados()
                if 'dados' in self._msg:
                    # print(self._msg)
                    self.__lixeiras = self._msg.get('dados')
            except Exception as ex:
                print("Erro ao receber dados => ", ex)
                break
            
    def run(self):
        """"Metodo que inicia o servidor MQTT
        """
        super().run()
        self._client_mqtt.subscribe('setor/adm/lixeiras')