import json
from math import dist
from threading import Thread

from server import Server

_TOPIC = ["setor/+/update/", "caminhao/", "adm/", "lixeira/"]


class SetorPrincial(Server):
    
    def __init__(self):
        self._server_id = 'setor/'
        self._setores_inscritos = {}
        self.__lixeiras_coletar = {}
        self.__lixeiras = {}
        Server.__init__(self, self._server_id, _TOPIC)
    
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
                    if 'setor' in msg.topic:
                        Thread(target=self.gerenciarSetor, args=(mensagem, )).start()
                        #self.gerenciarLixeiras(mensagem)
                    elif 'caminhao' in msg.topic:
                        Thread(target=self.gerenciarCaminhao, args=(mensagem, )).start()
                        #self.gerenciarCaminhao(mensagem)
                    elif 'lixeira' in msg.topic:
                        Thread(target=self.gerenciarLixeira, args=(mensagem, )).start()
                    else:
                        print(mensagem)
                return mensagem
            
            self._server.on_message = on_message
            self._server.loop_start()
            
    def gerenciarCaminhao(self, msg: dict):
        """Gerencia as mensagens recebidas do topico caminhao/

        Args:
            msg (dict): mensagem recebido do caminhao
        """
        if msg.get('acao') != '' and msg.get('acao') != None:
            mensagem = {'acao': 'esvaziar'}
            self.enviarDados('setor/caminhao/'+msg.get('acao'), mensagem)
   
    def gerenciarSetor(self, msg: dict):
        """Gerencia as mensagens recebidas do setor

        Args:
            msg (dict): mensagem recebido do setor
        """
        if msg.get('dados') != '' or msg.get('dados') != None:
            id =  msg.get('dados').get('setor').get('id')
            if id not in self._setores_inscritos:
                self._setores_inscritos[id] = msg.get('dados').get('setor')
            else:
                if msg.get('dados').get('lixeiras') != self.__lixeiras.get(id):
                    self.__lixeiras[id] = msg.get('dados').get('lixeiras')
                    self.enviarDadosAdm()
                if msg.get('dados').get('lixeiras_coletar') != self.__lixeiras_coletar.get(id):
                    self.__lixeiras_coletar[id] = msg.get('dados').get('lixeiras_coletar')
                    self.enviarDadosCaminhao()
            print("Lixeiras a coletar ---> ", self.__lixeiras_coletar)
            
    def gerenciarLixeira(self, msg: dict):
        """Aloca uma lixeira para o setor mais proximo a ela

        Args:
            msg (dict): dados da lixeira
        """
        if msg.get('dados') != '' and msg.get('dados') != None and len(self._setores_inscritos.values()) > 0:
            id_lixeira = msg.get('dados').get('id')
            posicao_lixeira = (int(msg.get('dados').get('latitude')), int(msg.get('dados').get('longitude')))
            setor_mais_prox =  self.maisProximo(posicao=posicao_lixeira, elementos=list(self._setores_inscritos.values()))
            mensagem = {'acao': f'atualizar_setor;{setor_mais_prox.get("id").split("/")[1]}'}
            self.enviarDados(f'setor/{id_lixeira}', mensagem)
        else:
            print("\nAguardando a inicialização dos setores")
    
    def enviarDadosCaminhao(self):
        """Envia as lixeiras a serem coletada para o tópico caminhao/
        """
        coletar = [lixeira for lixeiras_setor in self.__lixeiras_coletar.values() for lixeira in lixeiras_setor]
        if len(coletar):
            coletar = sorted(coletar, key=lambda l:l["porcentagem"], reverse=True)
            mensagemCaminhao = {'dados': coletar}
            self.enviarDados('setor/caminhao/listaColeta', mensagemCaminhao)
            
    def enviarDadosAdm(self):
        """Envia as lixeiras a serem coletada para o tópico adm/
        """
        lixeiras = [lixeira for lixeiras_setor in self.__lixeiras.values() for lixeira in lixeiras_setor]
        if len(lixeiras):
            lixeiras = sorted(lixeiras, key=lambda l:l["porcentagem"], reverse=True)
            mensageAdm = {'dados': lixeiras}
            self.enviarDados('setor/adm/lixeiras', mensageAdm)
        
    def maisProximo(self, posicao: tuple[int, int], elementos: list[dict]):
        """Seleciona o elemento mais proximo em relacao a uma linha reta

        Args:
            posicao (tuple[int, int]): localizacao do elemento a ser analizado
            elementos (list[dict]): lista de elementos a serem comparados

        Returns:
            mais_prox: elemento mais proximo
        """
        mais_prox = elementos[0] #tomandoo mais proximo como o primeiro elemento

        for e in elementos:    
            b = (e['latitude'], e['longitude'])
            c = (mais_prox['latitude'], mais_prox['latitude'])
            
            if (dist(posicao, b) < dist(posicao, c)):
                mais_prox = e
                
        return mais_prox

SetorPrincial().run()