from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
import os
import itertools
import requests
import csv
import re

my_path = os.getcwd()
my_path = my_path.replace('\\','/')

#Verificação da presença do arquivo de produtos
fileProducts = Path(my_path+'/produtos.csv')

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
        writer.writerow(['Código','Título','Descrição','Preço','Cor','Marca', 'Material','Dimensoes','Garantia', 'Img Links'])


#Inicialização dos serviços e navegador
service = Service('C:/Program Files/Google/Chrome/Application/chromedriver')
service.start()
driver = webdriver.Remote(service.service_url)
driver.get('https://www.lepostiche.com.br/')
actions = webdriver.ActionChains(driver)
touchActions = webdriver.TouchActions(driver)
soup = BeautifulSoup(driver.page_source)
sleep(2)
#Criação da variável de produtos já coletados
coletados = []
produtos = []

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

menus = driver.find_element_by_xpath('/html/body/section/header/div[5]/div/div/div/nav/ul').find_elements_by_tag_name('li')
a = []
categorias = []
for i in range(len(menus)):
    try:
        a.append(menus[i].find_element_by_tag_name('h3'))
    except:
        continue
for i in range(len(a)):
    categorias.append(a[i].find_element_by_tag_name('a').get_attribute('href'))

#Criar lista de produtos das categorias
for i in range(len(categorias)):
    pgAtual = int(1)
    driver.get(categorias[i]+'#/pagina-'+str(pgAtual))
    sleep(3)
    linksCapturados = []
    
    try:
        qtdPaginas = int(driver.find_element_by_xpath('/html/body/section/section/div/div/div[2]/div[3]/div/div/div/div[2]/footer/div/div[1]/div[1]/span[2]').text)
    except:
        qtdPaginas = int(driver.find_element_by_xpath('/html/body/section/section/div/div/div/div[3]/div/div/div/div[2]/footer/div/div[1]/div[1]/span[2]').text)        
    
    while pgAtual < qtdPaginas:
        try:
            vitrine = driver.find_element_by_xpath('/html/body/section/section/div/div/div[2]/div[3]/div/div/div/div[2]/article/div/ul').find_elements_by_tag_name('li')
        except:
            vitrine = driver.find_element_by_xpath('/html/body/section/section/div/div/div/div[3]/div/div/div/div[2]/article/div/ul').find_elements_by_tag_name('li')

        links = []
        for j in range(len(vitrine)):
            links.append(vitrine[j].find_element_by_tag_name('a').get_attribute('href'))
        for j in range(len(links)):
            if links[j] in linksCapturados:
                continue
            else:
                linksCapturados.append(links[j])
        pgAtual += 1
        driver.get(categorias[i]+'#/pagina-'+str(pgAtual))
        sleep(3)
        
    try:
        with open(my_path+'/linksLidos.csv', 'r') as f:
            linksRegistrados = list(csv.reader(f))
            for j in range(len(linksRegistrados)):
                linksRegistrados[i] = str(linksRegistrados[i])
        print('Já foram armazenados '+ str(len(linksRegistrados))+' links para coleta')
        sleep(0.2)
    except:
        print('Nenhum link separado para coleta ainda.')
        
    for k in range(len(linksCapturados)):
        with open(my_path+'/linksLidos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([linksCapturados[k]])


with open(my_path+'/linksLidos.csv', 'r') as f:
    linkList = list(csv.reader(f))
    for l in range(len(linkList)):
        produtos.append(str(linkList[l]))
print(str(len(produtos))+' produtos para coleta')
sleep(0.2)

for x in range(len(produtos)):
    produtos[x] = produtos[x].replace("['","")
    produtos[x] = produtos[x].replace("']","")

#Coleta dos dados dos produtos
for k in range(len(produtos)):
    #Se o link já constar na lista de coletados, pular
    if produtos[k] in coletados:
        print('Produto [' + produtos[k]+'] encontrado em arquivo!')
        continue
    
    driver.get(produtos[k])
    sleep(3)
    
    try:
        url = driver.current_url[-18:]
        code = url.split('/',1)[1]
        code = code.split('/')[0]
        soup = BeautifulSoup(driver.page_source)
        cod = soup.find('div', id=re.compile('^'+str(code)))
        codigo = driver.find_element_by_xpath(xpath_soup(cod)).find_element_by_class_name('sku').get_attribute('value')
    except:
        print('Código não encontrado!')
        #Salvar link na lista de produtos já coletados
        with open(my_path+'/linksComErro.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([produtos[k]])
        continue
        

    tit = soup.find('p', attrs={'class' : 'titlefake ativo'})
    titulo = driver.find_element_by_xpath(xpath_soup(tit)).text
        
    print(str(k+1),'-',titulo)
    
    try:
        categoria = driver.find_element_by_xpath('/html/body/section/section/div/div[1]/div/nav/ul/li[2]/a/span').text
    except:
        categoria = ''
    
    try:
        preco = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[1]/div/div[2]/div[3]/div[1]/div[1]/div/strong/span').text
    except:
        preco = ''
        
    descricao = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[4]/div/div/div[1]/div').text

    try:
        cor = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[1]/div/div[2]/div[2]/div[5]/div[1]/div[2]/p/span').text
    except:
        cor = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[1]/div/div[2]/div[2]/div[4]/div[1]/div[2]/p/span').text
    try: 
        caracteristicas = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[4]/div/div/div[2]/div[1]/div/div').text
        
        marca = caracteristicas.split("\nMarca: ")[1]
        marca = marca.split('\n')[0]
        
        material = caracteristicas.split("\nMaterial: ")[1]
        material = material.split('\n')[0]
        try:
            garantia = caracteristicas.split("\nGarantia do Fabricante: ")[1]
            garantia = garantia.split('\n')[0]
            garantia = garantia.split('.')[0]
        except:
            garantia = caracteristicas.split("\nGarantia: ")[1]
            garantia = garantia.split('\n')[0]
            garantia = garantia.split('.')[0]
    except:
        marca = ''
        material = ''
        garantia = ''

    
    altura = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[4]/div/div/div[2]/div[2]/div/div/ul/li[1]/span').text
    altura = altura.split(' cm')[0]
    largura = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[4]/div/div/div[2]/div[2]/div/div/ul/li[2]/span').text
    largura = largura.split(' cm')[0]
    profundidade = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[4]/div/div/div[2]/div[2]/div/div/ul/li[3]/span').text
    
    dimensoes = str(altura + 'x'+largura+'x'+profundidade)
    peso = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[4]/div/div/div[2]/div[2]/div/div/ul/li[4]/span').text
    
    imgLinks = []
    listaImagens = driver.find_element_by_xpath('/html/body/section/section/div/div[2]/article/div[1]/div/div[1]/figure/div[3]/ul/div/div').find_elements_by_tag_name('img')
    for l in range(len(listaImagens)):
        imgLinks.append(listaImagens[l].get_attribute('data-image-big'))

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
        #               [['Código','Título','Descrição','Preço','Cor','Marca', 'Material','Dimensoes','Garantia', 'Img Links']
        writer.writerow([codigo, titulo, descricao, preco, cor, marca, material, dimensoes, garantia, imagem])
    #Salvar link na lista de produtos já coletados
    with open(my_path+'/linksColetados.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([produtos[k]])