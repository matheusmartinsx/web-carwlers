from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
from datetime import datetime
import os
import ast
import itertools
import requests
import csv

my_path = os.getcwd()
my_path = my_path.replace('\\','/')

now = datetime.now()
now = str(now.year)+'-'+str(now.month)+'-'+str(now.day)

#Verificação da presença do arquivo de produtos
fileProducts = Path(my_path+'/produtos.csv')

#Verificação de coletas anteriores e criação de novo csv
if fileProducts.is_file():
    with open(my_path+'/produtos.csv', 'r', encoding="Latin1") as f:
        listaProdutos = list(csv.reader(f))
        for i in range(len(listaProdutos)):
            listaProdutos[i] = str(listaProdutos[i][0])
        print('Encontrados '+ str(len(listaProdutos)-1)+' produtos em arquivo')
        sleep(0.2)
else:
    with open(my_path+'/produtos.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Codigo','EAN','Título','Descrição','Preço','Imagens'])

#Verificação de coleta realizada no dia ou criação de novo arquivo de coleta
fileProducts = Path(my_path+'/leituras/produtos'+now+'.csv')
if fileProducts.is_file():
    with open(my_path+'/leituras/produtos-'+now+'.csv', 'r', encoding="Latin1") as f:
        listaProdutos = list(csv.reader(f))
        for i in range(len(listaProdutos)):
            listaProdutos[i] = str(listaProdutos[i][0])
        print('Encontrados '+ str(len(listaProdutos)-1)+' já lidos hoje')
        sleep(0.2)
else:
    with open(my_path+'/leituras/produtos-'+now+'.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Codigo','EAN','Título','Descrição','Preço','Imagens'])


#Inicialização dos serviços e navegador
service = Service('C:/Program Files/Google/Chrome/Application/chromedriver')
service.start()
driver = webdriver.Remote(service.service_url)
driver.get('https://www.chocolatesbrasilcacau.com.br/todos-os-produtos#1')
actions = webdriver.ActionChains(driver)
touchActions = webdriver.TouchActions(driver)
soup = BeautifulSoup(driver.page_source)
sleep(2)
#Criação da variável de produtos já coletados
coletados = []
produtos = []
linksCapturados = []

def xpath_soup(element):
    components = []
    child = element if element.name else element.parent 
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

#Atribuição dos itens já coletados na variável
try:
    with open(my_path+'/linksColetados.csv', 'r') as l:
        coletados = list(csv.reader(l))
        for i in range(len(coletados)):
            coletados[i] = str(coletados[i][0])
        print('Encontrados '+ str(len(coletados))+' links já coletados em arquivo')
        sleep(0.2)
except:      
    print('Dados anteriores não encontrados')   
                                #driver.findElement(By.xpath("//div[contains(text(),'"+expectedText+"')]")).click();


#Criar lista de produtos das categorias

while True:
    soup = BeautifulSoup(driver.page_source)
    btnNext = soup.find("button", {"class": "load-more"})
    sleep(0.5)
    try:
        btnNext = driver.find_element_by_xpath(xpath_soup(btnNext))
        driver.execute_script("arguments[0].scrollIntoView(false);", btnNext)
        sleep(0.5)
        btnNext.click()
        sleep(1)
    except:
        break
sleep(0.5)

try:
    with open(my_path+'/linksLidos.csv', 'r') as f:
        linksCapturados = list(csv.reader(f))
        for j in range(len(linksCapturados)):
            linksCapturados[i] = str(linksCapturados[i])
    print('Já foram armazenados '+ str(len(linksCapturados))+' links para coleta')
    sleep(0.2)
except:
    print('Nenhum link separado para coleta ainda.')
    
soup = BeautifulSoup(driver.page_source)
vitrines = soup.findAll("a", {"class": "product-item__img"})

for k in range(len(vitrines)):
    produtoAtual = driver.find_element_by_xpath(xpath_soup(vitrines[k])).get_attribute('href')
    if produtoAtual in produtos:
        continue
    else:
        produtos.append(produtoAtual)
        with open(my_path+'/linksLidos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([produtoAtual])

#Coleta dos dados dos produtos
for k in range(len(produtos)):
    #Se o link já constar na lista de coletados, pular
    if produtos[k] in coletados:
        print('Produto [' + produtos[k]+'] encontrado em arquivo!')
        continue
    
    driver.get(produtos[k])
    sleep(3)

    soup = BeautifulSoup(driver.page_source)
    scriptsPage = soup.findAll("script")
    info = ''
    
    for s in range(len(scriptsPage)):
        infoAx = str(scriptsPage[s])
        if 'vtex.events.addData(' in infoAx:
            infoAx = infoAx.split('vtex.events.addData(')[1]
            infoAx = infoAx.split(');\n</script>')[0]
            info = ast.literal_eval(infoAx)
        else:
            continue
    
    codigo = info['productReferenceId']
    ean = info['productEans'][0]
    titulo = info['productName']
    
    print(str(k+1),'-',titulo)

    try:
        preco = info['productPriceFrom']
    except:
        preco = info['productPriceTo']
    
    preco = preco.replace('.', ',')

    descricao = driver.find_element_by_xpath('/html/body/main/div[1]/div/div/div[2]/div[1]/div[6]/div[2]/div').text

    sleep(0.3)
    imgLinks = []
    imagens = driver.find_element_by_xpath('/html/body/main/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div/a/div/img')
    imgLinks.append(imagens.get_attribute('src'))
   
    cont = 0
    imagem = ''
    num = ''
    for l in range(len(imgLinks)):
        if cont > 0:
            num = '_' + str(cont)
        response = requests.get(imgLinks[l])
        file = open('imagens/' + codigo + num + '.jpg', 'wb')
        file.write(response.content)
        file.close()
        imagem += codigo + num + '.jpg, '
        sleep(0.5)
        cont += 1

    #Salvar produto na variável de coletados
    coletados.append(produtos[k])
    #Salvar dados no arquivo
    with open(my_path+'/produtos.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        #               ['Código','Título','Descrição','Preço','Imagens']
        writer.writerow([codigo, ean, titulo, descricao, preco, imagem])
    #Salvar link na lista de produtos já coletados
    with open(my_path+'/linksColetados.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([produtos[k]])