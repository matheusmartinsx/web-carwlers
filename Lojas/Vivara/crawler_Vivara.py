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
import ast
import os
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
        writer.writerow(['Código','Título','Descrição','Preço','Categoria','Imagens', 'Tamanho'])

#Verificação de coleta realizada no dia ou criação de novo arquivo de coleta
fileProducts = Path(my_path+'/leituras/produtos'+now+'.csv')
if fileProducts.is_file():
    with open(my_path+'/leituras/produtos'+now+'.csv', 'r', encoding="Latin1") as f:
        listaProdutos = list(csv.reader(f))
        for i in range(len(listaProdutos)):
            listaProdutos[i] = str(listaProdutos[i][0])
        print('Encontrados '+ str(len(listaProdutos)-1)+' já lidos hoje')
        sleep(0.2)
else:
    with open(my_path+'/leituras/produtos'+now+'.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Código','Título','Descrição','Preço','Categoria','Imagens', 'Tamanho'])

#Inicialização dos serviços e navegador
service = Service('C:/Program Files/Google/Chrome/Application/chromedriver')
service.start()
driver = webdriver.Remote(service.service_url)
driver.get('https://www.vivara.com.br/')
actions = webdriver.ActionChains(driver)
touchActions = webdriver.TouchActions(driver)
soup = BeautifulSoup(driver.page_source)
sleep(2)
#Criação da variável de produtos já coletados
coletados = []
produtos = []
linksCapturados = []
scroll_pause_time = 2

#Função de conversão de elemento BS para Xpath
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

#Coleta dos links do menu, ignorando os dois últimos
ulMenu = driver.find_elements_by_xpath('./html/body/div[3]/div[1]/div[1]/div[2]/div/header/nav/ul/li')
a = []
for i in range(len(ulMenu)-2):
    a.append(ulMenu[i].find_element_by_tag_name('a').get_attribute('href'))

#Repetição para leitura de todos os menus
for i in range(len(a)):
    #Ignora a categoria "Presentes"
    if 'https://www.vivara.com.br/presentes' in str(driver.page_source):
        continue
    #Inicializa a estrura de mudança de paginas
    cont = 0
    urlNext = a[i]+'?No='

    #Repetição de leitura de links enquanto houverem paginas novas
    while True:
        driver.get(urlNext+str(cont))
        sleep(3)
        soup = BeautifulSoup(driver.page_source)
        limiteScroll = soup.find("strong", {"class": "qtd-prod"})
        limiteScroll = driver.find_element_by_xpath(xpath_soup(limiteScroll))
        driver.execute_script("arguments[0].scrollIntoView(true);", limiteScroll)

        sleep(1)
        linksCapturados = []
        try:
            vitrines = soup.findAll("div", {"class": "box-product-new"})
        except:
            break
        cont += 20
        if len(vitrines) == 0:
            break
        for j in range(len(vitrines)):
            try:
                prod = driver.find_element_by_xpath(xpath_soup(vitrines[j]))
                linksCapturados.append(prod.find_element_by_tag_name('a').get_attribute('href'))
            except:
                continue
        sleep(0.5)
        try:
            with open(my_path+'/linksLidos.csv', 'r') as f:
                listaCapturados = list(csv.reader(f))
                for j in range(len(listaCapturados)):
                    listaCapturados[j] = str(listaCapturados[j])
            print('Já foram armazenados '+ str(len(listaCapturados))+' links para coleta')
            sleep(0.2)
        except:
            print('Nenhum link separado para coleta ainda.')
    
        for k in range(len(linksCapturados)):
            if linksCapturados[k] in produtos:
                continue
            elif 'https://www.vivara.com.br/vivara/produto/' not in str(linksCapturados[k]):
                continue
            else:
                produtos.append(linksCapturados[k])
                with open(my_path+'/linksLidos.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([linksCapturados[k]])


#Coleta dos dados dos produtos
for k in range(len(produtos)):
    #Se o link já constar na lista de coletados, pular
    if produtos[k] in coletados:
        print('Produto [' + produtos[k]+'] encontrado em arquivo!')
        continue
    
    driver.get(produtos[k])
    sleep(3)
    
    soup = BeautifulSoup(driver.page_source)
    info = soup.find("script", {"type": "application/ld+json"})
    info = str(info)
    try:
        info = info.split('<script type="application/ld+json">')[1]
        info = info.split('</script>')[0]
        dicInfo = ast.literal_eval(info)
    except:
        continue

    codigo = dicInfo['sku']
    titulo = dicInfo['name']
    print(str(k+1),'-',titulo)
    
    try:
        categoria = driver.find_element_by_xpath('/html/body/div[3]/div[2]/main/div/div[1]/div[1]/div/div/div/ul/li[3]/a').text
    except:
        try:
            categoria = driver.find_element_by_xpath('/html/body/div[3]/div[2]/main/div/div[1]/div[1]/div/div/div/ul/li[2]/a').text
        except:
            categoria = ''
    sleep(0.3) 
    
    try:
        preco = str(dicInfo['offers']['price']).replace('.',',')
    except:
        preco = ''
    sleep(0.3)
    
    tamList  = soup.findAll("span", {"class": "ng-binding ng-scope"})
    tamAux = []
    for j in range(len(tamList)):
        tamAux.append(str(tamList[j]))
    
    tam = ''
    for j in range(len(tamAux)):
        try:
            tamX = tamAux[j].split('<span class="ng-binding ng-scope">')[1]
            tamX = int(tamX.split('<!-- ngIf: s.availableStock')[0])
            tam += str(tamX)+';'
        except:
            continue
    tam = tam[:-1]

    desc = soup.find("div", {"class": "conteudo"})
    descricao = driver.find_element_by_xpath(xpath_soup(desc)).text
    descMenos = descricao.split('.')[-1]
    descricao = descricao.replace(descMenos, '')
    
    cont = -2    
    while len(descricao) > 400:
        descMenos = descricao.split('.')[cont]
        descricao = descricao.replace(descMenos, '')
        descricao = descricao[:-1]
        cont = -1
        
    sleep(0.3)
    imgLinks = dicInfo['image']
    for img in imgLinks:
        if 'http' not in img:
            imgLinks.remove(img)
    sleep(0.3)
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
    try:
        with open(my_path+'/produtos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            #               ['Código','Título','Descrição','Preço','Categoria','Imagens', 'Tamanho']
            writer.writerow([codigo, titulo, descricao, preco, categoria, imagem, tam])
            
        with open(my_path+'/leituras/produtos'+now+'.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            #               ['Código','Título','Descrição','Preço','Categoria','Imagens', 'Tamanho']
            writer.writerow([codigo, titulo, descricao, preco, categoria, imagem, tam])
    except UnicodeEncodeError:
            tituloEncode = titulo.encode("ascii", "ignore")
            titulo = tituloEncode.decode()
            with open(my_path+'/produtos.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                #               ['Código','Título','Descrição','Preço','Categoria','Imagens', 'Tamanho']
                writer.writerow([codigo, titulo, descricao, preco, categoria, imagem, tam])
                
            with open(my_path+'/leituras/produtos'+now+'.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                #               ['Código','Título','Descrição','Preço','Categoria','Imagens', 'Tamanho']
                writer.writerow([codigo, titulo, descricao, preco, categoria, imagem, tam])
            
    #Salvar link na lista de produtos já coletados
    with open(my_path+'/linksColetados.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([produtos[k]])
