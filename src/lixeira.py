from time import sleep
from client import Cliente
from random import randint
from threading import Thread

class Lixeira(Cliente):

    def __init__(self, id, latitude, longitude, id_setor):
        Cliente.__init__(self, id, type='lixeira', topic=f'setor/{id_setor}')
        self.__latitude = latitude
        self.__longitude = longitude
        self.__capacidade = 100 #m³
        self.__bloqueado = False
        self.__lixo = 0
        self.__porcentagem = 0
        self.__reservado = False
        self._msg['acao'] = 'iniciar'
        
    def dadosLixeira(self):
        """Informacoes da lixeira
        Returns:
            dict: informacoes da lixeira
        """
        if(self.__bloqueado == True):
            status = "Bloqueada"
        else:
            status = "Desbloqueada"

        return {
            "id": self._client_id,
            "latitude": self.__latitude, 
            "longitude": self.__longitude, 
            "status": status, 
            "qtd_lixo": self.__lixo,
            "capacidade": self.__capacidade, 
            "porcentagem": f'{self.__porcentagem:,.3f}'+'%',
            "reservado": self.__reservado
        }
    
    def addLixo(self, lixo: int):
        """Adiciona lixo na lixeira até o permitido
        
        Args
            lixo: int
                quantidade de lixo adiconada
                
        Returns: 
            boolean: retorna True se conseguir adionar lixo
        """
        if(self.__capacidade >= self.__lixo + lixo): #se a capacidade de lixo nao for excedida, o lixo é adicionado
            self.__lixo += lixo
            self.__porcentagem = self.__lixo/self.__capacidade*100
            if(self.__capacidade == self.__lixo): #se a capacidade de lixo chegar ao limite, o lixo e bloqueado
                self.__bloqueado = True
            self._msg['dados'] = self.dadosLixeira()
            self._msg['acao'] = ''
            self.enviarDados()
    
    def esvaziarLixeira(self):
        """Redefine a quantidade de lixo dentro da lixeira
        """
        if(self.__bloqueado == True):
            self.__bloqueado = False
        self.__lixo = 0
        self.__porcentagem = 0
        self.__reservado = False

        #retorna nova informacao sobre o objeto
        self._msg['dados'] = self.dadosLixeira()
        self._msg['acao'] = ''
        
        self.enviarDados()
        
        print(f"Lixeira {self._client_id} ESVAZIADA")
    
    def bloquear(self):
        """Trava a porta da lixeira
        """  
        if(self.__bloqueado == False):
            self.__bloqueado = True
            self._msg['dados'] = self.dadosLixeira()
            self._msg['acao'] = ''
            self.enviarDados()
            print(f"Lixeira {self._client_id} BLOQUEADA")

    def desbloquear(self):
        """Destrava a porta da lixeira
        """
        if(self.__capacidade > self.__lixo):
            self.__bloqueado = False
            print(f"Lixeira {self._client_id} DESBLOQUEADA")
            
            #retorna nova informacao sobre o objeto
            self._msg['dados'] = self.dadosLixeira()
            self._msg['acao'] = ''
            self.enviarDados()
        
        else:
            print(f"Lixeira Cheia! Impossível desbloquear Lixeira {self._client_id}")
    
    def generateRandomData(self):
        """Gera lixos em quantidades aleatorias
        """
        while self.__bloqueado == False:
            sleep(5)
            self.addLixo(randint(1,100))
    
    def receberDados(self):
        """Recebe a mensagem do servidor e realiza ações
        """
        while True:
            try:
                super().receberDados()
                # if( "atualizar_setor" in self._msg.get('acao')):
                #     id_setor = self._msg.get('acao').split(';')[1]
                #     self._msg['acao'] = ''
                #     print(f"\nAlocando Lixeira para o setor {id_setor}")
                #     self._client_mqtt.unsubscribe(self._topic)
                #     self._topic = self._topic.split('/')[0]+'/'+id_setor+'/'+self._client_id
                #     #self.connect_mqtt()
                #     self._client_mqtt.subscribe(self._topic)
                #     print('setor/caminhao/'+self._client_id)
                #     self._client_mqtt.subscribe('setor/caminhao/'+self._client_id)
                #     self.enviarDados()
                if 'reservar' == self._msg.get('acao'):
                    self.__reservado = True
                elif(self._msg.get('acao') == "esvaziar"):
                    print("Esvaziando Lixeira...")
                    self.esvaziarLixeira()
                elif(self._msg.get('acao') == "bloquear"):
                    print("Bloqueando Lixeira...")
                    self.bloquear()
                elif(self._msg.get('acao') == "desbloquear"):
                    print("Desbloqueando Lixeira...")
                    self.desbloquear()
                elif(self._msg.get('acao') == "iniciar"):
                    sleep(5)
                    self._msg['dados'] = self.dadosLixeira()
                    self.enviarDadosTopic(self._client_id)
            except Exception as ex:
                print("Erro ao receber dados => ", ex)
                break

    def run(self):
        super().run()
        Thread(target=self.generateRandomData).start()

def geradorLixeiras(qtd_lixeiras: int = 20,
                    velocicdade_gerarLixeira: int = 2)-> Lixeira:
    """Gera lixeiras com quantidades de lixo geradas de forma aleatoria
    Args:
        velocicdade_gerarLixeira (int): velocidade em segundos que a lixeira sera criada
            5 por padrao.
        velocidade_gerar_addLixo (int): velocidade em segundos que o lixo sera adicionado. 
            5 por padrao.
    """
    lixeiras = []
    id = 0
    for i in range (qtd_lixeiras):
        sleep(velocicdade_gerarLixeira)
        if i%5 == 0:
            id = int(i/5)
        lixeiras.append(Lixeira(id=i, latitude=randint(1, 2000), longitude=randint(1, 2000), id_setor=id+1))
        lixeiras[i].run()
   
geradorLixeiras() 
# l = Lixeira(1, 10, 10, 1)
# l.run()