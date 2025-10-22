import webbrowser
import pyautogui
import time
time.sleep(10)

# URL que você deseja abrir
url = 'http://192.168.1.97:5000/tela3'

# Abre a URL no navegador padrão
webbrowser.open(url)


# Dá um pequeno atraso para garantir que você tenha tempo de mudar o foco para a janela desejada
time.sleep(10)


# Pressiona a tecla F11
pyautogui.press('f11')
