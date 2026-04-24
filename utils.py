import unicodedata
import re
import os

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
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base_name} ({counter}){ext}"
        counter += 1
        
    return new_filename
