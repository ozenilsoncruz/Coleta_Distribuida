import json
from random import randint, choice
import string
from threading import Thread
from paho.mqtt.publish import single

from server import Server



class Setor(Server):
    
    def __init__(self, latitude: int, longitude: int):
        self._server_id = 'setor/'+"".join(choice(string.ascii_uppercase + string.digits) for _ in range(4))
        Server.__init__(self, self._server_id, [f'{self._server_id}/lixeira/']) #observar qual o erro
        self.__latitude = latitude
        self.__longitude = longitude
        self.__lixeiras_coletar = []
        self.__lixeiras = []
    
    def receberDados(self):
        """Recebe e gerencia as mensagens dos topicos para o qual o setor foi inscrito

        Returns:
            msg: mensagem de um determinado topico para o qual o setor se inscreveu
        """
        while True:
            def on_message(client, userdata, msg):
                mensagem = msg.payload
                if mensagem:
                    mensagem = json.loads(mensagem)
                    
                    if 'REQUEST' in mensagem.get('acao'):
                        print('000000000000000000000000000',msg.topic,mensagem)
                        
                        # PODE EXECUTAR AQUI, O SOLICITANTE É MAIS ANTIGO (TEM PRIORIDADE)
                        if float(mensagem.get('timestamp')) > self.timestamp and self.isRequesting == False:
                            msg = {'acao':'REPLY', 'timestamp': self.timestamp, 'setor':self._server_id }
                            self.enviarDados(self._server_id+'/timestamp/', msg)                              # ALTERAR TOPICO AQUI, POR UM MASSA QUE TODOS OS SETORES ESTEJAM INSCRITOS
                            
                        # DEU XABU, O RECEPTOR É MAIS ANTIGO (TEM PRIORIDADE)
                        else:
                            msg = {'acao':'DENIED', 'timestamp': self.timestamp, 'setor':self._server_id }
                            self.enviarDados(self._server_id+'/timestamp/', msg)                        # ALTERAR TOPICO AQUI, POR UM MASSA QUE SEJA SOMENTE O DO SETOR SOLICITANTE                            
                    
                    if 'REPLY' in mensagem.get('acao'):
                        # ACUMULAR UNICAMENTE OS SETORES E SEUS TIMESTAMPS AQUI PARA self.exclusaoMutua() EXECUTAR
                        # ATUALIZAR TIMESTAMP AQUI E MARCAR QUE self.isRequesting = True. DESMARCAR QUANDO PARAR DE EXECUTAR                  
                        Thread(target=self.gerenciarLixeiras, args=(mensagem, )).start()
                    
                    if 'DENIED' in mensagem.get('acao'):
                        print('aaaa')
                        # DO SOMETHING E RETORNAR SOLICITAÇÃO NEGADA
                    
                    if 'lixeira' in msg.topic:
                        Thread(target=self.gerenciarLixeiras, args=(mensagem, )).start()
                    else:
                        print(mensagem)
                return mensagem
            
            self._server.on_message = on_message
            self._server.loop_start()
                   
    def gerenciarLixeiras(self, msg):
        """Gerencia as mensagens recebidas  das lixeiras

        Args:
            msg (dict): mensagem recebida de uma determinada lixeira
        """
        if 'dados' in msg:
            
            # if self.exclusaoMutua() == True:
                
            lixeirasId = self.__separaIds(self.__lixeiras)
            lixeirasColetarId = self.__separaIds(self.__lixeiras_coletar)
            #se as lixeira nao estiver na lista de lixeras, ela sera adicionada, se estiver tera seu dados atualizado
            if msg.get('dados').get('id') not in lixeirasId:
                print(f"\nLixeira {msg['dados']['id']} conectada")
                self.__lixeiras.append(msg['dados'])
            else:
                self.__lixeiras[lixeirasId.index(msg['dados']['id'])] = msg['dados']
                
            #verifica se a lixeira ja esta em estado critico
            if float(msg.get('dados').get('porcentagem')[:3]) >= 75:
                print(f'LIXEIRA {msg["dados"]["id"]} ESTÁ EM ESTADO CRÍTICO!')
                if msg['dados']['id'] not in lixeirasColetarId:
                        self.__lixeiras_coletar.append(msg.get('dados'))
                else:
                    self.__lixeiras_coletar[lixeirasColetarId.index(msg.get('dados').get('id'))] = msg.get('dados')
                    
            else:
                if msg['dados']['id'] in lixeirasColetarId:
                    print(lixeirasColetarId.index(msg['dados']['id']))
                    self.__lixeiras_coletar.pop(lixeirasColetarId.index(msg['dados']['id']))
            print("\n\n\nLixeiras:    ", self.__lixeiras)
            print("\n\n\nLista de coleta:    ", self.__lixeiras_coletar,"\n\n\n")
            self.enviarDadosServidor()
            
            # else:
                # print('Eita, espera sua vez vei!')
                # print('Pedido negado')
                # msg = {'dados': {'lixeiras': [], 'lixeiras_coletar': [], 'setor': self.dadosSetor() } }
                # self.enviarDados(self._server_id+'/update/', msg)
            
    def enviarDadosServidor(self):
        """Envia informacoes de todas as para o topico do setor/
        """
        msg = {'dados': {'lixeiras': self.__lixeiras, 
                         'lixeiras_coletar': self.__lixeiras_coletar,
                         'setor': self.dadosSetor()
                         }
               }
        self.enviarDados(self._server_id+'/update/', msg)
   
    def __separaIds(self, lixeiras: list) -> list:
        """Organiza a ordem de coleta por parte do adm
        
        Args:
            lixeiras_coletar (list): lista de lixeiras criticas para serem coletadas

        Returns:
            list : todas as lixeiras mais criticas a serem coletadas
        """
        lista = []
        for l in lixeiras: #adiciono apenas o id na lista
            lista.append(l['id'])
        return lista
    
    def dadosSetor(self):
        """Informacoes do setor

        Returns:
            dict: informacoes do setor
        """
        return {
            "id": self._server_id,
            "latitude": self.__latitude, 
            "longitude": self.__longitude,
            "timestamp": self.timestamp
        }
    
    def exclusaoMutua(self, setoresTimestamps = {}):
        """
           setoresTimestamps : DICIONARIO DE TIMESTAMPS DE SETORES, NECESSARIO ADAPTAR PARA PEGAR SOMENTE OS TIMESTAMPS
        """
        # ENVIAR SELF.TIMESTAMP PARA TODOS OS DEMAIS SETORES, 
        # O SETOR RECEPTOR RETORNA TRUE SE:
            # SEU TIMESTAMP FOR MAIOR QUE O DO SOLICITANTE
            # E 
            # SE SELF.ISREQUESTING FOR FALSE
        # SE ALGUM SETOR RECEPTOR RETORNAR FALSE, NÃO DEVE EXECUTAR
        # SE TODOS FOREM TRUE, PODE EXECUTAR
        
        menorTimestamp = min(data[0] for data in setoresTimestamps.values())        # PEGA O MENOR TIMESTAMP DO DICIONARIO DE TIMESTAMPS DE TODOS OS SETORES
        
        if self.timestamp <= menorTimestamp:
            return True
        else:
            return False
        
    
    def run(self):
        super().run()
        self._server.subscribe(self._server_id)
        msg = json.dumps({'dados': {'lixeiras': self.__lixeiras, 
                         'lixeiras_coletar': self.__lixeiras_coletar,
                         'setor': self.dadosSetor()
                         }
                }).encode("utf-8") 
        #envia uma unica vez, uma mensagem com suas informacoes ao ser iniciado
        single(topic=self._server_id+'/update/', payload=msg, hostname=self._broker, port=self._port)
        
     
def geradorSetores(qtd_setores: int = 4) -> list[Setor]:
    """Gera setores com diferentes posicoes

    Args:
        qtd_setores (int, optional): quantidade de setores a ser gerado. 4 por padrao.

    Returns:
        list: lista de setores
    """
    setores = {}
    for i in range(qtd_setores):
        latitude = (i+2)*randint(1, 2*qtd_setores)
        longitude = (i+2) * randint(1 , 2*qtd_setores)
        
        #evita que setores com a mesma posicao sejam criados
        if (latitude, longitude) not in setores:
            setores[(latitude, longitude)] = Setor(latitude, longitude)
            continue
        i -= 1
    return list(setores.values())

lista_setores = geradorSetores()

print(lista_setores[0].dadosSetor())
lista_setores[0].run()
