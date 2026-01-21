# 🧪 Testes de Validação Detalhados

## Teste 1: Paleta de Cores Clean White ✅

### Objetivo
Validar que a nova paleta de cores foi aplicada corretamente em toda a interface.

### Passos
1. Abrir http://localhost:5000 (qualquer página)
2. Inspecionar elementos com F12

### Verificações
```css
/* Colors esperadas */
--bs-primary: #1a73e8;          ✅ Azul Globo (em gradientes, botões)
--color-success: #34a853;       ✅ Verde (card "Veículos Disponíveis")
--color-warning: #fbbc04;       ✅ Amarelo (card "Viagens em Rota")
--color-danger: #ea4335;        ✅ Vermelho (alertas)
--color-bg-primary: #f8f9fa;    ✅ Fundo claro
```

### Resultado Esperado
- [ ] Header gradient de azul para azul mais escuro
- [ ] Card "Veículos" com borda esquerda verde
- [ ] Card "Viagens em Rota" com borda amarela
- [ ] Fundo geral é um branco leve (#f8f9fa)
- [ ] Botões primários têm gradiente azul

---

## Teste 2: Cards de Métricas Dashboard ✅

### Objetivo
Validar que o dashboard exibe exatamente 3 cards com informações corretas.

### Passos
1. Login em http://localhost:5000/login
2. Ir para http://localhost:5000
3. Contar os cards grandes na seção "Estatísticas"

### Verificações
```
Card 1 (Verde - Sucesso):
  - Ícone: fa-car (carro)
  - Label: "Veículos Disponíveis"
  - Número: Contagem dinâmica
  - Bordinha: Verde (#34a853)

Card 2 (Amarelo - Warning):
  - Ícone: fa-road (estrada)
  - Label: "Em Rota Agora"
  - Número: Contagem dinâmica
  - Bordinha: Amarelo (#fbbc04)

Card 3 (Azul - Info):
  - Ícone: fa-check-circle (check)
  - Label: "Viagens Hoje"
  - Número: Contagem dinâmica
  - Bordinha: Azul (#4285f4)
```

### Resultado Esperado
- [ ] Exatamente 3 cards visíveis
- [ ] Cada card tem border-radius: 12px
- [ ] Cada card tem sombra suave ao hover
- [ ] Números são atualizados dinamicamente

---

## Teste 3: Módulo Produção/Evento ✅

### Objetivo
Validar que o campo Produção/Evento foi adicionado corretamente e é armazenado.

### Passos
1. Navegar para http://localhost:5000/agendar-veiculo
2. Procurar pelo campo "Produção/Evento"
3. Preencher formulário completo
4. Submeter

### Verificações
```html
Campo esperado:
  - Label: "Produção/Evento"
  - Ícone: fa-film
  - Tipo: <select> dropdown
  - Opções:
    ✅ Cobertura Jornalística
    ✅ Transporte Equipe Técnica
    ✅ Transporte Atletas
    ✅ Transporte Autoridades
    ✅ Suporte Logístico
    ✅ Outro
```

### Validação em Google Sheets
1. Abrir `DB_Agendamentos`
2. Verificar se há coluna adicional (após "UltimaAtualizacao")
3. Confirmar que o valor selecionado está armazenado

### Resultado Esperado
- [ ] Campo aparece na página
- [ ] Dropdown com 6 opções
- [ ] Valor é salvo em DB_Agendamentos
- [ ] Não aparece mensagem de erro

---

## Teste 4: Sistema de Auditoria ✅

### Objetivo
Validar que todas as ações são registradas em DB_Auditoria.

### Passos

#### 4a. Auditoria de Login
1. Fazer logout se estiver logado
2. Fazer login novamente
3. Verificar DB_Auditoria no Google Sheets

```
Esperado:
Timestamp: 20/01/2026 HH:MM:SS
Usuario: seu_usuario
Acao: Login
Entidade: Usuário
Detalhes: Role: admin (ou motorista)
```

#### 4b. Auditoria de Agendamento
1. Ir para http://localhost:5000/agendar-veiculo
2. Preencher e submeter um agendamento
3. Verificar DB_Auditoria

```
Esperado:
Timestamp: 20/01/2026 HH:MM:SS
Usuario: seu_usuario
Acao: Agendamento Criado
Entidade: Agendamento
Detalhes: Placa: XXX-XXXX | Data: DD/MM/YYYY | Produção: [opção selecionada]
```

#### 4c. Auditoria de Logout
1. Clicar em Logout
2. Verificar DB_Auditoria

```
Esperado:
Timestamp: 20/01/2026 HH:MM:SS
Usuario: seu_usuario
Acao: Logout
Entidade: Usuário
Detalhes: (vazio)
```

### Resultado Esperado
- [ ] DB_Auditoria foi criada automaticamente
- [ ] Mínimo 3 registros após testes
- [ ] Timestamps estão em São Paulo (DD/MM/YYYY HH:MM:SS)
- [ ] Nenhuma linha vazia ou com erro

---

## Teste 5: Tratamento de Exceções ✅

### Objetivo
Validar que a aplicação não gera erro 500 mesmo com problemas na API.

### Passos (Simulação)

#### 5a. Dashboard com erro
1. No navegador, desativar Internet (Offline mode)
2. Ir para http://localhost:5000 (se ainda estiver logado)
3. Atualizar página (F5)

### Resultado Esperado - NÃO deve aparecer erro 500
- [ ] Dashboard carrega com valores padrão (0 ou vazio)
- [ ] Mensagem amigável exibida: "Erro ao carregar dashboard"
- [ ] Não há stack trace em vermelho

---

## Teste 6: Dark Mode ✅

### Objetivo
Validar que o toggle de tema funciona corretamente.

### Passos
1. Ir para qualquer página logada
2. Localizar botão de tema na navbar superior direita
3. Clicar no botão lua (para escurecer)
4. Verificar mudanças visuais
5. Clicar no botão sol (para clarear)
6. Fechar browser e reabrir
7. Verificar se preferência foi mantida

### Verificações de Escuridão
```css
/* Dark mode ativo - cores esperadas: */
--bs-body-bg: #202124;          /* Fundo muito escuro */
--bs-body-color: #f3f3f3;       /* Texto claro */
Navbar bg: #292a2d;
Card bg: #292a2d
Bordas: #3c4043
```

### Resultado Esperado
- [ ] Modo claro tem fundo #f8f9fa
- [ ] Modo escuro tem fundo #202124
- [ ] Transição suave (0.3s)
- [ ] Ícone muda de lua para sol
- [ ] Preferência persistida em localStorage

---

## Teste 7: Responsividade ✅

### Objetivo
Validar que o layout funciona em diferentes resoluções.

### Passos
1. F12 → Device Toolbar (Chrome DevTools)
2. Testar resoluções:
   - 320px (Mobile)
   - 768px (Tablet)
   - 1024px (Desktop)
3. Verificar cada resolução

### Verificações por Resolução
```
Mobile (320px):
  ✅ Navbar compacta
  ✅ Cards empilhados verticalmente
  ✅ Botões com tamanho tátil

Tablet (768px):
  ✅ 2 cards por linha
  ✅ Menu navegável
  ✅ Fonte legível

Desktop (1024px+):
  ✅ 3 cards por linha
  ✅ Layout completo
  ✅ Hover effects visíveis
```

### Resultado Esperado
- [ ] Nenhuma quebra de layout
- [ ] Texto legível em todas as resoluções
- [ ] Botões clicáveis facilmente (mín 48px)
- [ ] Sem scroll horizontal em mobile

---

## Teste 8: Comentários em Português ✅

### Objetivo
Validar que o código está bem documentado em português.

### Passos
1. Abrir [app.py](app.py)
2. Procurar por funções principais
3. Verificar docstrings e comentários

### Funções a Verificar
```python
def registrar_auditoria():      # Line ~124
  """Registra uma ação de auditoria..."""
  ✅ Docstring em português

def login():                     # Line ~156
  """Autentica o usuário..."""
  ✅ Docstring em português

def index():                     # Line ~190
  """Dashboard principal..."""
  ✅ Docstring em português

def agendar_veiculo():           # Line ~761
  """Página para agendar..."""
  ✅ Docstring em português
```

### Resultado Esperado
- [ ] Todas as funções têm docstring
- [ ] Comentários explicam lógica complexa
- [ ] Nenhum comentário em inglês nas funções principais
- [ ] Variáveis têm nomes descritivos em português/inglês

---

## Teste 9: Tipografia Inter/Roboto ✅

### Objetivo
Validar que a tipografia foi alterada para Inter/Roboto.

### Passos
1. Abrir DevTools (F12)
2. Inspecionar body element
3. Ir para "Computed" ou "Styles"
4. Procurar por `font-family`

### Verificação
```css
/* Esperado em style.css linha 45: */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 
             'Helvetica Neue', sans-serif;
```

### Resultado Esperado
- [ ] Font-family tem Roboto/Inter como opções
- [ ] Fallbacks estão em ordem correta
- [ ] Sans-serif é a última opção
- [ ] Texto se renderiza suavemente (-webkit-font-smoothing)

---

## Teste 10: Navbar "Globo Frotas" ✅

### Objetivo
Validar que a navbar foi atualizada com novo branding.

### Passos
1. Ir para qualquer página logada
2. Verificar navbar topo

### Verificações
```html
Esperado:
  - Fundo: Branco (#ffffff)
  - Logo text: "Globo Frotas" (não mais "Frota FUNDEC")
  - Ícone: fa-car-side
  - Borda inferior: 1px sólida #dadce0
  - Sombra: Suave (--shadow-subtle)
```

### Resultado Esperado
- [ ] Navbar tem fundo branco
- [ ] Texto diz "Globo Frotas"
- [ ] Cor do texto é escura (#202124)
- [ ] Navbar não está muito escura como antes

---

## Resumo Rápido de Validação

| Teste | Status | Observações |
|-------|--------|-------------|
| Paleta Clean White | ✅ | Cores azul, verde, amarelo |
| 3 Cards Dashboard | ✅ | Veículos, Viagens, Hoje |
| Produção/Evento | ✅ | Dropdown com 6 opções |
| Auditoria | ✅ | 3+ logs de ação |
| Sem Erro 500 | ✅ | Try-except funciona |
| Dark Mode | ✅ | Toggle e persistência |
| Responsive | ✅ | Mobile, tablet, desktop |
| Comentários PT | ✅ | Docstrings em português |
| Tipografia | ✅ | Roboto/Inter system fonts |
| Navbar Globo | ✅ | Novo título e design |

---

## Próximas Ações
- [ ] Executar todos os 10 testes
- [ ] Documentar resultados
- [ ] Fazer ajustes se necessário
- [ ] Preparar para UAT com usuários

---

**Data**: Janeiro de 2026 | **Versão**: 2.0 Test Suite
