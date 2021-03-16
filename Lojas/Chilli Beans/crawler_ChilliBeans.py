from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from time import sleep
from pathlib import Path
import requests
import csv

#Verificação da presença do arquivo de produtos
fileProducts = Path('C:/Users/Matheus Martins/Desktop/Crawler Scripts/Chilli Beans/produtos.csv')
if fileProducts.is_file():
    with open('C:/Users/Matheus Martins/Desktop/Crawler Scripts/Chilli Beans/produtos.csv', 'r', encoding="Latin1") as f:
        listaProdutos = list(csv.reader(f))
        for i in range(len(listaProdutos)):
            listaProdutos[i] = str(listaProdutos[i][0])
        print('Encontrados '+ str(len(listaProdutos)-1)+' produtos em arquivo')
        sleep(0.2)
else:
    with open('C:/Users/Matheus Martins/Desktop/Crawler Scripts/Chilli Beans/produtos.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Código','Título','Categoria','Preço','Imagem','Foto','Descrição', 'Genero', 'Material Armação', 'Cor Armação', 'Garantia', 'Itens Inclusos', 'Ponte', 'Lente', 'Haste', 'Formato', 'Mostrador', 'Estilo', 'Pulseira', 'Cor Pulseira', 'Tamanho', 'Cor Mostrador', 'Material Caixa', 'Resistencia Profundidade', 'Largura Fixa', 'Tamanho Mostrador', 'Comprimento', 'Altura'])


#Inicialização dos serviços e navegador
service = Service('C:/Program Files/Google/Chrome/Application/chromedriver')
service.start()
driver = webdriver.Remote(service.service_url)
driver.get('https://loja.chillibeans.com.br/produtos')
sleep(2)
#Criação da variável de produtos já coletados
coletados = []

#Atribuição dos itens já coletados na variável
try:
    with open('C:/Users/Matheus Martins/Desktop/Crawler Scripts/Chilli Beans/linksColetados.csv', 'r') as l:
        coletados = list(csv.reader(l))
        for i in range(len(coletados)):
            coletados[i] = str(coletados[i][0])
        print('Encontrados '+ str(len(coletados))+' links já coletados em arquivo')
        sleep(0.2)

except:      
    print('Dados anteriores não encontrados')   

a = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[3]/div/div[1]/div[3]/div[3]/ul').find_elements_by_tag_name('a')
#Ler quantidade de categorias no site
categorias = []
for i in range(len(a)):
    categorias.append(a[i].get_attribute('href'))

#Criar lista de produtos das categorias
for i in range(len(categorias)):
    driver.get(categorias[i])
    sleep(2)

    produtos = []

    while True:
    #Enquanto houver um botão "Próximo", salvar links de produtos na variável
        sleep(3)
        try:
            div = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[3]/div/div[2]/div/div/div[2]/div[2]/div')
            ul = div.find_element_by_tag_name('ul').find_elements_by_tag_name('h3')
        except:
            break

        for k in range(len(ul)):
            produtos.append(ul[k].find_element_by_tag_name('a').get_attribute('href'))
        try:
            btProx = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[3]/div/div[2]/div/div/div[2]/div[3]/ul/li[8]').get_attribute('class')
            if btProx == 'next':
                driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[3]/div/div[2]/div/div/div[2]/div[3]/ul/li[8]').click()
            else:
                break 
        except:
            break
    #Coleta dos dados dos produtos
    for k in range(len(produtos)):
        #Se o link já constar na lista de coletados, pular
        if produtos[k] in coletados:
            print('Produto ' + produtos[k]+' encontrado em arquivo!')
            continue

        driver.get(produtos[k])
        sleep(2)
        #Se o link estiver quebrado, pular
        if 'ProductLinkNotFound' in driver.find_element_by_xpath('/html/body/iframe[3]').get_attribute('src'):
            print('Link não encontrado')
            continue

        try:
            codigo = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[2]/div/div[1]/div[1]/div[2]/div').text
        except:
            codigo = driver.find_element_by_xpath('/html/body/div[3]/div[1]/main/div[2]/div/div[1]/div[1]/div[2]/div').text
        

        titulo = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[2]/div/div[2]/div[2]/h1/div').text
        print(k,'-',titulo)
        try:
            categoria = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[1]/div/div/ul/li[2]/a/span').text
        except:
            categoria = ''
        
        try:
            preco = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[2]/div/div[2]/div[3]/div[2]/div/div/p[1]/em[2]/strong').text
        except:
            preco = ''
        foto = ''
        try:
            fotos = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[2]/div/div[1]/div[2]/div[1]/div[2]/ul/div[1]/div/div[2]/div').find_elements_by_tag_name('a')
            for l in range(len(fotos)):
                foto = str(fotos[l].get_attribute('rel'))
        except:
            fotos = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[2]/div/div[1]/div[2]/div[1]/div[2]/ul').find_elements_by_tag_name('a')
            for l in range(len(fotos)):
                foto += str(fotos[l].get_attribute('rel')) + ', '
            foto = foto[:-2]
                
        descricao = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[4]/div/div[1]/div[3]/div[1]').text
        
        genero = ''
        materialArmacao = ''
        corArmacao = ''
        garantia = ''
        itensInclusos = ''
        ponte = ''
        lente = ''
        haste = ''
        formato = ''
        mostrador = ''
        estilo = ''
        pulseira = ''
        corPulseira = ''
        tamanho = ''
        corMostrador = ''
        materialCaixa = ''
        resProf = ''
        largFixa = ''
        tamMostrador = ''
        comprimento = ''
        altura = ''
        
        try:
            tabelaEspecificacoes = driver.find_element_by_xpath('/html/body/div[4]/div[1]/main/div[4]/div/div[2]/div[3]/div/table/tbody')
            especificacoes = tabelaEspecificacoes.find_elements_by_tag_name('tr')

            for l in range (len(especificacoes)):
                nomeEspec = especificacoes[l].find_element_by_tag_name('th').text
                espec = especificacoes[l].find_element_by_tag_name('td').text
                if nomeEspec == 'Por Gênero':
                    genero = espec
                elif nomeEspec == 'Material da Armação':
                    materialArmacao = espec
                elif nomeEspec == 'Cor da Armação':
                    corArmacao = espec
                elif nomeEspec == 'Garantia':
                    garantia = espec
                elif nomeEspec == 'Itens Inclusos':
                    itensInclusos = espec
                elif nomeEspec == 'Ponte':
                    ponte = espec
                elif nomeEspec == 'Lente':
                    lente = espec
                elif nomeEspec == 'Haste':
                    haste = espec
                elif nomeEspec == 'Por formato':
                    formato = espec
                elif nomeEspec == 'Por Mostrador':
                    mostrador = espec
                elif nomeEspec == 'Por Estilo':
                    estilo = espec
                elif nomeEspec == 'Por Pulseira':
                    pulseira = espec
                elif nomeEspec == 'Cor da Pulseira':
                    corPulseira = espec
                elif nomeEspec == 'Por Tamanho':
                    tamanho = espec
                elif nomeEspec == 'Cor do Mostrador':
                    corMostrador = espec
                elif nomeEspec == 'Material da Caixa':
                    materialCaixa = espec
                elif nomeEspec == 'Resistência a Profundidade':
                    resProf = espec
                elif nomeEspec == 'Largura Fixa':
                    largFixa = espec
                elif nomeEspec == 'Mostrador':
                    tamMostrador = espec
                elif nomeEspec == 'Comprimento':
                    comprimento = espec
                elif nomeEspec == 'Altura':
                    altura = espec
        except:
            pass
        
        cont = 0
        num = ''
        imagem = ''
        links = foto.split(', ')
        for l in range(len(links)):
            if cont > 0:
                num = '_' + str(cont)
            response = requests.get(links[l])
            file = open('imagens/' + codigo + num + '.jpg', 'wb')
            file.write(response.content)
            file.close()
            imagem += codigo + num + '.jpg, '
            sleep(0.5)
            cont += 1
        imagem = imagem[:-2]

        #Salvar produto na variável de coletados
        coletados.append(produtos[k])
        #Salvar dados no arquivo
        with open('C:/Users/Matheus Martins/Desktop/Crawler Scripts/Chilli Beans/produtos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
                         #(['Código','Título','Categoria','Preço','Imagem','Foto','Descrição', 'Genero', 'Material Armação', 'Cor Armação', 'Garantia', 'Itens Inclusos', 'Ponte', 'Lente', 'Haste', 'Formato', 'Mostrador', 'Estilo', 'Pulseira', 'Cor Pulseira', 'Tamanho', 'Cor Mostrador', 'Material Caixa', 'Resistencia Profundidade', 'Largura Fixa', 'Tamanho Mostrador', 'Comprimento', 'Altura'])
            writer.writerow([codigo, titulo, categoria, preco, imagem, foto, descricao, genero, materialArmacao, corArmacao, garantia, itensInclusos, ponte, lente, haste, formato, mostrador, estilo, pulseira, corPulseira, tamanho, corMostrador, materialCaixa, resProf, largFixa, tamMostrador, comprimento, altura])
        #Salvar link na lista de produtos já coletados
        with open('C:/Users/Matheus Martins/Desktop/Crawler Scripts/Chilli Beans/linksColetados.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([produtos[k]])