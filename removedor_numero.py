entrada = "contatos.txt"
saida = "arquivo_editado.txt"

with open(entrada, "r", encoding="utf-8") as arq_in, open(saida, "w", encoding="utf-8") as arq_out:
    for linha in arq_in:
        nova_linha = linha[21:]  # Índice 21 é a coluna 22 (começando do 0)
        arq_out.write(nova_linha)
