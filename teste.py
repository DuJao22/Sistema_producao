from Producoes import Produzidos

dados = {}

for data in Produzidos[0]:
    for producao in Produzidos[0][data] :
        kg1 = producao["produzida"]
        g500 = producao["produzida500g"]
        g200 = producao["produzida200g"]
        id = producao["ID"]

        informacoes = {id:{}}
        dados.update()