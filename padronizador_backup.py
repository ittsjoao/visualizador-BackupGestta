import re
import os

def corrigir_arquivo(arquivo_entrada):
    nome_base, extensao = os.path.splitext(arquivo_entrada)
    arquivo_saida = f"{nome_base}_correção{extensao}"

    # Expressão para identificar início de linha válida (13 dígitos seguidos de espaço)
    padrao_linha_valida = re.compile(r'^\d{13}\s')

    linhas_corrigidas = []
    buffer = ""

    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.rstrip()

            if padrao_linha_valida.match(linha):
                if buffer:
                    linhas_corrigidas.append(buffer)
                buffer = linha
            else:
                buffer += " " + linha.strip()

        if buffer:
            linhas_corrigidas.append(buffer)

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        for linha in linhas_corrigidas:
            f.write(linha + '\n')

    print(f"Arquivo corrigido salvo como: {arquivo_saida}")
    
corrigir_arquivo('entrada.txt')