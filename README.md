# Coleta de lixo inteligente

## Problema 2 - Conectividade e Concorrência

### Autores
<div align="justify">
  <li><a href="https://github.com/ian-zaque">@ian-zaque</a></li>
  <li><a href="https://github.com/ozenilsoncruz">@ozenilsoncruz</a></li>
</div>

### Máquina
1. Sistema operacional:
  - Windows 10;
  - Ubuntu 22.04 LTS;
2. Linguagem de programação: Python 3.10.4;
  - Bibliotecas nativas utilizadas:
    - flask;
    - json;
    - paho_mqtt;
    - random;
    - string;
    - threading;

### Instruções

1. Clone o repositório.
   ```sh
   git clone https://github.com/ian-zaque/pbl_redes_2.git
   ```
2. Dentro da pasta, crie um novo ambiente.
   ```sh
   python3 -m venv venv
   ```

3. Use o novo ambiente.
   * No Windows, use:
     ```sh
     venv\Scripts\activate.bat
     ```
   * No Linux, use:
     ```sh
     source venv/bin/activate
     ```

4. Dentro da pasta, instale as bibliotecas especificadas por nós no arquivo require.txt.
   ```sh
   pip install -r requirements.txt
   ```

5. Execute os scripts seguindo a ordem:.
    1. Servidor:
        1. Servidor principal:
          ```sh
          python3 control/servidorPrincial.py
          ```
        2. Sevirdor 
          ```sh
          python3 control/setor.py
          ```
    2. Caminhão:
        ``` sh
        python3 model/caminhao.py
        ```

    3. Lixeras:
        ``` sh
        python3 model/lixeira.py
        ```
