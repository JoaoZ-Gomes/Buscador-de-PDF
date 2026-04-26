import unicodedata
import re
import os
import multiprocessing

# Lock global compartilhado entre processos para garantir nomes únicos de arquivo
# sem race conditions ao rodar com ProcessPoolExecutor
_filename_lock = multiprocessing.Lock()

def normalize_text(text):
    """
    Normaliza o texto removendo acentos, convertendo para minúsculas
    e removendo espaços em excesso ou quebras de linha.
    """
    if not text:
        return ""
    
    # Remove acentos
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    
    # Converte para minúsculas
    text = text.lower()
    
    # Substitui múltiplas quebras de linha ou espaços por um único espaço
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def get_unique_filename(directory, filename):
    """
    Gera um nome de arquivo único adicionando (1), (2), etc., se o arquivo já existir.
    Esta versão NÃO é segura para uso concorrente entre processos — use
    reserve_unique_filepath para operações paralelas.
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base_name} ({counter}){ext}"
        counter += 1
        
    return new_filename

def reserve_unique_filepath(directory, filename, lock):
    """
    Reserva atomicamente um caminho de arquivo único dentro de `directory`.
    Usa o `lock` fornecido para evitar race conditions entre processos paralelos.
    Cria um arquivo vazio como placeholder para garantir exclusividade antes de
    o conteúdo real ser gravado.

    Retorna o caminho completo reservado.
    """
    base_name, ext = os.path.splitext(filename)
    with lock:
        counter = 1
        candidate = filename
        while True:
            full_path = os.path.join(directory, candidate)
            if not os.path.exists(full_path):
                # Cria o arquivo vazio para "reservar" o nome
                open(full_path, 'wb').close()
                return full_path
            candidate = f"{base_name} ({counter}){ext}"
            counter += 1
