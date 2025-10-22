from flask import Flask , render_template , request ,url_for ,redirect,session,send_from_directory,jsonify
import os
from requisicao import Requisicao
from observacao import Observacao
from Producoes import Produzidos
from datetime import datetime
from Usuario import Usuario
from preset import Preset
from preset_cliever import Preset_cliever
from skus import Sku
from Qualidade import Qualidade
from datetime import datetime, timedelta
from Notificacao import Notificacao
from preset_maquina4 import MAQUINA_4
from preset_maquina4_cliever import MAQUINA_4_cliever
from skus_cliever import Sku_cliever
from teste_excel import Criar_excel
from feedback import Feedback



ref_maquina = ''
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'D220101')
unidade = 0
data = datetime.now().strftime('%d-%m-%Y')
data2 = datetime.now().strftime('%d-%m-%Y')
user = ""
letra_mes = ['','A','B','C','D','E','F','G','H','I','J','K','L']
mes_name = ['',"JAN",'FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ']
registro_pd = {}
id =''
dados_filtrados = {}


###########################
@app.route('/buscar', methods=['POST'])
def buscar():
    sku = request.form['sku']  # Converte o SKU para maiúsculas
    lote = request.form['lote'].upper()  # Converte o lote para maiúsculas
    resultados = []

    for data, producoes in Produzidos[0].items():
        for producao in producoes:
            print(producao["sku"])
            # Comparação case-insensitive
            if str(producao['sku']) == str(sku) and str(producao['lote'].upper()) == str(lote):
                resultados.append(producao)
    print(resultados)

    return render_template('editar_producao.html', resultados=resultados)


@app.route('/apagar', methods=['POST'])
def apagar():
    sku = request.form.get('sku')
    lote = request.form.get('lote')

    # Percorre as produções e tenta encontrar o item com o SKU e Lote correspondentes
    for data, producoes in Produzidos[0].items():
        for producao in producoes:
            if producao['sku'] == sku and producao['lote'] == lote:
                producoes.remove(producao)  # Remove a produção encontrada
                break  # Sai do loop após a remoção

    # Após remover, você pode redirecionar para a página de pesquisa ou exibir uma mensagem
    return redirect(url_for("editar_producao"))  # Redireciona para a página de pesquisa após apagar


@app.route('/salvar', methods=['POST'])
def salvar():
    index = 1
    for data, producoes in Produzidos[0].items():
        for producao in producoes:
            # Atualiza as informações de cada produção com base nos inputs enviados
            producao['ID'] = request.form.get(f'ID_{index}')
            producao['sku'] = request.form.get(f'sku_{index}')
            producao['lote'] = request.form.get(f'lote_{index}')
            producao['material'] = request.form.get(f'material_{index}')
            producao['cor'] = request.form.get(f'cor_{index}')
            producao['diametro'] = request.form.get(f'diametro_{index}')
            producao['produzida'] = request.form.get(f'produzida_{index}')
            producao['observacao'] = request.form.get(f'observacao_{index}')
            index += 1
    registrar_producao()
    # Após salvar, você pode redirecionar de volta para a página de busca ou exibir uma mensagem de sucesso
    return redirect(url_for('editar_producao'))  # redireciona para a página de pesquisa após salvar


@app.route('/editar_producao')
def editar_producao():
    return render_template('editar_producao.html')


############## -    DOWNLOAD    - #####################

FILE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "produzidos.xlsx")

@app.route('/download')
def download_file():
    # Envia o arquivo para o cliente
    return send_from_directory(
        directory=os.path.dirname(FILE_PATH),
        path=os.path.basename(FILE_PATH),
        as_attachment=True
    )


######### - feedback - ############

@app.route("/ver_feedbacks")
def ver_feedbacks():
    return render_template("ver_feedback.html",feedback_data = Feedback)

def gravar_feedback():
    with open("feedback.py","w",encoding='utf-8') as txt:
        txt.write(f"Feedback = {Feedback}")
        txt.close()
    

@app.route('/feedback-inicio')
def feedback_inicio():
    if not(session['username'] in Feedback):
        Feedback.update({session["username"]:[]})
    return render_template("feedback.html",feedback_data=Feedback[session['username']])

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Pega o feedback do formulário
        user_feedback = request.form['feedback']
        if not(session["username"] in Feedback):
            Feedback.update({session["username"]:[]})
        Feedback[session["username"]].append([data2,user_feedback])
        
        # Redireciona para uma página de confirmação ou para a página inicial
        gravar_feedback()
        return redirect(url_for('feedback_inicio'))
        

    # Renderiza o formulário de feedback
    return redirect(url_for("feedback-inicio"))



####### - EDITAR REQUISICAO - ##############

@app.route("/editar_requisicao",methods=['GET','POST'])
def editar_requisicao():
    return render_template("editar_requisicao.html" , requisicoes = Requisicao)


@app.route('/edit_quantity', methods=['GET', 'POST'])
def edit_quantity():
    if request.method == 'POST':
        maquina = request.form.get('maquina')
        requisicao = request.form.get('requisicao')
        quantidade = request.form.get('quantidade')

        if maquina in Requisicao and requisicao in Requisicao[maquina]:
            Requisicao[maquina][requisicao]['quantidade'] = float(quantidade)

            if Requisicao[maquina][requisicao]['quantidade'] <= 0:
                del Requisicao[maquina][requisicao]
                
        
        
        return redirect(url_for('editar_requisicao'))


####### - EDITAR USUARIO - ##################

@app.route("/editar_usuario",methods=["GET","POST"])
def editar_usuario():
    return render_template("editar_usuario.html",usuarios = Usuario)

@app.route('/edit_user', methods=['POST'])
def edit_user():
    user_id = request.form.get('id')
    if user_id in Usuario:
        user_info = Usuario[user_id]
        user_info['nome'] = request.form.get('nome', user_info['nome'])
        user_info['turno'] = request.form.get('turno', user_info['turno'])
        user_info['maquina'] = request.form.get('maquina', user_info['maquina'])
        user_info['password'] = request.form.get('password', user_info['password'])
        user_info['operador'] = 'operador' in request.form
        user_info['gestor'] = 'gestor' in request.form
        user_info['qualidade'] = 'qualidade' in request.form
        user_info['Link_qualidade'] = request.form.get('link_qualidade', user_info['Link_qualidade'])

        gravar_usuario()
    else:
        return "Não existe o usuario"
    
    return redirect(url_for('editar_usuario'))

########################################################
'''           CLIEVER                '''
########################################################
@app.route("/maquina4_preset_cliever",methods=["GET",'POST'])
def maquina4_preset_cliever():
    sku =  id
    maquina = "MAQUINA 4" 
    return render_template("maquina4_preset_cliever.html", sku=sku , maquina=maquina)

@app.route('/cadastrar_preset_maquina4_cliever', methods=['POST',"GET"])
def cadastrar_preset_maquina4_cliever():
    # Coletar os dados do formulário
    dados = {id:{
        'heater1': {
            'zona1': request.form.get('heater1_zona1'),
            'zona2': request.form.get('heater1_zona2'),
            'zona3': request.form.get('heater1_zona3'),
            'cabecote1': request.form.get('heater1_cabecote1'),
            'cabecote2': request.form.get('heater1_cabecote2'),
            'cabecote3': request.form.get('heater1_cabecote3')
        },
        'heater2': {
            'zona1': request.form.get('heater2_zona1'),
            'zona2': request.form.get('heater2_zona2'),
            'zona3': request.form.get('heater2_zona3'),
            'cabecote1': request.form.get('heater2_cabecote'),
            'bico': request.form.get('heater2_bico')
        },
        'heater3': {
            'zona1': request.form.get('heater3_zona1'),
            'zona2': request.form.get('heater3_zona2'),
            'zona3': request.form.get('heater3_zona3'),
            'cabecote1': request.form.get('heater3_cabecote1'),
            'cabecote2': request.form.get('heater3_cabecote2'),
            'cabecote3': request.form.get('heater3_cabecote3')
        }
    }}

    

    MAQUINA_4_cliever.update(dados)
    
    gravar_preset()
    return render_template("ok.html")

@app.route('/ver_cadastrados_por_sku_cliever', methods=['GET'])
def ver_cadastrados_por_sku_cliever():
    # Obtém o SKU digitado pelo usuário (pode ser vazio)
    input_sku = request.args.get('input_sku', '').strip().upper()  # Ajuste para considerar input vazio
    
    # Verifica se o campo de SKU está vazio
    if not input_sku:
        filtered_presets = Preset_cliever  # Retorna todos os dados se não houver SKU informado
    else:
        # Filtra os SKUs que correspondem ao SKU digitado
        filtered_presets = {}
        for maquina, skus in Preset_cliever.items():
            filtered_skus = {}
            for sku, values in skus.items():
                if input_sku in sku.upper():
                    filtered_skus[sku] = values
            
            if filtered_skus:
                filtered_presets[maquina] = filtered_skus
    
    return render_template('ver_cadastrados_cliever.html', presets=filtered_presets, Sku=Sku_cliever)
        
@app.route('/cadastrar_cliever', methods=['POST'])
def cadastrar_cliever():
    maquina = request.form.getlist('maquina')
    maquina = ''.join(maquina)

    sku = id
    zona1 = (request.form['zona1'])
    zona2 = (request.form['zona2'])
    zona3 = (request.form['zona3'])
    zona4 = (request.form['zona4'])
    cabecote = (request.form['cabecote'])
    bico = (request.form['bico'])
    calha1 = (request.form['calha1'])
    calha2 = (request.form['calha2'])

    if not(maquina in Preset_cliever):
        Preset_cliever.update({maquina:{}})
    
    Preset_cliever[maquina].update({ sku : [zona1, zona2, zona3, zona4, cabecote, bico, calha1, calha2]})
    
    
    gravar_preset()
    return redirect(url_for("opcoes_cadastros_sku"))

@app.route("/preset_cliever",methods=["GET","POST"])
def preset_cliever():
    return render_template("preset_cliever.html",presets=Preset_cliever,id=id)

@app.route("/gravar_sku_cliever",methods=["GET","POST"])
def grava_sku_cliever():
    sku = request.form["sku"]
    material = request.form["material"]
    cor = request.form["cor"]
    porcentagem = request.form["porcentagem"]
    diametro = request.form["diametro"]
    peso = request.form["peso"]
    base = request.form["base"]
    bico = request.form["bico"]
    
    info = f'Bico:{bico} Base:{base}'

    novo = {sku:[material,cor,diametro,peso,info,porcentagem]}
    
    Sku_cliever.update(novo)
    global id
    id = sku
    
    return redirect(url_for("preset_cliever"))

@app.route("/gerar_sku_cliever",methods=["POST","GET"])
def gerar_sku_cliever():
    return render_template("gerar_sku_cliever.html")

@app.route("/ver_cadastrados_cliever")
def ver_cadastrados_cliever():
    
    filtered_presets = Preset_cliever.copy()
    machine_select = request.args.get('machine_select', '')
    if machine_select:
        filtered_presets = {machine_select: Preset_cliever.get(machine_select, {})}
    return render_template('ver_cadastrados_cliever.html', presets=filtered_presets, Sku=Sku_cliever)

@app.route("/cadastrados_maquina4_cliever")
def cadastrados_maquina4_cliever():
    search_sku = request.args.get('search_sku', '').strip()
    
    if search_sku:
        filtered_presets = {sku: MAQUINA_4_cliever.get(sku, {}) for sku in MAQUINA_4_cliever if search_sku in sku}
    else:
        filtered_presets = MAQUINA_4_cliever
    
    return render_template('cadastrados_maquina4_cliever.html', filtered_presets=filtered_presets, Sku=Sku_cliever)

#########################################################
@app.route("/desativar_notificacao",methods=["GET","POST"])
def desativar_notificacao():
    id = request.form['id']
    
    if str(id) in Notificacao:
        Notificacao[id][5] = False
        gravar_notificacao()
        return render_template("notificar_operador.html",registros=Qualidade,Notificacao=Notificacao)

    else:
        return f"Notificação com ID {id} não encontrada."

def gravar_usuario():
    with open("Usuario.py", 'w', encoding="utf-8") as txt:
        txt.write(f"Usuario = {Usuario}")
        txt.close()

@app.route('/adicionar_user', methods=['POST'])
def adicionar_user():
    # Obtém os dados do formulário
    id_ = request.form.get('id')
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    maquina = request.form.get('maquina', '')
    turno = request.form.get('turno', '')
    operador = 'operador' in request.form
    gestor = 'gestor' in request.form
    qualidade = 'qualidade' in request.form
    link_qualidade = request.form.get('link_qualidade', '')

    # Cria um dicionário com os dados do formulário
    dados_usuario = {
        id_:{
        'nome': nome,
        "id":id_,
        'turno': turno if turno else '-',
        'maquina': maquina if maquina else '-',
        "password":senha,
        'operador': operador,
        'gestor': gestor,
        'qualidade': qualidade,
        'Link_qualidade': link_qualidade if link_qualidade else '-'
        }}

    Usuario.update(dados_usuario)
    gravar_usuario()

    return render_template("admin.html",usuarios=Usuario)



@app.route("/cadastrados_maquina4")
def cadastrados_maquina4():
    search_sku = request.args.get('search_sku', '').strip()
    
    if search_sku:
        filtered_presets = {sku: MAQUINA_4.get(sku, {}) for sku in MAQUINA_4 if search_sku in sku}
    else:
        filtered_presets = MAQUINA_4
    
    return render_template('cadastrados_maquina4.html', filtered_presets=filtered_presets, Sku=Sku)
    
@app.route('/cadastrar_preset_maquina4', methods=['POST',"GET"])
def cadastrar_preset_maquina4():
    # Coletar os dados do formulário
    dados = {id:{
        'heater1': {
            'zona1': request.form.get('heater1_zona1'),
            'zona2': request.form.get('heater1_zona2'),
            'zona3': request.form.get('heater1_zona3'),
            'cabecote1': request.form.get('heater1_cabecote1'),
            'cabecote2': request.form.get('heater1_cabecote2'),
            'cabecote3': request.form.get('heater1_cabecote3')
        },
        'heater2': {
            'zona1': request.form.get('heater2_zona1'),
            'zona2': request.form.get('heater2_zona2'),
            'zona3': request.form.get('heater2_zona3'),
            'cabecote1': request.form.get('heater2_cabecote'),
            'bico': request.form.get('heater2_bico')
        },
        'heater3': {
            'zona1': request.form.get('heater3_zona1'),
            'zona2': request.form.get('heater3_zona2'),
            'zona3': request.form.get('heater3_zona3'),
            'cabecote1': request.form.get('heater3_cabecote1'),
            'cabecote2': request.form.get('heater3_cabecote2'),
            'cabecote3': request.form.get('heater3_cabecote3')
        }
    }}

    # Exibir os dados no console para depuração (ou processar conforme necessário)

    MAQUINA_4.update(dados)
    
    gravar_preset()
    return render_template("ok.html")

@app.route("/maquina4_preset",methods=["GET",'POST'])
def maquina4_preset():
    sku =  id
    maquina = "MAQUINA 4" 
    return render_template("maquina4_preset.html", sku=sku , maquina=maquina)

# Função para verificar se a data está até 3 dias antes da data atual
def is_within_3_days(date_str):
    try:
        data_atual = datetime.now()
        data_dado = datetime.strptime(date_str, "%d-%m-%Y")
        diff = data_atual - data_dado
        return 0 <= diff.days <= 3
    except ValueError:
        return False

@app.route("/operador")
def operador():
    # Verificar se o usuário está autenticado e tem permissão de operador
    username = session.get('username')
    if not username or not session.get(username, {}).get("operador"):
        return redirect(url_for("autenticar_login"))

    # Obter dados do usuário e realizar cálculos
    dados = session.get(username, {})
    meta = 1600
    produzido_500 = []
    produzido_200 = [] 
    produzido = []
    perda = []
    low = []

    for data in Produzidos[0]:
        data_obj = datetime.strptime(data, '%d-%m-%Y')
        agora = datetime.now()
        mes_atual = agora.month
        mes = data_obj.month
        
        for producao in Produzidos[0][data]:
            
            if mes == mes_atual:
                if username == producao["ID"]:
                    print(producao)
                    produzido.append(float(producao["produzida"]))
                    if producao["produzida200g"] == "-" :
                        producao["produzida200g"] = 0
                    if producao["produzida500g"] == "-" :
                        producao["produzida500g"] = 0
                    produzido_200.append(float(producao["produzida200g"]))
                    produzido_500.append(float(producao["produzida500g"]))
                    
                    if producao["perda"] == "" or producao["perda"] == "-":
                        producao["perda"] = 0
                    perda.append(float(producao["perda"]))
                    if producao["low"] == "-" or producao["low"] == "":
                        producao["low"] = 0  
                    low.append(float(producao["low"]))
        
    falta_meta = 0
    pperda = 0
    plow = 0
    if len(produzido) != 0:
        falta_meta = meta - sum(produzido)
        pperda = (sum(perda) / sum(produzido)) * 100 if sum(produzido) != 0 else 0
        plow = (sum(low) / sum(produzido)) * 100

    dados_filtrados = {}
    for chave, dados in Qualidade.items():
        nome = dados[1]
        if str(session[str(session["username"])]["nome"]) == str(nome) :
            if is_within_3_days(dados[0]):
                dados_filtrados[chave] = dados

    notifica = {}
    for id,dados in Notificacao.items():
        nome = dados[1]
        if str(session[str(session["username"])]["nome"]) == str(nome) :
            if dados[5] == True:
                notifica.update({id:dados})
    
    p200 = sum(produzido_200)/5
    p500 = sum(produzido_500)/2
    produzido.append(p200)
    produzido.append(p500)
    
    return render_template("operador.html",mes=mes_atual,
                           notificacao=notifica,
                           qualidade=dados_filtrados,
                           meta=meta,
                           pperda=str(pperda)[:4],
                           plowc=str(plow)[:4],
                           lowc=sum(low),
                           perda=sum(perda),
                           info_user=Usuario.get(username, {}),
                           produzida=sum(produzido),
                           fmeta=falta_meta,data2=data2)

def gravar_notificacao():
    with open("Notificacao.py", 'w', encoding="utf-8") as txt:
        txt.write(f"Notificacao = {Notificacao}")
        txt.close()

def gravar_qualidade():
    with open("Qualidade.py", 'w', encoding="utf-8") as txt:
        txt.write(f"Qualidade = {Qualidade}")
        txt.close()

@app.route('/registrar_notificacao', methods=['GET','POST'])
def registrar_notificacao():
    operadores_selecionados = request.form.getlist('operador')
    nao_conformidade = request.form['naoConformidade']
    correcao = request.form['correcao']
    lote = request.form['lote']

    if request.form.get('action') == 'rnc_interna':
        # Gerar novo ID (apenas para simulação, você pode ajustar conforme necessário)
        novo_id = str(len(Qualidade) + 1)
        Qualidade[novo_id] = [data, ''.join(operadores_selecionados),lote, nao_conformidade, correcao]

        gravar_qualidade()
        # Após atualizar os registros, redirecionar para a página principal
        return render_template('notificar_operador.html', registros=Qualidade,Notificacao=Notificacao)
    
    elif request.form.get('action') == 'notificar_operador':
        novo_id = str(len(Notificacao) + 1)
        Notificacao[novo_id] = [data, ''.join(operadores_selecionados),lote, nao_conformidade, correcao,True]
        gravar_notificacao()
        return render_template('notificar_operador.html', registros=Qualidade,Notificacao=Notificacao)

@app.route("/notificar_operador")
def notificar_operador():
    return render_template("notificar_operador.html",registros=Qualidade,Notificacao=Notificacao)

@app.route('/ver_cadastrados_por_sku', methods=['GET'])
def ver_cadastrados_por_sku():
    # Obtém o SKU digitado pelo usuário (pode ser vazio)
    input_sku = request.args.get('input_sku', '').strip().upper()  # Ajuste para considerar input vazio
    
    # Verifica se o campo de SKU está vazio
    if not input_sku:
        filtered_presets = Preset  # Retorna todos os dados se não houver SKU informado
    else:
        # Filtra os SKUs que correspondem ao SKU digitado
        filtered_presets = {}
        for maquina, skus in Preset.items():
            filtered_skus = {}
            for sku, values in skus.items():
                if input_sku in sku.upper():
                    filtered_skus[sku] = values
            
            if filtered_skus:
                filtered_presets[maquina] = filtered_skus
    
    return render_template('ver_cadastrados.html', presets=filtered_presets, Sku=Sku)
        
@app.route("/ver_cadastrados")
def ver_cadastrados():
    
    filtered_presets = Preset.copy()
    machine_select = request.args.get('machine_select', '')
    if machine_select:
        filtered_presets = {machine_select: Preset.get(machine_select, {})}
    return render_template('ver_cadastrados.html', presets=filtered_presets, Sku=Sku)
    
@app.route("/gravar_sku",methods=["GET","POST"])
def grava_sku():
    sku = request.form["sku"]
    material = request.form["material"]
    cor = request.form["cor"]
    diametro = request.form["diametro"]
    peso = request.form["peso"]
    base = request.form["base"]
    bico = request.form["bico"]
    porcentagem = request.form["porcentagem"]
    
    info = f'Bico:{bico} Base:{base}'

    novo = {sku:[material,cor,diametro,peso,info,porcentagem]}
    
    Sku.update(novo)
    global id
    id = sku
    
    return redirect(url_for("preset"))

@app.route("/gerar_sku_3d",methods=["POST","GET"])
def gerar_sku_3d():
    return render_template("gerar_sku.html")

@app.route("/opcoes_cadastros_sku")
def opcoes_cadastros_sku():
    return render_template("opcoes_cadastros_sku.html")

def gravar_preset():

    txt = open("Skus.py","w",encoding='utf-8')
    txt.write(f"# -*- coding: utf-8 -*-\nSku = {Sku}")
    txt.close()

    txt = open("preset.py","w",encoding='utf-8')
    txt.write(f"Preset = {Preset}")
    txt.close()

    txt = open("preset_maquina4.py","w",encoding='utf-8')
    txt.write(f"MAQUINA_4 = {MAQUINA_4}")
    txt.close()

    ######## CLIEVER ##########
    txt = open("Skus_cliever.py","w",encoding='utf-8')
    txt.write(f"# -*- coding: utf-8 -*-\nSku_cliever = {Sku_cliever}")
    txt.close()

    txt = open("preset_cliever.py","w",encoding='utf-8')
    txt.write(f"Preset_cliever = {Preset_cliever}")
    txt.close()

    txt = open("preset_maquina4_cliever.py","w",encoding='utf-8')
    txt.write(f"MAQUINA_4_cliever = {MAQUINA_4_cliever}")
    txt.close()

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    maquina = request.form.getlist('maquina')
    maquina = ''.join(maquina)

    sku = id
    zona1 = int(request.form['zona1'])
    zona2 = int(request.form['zona2'])
    zona3 = int(request.form['zona3'])
    zona4 = int(request.form['zona4'])
    cabecote = int(request.form['cabecote'])
    bico = int(request.form['bico'])
    calha1 = int(request.form['calha1'])
    calha2 = int(request.form['calha2'])

    if not(maquina in Preset):
        Preset.update({maquina:{}})
    
    Preset[maquina].update({ sku : [zona1, zona2, zona3, zona4, cabecote, bico, calha1, calha2]})
    
    
    gravar_preset()
    return redirect(url_for("opcoes_cadastros_sku"))

@app.route("/preset",methods=["GET","POST"])
def preset():
    return render_template("preset.html",presets=Preset,id=id)

@app.route("/ADMIM",methods=['GET','POST'])
def admim():
    return render_template("admin.html",usuarios=Usuario)

@app.route('/autenticar_login', methods=['POST'])
def autenticar_login():
    id = str(request.form["username"])
    senha = request.form["password"]

    if id in Usuario:
        if str(senha) == str(Usuario[id]["password"]):
            # Armazenar todas as informações do usuário em um dicionário na sessão
            session[id] = {
                'username': id,
                'gestor': Usuario[id]["gestor"],
                'qualidade': Usuario[id]["qualidade"],
                'operador': Usuario[id]["operador"],
                'nome': Usuario[id]["nome"],
                'turno': Usuario[id]["turno"],
                'maquina': Usuario[id]["maquina"],
                'id': Usuario[id]["id"]
            }
            session['username'] = id
            # Debug
            

            usuario_info = session[id]

            

            # Verificar permissões e redirecionar conforme necessário
            if usuario_info['gestor'] == True or usuario_info['qualidade'] == True:
                
                return redirect(url_for("gestor"))
            elif usuario_info['operador'] == True:
                return redirect(url_for("operador"))
            else:
                return "Acesso não autorizado"
        else:
            return 'Senha inválida'
    else:
        return "Usuário inválido"
    
@app.route("/login",methods=["GET","POST"])
def login():
    return render_template("login.html")

def filter_producao(data, operador, sku, start_date, end_date):
    filtered = []
    for date, items in data[0].items():
        if start_date <= datetime.strptime(date, '%d-%m-%Y').date() <= end_date:
            for item in items:
                if (operador == '' or item['ID'] == operador) and (sku == '' or item['sku'] == sku):
                    filtered.append(item)
    return filtered



@app.route('/ver-producao', methods=["GET", "POST"])
def ver_producao():
    operador = request.form.get('operador', '')
    sku = request.form.get('sku', '')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    # Converte as datas para o formato de data
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.min.date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else datetime.max.date()

    # Filtra os dados
    producao_filtrada = filter_producao(Produzidos, operador, sku, start_date, end_date)
    
    return render_template('ver_producao.html', producao=producao_filtrada, 
                           operadores=set(item['ID'] for date, items in Produzidos[0].items() for item in items))

    

def grava_producao():

    script =  open("Producoes.py", "w",encoding="utf-8")
    txt = f"#coding : utf-8 \nProduzidos = [{registro_pd}]"
    script.write(txt)
    script.close
    

@app.route("/fechamento",methods=['GET','POST'])
def fechamento():
    usuario = Usuario[session['username']]
    nome = usuario["nome"]

    return render_template("fechamento.html",nome=nome ,info_user=usuario,productions=Produzidos[0],infid=usuario['id'],skus_dict=Sku,skus_dict_cliever=Sku_cliever)

@app.route('/registrar-producao', methods=['POST'])
def registrar_producao():
    usuario = Usuario[session['username']]
    quantidade_produzida1kg = request.form['quantidade_produzida1kg']
    quantidade_produzida500g = request.form['quantidade_produzida500g']
    quantidade_produzida200g = request.form['quantidade_produzida200g']
    perda_kg = request.form['perda_kg']
    low_cort = request.form['low_cort']
    sku = request.form["sku_carretel"]
    observacao = request.form["observacao"]
    materia_prima = request.form["materia_prima"]

    peso = Sku[sku][3]
    material = Sku[sku][0]
    cor = Sku[sku][1]
    diametro = Sku[sku][2]
    
    id = usuario['id']
    ano = str(datetime.today().year)[3:]
    mes = datetime.today().month
    dia = datetime.today().day
    turno = str(Usuario[str(session['username'])]['turno'])[0]
    maquina = str(Usuario[str(session['username'])]['maquina'])

    # Formatação do dia
    if len(str(dia)) == 1:
        dia = f"0{dia}"
    
    lote = f"{ano}{letra_mes[mes]}{dia}{turno}{maquina}"
    
    # Armazenar os dados de produção em uma chave
    production_data = {
        'sku': sku,
        "materia_prima":materia_prima,
        'material':material,
        "cor":cor,
        "diametro":diametro,
        'produzida': quantidade_produzida1kg,
        "produzida500g":quantidade_produzida500g,
        "produzida200g":quantidade_produzida200g,
        'perda': perda_kg,
        'low': low_cort,
        "ID": id,
        'lote': lote,
        "observacao" : observacao
    }
    
    global Produzidos
    
    # Verifica se a data está no dicionário Produzidos[0]
    if data2 not in Produzidos[0]:
        Produzidos[0][data2] = []

    # Adiciona a produção no início da lista para a data
    Produzidos[0][data2].insert(0, production_data)
    
    # Atualiza o dicionário global
    registro_pd.update(Produzidos[0])

    # Verifica e atualiza o Requisicao
    if str(production_data["sku"]) in Requisicao[maquina]:
        valor = float(Requisicao[maquina][sku]['quantidade'])
        valor -= float(production_data["produzida"])
        Requisicao[maquina][sku]['quantidade'] = valor
        if Requisicao[maquina][sku]['quantidade'] <= 0:
            del Requisicao[maquina][sku]
    

        nome = usuario["nome"]
        
        # Funções para gravar dados
        grava_producao()
        gravar_requisicao()
        Criar_excel()
        
        # Renderiza a página com as informações atualizadas
        return redirect(url_for("fechamento"))
    else:
        return render_template("erro_sku.html")     

@app.route('/registrar-producao-cliever', methods=['POST'])
def registrar_producao_cliever():
    usuario = Usuario[session['username']]
    quantidade_produzida1kg = request.form['quantidade_produzida1kg']
    quantidade_produzida500g = request.form['quantidade_produzida500g']
    quantidade_produzida200g = request.form['quantidade_produzida200g']
    perda_kg = request.form['perda_kg']
    low_cort = request.form['low_cort']
    sku = request.form['sku_carretel']
    observacao = request.form['observacao']
    materia_prima = request.form['materia_prima']

    peso = Sku_cliever[sku][3]
    material = Sku_cliever[sku][0]
    cor = Sku_cliever[sku][1]
    diametro = Sku_cliever[sku][2]
    
    id = usuario['id']
    ano = data[-1:]
    mes = datetime.today().month
    dia = datetime.today().day
    turno = str(Usuario[str(session['username'])]['turno'])[0]
    maquina = str(Usuario[str(session['username'])]['maquina'])

    if len(str(dia)) == 1:
        dia = f"0{dia}"
    
    lote = f"{ano}{letra_mes[mes]}{dia}{turno}{maquina}"
    
    # Armazenar os dados de produção em uma chave
    production_data = {
        'sku': sku,
        "materia_prima":materia_prima,
        'material':material,
        'cor':cor,
        "diametro":diametro,
        'produzida': quantidade_produzida1kg,
        "produzida500g":quantidade_produzida500g,
        "produzida200g":quantidade_produzida200g,
        'perda': perda_kg,
        'low': low_cort,
        "ID": id,
        'lote': lote,
        'observacao':observacao
    }

    global Produzidos

    # Verifica se a data está no dicionário Produzidos[0]
    if data2 not in Produzidos[0]:
        Produzidos[0][data2] = []

    # Adiciona a produção no início da lista para a data
    Produzidos[0][data2].insert(0, production_data)
        
    # Atualiza o dicionário global
    registro_pd.update(Produzidos[0])

    if str(production_data["sku"]) in str(Requisicao[maquina]):
        valor = float(Requisicao[maquina][sku]['quantidade'])
        valor -= float(production_data["produzida"])
        Requisicao[maquina][sku]['quantidade'] = valor
        if Requisicao[maquina][sku]['quantidade'] <= 0:
            del Requisicao[maquina][sku]

    grava_producao()
    gravar_requisicao()

    # Renderiza a página com as informações atualizadas
    return redirect(url_for("fechamento"))



def gravar_observacao():
    script = f'#coding : utf-8 \nObservacao = {Observacao}'
    txt = open('observacao.py','w',encoding="utf-8")
    txt.write(script)
    txt.close()

@app.route("/enviar_observacao",methods=["GET",'POST'])
def enviar_observacao():
    observacao = request.form.get('observacao')
    maquinas = request.form.getlist('maquinas')
    global Observacao
    
    if Observacao != 0:
        Observacao = {
            'maquina1':"",
            'maquina2':'',
            'maquina3':''
        }

    for maquina in maquinas:
        Observacao[maquina] = str(observacao).upper()
    
    gravar_observacao()
    
    return render_template("adicionar_observacao.html")

@app.route("/adicionar_observacao",methods=["GET","POST"])
def adicionar_observacao():
    return render_template("adicionar_observacao.html")

def gravar_requisicao():
    script = f'#coding : utf-8 \nRequisicao = {Requisicao}'
    txt = open('requisicao.py','w',encoding="utf-8")
    txt.write(script)
    txt.close()
   

dados = {}
def preencher_dados(id):
    global dados
    if id in MAQUINA_4:
        maquina_info = MAQUINA_4[id]
        dados[id] = {}  # Inicializa a estrutura para o id
        for heater, zonas in maquina_info.items():
            dados[id][heater] = {}
            for key, value in zonas.items():
                # Atualiza os dados com os valores de MAQUINA_4
                dados[id][heater][key] = value
    elif id in MAQUINA_4_cliever:
        maquina_info = MAQUINA_4_cliever[id]
        dados[id] = {}  # Inicializa a estrutura para o id
        for heater, zonas in maquina_info.items():
            dados[id][heater] = {}
            for key, value in zonas.items():
                # Atualiza os dados com os valores de MAQUINA_4
                dados[id][heater][key] = value

    return dados


@app.route('/registrar-requisicao', methods=["GET", "POST"])
def registrar_requisicao():
    data = request.form['data']
    sku = request.form['sku']

    # Verificar se o SKU e a máquina são válidos
    if str(sku) in Preset.get(f"MAQUINA {ref_maquina}", {}) and sku in Sku:
        tipo_material = str(Sku[sku][0]).upper()
        cor = str(Sku[sku][1]).upper()
        porcentagem = Sku[sku][5]
        carretel = Sku[sku][3]
        quantidade = request.form['quantidade']
        velocidade = request.form['velocidade']
        diametro = Sku[sku][2]
        
        # Obter dados específicos para a máquina
        if f"MAQUINA {ref_maquina}" in Preset :
            preset_data = Preset[f"MAQUINA {ref_maquina}"]
            zona1 = preset_data[sku][0]
            zona2 = preset_data[sku][1]
            zona3 = preset_data[sku][2]
            zona4 = preset_data[sku][3]
            cabecote = preset_data[sku][4]
            bico = preset_data[sku][5]
            c1 = preset_data[sku][6]
            c2 = preset_data[sku][7]
        else:
            # Se a máquina não tiver preset, definir valores padrão ou tratar erro
            zona1 = zona2 = zona3 = zona4 = cabecote = bico = 0

        # Criar um dicionário com as informações da produção
        production_info = {
            sku: {
                'tipo_material': tipo_material,
                'cor': cor,
                'porcentagem': porcentagem,
                'carretel': carretel,
                'quantidade': quantidade,
                'quantidade_solicitada': quantidade,
                'velocidade': velocidade,
                'diametro': diametro,
                "data":data,
                'zona1': zona1,
                'zona2': zona2,
                'zona3': zona3,
                'zona4': zona4,
                'cabecote': cabecote,
                'bico': bico,
                "c1":c1,
                "c2":c2
            }
        }

    elif str(sku) in Preset_cliever.get(f"MAQUINA {ref_maquina}", {}) and sku in Sku_cliever:
        tipo_material = str(Sku_cliever[sku][0]).upper()
        cor = str(Sku_cliever[sku][1]).upper()
        porcentagem = Sku_cliever[sku][5]
        carretel = Sku_cliever[sku][3]
        quantidade = request.form['quantidade']
        velocidade = request.form['velocidade']
        diametro = Sku_cliever[sku][2]
        
        # Obter dados específicos para a máquina
        if f"MAQUINA {ref_maquina}" in Preset_cliever :
            preset_data = Preset_cliever[f"MAQUINA {ref_maquina}"]
            zona1 = preset_data[sku][0]
            zona2 = preset_data[sku][1]
            zona3 = preset_data[sku][2]
            zona4 = preset_data[sku][3]
            cabecote = preset_data[sku][4]
            bico = preset_data[sku][5]
            c1 = preset_data[sku][6]
            c2 = preset_data[sku][7]
        else:
            # Se a máquina não tiver preset, definir valores padrão ou tratar erro
            zona1 = zona2 = zona3 = zona4 = cabecote = bico = 0

        # Criar um dicionário com as informações da produção
        production_info = {
            sku: {
                'tipo_material': tipo_material,
                'cor': cor,
                'porcentagem': porcentagem,
                'carretel': carretel,
                'quantidade': quantidade,
                'quantidade_solicitada': quantidade,
                'velocidade': velocidade,
                'diametro': diametro,
                "data":data,
                'zona1': zona1,
                'zona2': zona2,
                'zona3': zona3,
                'zona4': zona4,
                'cabecote': cabecote,
                'bico': bico,
                "c1":c1,
                "c2":c2
            }
        }

    
    elif ref_maquina == "4" and sku in MAQUINA_4 and sku in Sku:
        tipo_material = str(Sku[sku][0]).upper()
        cor = str(Sku[sku][1]).upper()
        porcentagem = Sku[sku][5]
        carretel = Sku[sku][3]
        quantidade = request.form['quantidade']
        velocidade = request.form['velocidade']
        diametro = Sku[sku][2]

        preencher_dados(sku)  # Presumindo que isso define a variável 'dados'

        
        # Criar um dicionário com as informações da produção
        production_info = {
            sku: {
                'tipo_material': tipo_material,
                'cor': cor,
                'porcentagem': porcentagem,
                'carretel': carretel,
                'quantidade': quantidade,
                'quantidade_solicitada': quantidade,
                'velocidade': velocidade,
                'diametro': diametro,
                "data":data,
                'configuracao': dados[sku]
            }
        }
    
    
    elif ref_maquina == "4" and sku in MAQUINA_4_cliever and sku in Sku_cliever:
        tipo_material = str(Sku_cliever[sku][0]).upper()
        cor = str(Sku_cliever[sku][1]).upper()
        porcentagem = Sku_cliever[sku][5]
        carretel = Sku_cliever[sku][3]
        quantidade = request.form['quantidade']
        velocidade = request.form['velocidade']
        diametro = Sku_cliever[sku][2]

        preencher_dados(sku)  # Presumindo que isso define a variável 'dados'
       
        # Criar um dicionário com as informações da produção
        production_info = {
            sku: {
                'tipo_material': tipo_material,
                'cor': cor,
                'porcentagem': porcentagem,
                'carretel': carretel,
                'quantidade': quantidade,
                'quantidade_solicitada': quantidade,
                'velocidade': velocidade,
                'diametro': diametro,
                "data":data,
                'configuracao': dados[sku]
            }
        }
    
    
    else:
        return "sku nao vinculado ao preset"

    # Atualizar o dicionário Requisicao
    if ref_maquina not in Requisicao:
        Requisicao[ref_maquina] = {}

    

    Requisicao[ref_maquina].update(production_info)

    # Função fictícia para salvar os dados no banco de dados ou arquivo
    gravar_requisicao()
    
    return render_template("requisitar_producao.html", Requisicao=Requisicao,maquina=ref_maquina,ref_maquina=ref_maquina)


    

@app.route('/maquina1',methods=["GET","POST"])
def maquina1():
    maquina="1"
    global ref_maquina
    ref_maquina = maquina
    return render_template("requisitar_producao.html",Requisicao=Requisicao,maquina=maquina,ref_maquina=ref_maquina)

@app.route('/maquina2',methods=["GET","POST"])
def maquina2():
    maquina="2"
    global ref_maquina
    ref_maquina = maquina
    return render_template("requisitar_producao.html",Requisicao=Requisicao,maquina=maquina,ref_maquina=ref_maquina)

@app.route('/maquina3',methods=["GET","POST"])
def maquina3():
    maquina="3"
    global ref_maquina
    ref_maquina = maquina
    return render_template("requisitar_producao.html",Requisicao=Requisicao,maquina=maquina,ref_maquina=ref_maquina)

@app.route('/maquina4',methods=["GET","POST"])
def maquina4():
    maquina="4"
    global ref_maquina
    ref_maquina = maquina
    return render_template("requisitar_producao.html",Requisicao=Requisicao,maquina=maquina,ref_maquina=ref_maquina)

@app.route('/requisita-producao',methods=["GET",'POST'])
def requisitar_producao():
    return render_template("requisitar.html")

@app.route("/gestor",methods=["GET","POST"])
def gestor():
    return render_template("gestao.html",data=data ,usuario = Usuario[str(session['username'])] , gestor=Usuario[str(session['username'])]["gestor"],qualidade=Usuario[str(session['username'])])

@app.route("/",methods=["GET",'POST'])
def adm_tela():
    return render_template("adm_tela.html")

@app.route("/tela",methods=["GET",'POST'])
def tela():
    dados_maquina = {}
    id = request.form['tela']

    
    
    if len(Requisicao) != 0:
        for maquina in Requisicao:
            if int(id) == int(maquina):
                
                if id not in dados_maquina:
                    dados_maquina[id] = {}
                for sku in Requisicao[id]:
                    info = Requisicao[id][sku]
                    dados_maquina[id][sku] = info
    
    configuracao = ''
    producao_atual = ""
    primeiro_sku = ''
    if len(dados_maquina) != 0 :
        if len(dados_maquina[id]) != 0:
            primeiro_sku = list(dados_maquina[id].keys())[0]
            sku_detalhes = dados_maquina[id][primeiro_sku]
            producao_atual = sku_detalhes
            configuracao = {primeiro_sku:sku_detalhes}

    
       
     

    Requisicao_ordenado = ""
    

    # Obter as chaves do dicionário interno
    if id in dados_maquina:
        skus = list(dados_maquina[id].keys())

    # Remover o primeiro SKU
        if skus:
            primeiro_sku = skus[0]
            # Criar uma nova cópia do dicionário sem o primeiro SKU
            dados_filtrados = {sku: detalhes for sku, detalhes in dados_maquina[id].items() if sku != primeiro_sku}

            Requisicao_ordenado = dados_filtrados
    
    preset = producao_atual
    texto = ""
    produzidos = []

    
    if primeiro_sku in Requisicao[id]:
        base = Requisicao[id][primeiro_sku]
        produzidos.append(int(int(base['quantidade_solicitada']) - int(base['quantidade'])))


                    
    if len(Observacao) != 0:
        if not f"maquina{id}" in Observacao:
            Observacao.update({f"maquina{id}":""})
        texto = Observacao[f'maquina{id}']
    
    pd = ""
    falta_produzir = ''
    if len(producao_atual) != 0:
        producao_atual["quantidade"]
        falta_produzir = producao_atual["quantidade"]
    
    ja_produzido = sum(produzidos)

    if id == "4":
        
        config_preset = {}
        if 'configuracao' in producao_atual:
            config_preset = producao_atual["configuracao"]
        return render_template("tela_maquina4.html",primeiro_item=configuracao,config_preset=config_preset,pendente=producao_atual,ja_produzido = sum(produzidos),texto=Observacao["maquina4"])

    return render_template("tela.html",Requisicao=Requisicao_ordenado,maquina=id,primeiro_item=configuracao,proxima_item=pd,texto=texto,preset=preset,ja_produzido=ja_produzido,falta_produzir=falta_produzir)

################################

@app.route("/tela1",methods=["GET",'POST'])
def tela1():
    dados_maquina = {}
    id = "1"

    
    
    if len(Requisicao) != 0:
        for maquina in Requisicao:
            if int(id) == int(maquina):
                
                if id not in dados_maquina:
                    dados_maquina[id] = {}
                for sku in Requisicao[id]:
                    info = Requisicao[id][sku]
                    dados_maquina[id][sku] = info
    
    configuracao = ''
    producao_atual = ""
    primeiro_sku = ''
    if len(dados_maquina) != 0 :
        if len(dados_maquina[id]) != 0:
            primeiro_sku = list(dados_maquina[id].keys())[0]
            sku_detalhes = dados_maquina[id][primeiro_sku]
            producao_atual = sku_detalhes
            configuracao = {primeiro_sku:sku_detalhes}

    
     
     

    Requisicao_ordenado = ""
    

    # Obter as chaves do dicionário interno
    if id in dados_maquina:
        skus = list(dados_maquina[id].keys())

    # Remover o primeiro SKU
        if skus:
            primeiro_sku = skus[0]
            # Criar uma nova cópia do dicionário sem o primeiro SKU
            dados_filtrados = {sku: detalhes for sku, detalhes in dados_maquina[id].items() if sku != primeiro_sku}

            Requisicao_ordenado = dados_filtrados
    
    preset = producao_atual
    texto = ""
    produzidos = []

    
    if primeiro_sku in Requisicao[id]:
        base = Requisicao[id][primeiro_sku]
        produzidos.append(int(int(base['quantidade_solicitada']) - int(base['quantidade'])))


                    
    if len(Observacao) != 0:
        if not f"maquina{id}" in Observacao:
            Observacao.update({f"maquina{id}":""})
        texto = Observacao[f'maquina{id}']
    
    pd = ""
    falta_produzir = ''
    if len(producao_atual) != 0:
        producao_atual["quantidade"]
        falta_produzir = producao_atual["quantidade"]
    
    ja_produzido = sum(produzidos)

    if len(Requisicao_ordenado) >= 3:
        Requisicao_ordenado = dict(list(Requisicao_ordenado.items())[:4])
    return render_template("tela.html",Requisicao=Requisicao_ordenado,maquina=id,primeiro_item=configuracao,proxima_item=pd,texto=texto,preset=preset,ja_produzido=ja_produzido,falta_produzir=falta_produzir)


@app.route("/tela2",methods=["GET",'POST'])
def tela2():
    dados_maquina = {}
    id = "2"

    
    
    if len(Requisicao) != 0:
        for maquina in Requisicao:
            if int(id) == int(maquina):
                
                if id not in dados_maquina:
                    dados_maquina[id] = {}
                for sku in Requisicao[id]:
                    info = Requisicao[id][sku]
                    dados_maquina[id][sku] = info
    
    configuracao = ''
    producao_atual = ""
    primeiro_sku = ''
    if len(dados_maquina) != 0 :
        if len(dados_maquina[id]) != 0:
            primeiro_sku = list(dados_maquina[id].keys())[0]
            sku_detalhes = dados_maquina[id][primeiro_sku]
            producao_atual = sku_detalhes
            configuracao = {primeiro_sku:sku_detalhes}

    
     
     

    Requisicao_ordenado = ""
    

    # Obter as chaves do dicionário interno
    if id in dados_maquina:
        skus = list(dados_maquina[id].keys())

    # Remover o primeiro SKU
        if skus:
            primeiro_sku = skus[0]
            # Criar uma nova cópia do dicionário sem o primeiro SKU
            dados_filtrados = {sku: detalhes for sku, detalhes in dados_maquina[id].items() if sku != primeiro_sku}

            Requisicao_ordenado = dados_filtrados
    
    preset = producao_atual
    texto = ""
    produzidos = []

    
    
    if primeiro_sku in Requisicao[id]:
        base = Requisicao[id][primeiro_sku]
        produzidos.append(int(int(base['quantidade_solicitada']) - int(base['quantidade'])))

                    
    if len(Observacao) != 0:
        if not f"maquina{id}" in Observacao:
            Observacao.update({f"maquina{id}":""})
        texto = Observacao[f'maquina{id}']
    
    pd = ""
    falta_produzir = ''
    if len(producao_atual) != 0:
        producao_atual["quantidade"]
        falta_produzir = producao_atual["quantidade"]
    
    ja_produzido = sum(produzidos)

    if len(Requisicao_ordenado) >= 3:
        Requisicao_ordenado = dict(list(Requisicao_ordenado.items())[:4])

    return render_template("tela.html",Requisicao=Requisicao_ordenado,maquina=id,primeiro_item=configuracao,proxima_item=pd,texto=texto,preset=preset,ja_produzido=ja_produzido,falta_produzir=falta_produzir)


@app.route("/tela3",methods=["GET",'POST'])
def tela3():
    dados_maquina = {}
    id = "3"

    
    
    if len(Requisicao) != 0:
        for maquina in Requisicao:
            if int(id) == int(maquina):
                
                if id not in dados_maquina:
                    dados_maquina[id] = {}
                for sku in Requisicao[id]:
                    info = Requisicao[id][sku]
                    dados_maquina[id][sku] = info
    
    configuracao = ''
    producao_atual = ""
    primeiro_sku = ''
    if len(dados_maquina) != 0 :
        if len(dados_maquina[id]) != 0:
            primeiro_sku = list(dados_maquina[id].keys())[0]
            sku_detalhes = dados_maquina[id][primeiro_sku]
            producao_atual = sku_detalhes
            configuracao = {primeiro_sku:sku_detalhes}

    
        
     

    Requisicao_ordenado = ""
    

    # Obter as chaves do dicionário interno
    if id in dados_maquina:
        skus = list(dados_maquina[id].keys())

    # Remover o primeiro SKU
        if skus:
            primeiro_sku = skus[0]
            # Criar uma nova cópia do dicionário sem o primeiro SKU
            dados_filtrados = {sku: detalhes for sku, detalhes in dados_maquina[id].items() if sku != primeiro_sku}

            Requisicao_ordenado = dados_filtrados
    
    preset = producao_atual
    texto = ""
    produzidos = []

    

    if primeiro_sku in Requisicao[id]:
        base = Requisicao[id][primeiro_sku]
        produzidos.append(int(int(base['quantidade_solicitada']) - int(base['quantidade'])))
                    
    if len(Observacao) != 0:
        if not f"maquina{id}" in Observacao:
            Observacao.update({f"maquina{id}":""})
        texto = Observacao[f'maquina{id}']
    
    pd = ""
    falta_produzir = ''
    if len(producao_atual) != 0:
        producao_atual["quantidade"]
        falta_produzir = producao_atual["quantidade"]
    
    ja_produzido = sum(produzidos)
    
    if len(Requisicao_ordenado) >= 3:
        Requisicao_ordenado = dict(list(Requisicao_ordenado.items())[:4])

    
    return render_template("tela.html",Requisicao=Requisicao_ordenado,maquina=id,primeiro_item=configuracao,proxima_item=pd,texto=texto,preset=preset,ja_produzido=ja_produzido,falta_produzir=falta_produzir)


@app.route("/tela4",methods=["GET",'POST'])
def tela4():
    dados_maquina = {}
    id = "4"

    
    
    if len(Requisicao) != 0:
        for maquina in Requisicao:
            if int(id) == int(maquina):
                
                if id not in dados_maquina:
                    dados_maquina[id] = {}
                for sku in Requisicao[id]:
                    info = Requisicao[id][sku]
                    dados_maquina[id][sku] = info
    
    configuracao = ''
    producao_atual = ""
    primeiro_sku = ''
    if len(dados_maquina) != 0 :
        if len(dados_maquina[id]) != 0:
            primeiro_sku = list(dados_maquina[id].keys())[0]
            sku_detalhes = dados_maquina[id][primeiro_sku]
            producao_atual = sku_detalhes
            configuracao = {primeiro_sku:sku_detalhes}

    
    
     

    Requisicao_ordenado = ""
    

    # Obter as chaves do dicionário interno
    if id in dados_maquina:
        skus = list(dados_maquina[id].keys())

    # Remover o primeiro SKU
        if skus:
            primeiro_sku = skus[0]
            # Criar uma nova cópia do dicionário sem o primeiro SKU
            dados_filtrados = {sku: detalhes for sku, detalhes in dados_maquina[id].items() if sku != primeiro_sku}

            Requisicao_ordenado = dados_filtrados
    
    preset = producao_atual
    texto = ""
    produzidos = []

    
    if primeiro_sku in Requisicao[id]:
        base = Requisicao[id][primeiro_sku]
        produzidos.append(int(int(base['quantidade_solicitada']) - int(base['quantidade'])))


                    
    if len(Observacao) != 0:
        if not f"maquina{id}" in Observacao:
            Observacao.update({f"maquina{id}":""})
        texto = Observacao[f'maquina{id}']
    
    pd = ""
    falta_produzir = ''
    if len(producao_atual) != 0:
        producao_atual["quantidade"]
        falta_produzir = producao_atual["quantidade"]
    
    ja_produzido = sum(produzidos)

    
        
    config_preset = {}
    if 'configuracao' in producao_atual:
        config_preset = producao_atual["configuracao"]
    if len(Requisicao_ordenado) >= 3:
        Requisicao_ordenado = dict(list(Requisicao_ordenado.items())[:2])
    
    
    return render_template("tela_maquina4.html",Requisicao = Requisicao_ordenado,primeiro_item=configuracao,config_preset=config_preset,pendente=producao_atual,ja_produzido = sum(produzidos),texto=Observacao["maquina4"])

    


if __name__ == "__main__":
    import os
    print("Servidor Online ")
    
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    app.run(debug=debug, host="0.0.0.0", port=port)
    
