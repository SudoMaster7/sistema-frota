import gspread
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import os
import json

# --- CONFIGURAÇÃO INICIAL ---
app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

# --- CONFIGURAÇÃO DO FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redireciona para a página de login se não estiver logado
login_manager.login_message = "Por favor, faça o login para acessar esta página."
login_manager.login_message_category = "info"


# --- CONEXÃO COM GOOGLE SHEETS (VERSÃO PARA DEPLOY) ---
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

    # Pega o conteúdo do JSON da variável de ambiente
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if not creds_json_str:
        raise ValueError("A variável de ambiente GOOGLE_CREDENTIALS_JSON não foi encontrada.")

    # Converte a string JSON em um dicionário Python
    creds_dict = json.loads(creds_json_str)

    # Autoriza usando o dicionário de credenciais
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key('1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I')
    # ... (resto das planilhas) ...
    viagens_sheet = spreadsheet.worksheet("DB_Viagens")
    motoristas_sheet = spreadsheet.worksheet("DB_Motoristas")
    veiculos_sheet = spreadsheet.worksheet("DB_Veiculos")
    usuarios_sheet = spreadsheet.worksheet("DB_Usuarios")
    print("Conexão com Google Sheets estabelecida com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO ao conectar com Google Sheets: {e}")
    # Em um ambiente de produção, você pode querer lidar com isso de forma mais elegante
    # Por enquanto, vamos parar a aplicação se a conexão falhar.
    exit()

# --- MODELO DE USUÁRIO ---
class User(UserMixin):
    def __init__(self, id, password_hash, role):
        self.id = id
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def get(user_id):
        try:
            user_data = usuarios_sheet.find(user_id)
            user_row = usuarios_sheet.row_values(user_data.row)
            return User(id=user_row[0], password_hash=user_row[1], role=user_row[2])
        except Exception as e:
            return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Acesso restrito a administradores.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function
# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get(username)
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

# --- FUNÇÕES AUXILIARES ---
def get_all_records(sheet):
    return sheet.get_all_records()

# --- ROTAS PRINCIPAIS ---

@app.route('/')
@login_required
def index():
    """Dashboard principal com resumo das atividades."""
    # Estatísticas gerais
    viagens_em_rota = [v for v in get_all_records(viagens_sheet) if v['Status'] == 'Em Rota']
    viagens_finalizadas_hoje = []
    
    hoje = datetime.now().strftime('%d/%m/%Y')
    for v in get_all_records(viagens_sheet):
        if v['Status'] == 'Finalizada' and v['DataSaida'] == hoje:
            viagens_finalizadas_hoje.append(v)
    
    total_veiculos = len(veiculos_sheet.get_all_records())
    veiculos_disponiveis = len([v for v in veiculos_sheet.get_all_records() if v['Status'] == 'Disponível'])
    veiculos_em_uso = len([v for v in veiculos_sheet.get_all_records() if v['Status'] == 'Em Uso'])
    
    # Para motoristas, mostrar apenas seu próprio painel
    motoristas = []
    if current_user.role == 'admin':
        motoristas = motoristas_sheet.get_all_records()
    
    veiculos_disponiveis_list = [v for v in veiculos_sheet.get_all_records() if v['Status'] == 'Disponível']
    
    # Calcular distância total do dia
    distancia_total_hoje = 0
    for v in viagens_finalizadas_hoje:
        try:
            km_inicial = int(v.get('KmInicial', 0))
            km_final = int(v.get('KmFinal', 0))
            if km_final > km_inicial:
                distancia_total_hoje += (km_final - km_inicial)
        except:
            pass
    
    contexto = {
        'motoristas': motoristas,
        'veiculos': veiculos_disponiveis_list,
        'current_user': current_user,
        # Estatísticas
        'viagens_em_rota': len(viagens_em_rota),
        'viagens_hoje': len(viagens_finalizadas_hoje),
        'total_veiculos': total_veiculos,
        'veiculos_disponiveis': veiculos_disponiveis,
        'veiculos_em_uso': veiculos_em_uso,
        'distancia_hoje': distancia_total_hoje
    }
    
    return render_template('index.html', **contexto)


@app.route('/registrar-saida', methods=['POST'])
@login_required
def registrar_saida():
    """Processa os dados do formulário de saída."""
    try:
        # ALTERAÇÃO: Lógica para definir o nome do motorista baseado na permissão (role)
        if current_user.role == 'admin':
            # Se for admin, pega o motorista selecionado no formulário
            motorista = request.form.get('motorista')
            if not motorista:
                flash('Como administrador, você deve selecionar um motorista.', 'danger')
                return redirect(url_for('index'))
        else:
            # Se não for admin, o motorista é o próprio usuário logado
            motorista = current_user.id

        # O restante da lógica permanece igual
        placa = request.form.get('veiculo')
        km_inicial = request.form.get('km_inicial')
        destinos = request.form.get('destinos')
        passageiros = request.form.get('passageiros', '0')
        observacoes = request.form.get('observacoes', '')
        
        # Novos campos: data e hora
        data_saida_input = request.form.get('data_saida')
        hora_saida_input = request.form.get('hora_saida')
        
        # Validar se os campos foram preenchidos
        if not data_saida_input or not hora_saida_input:
            flash('Data e hora são obrigatórias.', 'danger')
            return redirect(url_for('index'))
        
        # Converter para o formato correto
        data_saida = data_saida_input  # Já vem no formato YYYY-MM-DD, converter para DD/MM/YYYY
        hora_saida = hora_saida_input  # Já vem no formato HH:MM
        
        # Converter data de YYYY-MM-DD para DD/MM/YYYY se necessário
        try:
            data_obj = datetime.strptime(data_saida, '%Y-%m-%d')
            data_saida = data_obj.strftime('%d/%m/%Y')
        except:
            # Se já estiver no formato correto, manter como está
            pass

        # Nova viagem com estrutura compatível com a planilha
        nova_viagem = [
            len(get_all_records(viagens_sheet)) + 2,  # ID
            motorista,                                  # Motorista
            placa,                                      # PlacaVeiculo
            km_inicial,                                 # KmInicial
            "",                                         # KmFinal (vazio, será preenchido na chegada)
            data_saida,                                 # DataSaida
            hora_saida,                                 # HoraSaida
            "",                                         # DataChegada (vazio, será preenchido na chegada)
            "",                                         # HoraChegada (vazio, será preenchido na chegada)
            destinos,                                   # Destinos
            "Em Rota",                                  # Status
            passageiros,                                # Passageiros
            observacoes                                 # Observacoes
        ]
        viagens_sheet.append_row(nova_viagem)
        
        # CORREÇÃO: Lógica para encontrar e atualizar célula usando a exceção correta
        try:
            cell = veiculos_sheet.find(placa)
            veiculos_sheet.update_cell(cell.row, 4, "Em Uso")
        except Exception as e:
            flash(f'AVISO: Placa {placa} não encontrada na planilha de veículos para atualização de status.', 'warning')

        flash('Saída registrada com sucesso!', 'success')
        return redirect(url_for('cronograma'))
    except Exception as e:
        print(f"ERRO ao registrar saída: {e}")  # Log para debug
        flash(f'Erro ao registrar saída: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/chegada')
@login_required
def chegada():
    veiculos_em_uso = [v for v in veiculos_sheet.get_all_records() if v['Status'] == 'Em Uso']
    return render_template('registrar_chegada.html', veiculos_em_uso=veiculos_em_uso)

@app.route('/registrar-chegada', methods=['POST'])
@login_required
def registrar_chegada():
    placa = request.form.get('veiculo')
    km_final_str = request.form.get('km_final')
    
    # SUGESTÃO 1: VALIDAÇÃO DE DADOS
    km_final = int(km_final_str)
    km_inicial = -1
    viagem_a_finalizar_row = -1

    viagens_cells = viagens_sheet.findall(placa)
    for cell in reversed(viagens_cells):
        row_data = viagens_sheet.row_values(cell.row)
        if row_data[10] == 'Em Rota': # Coluna 11 (K) é o Status
            km_inicial = int(row_data[3]) # Coluna 4 (D) é KmInicial
            viagem_a_finalizar_row = cell.row
            break
            
    if km_inicial == -1:
        flash(f'Erro: Nenhuma viagem em rota encontrada para a placa {placa}.', 'danger')
        return redirect(url_for('chegada'))

    if km_final <= km_inicial:
        flash(f'Erro: A quilometragem final ({km_final} km) deve ser maior que a inicial ({km_inicial} km).', 'danger')
        return redirect(url_for('chegada'))

    # Se a validação passou, continua com o registro
    fuso_horario_sp = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso_horario_sp)
    data_chegada = agora.strftime('%d/%m/%Y')
    hora_chegada = agora.strftime('%H:%M:%S')

    viagens_sheet.update_cell(viagem_a_finalizar_row, 5, km_final)
    viagens_sheet.update_cell(viagem_a_finalizar_row, 8, data_chegada)
    viagens_sheet.update_cell(viagem_a_finalizar_row, 9, hora_chegada)
    viagens_sheet.update_cell(viagem_a_finalizar_row, 11, "Finalizada")

    try:
        cell_veiculo = veiculos_sheet.find(placa)
        veiculos_sheet.update_cell(cell_veiculo.row, 4, "Disponível")
    except Exception as e:
        flash(f'AVISO: Placa {placa} não encontrada para liberar o status.', 'warning')
    
    flash('Chegada registrada com sucesso!', 'success')
    return redirect(url_for('index'))

# --- PÁGINAS DE VISUALIZAÇÃO ---

@app.route('/cronograma')
@login_required
def cronograma():
    viagens_em_rota = [v for v in get_all_records(viagens_sheet) if v['Status'] == 'Em Rota']
    
    # Enriquecer os dados com informações adicionais
    for viagem in viagens_em_rota:
        # Garantir que todos os campos existem, mesmo que vazios
        if 'Passageiros' not in viagem:
            viagem['Passageiros'] = '0'
        if 'Observacoes' not in viagem:
            viagem['Observacoes'] = ''
        if 'HoraChegada' not in viagem:
            viagem['HoraChegada'] = ''
    
    return render_template('cronograma.html', viagens=viagens_em_rota)

@app.route('/cancelar-viagem', methods=['POST'])
@admin_required
def cancelar_viagem():
    """Cancela uma viagem agendada (apenas para admin)."""
    try:
        viagem_id = request.form.get('viagem_id')
        
        if not viagem_id:
            flash('ID da viagem não fornecido.', 'danger')
            return redirect(url_for('cronograma'))
        
        # Encontrar a viagem com o ID e atualizar seu status
        viagens_records = viagens_sheet.get_all_records()
        viagem_encontrada = False
        
        for idx, viagem in enumerate(viagens_records, 2):  # Começa da linha 2
            if str(viagem.get('ID')) == str(viagem_id):
                # Atualizar o status para "Cancelada"
                viagens_sheet.update_cell(idx, 11, "Cancelada")  # Coluna 11 é Status
                viagem_encontrada = True
                
                # Liberar o veículo se estava em uso
                placa = viagem.get('PlacaVeiculo')
                if placa:
                    try:
                        cell = veiculos_sheet.find(placa)
                        veiculos_sheet.update_cell(cell.row, 4, "Disponível")
                    except:
                        pass
                
                break
        
        if viagem_encontrada:
            flash('Viagem cancelada com sucesso!', 'success')
        else:
            flash('Viagem não encontrada.', 'danger')
        
        return redirect(url_for('cronograma'))
    except Exception as e:
        print(f"ERRO ao cancelar viagem: {e}")
        flash(f'Erro ao cancelar viagem: {e}', 'danger')
        return redirect(url_for('cronograma'))

@app.route('/historico')
@login_required
def historico():
    viagens_finalizadas = [v for v in get_all_records(viagens_sheet) if v['Status'] == 'Finalizada']
    return render_template('historico.html', viagens=viagens_finalizadas)

# --- ROTAS DE ADMIN (PROTEGIDAS E COM VERIFICAÇÃO DE PAPEL) ---

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403) # Erro de Acesso Proibido
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# --- PÁGINA DE GERENCIAMENTO ---

@app.route('/gerenciar')
@admin_required
def gerenciar():
    """Página para gerenciar motoristas, veículos E USUÁRIOS."""
    motoristas = motoristas_sheet.get_all_records()
    veiculos = veiculos_sheet.get_all_records()
    usuarios = usuarios_sheet.get_all_records()
    return render_template('gerenciar.html', motoristas=motoristas, veiculos=veiculos, usuarios=usuarios)


@app.route('/relatorios')
@admin_required
def relatorios():
    """
    Exibe um relatório diário de KM por veículo e por motorista.
    Permite a consulta de dias anteriores através de um parâmetro na URL.
    """
    # --- LÓGICA DE DATA ---
    # Pega a data da URL (formato YYYY-MM-DD)
    data_str = request.args.get('data')
    
    if data_str:
        try:
            data_selecionada_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            # Se a data for inválida, usa a data de hoje
            data_selecionada_obj = datetime.now().date()
            flash("Formato de data inválido. Exibindo relatório de hoje.", "warning")
    else:
        # Se nenhuma data for fornecida, usa a data de hoje
        data_selecionada_obj = datetime.now().date()

    # Formata a data para dois padrões:
    # 1. Para exibir no HTML (DD/MM/YYYY)
    data_display = data_selecionada_obj.strftime('%d/%m/%Y')
    # 2. Para comparar com os dados da planilha (que também é DD/MM/YYYY)
    data_comparacao = data_selecionada_obj.strftime('%d/%m/%Y')
    # 3. Para preencher o valor do input date no HTML (YYYY-MM-DD)
    data_input_value = data_selecionada_obj.strftime('%Y-%m-%d')

    # --- LÓGICA DE CÁLCULO ---
    viagens_finalizadas = [v for v in viagens_sheet.get_all_records() if v.get('Status') == 'Finalizada']
    
    # Filtra as viagens para incluir apenas as do dia selecionado (baseado na data de SAÍDA)
    viagens_do_dia = [v for v in viagens_finalizadas if v.get('DataSaida') == data_comparacao]
    
    relatorio_veiculos = {}
    relatorio_motoristas = {}

    for viagem in viagens_do_dia:
        try:
            km_inicial = int(viagem.get('KmInicial', 0))
            km_final = int(viagem.get('KmFinal', 0))
            
            # Garante que os dados são válidos para o cálculo
            if km_final > km_inicial:
                distancia = km_final - km_inicial
                
                # Acumula por veículo
                placa = viagem.get('PlacaVeiculo')
                if placa:
                    relatorio_veiculos[placa] = relatorio_veiculos.get(placa, 0) + distancia
                
                # Acumula por motorista
                motorista = viagem.get('Motorista')
                if motorista:
                    relatorio_motoristas[motorista] = relatorio_motoristas.get(motorista, 0) + distancia
        except (ValueError, TypeError):
            # Ignora linhas com KM inválido que não pode ser convertido para número
            continue
            
    return render_template('relatorios.html', 
                           relatorio_veiculos=relatorio_veiculos,
                           relatorio_motoristas=relatorio_motoristas,
                           data_display=data_display,
                           data_input_value=data_input_value)

@app.route('/add-motorista', methods=['POST'])
def add_motorista():
    try:
        nome = request.form.get('nome')
        matricula = request.form.get('matricula')
        motoristas_sheet.append_row([nome, matricula])
        flash(f'Motorista {nome} adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar motorista: {e}', 'danger')
    return redirect(url_for('gerenciar'))

@app.route('/add-veiculo', methods=['POST'])
def add_veiculo():
    try:
        modelo = request.form.get('modelo')
        placa = request.form.get('placa')
        ano = request.form.get('ano')
        veiculos_sheet.append_row([modelo, placa, ano, 'Disponível'])
        flash(f'Veículo {modelo} - {placa} adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar veículo: {e}', 'danger')
    return redirect(url_for('gerenciar'))

@app.route('/add-user', methods=['POST'])
@admin_required
def add_user():
    """Processa o formulário de criação de novo usuário."""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # Verifica se o usuário já existe
        if User.get(username):
            flash(f'O nome de usuário "{username}" já existe. Tente outro.', 'danger')
            return redirect(url_for('gerenciar'))

        # Validação simples
        if not username or not password or not role:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('gerenciar'))

        # Criptografa a senha
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Adiciona o novo usuário na planilha
        usuarios_sheet.append_row([username, password_hash, role])
        flash(f'Usuário {username} criado com sucesso!', 'success')

    except Exception as e:
        flash(f'Ocorreu um erro ao criar o usuário: {e}', 'danger')

    return redirect(url_for('gerenciar'))

# --- EXECUÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    app.run(debug=True)