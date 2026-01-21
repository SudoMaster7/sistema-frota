# 🧪 Checklist de Validação - Refatoração Globo Frotas

## ✅ Validação de Implementação

### 1. Design Visual
- [ ] **Navegação**: Navbar com fundo branco, ícone "Globo Frotas"
  - Acesso: Qualquer página logada
  - Esperado: Navbar limpa, branca, com título "Globo Frotas"

- [ ] **Paleta de Cores**: Azul Globo #1a73e8
  - Acesso: Qualquer página
  - Esperado: Gradiente azul nos headers e botões

- [ ] **Cards de Métricas**: 3 cards no dashboard
  - Acesso: `/` (home)
  - Esperado: 3 cards com ícones, números e labels
    - Verde: Veículos Disponíveis
    - Amarelo: Viagens em Rota
    - Azul: Viagens Hoje

- [ ] **Dark Mode**: Toggle de tema funcional
  - Acesso: Botão lua/sol na navbar
  - Esperado: Interface escurece/clareia suavemente

### 2. Backend - Auditoria

- [ ] **Criação de DB_Auditoria**: Planilha criada automaticamente
  - Acesso: Console ao iniciar `python app.py`
  - Esperado: Mensagem "✅ Planilha de Auditoria criada" ou "encontrada"

- [ ] **Log de Login**: Auditoria registra login
  - Acesso: Fazer login → Abrir Google Sheets DB_Auditoria
  - Esperado: Linha com `Timestamp | usuario | Login | Usuário | Role: admin/motorista`

- [ ] **Log de Agendamento**: Auditoria registra novo agendamento
  - Acesso: Agendar veículo → Abrir Google Sheets DB_Auditoria
  - Esperado: Linha com `Timestamp | usuario | Agendamento Criado | Agendamento | Detalhes`

### 3. Backend - Produção/Evento

- [ ] **Campo no Formulário**: Seletor de Produção/Evento visível
  - Acesso: `/agendar-veiculo`
  - Esperado: Dropdown com opções:
    - Cobertura Jornalística
    - Transporte Equipe Técnica
    - Transporte Atletas
    - Transporte Autoridades
    - Suporte Logístico
    - Outro

- [ ] **Armazenamento**: Produção/Evento salvo no DB_Agendamentos
  - Acesso: Agendar com "Cobertura Jornalística" → Abrir Google Sheets
  - Esperado: Coluna adicional com valor selecionado

- [ ] **Auditoria de Produção**: Log inclui informação de produção
  - Acesso: Agendar veículo → Abrir DB_Auditoria
  - Esperado: Campo "Detalhes" inclui `Produção: Cobertura Jornalística`

### 4. Tratamento de Exceções

- [ ] **Try-Except em index()**: Dashboard funciona mesmo com erro de API
  - Acesso: Desabilitar Google Sheets (teste) → `/`
  - Esperado: Mensagem amigável, não erro 500

- [ ] **Try-Except em login()**: Login com erro de API
  - Acesso: Desabilitar Google Sheets (teste) → `/login`
  - Esperado: Mensagem amigável, não erro 500

- [ ] **Try-Except em agendar_veiculo()**: Agendamento com erro
  - Acesso: Desabilitar Google Sheets (teste) → `/agendar-veiculo`
  - Esperado: Mensagem amigável, não erro 500

### 5. Código & Comentários

- [ ] **Comentários em Português**: Funções principais comentadas
  - Acesso: Abrir [app.py](app.py)
  - Esperado: Docstrings em português acima de cada função principal

- [ ] **Função registrar_auditoria()**: Implementada corretamente
  - Acesso: Grep `def registrar_auditoria` em [app.py](app.py)
  - Esperado: Função com try-except e documentação

---

## 🧪 Testes Práticos (Passo a Passo)

### Teste 1: Login e Dashboard
```
1. Abrir http://localhost:5000/login
2. Fazer login com credenciais válidas
3. Verificar:
   - ✅ Navbar branca com "Globo Frotas"
   - ✅ 3 cards de métricas no dashboard
   - ✅ Cor azul (#1a73e8) no header
   - ✅ Auditoria registrada em DB_Auditoria
```

### Teste 2: Agendar Veículo
```
1. Navegar para "/agendar-veiculo"
2. Preencher formulário:
   - Veículo: Selecione um
   - Motorista: Selecione um
   - Data: Próximo dia
   - Horários: 10:00 - 12:00
   - Destinos: "Local de teste"
   - Passageiros: 5
   - Produção/Evento: "Cobertura Jornalística"  ← NOVO
   - Observações: "Teste"
3. Clicar em "Agendar"
4. Verificar:
   - ✅ Agendamento salvo
   - ✅ DB_Agendamentos inclui campo Produção/Evento
   - ✅ DB_Auditoria registra ação
```

### Teste 3: Dark Mode
```
1. Qualquer página logada
2. Clicar no botão lua (navbar superior direita)
3. Verificar:
   - ✅ Interface fica escura
   - ✅ Botão muda para sol
   - Clicar novamente
   - ✅ Interface volta a clara
   - ✅ Preferência salva em localStorage
```

### Teste 4: Tratamento de Erro
```
1. Simular erro desabilitando Google Sheets
2. Navegar para "/agendar-veiculo"
3. Clicar em "Agendar"
4. Verificar:
   - ✅ NÃO aparece erro 500
   - ✅ Mensagem amigável exibida: "Erro ao carregar dados..."
```

---

## 📊 Arquivos para Inspecionar

| Arquivo | O que Verificar |
|---------|-----------------|
| [app.py](app.py#L1-L50) | Imports, configuração de sheets, criação de DB_Auditoria |
| [app.py](app.py#L124-L145) | Função `registrar_auditoria()` |
| [app.py](app.py#L190-L210) | Try-except em `index()` |
| [app.py](app.py#L156-L190) | Try-except em `login()` e `logout()` |
| [app.py](app.py#L761-L870) | Campo `producao_evento` em `agendar_veiculo()` |
| [static/css/style.css](static/css/style.css#L1-L100) | Cores, cards, dashboard |
| [templates/base.html](templates/base.html#L1-L20) | Navbar, título |
| [templates/index.html](templates/index.html) | 3 cards de métricas |
| [templates/agendar_veiculo.html](templates/agendar_veiculo.html#L370-L395) | Campo Produção/Evento |

---

## 🐛 Debugging

### Se o DB_Auditoria não foi criado
```python
# No console Python:
from app import spreadsheet
auditoria_sheet = spreadsheet.worksheet("DB_Auditoria")
# Deve funcionar ou retornar erro que precisa criar
```

### Se as cores não estão corretas
```css
/* Verificar em style.css - Cores primárias:
--bs-primary: #1a73e8;  (Azul Globo)
--color-success: #34a853;  (Verde)
--color-warning: #fbbc04;  (Amarelo)
```

### Se o campo Produção/Evento não aparece
```html
<!-- Verificar em agendar_veiculo.html linha ~370:
<select class="form-control" id="producao_evento" name="producao_evento">
```

---

## 📋 Requisitos de Aprovação

- [ ] Todos os 5 testes práticos passarem
- [ ] Não há erros 500 no console
- [ ] DB_Auditoria está sendo populada corretamente
- [ ] Campo Produção/Evento aparece e é salvo
- [ ] Dark mode funciona
- [ ] Navbar com novo branding

---

## 🚀 Deploy

Quando validado, fazer:

```bash
# 1. Atualizar requirements.txt (se houver novas dependências)
pip freeze > requirements.txt

# 2. Commit das mudanças
git add .
git commit -m "refactor: Globo Frotas design, auditoria e Produção/Evento"

# 3. Push para repositório
git push

# 4. Deploy (instruções do seu servidor)
```

---

**Última atualização**: Janeiro de 2026 | **Versão**: 2.0-refactor
