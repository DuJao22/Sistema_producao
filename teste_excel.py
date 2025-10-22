import os
import pandas as pd
from Producoes import Produzidos

def Criar_excel():
    # Transformar os dados em um DataFrame
    data = []
    for entry in Produzidos:
        for date, records in entry.items():
            for record in records:
                record['data'] = date
                data.append(record)

    df = pd.DataFrame(data)

    # Obtém o caminho da área de trabalho
    home = os.path.expanduser("~")
    desktop_path = os.path.join(home, 'Desktop')

    # Define o caminho completo para o arquivo Excel
    excel_path = os.path.join(desktop_path, 'produzidos.xlsx')

    # Salvar o DataFrame em um arquivo Excel
    df.to_excel(excel_path, index=False, engine='openpyxl')

    print(f"Arquivo salvo em: {excel_path}")

# Chama a função para criar o Excel

