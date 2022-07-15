from datetime import datetime
import json
from math import dist
from random import randint
from threading import Thread
from server import Server

class Setor(Server):
    
    def __init__(self, id, latitude: int, longitude: int):
        self._server_id = f'setor/{id}'
        Server.__init__(self, self._server_id, [f'{self._server_id}/', 'setor/',]) #observar qual o erro
        self.__latitude = latitude
        self.__longitude = longitude
        self.__caminhao = {}
        self.__lixeiras_coletar = []
        self.__lixeiras = []
        self.__lixeiras_setor = {}
        self.__lixeira_solicitada = {}
        self.__setores = {}
    
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
                    
                    if self._server_id+'/lixeira' in msg.topic:
                        Thread(target=self.gerenciarLixeiras, args=(mensagem, )).start()
                    elif self._server_id+'/caminhao' in msg.topic:
                        Thread(target=self.gerenciarCaminhao, args=(mensagem, )).start()
                    elif self._server_id+"/request" == msg.topic:
                        Thread(target=self.gerenciarThisSetor, args=(mensagem, )).start()
                    elif 'setores' in msg.topic and self._server_id not in msg.topic:
                        #print("\n\nEntrei no topico geral dos setores\n\n")
                        print(msg.topic)
                        Thread(target=self.gerenciarSetor, args=(mensagem, )).start()
                return mensagem
            
            self._server.on_message = on_message
            self._server.loop_start()
 
    def gerenciarCaminhao(self, msg: dict):
        """Gerencia as mensagens recebidas do topico caminhao/

        Args:
            msg (dict): mensagem recebido do caminhao
        """

        if msg.get('dados') != None and msg.get('dados') != '':
            if msg.get('dados').get('caminhao') != None and msg.get('dados').get('caminhao').get('id') not in self.__caminhao:
                print('\nCaminhão ', msg.get('dados').get('caminhao').get('id'), ' conectado!\n')
                self.__caminhao[msg.get('dados').get('caminhao').get('id')] = msg.get('dados').get('caminhao')
        
        if msg.get('acao') != None and msg.get('acao') != '':
            if 'REQUEST' == msg.get('acao'): #solicita as lixeiras para o caminhao
                if len(self.__lixeiras_coletar) < 3:
                    aux = []
                    aux = [aux.extend(i) for i in list(self.__lixeiras_setor.values())]
                    if len(aux) > 0:
                        self.solicitarLixeira()
                else:
                    self.enviarDadosCaminhao()      
            elif 'lixeira' in msg.get('acao'):
                print(msg.get('acao'))
                mensagem = {'acao': 'esvaziar'}
                self.enviarDados(f'{self._server_id}/caminhao/'+msg.get('acao'), mensagem)
                   
    def gerenciarLixeiras(self, msg):
        """Gerencia as mensagens recebidas  das lixeiras

        Args:
            msg (dict): mensagem recebida de uma determinada lixeira
        """
        if 'dados' in msg:     
            lixeirasId = self.__separaIds(self.__lixeiras)
            lixeirasColetarId = self.__separaIds(self.__lixeiras_coletar)
            #se as lixeira nao estiver na lista de lixeras, ela sera adicionada, se estiver tera seu dados atualizado
            # print(lixeirasId)
            # print(msg.get('dados').get('id'))
            # print(msg.get('dados').get('id') in lixeirasId)
            if msg.get('dados').get('id') not in lixeirasId:
                print(f"\nLixeira {msg['dados']['id']} conectada")
                self.__lixeiras.append(msg['dados'])
            else:
                self.__lixeiras[lixeirasId.index(msg['dados']['id'])] = msg['dados']
                
            #verifica se a lixeira ja esta em estado critico
            if float(msg.get('dados').get('porcentagem')[:3]) >= 75:
                print(f'LIXEIRA {msg["dados"]["id"]} ESTÁ EM ESTADO CRÍTICO!')
                
                # #reservando lixeira
                # mensagem = {'acao': 'reservar'}
                # self.enviarDados(msg.get('dados').get('id'), mensagem)
                if msg['dados']['id'] not in lixeirasColetarId:
                        self.__lixeiras_coletar.append(msg.get('dados'))
                else:
                    self.__lixeiras_coletar[lixeirasColetarId.index(msg.get('dados').get('id'))] = msg.get('dados')
                    
            else:
                if msg['dados']['id'] in lixeirasColetarId:
                    print(lixeirasColetarId.index(msg['dados']['id']))
                    self.__lixeiras_coletar.pop(lixeirasColetarId.index(msg['dados']['id']))
            
            self.__lixeiras = [dict(t) for t in {tuple(d.items()) for d in  self.__lixeiras}]
            self.__lixeiras_coletar = [dict(t) for t in {tuple(d.items()) for d in self.__lixeiras_coletar}]
            
            # print("\n\n\nLixeiras:    ", self.__lixeiras)
            # print("\n\n\nLista de coleta:    ", self.__lixeiras_coletar,"\n\n\n")
            self.enviarDadosServidor()

    def gerenciarSetor(self, msg: dict):
        """Gerencia as mensagens recebidas do setor

        Args:
            msg (dict): mensagem recebido do setor
        """
        if msg.get('dados') != '' or msg.get('dados') != None:
            id =  msg.get('dados').get('id')
            if msg.get('dados').get('lixeirasCriticas') != self.__lixeiras_setor.get(id):
                self.__lixeiras_setor[id] = msg.get('dados').get('lixeirasCriticas')
            if 'REQUEST' in msg.get('acao').get('permissao'):
                print('\n\nSetor ', msg.get('dados').get('id'), ' deseja realizar uma requisição...\n\n')
                mensagem = {'dados': {'acao': {'permissao': '', 
                                               'objeto': msg.get('acao').get('objeto')}, 
                                      'dados': msg.get('dados')}}       
                #Se a lixeira solicitada pelo outro for diferenta lixeira solicita
                #ou se o momento de solicitacao do outro setor for menor, ele recebera a permissao
                if msg.get('acao').get('objeto') not in self.__lixeiras_coletar:
                    if self.__lixeira_solicitada != msg.get('acao').get('objeto') or self.timestamp > float(msg.get('dados').get('timestamp')):
                        mensagem['dados']['acao']['permissao'] = 'REPLY'
                # DEU XABU, O RECEPTOR É MAIS ANTIGO (TEM PRIORIDADE)
                else:
                    mensagem['dados']['acao']['permissao'] = 'DENIED'
                self.enviarDados(id+"/request", mensagem)                        # ALTERAR TOPICO AQUI, POR UM MASSA QUE SEJA SOMENTE O DO SETOR SOLICITANTE                            
            
    def gerenciarThisSetor(self, msg: dict):
        """Gerencia as mensagem enviada para o proprio setor

        Args:
            msg (dict): mensagem recebida
        """
        if 'REPLY' in msg.get('acao'):
            id =  msg.get('dados').get('id')
            self.__setores[id] = msg.get('dados')
            # ACUMULAR UNICAMENTE OS SETORES E SEUS TIMESTAMPS AQUI PARA self.exclusaoMutua() EXECUTAR
            if len(self.__setores.keys()) == 3:
                print('\nRecurso disponível!\n')
                print('\n\nReservando lixeira de outro setor...\n\n')
                #reservando lixeira
                # mensagem = {'acao': 'reservar'}
                # self.enviarDados('lixeira/'+msg.get('dados').get('id'), mensagem)
                # print("Lixeira ", self.__lixeira_solicitada.get('id'), " reservada!")
                # self.__lixeiras_coletar.append(self.__lixeira_solicitada) 
                # self.solicitarLixeira()
                # self.__setores.clear()
        #se a permisssao da lixera em questao for negada, uma nova solicitacao para outra lixeira sera realizada
        if 'DENIED' in msg.get('acao').get('permissao'):
            print('Recurso negado!\n')
            self.solicitarLixeira()
      
    def enviarDadosCaminhao(self):
        """Envia as lixeiras a serem coletada para o tópico caminhao/
        """
        coletar = [l for l in self.__lixeiras_coletar]
        if len(coletar):
            coletar = sorted(coletar, key=lambda l:l["porcentagem"], reverse=True)
            mensagemCaminhao = {'dados': {'lixeiras': coletar}}
            
            #enviando msg para a lixeira
            idSetor = self._server_id.split('/')
            idSetor = idSetor[1]
            
            self.enviarDados(f'{self._server_id}/caminhao/{idSetor}/listaColeta', mensagemCaminhao)
          
    def enviarDadosServidor(self, permissao: str = '', objeto: dict = {}):
        """Envia informacoes de todas as para o topico do setor/
        """
        msg = {
            'acao': {'permissao': permissao,
                     'objeto': objeto},
            'dados': self.dadosSetor()      
        }
        #print('Enviando mensgem para os setores ---> ', msg)
        self.enviarDados(self._server_id+'/setores', msg)
   
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
            "lixeirasCriticas": [l for l in self.__lixeiras_coletar if not l.get('reservado')], #seleciona apenas as lixeiras que nao estiverem reservadas
            "latitude": self.__latitude,
            "longitude": self.__longitude,
            "timestamp": self.timestamp
        }
        
    def maisProximo(self, posicao: tuple[int, int], elementos: list[dict]):
        """Seleciona o elemento mais proximo considerando a distancia euclidiana

        Args:
            posicao (tuple[int, int]): localizacao do elemento a ser analizado
            elementos (list[dict]): lista de elementos a serem comparados

        Returns:
            mais_prox: elemento mais proximo
        """
        mais_prox = elementos[0] #tomandoo mais proximo como o primeiro elemento

        for e in elementos:    
            b = (int(e['latitude']), int(e['longitude']))
            c = (int(mais_prox['latitude']), int(mais_prox['longitude']))

            if (dist(posicao, b) < dist(posicao, c)):
                mais_prox = e
                
        return mais_prox
    
    def run(self):
        super().run()
        self._server.subscribe(self._server_id)
        
    def solicitarLixeira(self):
        """Solicita uma lixeira para todos os setores
        """
        if len(self.__lixeiras_coletar) <= 4:
            auxiliar = []
            coletar = [lixeira for lixeiras_setor in self.__lixeiras_setor.values() for lixeira in lixeiras_setor]
            if len(coletar):
                posicao_caminhao = (int(self.__caminhao.get('latitude')), int(self.__caminhao.get('longitude')))
                
                coletar = sorted(coletar, key=lambda l:l["porcentagem"], reverse=True)
                for l in coletar:
                    if l != self.__lixeira_solicitada:
                        #pega a lixeira mais proxima 
                        lixeira_mais_proxima = self.maisProximo(posicao=posicao_caminhao, elementos=coletar)
                        if float(lixeira_mais_proxima.get('porcentagem')[:3]) <= float(l.get('porcentagem')[:3]):
                            auxiliar = lixeira_mais_proxima
            self.__lixeira_solicitada = auxiliar
            self.timestamp = datetime.now().timestamp()
            self.enviarDadosServidor(permissao='REQUEST', objeto=self.__lixeira_solicitada)
     
def geradorSetores(qtd_setores: int = 4) -> list[Setor]:
    """Gera setores com diferentes posicoes

    Args:
        qtd_setores (int, optional): quantidade de setores a ser gerado. 4 por padrao.

    Returns:
        list: lista de setores
    """
    listaSetores = []        
    for i in range (qtd_setores):    
        listaSetores.append(Setor(latitude=(i+1)*randint(1, 2000), longitude=(i+1)*randint(1, 2000), id=i+1))
        listaSetores[i].run()
        
    return listaSetores

geradorSetores(1)