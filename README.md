# 🔍 Buscador de PDFs

Uma aplicação Desktop robusta e elegante desenvolvida em Python para automatizar a busca de nomes em grandes volumes de arquivos PDF. 

O sistema analisa recursivamente uma pasta escolhida, procura pelo nome desejado no texto de cada PDF e **extrai apenas as páginas onde o nome ocorre**, salvando-as de forma organizada em uma pasta de destino.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-Dark%20Mode-blue?style=for-the-badge)

## ✨ Funcionalidades

- **Busca Rápida Direta no Texto**: Utiliza `pypdf` para leitura direta e extremamente rápida de PDFs que já possuem texto digitalizado, sem a necessidade de processamento lento via OCR.
- **Normalização Inteligente**: Ignora letras maiúsculas/minúsculas, remove acentuações e padroniza espaços extras para evitar que o nome seja "mascarado" por problemas de formatação no PDF.
- **Extração Precisa**: Ao encontrar uma correspondência, extrai exclusivamente a página afetada e salva com um nome claro e fácil de rastrear: `[NomeOriginal]_pagina[Num]_[NomeBuscado].pdf`.
- **Prevenção contra Sobrescrita**: Se o arquivo já existir na pasta destino, a aplicação acrescenta um sufixo numérico (ex: `(1)`) automaticamente.
- **Interface Profissional (UI/UX)**: Interface completamente moderna construída com `customtkinter`, rodando em Dark Mode nativo.
  - **Dashboard em Tempo Real**: Cards interativos exibindo o número de PDFs na pasta, arquivos já lidos e total de páginas extraídas.
  - **Execução em Segundo Plano**: Utiliza *Multithreading* nativo para que a interface nunca trave durante varreduras longas.
  - **Safe Stop**: Permite interromper a busca a qualquer momento com segurança através de uma caixa de confirmação.

## 📦 Como usar (Sem instalar nada)

Para usuários finais, o projeto foi compilado num executável autossuficiente (`.exe`).
1. Vá até a pasta `dist/` do projeto.
2. Dê dois cliques em **`Buscador_de_PDF.exe`**.
3. A interface se abrirá! Basta selecionar as pastas e o nome desejado.

*(Nota: O `.exe` não é subido para o GitHub pelo seu peso, mas você pode gerá-lo localmente seguindo os passos de empacotamento abaixo)*.

## 💻 Para Desenvolvedores (Rodando do código-fonte)

### Pré-requisitos

- Python 3.10+
- Dependências listadas no `requirements.txt`

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/JoaoZ-Gomes/Buscador-de-PDF.git
cd Buscador-de-PDF
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python main.py
```

## 🛠️ Empacotamento (Gerando seu próprio .exe)

Caso faça modificações no código e queira gerar um novo `.exe` atualizado para compartilhar com usuários leigos:

Execute o seguinte comando na raiz do projeto (usando o terminal do VSCode ou PowerShell):

```bash
python -m PyInstaller --noconsole --onefile --name "Buscador_de_PDF" --collect-all customtkinter -y main.py
```

O arquivo gerado ficará disponível dentro da pasta `dist/`.

## 📁 Estrutura do Projeto

```text
├── main.py              # Ponto de entrada (Entrypoint)
├── gui.py               # Interface gráfica (CustomTkinter)
├── pdf_processor.py     # Lógica central (Busca e extração com pypdf)
├── utils.py             # Funções utilitárias (Normalização de strings)
├── requirements.txt     # Dependências (Bibliotecas)
└── .gitignore           # Arquivos e pastas a serem ignorados pelo Git
```
