import csv
import os
import re
import unicodedata

ARQUIVO_ENTRADA = "backup_original.txt"
ARQUIVO_CONTATOS = "contatos_editado.txt"
ARQUIVO_SAIDA = "entrada_final.csv"

# --- Utilidades ---

def normalizar_espacos(s: str) -> str:
    return " ".join(s.strip().split())

def remover_acentos(s: str) -> str:
    # normaliza para comparar nomes sem depender de acentos
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def nome_norm(s: str) -> str:
    # colapsa espaços, remove acentos e usa casefold p/ comparação robusta
    return remover_acentos(normalizar_espacos(s)).casefold()

# --- 1) Carregar contatos numero->nome ---

def carregar_contatos(arquivo_contatos: str) -> dict:
    mapa = {}
    with open(arquivo_contatos, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or ";" not in linha:
                continue
            numero, nome = linha.split(";", 1)
            numero = numero.strip()
            nome = normalizar_espacos(nome)
            # considera apenas números válidos com 13 dígitos
            if re.fullmatch(r"\d{13}", numero):
                mapa[numero] = nome
    return mapa

# --- 2) Juntar quebras de linha (somente linhas que começam com 13 dígitos são "novas") ---

PADRAO_LINHA = re.compile(r"^(\d{13})\s")

def gerar_linhas_unificadas(arquivo_entrada: str):
    buffer = ""
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        for bruta in f:
            linha = bruta.rstrip("\n").rstrip("\r")
            if PADRAO_LINHA.match(linha):
                # nova linha válida: descarrega buffer anterior
                if buffer:
                    yield buffer
                buffer = linha
            else:
                # continuação: agrega
                if buffer:
                    buffer += " " + linha.strip()
                else:
                    # linha solta (sem 13 dígitos no começo) – ignora ou acumula?
                    # Vamos acumular como buffer isolado (caso arquivo comece "estranho")
                    buffer = linha.strip()
        if buffer:
            yield buffer

# --- 3) Extrair campos ---

PADRAO_DATA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z")

def extrair_campos(linha: str, contatos_map: dict):
    m_num = PADRAO_LINHA.match(linha)
    if not m_num:
        return None

    numero = m_num.group(1)

    m_data = PADRAO_DATA.search(linha)
    if not m_data:
        # sem data ISO → não conseguimos separar Autor/Mensagem com segurança
        return None

    data = m_data.group(0)
    idx_inicio_conteudo = m_num.end()
    idx_data = m_data.start()

    intermediario = linha[idx_inicio_conteudo:idx_data].strip()
    mensagem = linha[m_data.end():].strip()

    # Regra para Contato/Autor:
    # - Se numero está na lista e o início do "intermediario" corresponde ao NOME COMPLETO do contato,
    #   então Contato = nome do arquivo de contatos e Autor = resto.
    # - Caso contrário, Contato = "" e Autor = intermediario (sem “adivinhar” por primeiro nome).
    contato_esperado = contatos_map.get(numero, "")
    contato = ""
    autor = intermediario

    if contato_esperado:
        # Compara por nome completo (normalizado), garantindo que o nome apareça no INÍCIO.
        # Usamos regex para pegar a posição real do match (respeitando maiúsc./minúsc. e espaços múltiplos).
        # Aceita variações de espaço e caixa, mas exige o nome todo no começo.
        contato_regex = re.compile(
            r"^\s*" + re.escape(contato_esperado),
            flags=re.IGNORECASE
        )
        m_contato_exato = contato_regex.match(intermediario)

        # Confirma com normalização robusta (evita “vinicius” bater com “vinicius rodrigues” e vice-versa)
        if m_contato_exato:
            inicio, fim = m_contato_exato.span()
            prefixo = intermediario[inicio:fim]
            if nome_norm(prefixo) == nome_norm(contato_esperado):
                contato = contato_esperado  # mantém forma “canônica” do arquivo de contatos
                autor = intermediario[fim:].strip()

    return [numero, contato, autor, data, mensagem]

# --- 4) Pipeline principal ---

def processar(arquivo_entrada: str, arquivo_contatos: str, arquivo_saida: str):
    contatos_map = carregar_contatos(arquivo_contatos)

    with open(arquivo_saida, "w", newline="", encoding="utf-8") as out_csv:
        writer = csv.writer(out_csv, delimiter=";")
        writer.writerow(["NumeroGrupo", "Contato", "Autor", "Data", "Mensagem"])

        for linha in gerar_linhas_unificadas(arquivo_entrada):
            campos = extrair_campos(linha, contatos_map)
            if campos:
                writer.writerow(campos)

    print(f"CSV gerado: {arquivo_saida}")

if __name__ == "__main__":
    processar(ARQUIVO_ENTRADA, ARQUIVO_CONTATOS, ARQUIVO_SAIDA)
