# 🔴 Solução para Erro 403 - Permissão Negada no Google Sheets

## ❌ Problema

Ao tentar agendar um veículo, o sistema retorna o erro:

```
Erro ao agendar: APIError: [403]: The caller does not have permission
```

## 🔍 Causa

A **conta de serviço do Google** não tem permissão de **Editor** na planilha do Google Sheets. Por padrão, as planilhas são privadas e precisam ser compartilhadas explicitamente com a conta de serviço.

## ✅ Solução Passo a Passo

### 1️⃣ Identifique o Email da Conta de Serviço

Abra o arquivo `credentials.json` e procure por `"client_email"`:

```json
{
  "type": "service_account",
  "client_email": "frotaglobo@gen-lang-client-0063703030.iam.gserviceaccount.com",
  ...
}
```

**Email da sua conta de serviço:**
```
frotaglobo@gen-lang-client-0063703030.iam.gserviceaccount.com
```

### 2️⃣ Compartilhe a Planilha

1. **Abra sua planilha** no navegador:
   ```
   https://docs.google.com/spreadsheets/d/1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I
   ```

2. **Clique no botão "Compartilhar"** (canto superior direito, botão azul)

3. **Cole o email da conta de serviço:**
   ```
   frotaglobo@gen-lang-client-0063703030.iam.gserviceaccount.com
   ```

4. **Configure as permissões:**
   - ✅ Selecione **"Editor"** no dropdown (NÃO selecione "Visualizador")
   - ✅ Desmarque a opção **"Notificar pessoas"** (a conta de serviço não precisa de email)

5. **Clique em "Compartilhar"** ou **"Enviar"**

### 3️⃣ Verifique o Compartilhamento

Após compartilhar, você deve ver na lista de pessoas com acesso:

```
✅ frotaglobo@gen-lang-client-0063703030.iam.gserviceaccount.com (Editor)
```

### 4️⃣ Teste as Permissões

Execute o script de teste que criamos:

```cmd
testar_permissoes.bat
```

Ou manualmente:

```powershell
.\venv\Scripts\activate
python testar_permissoes.py
```

**Resultado esperado:**

```
======================================================================
🔍 TESTE DE PERMISSÕES - GOOGLE SHEETS
======================================================================

1️⃣ Carregando credentials.json...
   ✅ Credenciais carregadas com sucesso!

2️⃣ Conectando ao Google Sheets...
   ✅ Autorização bem-sucedida!

3️⃣ Abrindo planilha...
   ✅ Planilha aberta: '[Nome da sua planilha]'

4️⃣ Testando LEITURA das worksheets...
   ✅ DB_Viagens: X registros encontrados
   ✅ DB_Motoristas: X registros encontrados
   ✅ DB_Veiculos: X registros encontrados
   ✅ DB_Usuarios: X registros encontrados
   ✅ DB_Agendamentos: X registros encontrados

5️⃣ Testando ESCRITA (append) em DB_Agendamentos...
   📝 Tentando adicionar linha de teste...
   ✅ ESCRITA FUNCIONOU! Permissão OK!
   🧹 Removendo linha de teste...
   ✅ Linha de teste removida!

======================================================================
✅ TODOS OS TESTES PASSARAM!
======================================================================

✨ A aplicação está pronta para funcionar!
   Execute: python app.py
```

### 5️⃣ Execute a Aplicação

Agora você pode usar o sistema normalmente:

```cmd
rodar.bat
```

Ou:

```powershell
.\venv\Scripts\activate
python app.py
```

## 🔧 Troubleshooting

### Ainda recebe erro 403?

**Verifique:**

1. ✅ O email está **exatamente** como mostrado (copie e cole)
2. ✅ A permissão é **"Editor"** (não "Visualizador" ou "Comentador")
3. ✅ Você clicou em **"Compartilhar"** após adicionar o email
4. ✅ Aguarde 30-60 segundos para as permissões propagarem

### Erro: "Invalid credentials"

- Verifique se o arquivo `credentials.json` está na **raiz do projeto**
- Certifique-se de que não está corrompido (abra no VSCode e verifique)

### Erro: "Spreadsheet not found"

- Verifique se o ID da planilha no código está correto:
  ```python
  spreadsheet = client.open_by_key('1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I')
  ```

## 📚 Documentação Adicional

Para mais informações sobre configuração de credenciais, consulte:

- **CONFIGURAR_CREDENCIAIS.md** - Guia completo de configuração
- **README.md** - Documentação geral do sistema

## ⚠️ Importante - Segurança

- ❌ **NUNCA** compartilhe o arquivo `credentials.json` publicamente
- ❌ **NUNCA** faça commit do `credentials.json` no GitHub
- ✅ O arquivo já está no `.gitignore` por segurança
- ✅ Use variáveis de ambiente em produção (veja CONFIGURAR_CREDENCIAIS.md)

## 🎯 Resumo

**Problema:** Erro 403 ao agendar veículo  
**Causa:** Conta de serviço sem permissão de Editor  
**Solução:** Compartilhar planilha com `frotaglobo@gen-lang-client-0063703030.iam.gserviceaccount.com` como Editor  
**Teste:** Execute `testar_permissoes.bat`  

---

**Última atualização:** Janeiro 2026  
**Status:** ✅ Resolvido
