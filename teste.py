from DrissionPage import ChromiumPage
from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
import re
from altera_registro import seleciona_certificado

def validar_cnpj(cnpj: str) -> bool:
    print('VALIDANDO CNPJ')
    # Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, cnpj))

    # Verifica se o CNPJ tem 14 dígitos ou se todos os dígitos são iguais
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    # Definindo os pesos para o cálculo dos dígitos verificadores
    pesos_primeiro_dv = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo_dv = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcula o primeiro dígito verificador
    soma1 = sum(int(cnpj[i]) * pesos_primeiro_dv[i] for i in range(12))
    digito1 = (soma1 % 11)
    digito1 = 0 if digito1 < 2 else 11 - digito1

    # Calcula o segundo dígito verificador
    soma2 = sum(int(cnpj[i]) * pesos_segundo_dv[i] for i in range(13))
    digito2 = (soma2 % 11)
    digito2 = 0 if digito2 < 2 else 11 - digito2

    # Verifica se os dígitos verificadores estão corretos
    return digito1 == int(cnpj[12]) and digito2 == int(cnpj[13])

def extrair_mes_ano(data):
    try:
        # Divide a data no formato DD.MM.AAAA
        print(data)
        data = str(data).replace('/','.')
        print(data)
        partes = data.split(".")
        if len(partes) == 3:
            dia, mes, ano = partes
            # Retorna mês e ano como inteiros
            return mes, ano
        else:
            raise ValueError("Formato de data inválido. Use DD.MM.AAAA.")
    except Exception as e:
        print(f"Erro: {e}")
        return None

def formata_cnpj(cnpj):
    print('FORMATANDO CNPJ')
    cnpj_formatado = cnpj.replace('/','').replace('-','').replace('.','')
    return cnpj_formatado

def acessa_issnet(cnpj):
    seleciona_certificado()
    print('ACESSANDO ISS')
    global page
    try:
        page = ChromiumPage()
        page.set.when_download_file_exists('overwrite')
        page.get('https://iss.fazenda.df.gov.br/online/default/empresas.aspx')
    except:
        acessa_issnet(cnpj)
        return
    
    botao_logar_com_certificado = page.ele('xpath://*[@id="btnAcionaCertificado"]')
    
    if botao_logar_com_certificado: 
        botao_logar_com_certificado.click()
        area_empresas(cnpj)
        return
    else:
        print('botao_logar_com_certificado NÃO ENCONTRADO')
        area_empresas(cnpj)
        return

def area_empresas(cnpj):
    print('ACESSANDO AREA EMPRESAS')
    cnpj = formata_cnpj(cnpj)
    print(cnpj)
    page.wait(1)
    input_cpf_cnpj = page.ele('xpath://*[@id="TxtCPF"]')
    input_cpf_cnpj.input(cnpj)
    
    botao_pesquisar = page.ele('xpath://*[@id="imbLocalizar"]')
    botao_pesquisar.click()
    
    if page.ele('text:Contribuinte não encontrado.'):
        print(f'POR FAVOR VERIFIQUE SE O CERTIFICADO RELAMENTE POSSUI PROCURAÇÃO PARA A EMPRESA {razao_social}')
        return
    
    page.wait(5)
    erro = page.ele('xpath:/html/body/div[1]/div/div/div[2]/div')
    if erro:
        acessa_issnet(cnpj)
        return
    else:
        cancelar_informacao_cadastral(cnpj)
        return

def cancelar_informacao_cadastral(cnpj):
    print('CANCELANDO INFORMAÇÃO CADASTRAL')
    erro_internet = page.ele('xpath://*[@id="main-message"]/h1/span')
    
    if erro_internet:
        acessa_issnet(cnpj)
        return
    else:
        try:
            print('CANCELANDO INFORMAÇÕES CADASTRAIS')
            page.wait(3)
            botao_cancelar = page.ele('xpath://*[@id="btnVoltar"]', timeout=10)
            botao_cancelar.click()
        except:
            acessa_issnet(cnpj)
        area_principal()
        return

def area_principal():
    print('ENTRANDO NA AREA PRINCIPAL')
    page.wait(5)
    
    menu = page.ele('xpath://*[@id="contMenu"]')
    
    nota_eletronica = menu.ele('text:Nota Eletrônica')    
    if nota_eletronica :
        nota_eletronica.click()
        page.wait(1)
        
        box_nota_eletronica = nota_eletronica.parent().parent()
        print(box_nota_eletronica)
        
        nota_eletronica_em_lote = box_nota_eletronica.ele('text:Solicitação de Notas em Lote')
        nota_eletronica_em_lote.click()
        
                
        incluir_solicitacao = box_nota_eletronica.ele('text:Incluir')
        incluir_solicitacao.click()
                
        solicitar_notas_em_lote(data_inicial_formatada, data_final_formatada)
        return
    else:
        print('EMPRESA NÃO EMITE NOTAS DE SERVIÇO')
        tomador(data_inicial, data_final, nfse_nacional = False)
   
def solicitar_notas_em_lote(data_inicial, data_final):
    print('SOLICITANDO NOTAS EM LOTE')
    
    try:
        botao_filtros_adicionais = page.ele('xpath://*[@id="imbArrow"]')
        botao_filtros_adicionais.click()
        
        page.wait(3)
        
        botao_filtros_adicionais_conferencia = page.ele('xpath://*[@id="imbArrow"]')
        if botao_filtros_adicionais_conferencia:
            botao_filtros_adicionais.click()
    except:
        print('DEU ERRO DE POSICIONAMENTO NA SETINHA')
        page.refresh()
        page.wait(10)
        area_principal()
        return
        
    page.wait(5)
    try :
        input_data_inicial = page.ele('xpath://*[@id="datetimepicker1"]/span')
        input_data_inicial.focus()
        input_data_inicial.click()
        input_data_inicial.clear()
        input_data_inicial.input(data_inicial)
        page.wait(2)
        input_data_final = page.ele('xpath://*[@id="txtDtEmissaoFim"]')
        input_data_final.focus()
        input_data_final.click()
        input_data_final.clear()
        input_data_final.input(data_final)
        
        select_situacao_nf = page.ele('xpath://*[@id="ddlStatusNfse"]/option[2]')
        select_situacao_nf.click()
        
        btn_localizar  = page.ele('xpath://*[@id="btnLocalizar"]')
        btn_localizar.click()
        
        nenhum_xml_encontrado = page.ele('text:Nenhum registro encontrado.')
        if nenhum_xml_encontrado:
            mensagem = (f'A empresa: {razao_social}, não possui notas NFSe no período {data_inicial} - {data_final}\n')
            print(mensagem)
            relatorio.write(mensagem)
            page.refresh()
            
            mes, ano = extrair_mes_ano(data_inicial)
            diretorio_final = f'{diretorio_para_salvar_arquivos}/{numero_empresa}/{ano}/{mes}.{ano}'
            
            # Garantir que o diretório existe
            os.makedirs(diretorio_final, exist_ok=True)

            caminho_arquivo = os.path.join(
                diretorio_final, 
                f'NÃO FORAM ENCONTRADAS NOTAS DO TIPO NFSE PRESTADOR NO PERÍODO.txt'
            )

            # Criação do arquivo
            with open(caminho_arquivo, "w") as arquivo:
                arquivo.write(f'NÃO FORAM ENCONTRADAS NOTAS DO TIPO NFSE PRESTADOR NO PERÍODO {data_inicial}-{data_final}')
            
            tomador(data_inicial, data_final)
            return
        else:
            btn_solicitar_xml = page.ele('xpath://*[@id="btnSolicitarXML"]')
            btn_solicitar_xml.click()
    except :
        page.refresh()
        solicitar_notas_em_lote(data_inicial, data_final)
        return

    popup_sucesso = page.ele('xpath:/html/body/div[1]/div/div/div[3]/div/button')
    if popup_sucesso:
        try:
            popup_sucesso.click()
        except Exception as e:
            # Recarrega o elemento novamente
            popup_sucesso = page.ele('xpath:/html/body/div[1]/div/div/div[3]/div/button')
            popup_sucesso.click()   
    
    consultar_solicitacoes()
    return

def consultar_solicitacoes():
    print('CONSULTANDO SOLICITAÇÕES')
    menu = page.ele('xpath://*[@id="contMenu"]')
    
    nota_eletronica = menu.ele('text:Nota Eletrônica')    
    
    page.wait(1)
    
    box_nota_eletronica = nota_eletronica.parent().parent()
    
    btn_consultar = box_nota_eletronica.ele('text:Consultar')
    
    if btn_consultar.states.is_clickable:
        btn_consultar.click()
    else:
        page.refresh()
        area_principal()

    
    page.wait(3)
    
    status_aguardando = page.ele('xpath://*[@id="ddlStatus"]/option[2]')
    status_aguardando.click()
    
    btn_localizar = page.ele('xpath://*[@id="btnLocalizar"]')
    btn_localizar.click()
    
    nenhum_arquivo_aguardado = page.ele('xpath:/html/body/div[1]/div/div/div[2]/div')
    if nenhum_arquivo_aguardado:
        btn_ok = page.ele('xpath:/html/body/div[1]/div/div/div[3]/div/button')
        btn_ok.click()
        
        status_disponivel = page.ele('xpath://*[@id="ddlStatus"]/option[3]')
        status_disponivel.click()
        
        btn_localizar = page.ele('xpath://*[@id="btnLocalizar"]')
        btn_localizar.click()
        
        btn_localizar = page.ele('xpath://*[@id="btnLocalizar"]')
        if btn_localizar:
            btn_localizar.click()
        baixar_arquivos(data_inicial_formatada, data_final_formatada)
        return
    else:
        print('ARQUIVO ESTÁ SENDO AGUARDADO')
        btn_localizar = page.ele('xpath://*[@id="btnLocalizar"]')
        btn_localizar.click()
        
        btn_ok = page.ele('xpath:/html/body/div[1]/div/div/div[3]/div/button')
        
        if btn_ok : 
            btn_ok.click()
            consultar_solicitacoes()
            return
        else: 
            page.refresh()
            consultar_solicitacoes()
            return
   
def baixar_arquivos(data_inicial, data_final):
    print('BAIXANDO ARQUIVOS')
    data_inicial = data_inicial.replace('/','.')
    data_final = data_final.replace('/','.')
    try:
        mes, ano = extrair_mes_ano(data_inicial)
        baixar_arquivos = page.ele('xpath://*[@id="dgSolicitacoes__ctl3_btnDownload"]')
        baixar_arquivos.click.to_download(save_path=f"{diretorio_para_salvar_arquivos}/{numero_empresa}/{ano}/{mes}.{ano}", rename=f'PRESTADOR NFSE -{cnpj.replace('/','').replace('.','').replace('-','')}-{data_inicial}-{data_final}.zip')
        page.wait.download_begin()
        page.wait.all_downloads_done()
    except:
        page.refresh()
        area_principal()
    
    tomador(data_inicial, data_final)
    return

def tomador(data_inicial, data_final, nfse_nacional = False):
    print('CHAMOU TOMADOR')
    # try:
    menu = page.ele('xpath://*[@id="contMenu"]')
    
    botao_solicitacao_documentos_tomador = menu.ele('text:Declaração de Serviços Contratados')
    botao_solicitacao_documentos_tomador.click()
    
    box_servicos_tomador = botao_solicitacao_documentos_tomador.parent().parent()
    print(box_servicos_tomador)
    
    # page.wait(1000)
    
    consulta_notas_tomadas = box_servicos_tomador.ele('text:Consulta de Notas Tomadas')
    consulta_notas_tomadas.click()
    
    if nfse_nacional: 
        nfse_nacional_select = page.ele('xpath://*[@id="ddlSerie"]/option[4]')
        nfse_nacional_select.click()
        nome_arquivo = 'TOMADOR NFSE - NACIONAL' 
    else:
        nfse_select = page.ele('xpath://*[@id="ddlSerie"]/option[2]')
        nfse_select.click()
        nome_arquivo = 'TOMADOR NFSE' 
        
    botao_filtros_adicionais = page.ele('xpath://*[@id="imbArrow"]')
    botao_filtros_adicionais.click()
    
    page.wait(3)
    
    botao_filtros_adicionais_conferencia = page.ele('xpath://*[@id="imbArrow"]')
    if botao_filtros_adicionais_conferencia:
        botao_filtros_adicionais.click()

    page.wait(10)
    
    input_data_inicial = page.ele('xpath://*[@id="txtDtEmissaoIni"]')
    input_data_inicial.focus()
    input_data_inicial.click()
    input_data_inicial.clear()
    data_inicial = datetime.strptime(data_inicial, '%Y.%m.%d').strftime('%Y-%m-%d')
    input_data_inicial.input(data_inicial)
    
    input_data_final = page.ele('xpath://*[@id="txtDtEmissaoFim"]')
    input_data_final.focus()
    input_data_final.click()
    input_data_final.clear()
    input_data_final.input(data_final.replace('.',''))
    
    page.wait(3)
        
    # btn_localizar  = page.ele('xpath://*[@id="btnBuscarNotas"]')
    btn_localizar = page.ele('xpath:/html/body/form/div/div[2]/div/div/div/div/div[2]/div/div/ul/li[2]/a')
    input_data_inicial.focus()
    btn_localizar.click()
    
    btn_baixar_todos_xmls = page.ele('xpath://*[@id="dgDocumentos__ctl2_btnExpTodos"]')
    qtd_tr = page.eles('tag:tr')
    
    mes, ano = extrair_mes_ano(data_inicial)
    diretorio_final = f'{diretorio_para_salvar_arquivos}/{numero_empresa}/{ano}/{mes}.{ano}'

    # Verifica se o diretório existe, se não, cria
    if not os.path.exists(diretorio_final):
        os.makedirs(diretorio_final)

    if len(qtd_tr) > 2:
        data_inicial = data_inicial.replace('/', '.')
        data_final = data_final.replace('/', '.')

        btn_baixar_todos_xmls.click.to_download(
            save_path=f"{diretorio_final}", 
            rename=f'{nome_arquivo}-{cnpj.replace('/','').replace('.','').replace('-','')}-{data_inicial}-{data_final}.zip'
        )
        page.wait.download_begin()
        page.wait.all_downloads_done()
        
        if not nfse_nacional:
            tomador(data_inicial, data_final, True)
            return
        else:
            return
    else:
        print(f'A empresa: {razao_social}, não possui notas {nome_arquivo} no periodo {data_inicial} - {data_final}\n')
        relatorio.write(f'A empresa: {razao_social}, não possui notas {nome_arquivo} no periodo {data_inicial} - {data_final}\n')

        # Caminho completo do arquivo de texto
        caminho_arquivo = os.path.join(diretorio_final, f'NÃO FORAM ENCONTRADAS NOTAS DO TIPO {nome_arquivo}.txt')

        # Criação do arquivo
        with open(caminho_arquivo, "w") as arquivo:
            arquivo.write(f'NÃO FORAM ENCONTRADAS NOTAS DO TIPO {nome_arquivo}\n')
                
        if nfse_nacional == False:
            tomador(data_inicial, data_final, True)
            return
        else:
            return
    # except:
    #     page.refresh()
    #     tomador(data_inicial, data_final, nfse_nacional)
    #     return

diretorio_atual = os.getcwd()
diretorio_para_salvar_arquivos = os.path.join(diretorio_atual, 'ARQUIVOS BAIXADOS')
arquivos_na_pasta = os.listdir(diretorio_atual)
arquivo_excel = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')][0]
excel = pd.read_excel(arquivo_excel, true_values='X')

# Garantir que as datas estão no formato correto
excel['DATA INICIAL'] = pd.to_datetime(excel['DATA INICIAL'], format='%d/%m/%Y', errors='coerce')
excel['DATA FINAL'] = pd.to_datetime(excel['DATA FINAL'], format='%d/%m/%Y', errors='coerce')

# Abrir arquivo de relatório apenas uma vez
with open('relatorio_de_importacao.txt', 'a') as relatorio:
    
    for index, row in excel.iterrows():
        # Tratamento do CNPJ
        cnpj = re.sub(r'\D', '', str(row['CNPJ'])).zfill(14)
        print(cnpj)
        data_inicial = row['DATA INICIAL']
        data_final = row['DATA FINAL']
        razao_social = row['RAZAO SOCIAL']
        numero_empresa = str(row['NUMERO EMPRESA']).zfill(6)
        
        # Validação do CNPJ
        if not validar_cnpj(cnpj): 
            relatorio.write(f'O CNPJ: {cnpj} da empresa: {razao_social}, não é válido\n')
            print(f'CNPJ INVÁLIDO {cnpj} - {razao_social}')
            continue
        
        data_atual = data_inicial

        while data_atual <= data_final:
            
            data_inicio_intervalo = data_atual
            ultimo_dia_mes = monthrange(data_atual.year, data_atual.month)[1]
            data_fim_intervalo = datetime(data_atual.year, data_atual.month, ultimo_dia_mes)
            
            if data_fim_intervalo > data_final:
                data_fim_intervalo = data_final
                
            data_inicial_formatada = data_inicio_intervalo.strftime('%d/%m/%Y')
            data_final_formatada = data_fim_intervalo.strftime('%d/%m/%Y')
            
            # Chamar as funções
            try:
                
                acessa_issnet(cnpj)
            except:
                acessa_issnet(cnpj)
            # Incrementar para o próximo mês
            data_atual += relativedelta(months=1)