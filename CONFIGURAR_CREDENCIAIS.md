# 🔐 Configurar Credenciais do Google Sheets

Este guia explica como obter e configurar as credenciais necessárias para o sistema de Frota FUNDEC funcionar.

## 📋 Opções de Configuração

Existem **2 formas** de configurar as credenciais:

### ✅ Opção 1: Arquivo `credentials.json` (Recomendado para Desenvolvimento)

1. **Acesse o Google Cloud Console:**
   - Vá para [console.cloud.google.com](https://console.cloud.google.com)
   - Crie um novo projeto ou selecione um existente

2. **Ative a Google Sheets API:**
   - Na barra de pesquisa, busque "Google Sheets API"
   - Clique em "Ativar"

3. **Crie uma Conta de Serviço:**
   - Acesse "APIs e Serviços" → "Credenciais"
   - Clique em "Criar Credenciais" → "Conta de Serviço"
   - Preencha um nome para a conta de serviço
   - Clique em "Criar e Continuar"

4. **Gere a Chave JSON:**
   - Na página da conta de serviço, vá em "Chaves"
   - Clique em "Adicionar chave" → "Criar nova chave"
   - Selecione o tipo "JSON"
   - O arquivo será baixado automaticamente

5. **Coloque o arquivo na pasta do projeto:**
   - Renomeie o arquivo para `credentials.json` (se necessário)
   - Coloque-o na **raiz do projeto** (mesma pasta de `app.py`)
   
   ```
   sistema-frota-fundec/
   ├── credentials.json  ← AQUI
   ├── app.py
   ├── README.md
   └── ...
   ```

6. **⚠️ IMPORTANTE - Segurança:**
   - Nunca envie `credentials.json` para o GitHub
   - O arquivo já está no `.gitignore`, mas verifique se está lá

---

### ✅ Opção 2: Variável de Ambiente (Recomendado para Produção/Deploy)

#### No PowerShell (Windows):

```powershell
# Leia o arquivo credentials.json e defina como variável de ambiente
$env:GOOGLE_CREDENTIALS_JSON = Get-Content -Raw -Path .\credentials.json

# Verifique se foi definida corretamente
Write-Host $env:GOOGLE_CREDENTIALS_JSON
```

#### No Command Prompt (Windows):

```cmd
# Copie o conteúdo do credentials.json e defina a variável
set GOOGLE_CREDENTIALS_JSON={"type": "service_account", ...}
```

#### No Bash/Linux/Mac:

```bash
export GOOGLE_CREDENTIALS_JSON=$(cat credentials.json)
```

---

## 🔗 Compartilhar a Planilha com a Conta de Serviço

Após gerar o `credentials.json`:

1. **Abra o arquivo** e procure por `"client_email"`
2. **Copie o email** (exemplo: `frota@seu-projeto.iam.gserviceaccount.com`)
3. **Abra sua planilha** no Google Sheets
4. **Clique em "Compartilhar"** (canto superior direito)
5. **Cole o email** e dê permissão de editor
6. **Não envie convite por email** (a conta de serviço não precisa)

---

## ✨ Verificar se Está Funcionando

Depois de configurar, rode a aplicação:

```bash
# Ative o ambiente virtual
.\venv\Scripts\activate.bat

# Execute a aplicação
python app.py
# ou
flask run
```

Se a configuração estiver correta, você verá:
```
✅ Usando arquivo credentials.json local
✅ Conexão com Google Sheets estabelecida com sucesso!
```

---

## 🆘 Solucionar Problemas

### ❌ "Arquivo não encontrado"
- Verifique se o arquivo `credentials.json` está na **pasta raiz** do projeto
- Reinicie o terminal/IDE após adicionar o arquivo

### ❌ "Acesso negado (403)"
- Verifique se compartilhou a planilha com o email da conta de serviço
- Verifique se deu **permissão de editor**

### ❌ "Erro ao decodificar JSON"
- Verifique se a variável de ambiente foi definida corretamente
- Certifique-se de não incluir aspas extras ao definir a variável

### ❌ "Planilha não encontrada"
- Verifique o ID da planilha em `app.py` (procure por `open_by_key`)
- Certifique-se de que a conta de serviço tem acesso a essa planilha

---

## 📝 Referências

- [Google Cloud Console](https://console.cloud.google.com)
- [Documentação da Google Sheets API](https://developers.google.com/sheets/api/guides/authorizing)
- [Guia gspread (Python)](https://docs.gspread.org/)

---

**Dúvidas?** Consulte o README.md ou entre em contato com o admin do sistema.
