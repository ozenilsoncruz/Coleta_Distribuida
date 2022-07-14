from flask import Flask, render_template
from src.adm import Adm

app = Flask(__name__)
app.config['DEBUG'] = True
adm = Adm()

@app.route('/')
def index():
    return render_template('index.html')

########## ROTAS LIXEIRA ##########
@app.route('/lixeiras/<number>', methods=['GET'])
def getLixeirasByNumber(number: int):
    try:
        lixeiras = adm.getLixeirasByNumber(number)
        return str(lixeiras)
    except Exception as ex:
        return f"Erro: {ex}"

@app.route('/lixeira/<id>', methods=['GET'])
def getLixeiraByID(id):
    try:
        lixeiras = adm.getLixeiraByID(id)
        return str(lixeiras)
    except Exception as ex:
        return f"Erro: {ex}"
########## ROTAS LIXEIRA ##########

app.run()