import csv
import re

def carregar_contatos(arquivo_contatos):
    with open(arquivo_contatos, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]

def extrair_campos(linha, contatos_validos):
    regex_inicio = r'^(\d{13})'
    regex_data = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z'

    match_numero = re.match(regex_inicio, linha)
    match_data = re.search(regex_data, linha)

    if match_numero and match_data:
        numero = match_numero.group(1)
        data = match_data.group(0)

        index_num = linha.find(numero) + len(numero)
        index_data = linha.find(data)

        intermediario = linha[index_num:index_data].strip()
        mensagem = linha[index_data + len(data):].strip()

        contato_encontrado = ""
        for contato in contatos_validos:
            if intermediario.startswith(contato):
                contato_encontrado = contato
                break

        if contato_encontrado:
            autor = intermediario[len(contato_encontrado):].strip()
            return [numero, contato_encontrado, autor, data, mensagem]
        else:
            return [numero, "", intermediario, data, mensagem]

    return None

def processar_com_contatos(arquivo_txt, arquivo_contatos):
    nome_csv = arquivo_txt.replace('.txt', '.csv')
    contatos_validos = carregar_contatos(arquivo_contatos)

    with open(arquivo_txt, 'r', encoding='utf-8') as entrada, \
         open(nome_csv, 'w', newline='', encoding='utf-8') as saida:

        escritor = csv.writer(saida, delimiter=';')
        escritor.writerow(['NumeroGrupo', 'Contato', 'Autor', 'Data', 'Mensagem'])

        for linha in entrada:
            linha = linha.strip()
            campos = extrair_campos(linha, contatos_validos)
            if campos:
                escritor.writerow(campos)

    print(f"Arquivo CSV gerado com separação por contato: {nome_csv}")

processar_com_contatos('entrada_correção.txt', 'arquivo_editado.txt')
