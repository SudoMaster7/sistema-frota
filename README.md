# Sistema de Controle de Frota - FUNDEC

Sistema web desenvolvido em Python com Flask para o gerenciamento e controle de viagens da frota de veículos da FUNDEC.

## ✨ Funcionalidades

- **Controle de Viagens:** Registro de saída e chegada de veículos.
- **Gestão de Dados:** Adição de novos motoristas, veículos e usuários do sistema.
- **Sistema de Login:** Autenticação segura com diferenciação de permissões (Admin vs. Usuário/Motorista).
- **Relatórios Diários:** Geração de relatórios de quilometragem por veículo e por motorista, com consulta por data.
- **Interface Moderna:** Estilo baseado em Bootstrap 5 com seletor de tema (modo claro/escuro).
- **Persistência de Dados:** Integração direta com planilhas do Google Sheets para armazenamento de dados.

## 🚀 Tecnologias Utilizadas

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Banco de Dados:** Google Sheets API
- **Autenticação:** Flask-Login, Flask-Bcrypt

## ⚙️ Como Executar o Projeto Localmente

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)
    cd SEU-REPOSITORIO
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install Flask gspread oauth2client Flask-Login Flask-Bcrypt
    ```

4.  **Configure as credenciais do Google:**
    - Siga o tutorial da API do Google para gerar um arquivo `credentials.json`.
    - Coloque este arquivo na raiz do projeto.
    - Compartilhe sua planilha do Google com o `client_email` encontrado no arquivo de credenciais.

5.  **Execute a aplicação:**
    ```bash
    flask run
    ```
