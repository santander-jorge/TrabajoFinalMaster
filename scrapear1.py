import pandas as pd
import os
import numpy as np


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

ruta_entrada = 'C:/Users/Usuario/Desktop/Datasets/dataset_rusia/tweets/dividido/1.csv'
ruta_salida = 'C:/Users/Usuario/Desktop/Datasets/dataset_rusia/tweets/finales/1.csv'

# Configuración de Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')  # Ejecuta Chrome en modo headless
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')  # Deshabilita el uso de GPU
chrome_options.add_argument('--disable-software-rasterizer')  # Deshabilita el rasterizador de software
chrome_options.add_argument('--disable-extensions')  # Deshabilita las extensiones de Chrome
chrome_options.add_argument('--disable-in-process-stack-traces')  # Deshabilita los stack traces en proceso
chrome_options.add_argument('--disable-logging')  # Deshabilita el registro
chrome_options.add_argument('--log-level=3')  # Establece el nivel de registro a 3 (solo errores fatales)
chrome_options.add_argument('--single-process')  # Ejecuta Chrome en un solo proceso
chrome_options.add_argument('--ignore-certificate-errors')  # Ignora errores de certificados SSL
chrome_options.add_argument('--homedir=/tmp')  # Usa /tmp como directorio home


chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# Ruta al ChromeDriver
chrome_driver_path = "C:/Users/Usuario/Desktop/chromedriver-win64/chromedriver-win64/chromedriver.exe"

# Crear el servicio de ChromeDriver
service = Service(chrome_driver_path)

# Inicializar el navegador
driver = webdriver.Chrome(service=service, options=chrome_options)


def get_tweet_author(tweet_url):
    
    account_name = ""
    account_handle = ""
    try:
        for url in tweet_url:


            # Abre la URL del tweet
            driver.get(url)
            
            # Espera hasta que el nombre del usuario esté presente en la página
            driver.implicitly_wait(np.random.randint(5, 10))
            
            try:
                # Extraer el nombre de la cuenta
                account_name_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"] span.css-1jxf684')
                account_name = account_name_element.text
                
                tweet_content_element = driver.find_element(By.TAG_NAME, 'article')
                tweet_content = tweet_content_element.text

                # Buscar la dirección de la cuenta dentro del contenido del tweet
                for word in tweet_content.split():
                    if word.startswith("@"):
                        account_handle = word
                        break

                
                account_handle = account_handle.replace('@', '')


                if account_name != "" or account_handle != "":
                    print(f"{account_name}\n@{account_handle}\nURL: {url}\n\n")
                    return [account_name, account_handle]
            
                # print(f"Nombre de la cuenta: {account_name}\nDirección de la cuenta: @{account_handle}\nURL: {url}\n\n")
            except Exception as e:
                # print(f'Error al cargar la URL: {url}\n')
                continue
                
        
        return [account_name, account_handle]
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
df = pd.read_csv(ruta_entrada, low_memory=False)

lista_tweets_en_rtweets = df[df['Tweet Type'] == 'ReTweet']['Tweet Content'].unique()
lista_tweets_explicitos = df[df['Tweet Type'] == 'Tweet']['Tweet Content'].unique()

lista_tweets_final = df['Tweet Content'].unique()

tweets_para_scrapear = [tweet for tweet in lista_tweets_final if tweet not in lista_tweets_explicitos]

# Sacar el diccionario con los tweets explicitos para ponerlos en los retweets
diccionario_tweets_explicitos = {}
for tweet in lista_tweets_explicitos:
    diccionario_tweets_explicitos[tweet] = df[df['Tweet Content'] == tweet]['Username'].values[0]

for tweet in diccionario_tweets_explicitos:
    df.loc[(df['Tweet Content'] == tweet) & (df['Tweet Type'] == 'ReTweet'), 'Original_Author'] = diccionario_tweets_explicitos[tweet]




import IPython.display as display

diccionario_tweets_faltantes = {}
actual = 0
total = len(tweets_para_scrapear)
for tweet_para_scrapeo in tweets_para_scrapear:
    urls_posibles = df[df['Tweet Content'] == tweet_para_scrapeo]['Tweet URL'].unique()
    actual+=1
    display.clear_output()
    print(f"Procesando tweet {actual} de {total}")
    diccionario_tweets_faltantes[tweet_para_scrapeo] = get_tweet_author(urls_posibles)

for texto_tweet in diccionario_tweets_faltantes:
    df.loc[(df['Tweet Content'] == texto_tweet) & (df['Tweet Type']=='ReTweet'), 'Original_Author'] = diccionario_tweets_faltantes[texto_tweet][1]



df.to_csv(ruta_salida, sep=';', index=False)


#Cerramos el navegador
driver.quit()