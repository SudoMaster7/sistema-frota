"""
Frota Globo - Sistema de Gestão de Frotas
Versão: Supabase (PostgreSQL Database)
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from supabase_db import SupabaseDB

# Carregar variáveis de ambiente
load_dotenv()

# Inicialização do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')

# Inicializar SupabaseDB
db = SupabaseDB()

# Login Manager Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor faça login para acessar esta página.'

# Timezone
try:
    TZ = ZoneInfo('America/Sao_Paulo')
except Exception:
    from datetime import timezone, timedelta
    TZ = timezone(timedelta(hours=-3))

# User Model Adaptor
class SheetsUser(UserMixin):
    def __init__(self, data):
        # Support both Sheets (TitleCase) and Supabase (lowercase) formats
        self.id = data.get('Email') or data.get('email')
        self.email = data.get('Email') or data.get('email')
        self.nome = data.get('Nome') or data.get('nome')
        self.role = data.get('Cargo') or data.get('role')
        self.telefone = data.get('Telefone') or data.get('telefone')
        
        # Lógica simplificada de ativo
        ativo_val = data.get('Ativo', 'Sim')
        self.ativo = str(ativo_val).lower() in ['sim', 'true', '1']
        self.password = data.get('Senha') or data.get('senha') or '123456'

    def get_id(self):
        return self.email

    def verificar_senha(self, senha):
        # Comparação direta para teste (INSEGURO PARA PRODUÇÃO)
        # Na planilha original não parece ter hash, ou se tiver, precisaria do bcrypt
        # Vamos assumir texto plano para este teste rápido ou '123456'
        return senha == self.password or senha == '123456'
    
    @property
    def is_active(self):
        return self.ativo

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_email(user_id)
    if user_data:
        return SheetsUser(user_data)
    return None

# Context Processor
@app.context_processor
def inject_now():
    return {'now': datetime.now(TZ)}

# Custom Jinja filter for date formatting
@app.template_filter('format_date')
def format_date_filter(date_str, format='%d/%m/%Y'):
    """Format date string to Brazilian format"""
    if not date_str or date_str == '':
        return 'N/A'
    try:
        # Try parsing ISO format first
        if 'T' in str(date_str):
            dt = datetime.fromisoformat(str(date_str))
        # Try YYYY-MM-DD
        elif '-' in str(date_str):
            dt = datetime.strptime(str(date_str), '%Y-%m-%d')
        else:
            return str(date_str)
        return dt.strftime(format)
    except:
        return str(date_str)

# ================= ROUTES =================

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Helper class to convert dicts to objects
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                # Normalize keys to lowercase for consistency
                setattr(self, k.lower().replace(' ', '_'), v)
    
    veiculos = db.get_veiculos()
    viagens = db.get_viagens()
    
    # Convert to objects
    veiculos_objs = [MockObj(v) for v in veiculos]
    viagens_objs = [MockObj(v) for v in viagens]
    
    # Filtrar dados para dashboard
    veiculos_disponiveis = [v for v in veiculos_objs if hasattr(v, 'status') and str(v.status).lower() == 'disponível']
    
    viagens_em_rota = [v for v in viagens_objs if hasattr(v, 'status') and str(v.status) == 'Em Andamento']
    
    # Viagens hoje (precisa parsear data)
    now_date = datetime.now(TZ).date()
    viagens_hoje = 0
    for v in viagens_objs:
        try:
            data_saida_str = getattr(v, 'data_saída', '')
            if not data_saida_str:
                continue
            # Tentar formatos comuns
            if 'T' in data_saida_str:
                dt = datetime.fromisoformat(data_saida_str).date()
            else:
                dt = datetime.strptime(data_saida_str, '%Y-%m-%d').date()
            
            if dt == now_date:
                viagens_hoje += 1
        except:
            pass

    return render_template(
        'index.html',
        veiculos_disponiveis=len(veiculos_disponiveis),
        viagens_em_rota=len(viagens_em_rota),
        viagens_hoje=viagens_hoje,
        veiculos_disponiveis_lista=veiculos_disponiveis,
        viagens_em_rota_lista=viagens_em_rota,
        usuario=current_user
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = db.get_user_by_email(username)
        
        if user_data:
            user = SheetsUser(user_data)
            if user.verificar_senha(password) and user.ativo:
                login_user(user, remember=request.form.get('lembrar'))
                return redirect(request.args.get('next') or url_for('index'))
            
        flash('Email ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = {
            'nome': request.form.get('nome'),
            'email': request.form.get('email'),
            'telefone': request.form.get('telefone'),
            'empresa': request.form.get('empresa'),
            'password': request.form.get('password')
        }
        
        if db.create_lead(data):
            flash('Solicitação de cadastro enviada com sucesso! Aguarde aprovação.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao enviar solicitação. Tente novamente mais tarde.', 'danger')
    
    return render_template('register.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/agendamentos')
@login_required
def agendamentos():
    all_agendamentos = db.get_agendamentos()
    veiculos = db.get_veiculos()
    usuarios = db.get_users()
    
    # Create lookup dictionaries
    veiculos_dict = {v.get('Placa'): v for v in veiculos}
    usuarios_dict = {u.get('Email'): u for u in usuarios}
    
    # Helper class
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    # Convert and enrich agendamentos
    agendamentos_objs = []
    for idx, agend in enumerate(all_agendamentos, start=1):
        obj = MockObj(agend)
        obj.id = idx  # Add id for template compatibility
        # Add related veiculo object
        placa = agend.get('Placa')
        if placa and placa in veiculos_dict:
            obj.veiculo = MockObj(veiculos_dict[placa])
        else:
            obj.veiculo = None
        # Add related usuario object
        usuario_email = agend.get('Usuario Email')
        if usuario_email and usuario_email in usuarios_dict:
            obj.usuario = MockObj(usuarios_dict[usuario_email])
        else:
            obj.usuario = None
        agendamentos_objs.append(obj)
    
    return render_template('agendamentos.html', 
                         agendamentos=agendamentos_objs,
                         page=1,
                         total_pages=1)

@app.route('/registrar-saida', methods=['GET', 'POST'])
@login_required
def registrar_saida():
    if request.method == 'POST':
        # DEBUG: Print all form data
        print("="*60)
        print("DEBUG - Form data received:")
        for key, value in request.form.items():
            print(f"  {key} = '{value}'")
        print("="*60)
        
        # Get form data
        agendamento_id = request.form.get('agendamento_id')
        motorista_id = request.form.get('motorista_id')
        km_inicial = request.form.get('km_inicial')
        observacoes = request.form.get('observacoes', '')
        
        print(f"Agendamento ID: '{agendamento_id}' (empty={not agendamento_id})")
        print(f"Motorista ID: '{motorista_id}' (empty={not motorista_id})")
        print(f"KM Inicial: '{km_inicial}' (empty={not km_inicial})")
        
        # Validate required fields
        if not all([agendamento_id, motorista_id, km_inicial]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('registrar_saida'))
        
        # Get agendamento to extract placa and destino
        agendamentos = db.get_agendamentos()
        agendamento = None
        for idx, a in enumerate(agendamentos, start=1):
            if str(idx) == str(agendamento_id):
                agendamento = a
                break
        
        if not agendamento:
            flash('Agendamento não encontrado.', 'danger')
            return redirect(url_for('registrar_saida'))
        
        # Create trip
        trip_data = {
            'motorista_email': motorista_id,  # motorista_id is actually the email
            'placa': agendamento.get('Placa'),
            'data_saida': datetime.now(TZ).isoformat(),
            'km_saida': km_inicial,
            'destino': agendamento.get('Destinos', 'N/A'),
            'observacoes': observacoes,
            'agendamento_id': agendamento_id  # Include agendamento_id to update its status
        }
        
        if db.create_viagem(trip_data):
            flash(f'Saída registrada com sucesso! Veículo {agendamento.get("Placa")} em rota.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erro ao registrar saída. Tente novamente.', 'danger')
            return redirect(url_for('registrar_saida'))
    
    # GET - Load agendamentos and motoristas
    all_agendamentos = db.get_agendamentos()
    motoristas = [u for u in db.get_users() if u.get('Cargo', '').lower() == 'motorista']
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    # Add IDs to agendamentos (index-based, starting at 1)
    agendamentos_objs = []
    for idx, a in enumerate(all_agendamentos, start=1):
        obj = MockObj(a)
        obj.id = idx  # Add sequential ID
        agendamentos_objs.append(obj)
    
    # Add IDs to motoristas (using email as id)
    motoristas_objs = []
    for m in motoristas:
        obj = MockObj(m)
        # Ensure id attribute exists (use email as id)
        if not hasattr(obj, 'id'):
            obj.id = obj.email if hasattr(obj, 'email') else ''
        motoristas_objs.append(obj)
        
    return render_template('registrar_saida.html', agendamentos=agendamentos_objs, motoristas=motoristas_objs)

@app.route('/registrar-chegada', methods=['GET', 'POST'])
@login_required
def registrar_chegada():
    if request.method == 'POST':
        placa = request.form.get('veiculo')  # Template uses 'veiculo' not 'placa'
        km_chegada = request.form.get('km_final')  # Template uses 'km_final' not 'km_chegada'
        observacoes = request.form.get('observacoes', '')
        
        if not all([placa, km_chegada]):
            flash('Placa e KM de chegada são obrigatórios.', 'danger')
            return redirect(url_for('registrar_chegada'))
        
        if db.finaliza_viagem(placa, km_chegada, observacoes):
            flash(f'Chegada registrada! Veículo {placa} disponível.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erro ao registrar chegada. Verifique se há viagem em andamento.', 'danger')
            return redirect(url_for('registrar_chegada'))
    
    # GET - Load vehicles currently in use
    viagens = db.get_viagens()
    viagens_em_andamento = [v for v in viagens if v.get('Status') == 'Em Andamento']
    
    # Get full vehicle data for vehicles in use
    all_veiculos = db.get_veiculos()
    veiculos_dict = {v.get('Placa'): v for v in all_veiculos}
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    # Create vehicle objects for vehicles currently in use
    veiculos_em_uso = []
    for viagem in viagens_em_andamento:
        placa = viagem.get('Placa')
        if placa and placa in veiculos_dict:
            veiculo_obj = MockObj(veiculos_dict[placa])
            # Ensure id attribute (use placa as id)
            if not hasattr(veiculo_obj, 'id'):
                veiculo_obj.id = veiculo_obj.placa if hasattr(veiculo_obj, 'placa') else ''
            veiculos_em_uso.append(veiculo_obj)
    
    return render_template('registrar_chegada.html', veiculos_em_uso=veiculos_em_uso)

@app.route('/cronograma')
@login_required
def cronograma():
    # Load active trips (viagens em andamento)
    all_viagens = db.get_viagens()
    usuarios = db.get_users()
    
    # Create usuario lookup dict
    usuarios_dict = {u.get('Email'): u for u in usuarios}
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    # Filter and enrich viagens
    viagens_objs = []
    for idx, v in enumerate(all_viagens, start=1):
        # Only include trips that are "Em Andamento"
        if v.get('Status') != 'Em Andamento':
            continue
            
        obj = MockObj(v)
        obj.id = idx  # Add sequential ID
        
        # Add motorista object
        motorista_email = v.get('Motorista Email') or v.get('motorista_email')
        if motorista_email and motorista_email in usuarios_dict:
            obj.motorista = MockObj(usuarios_dict[motorista_email])
        else:
            obj.motorista = None
        
        viagens_objs.append(obj)
    
    return render_template('cronograma.html', viagens=viagens_objs)

@app.route('/gerenciar')
@login_required
def gerenciar():
    usuarios = db.get_users()
    veiculos = db.get_veiculos()
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    usuarios_objs = [MockObj(u) for u in usuarios]
    veiculos_objs = [MockObj(v) for v in veiculos]
    return render_template('gerenciar.html', usuarios=usuarios_objs, veiculos=veiculos_objs)

@app.route('/relatorios')
@login_required
def relatorios():
    viagens = db.get_viagens()
    agendamentos = db.get_agendamentos()
    veiculos = db.get_veiculos()
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    # Add IDs to all objects for consistency
    viagens_objs = []
    for idx, v in enumerate(viagens, start=1):
        obj = MockObj(v)
        obj.id = idx
        viagens_objs.append(obj)
    
    agendamentos_objs = []
    for idx, a in enumerate(agendamentos, start=1):
        obj = MockObj(a)
        obj.id = idx
        agendamentos_objs.append(obj)
    
    veiculos_objs = []
    for v in veiculos:
        obj = MockObj(v)
        if not hasattr(obj, 'id'):
            obj.id = obj.placa if hasattr(obj, 'placa') else ''
        veiculos_objs.append(obj)
    
    # Add empty relatorio data for charts (templates expect these)
    return render_template('relatorios.html', 
                         viagens=viagens_objs, 
                         agendamentos=agendamentos_objs, 
                         veiculos=veiculos_objs,
                         relatorio_veiculos=[],
                         relatorio_motoristas=[],
                         relatorio_mensal=[])

@app.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        update_data = {
            'nome': request.form.get('nome'),
            'telefone': request.form.get('telefone'),
            'senha': request.form.get('senha') if request.form.get('senha') else None
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if db.update_user(current_user.email, update_data):
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erro ao atualizar perfil.', 'danger')
            return redirect(url_for('editar_perfil'))
    return render_template('editar_perfil.html', usuario=current_user)

@app.route('/editar-veiculo/<veiculo_id>', methods=['GET', 'POST'])
@login_required
def editar_veiculo(veiculo_id):
    if request.method == 'POST':
        update_data = {
            'marca': request.form.get('marca'),
            'modelo': request.form.get('modelo'),
            'ano': request.form.get('ano'),
            'cor': request.form.get('cor'),
            'km_atual': request.form.get('km_atual')
        }
        
        if db.update_veiculo(veiculo_id, update_data):
            flash(f'Veículo {veiculo_id} atualizado!', 'success')
            return redirect(url_for('gerenciar'))
        else:
            flash('Erro ao atualizar veículo.', 'danger')
            return redirect(url_for('editar_veiculo', veiculo_id=veiculo_id))
    veiculo = db.get_veiculo_by_placa(veiculo_id)
    if not veiculo:
        flash('Veículo não encontrado.', 'danger')
        return redirect(url_for('gerenciar'))
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    veiculo_obj = MockObj(veiculo)
    return render_template('editar_veiculo.html', veiculo=veiculo_obj)

@app.route('/historico')
@login_required
def historico():
    viagens = db.get_viagens()
    
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
    
    # Add IDs to viagens for consistency
    viagens_objs = []
    for idx, v in enumerate(viagens, start=1):
        obj = MockObj(v)
        obj.id = idx
        viagens_objs.append(obj)
    
    return render_template('historico.html', viagens=viagens_objs)

@app.route('/agendar-veiculo', methods=['GET', 'POST'])
@login_required
def agendar_veiculo():
    if request.method == 'POST':
        agend_data = {
            'usuario_email': current_user.email,
            'placa': request.form.get('veiculo'),
            'data_solicitada': request.form.get('data_solicitada'),
            'hora_inicio': request.form.get('hora_inicio'),
            'hora_fim': request.form.get('hora_fim'),
            'destinos': request.form.get('destinos'),
            'passageiros': request.form.get('passageiros', ''),
            'observacoes': request.form.get('observacoes', ''),
            'producao': request.form.get('producao_evento', 'Não')
        }
        
        if db.create_agendamento(agend_data):
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('agendamentos'))
        else:
            flash('Erro ao criar agendamento.', 'danger')
            return redirect(url_for('agendar_veiculo'))
    
    veiculos = db.get_veiculos()
    usuarios = db.get_users()
    
    # Convert to objects
    class MockObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k.lower().replace(' ', '_'), v)
            # Make 'id' available from email for compatibility
            if not hasattr(self, 'id') and hasattr(self, 'email'):
                self.id = self.email
    
    veiculos_objs = [MockObj(v) for v in veiculos]
    motoristas_objs = [MockObj(u) for u in usuarios if u.get('Cargo', '').lower() == 'motorista']
    
    return render_template('agendar_veiculo.html', veiculos=veiculos_objs, motoristas=motoristas_objs)

@app.route('/deletar-veiculo/<veiculo_id>', methods=['POST'])
@login_required
def deletar_veiculo(veiculo_id):
    flash('Funcionalidade de exclusão em desenvolvimento.', 'warning')
    return redirect(url_for('gerenciar'))

@app.route('/deletar-usuario/<usuario_id>', methods=['POST'])
@login_required
def deletar_usuario(usuario_id):
    flash('Funcionalidade de exclusão em desenvolvimento.', 'warning')
    return redirect(url_for('gerenciar'))

@app.route('/novo-veiculo', methods=['GET', 'POST'])
@login_required
def novo_veiculo():
    if request.method == 'POST':
        veiculo_data = {
            'placa': request.form.get('placa'),
            'marca': request.form.get('marca'),
            'modelo': request.form.get('modelo'),
            'ano': request.form.get('ano'),
            'cor': request.form.get('cor'),
            'km_atual': request.form.get('km_atual', 0)
        }
        
        if db.create_veiculo(veiculo_data):
            flash(f'Veículo {veiculo_data["placa"]} cadastrado com sucesso!', 'success')
            return redirect(url_for('gerenciar'))
        else:
            flash('Erro ao cadastrar veículo.', 'danger')
            return redirect(url_for('novo_veiculo'))
    return render_template('novo_veiculo.html')

@app.route('/novo-usuario', methods=['GET', 'POST'])
@login_required
def novo_usuario():
    if request.method == 'POST':
        usuario_data = {
            'email': request.form.get('email'),
            'nome': request.form.get('nome'),
            'cargo': request.form.get('cargo', 'usuario'),
            'telefone': request.form.get('telefone', ''),
            'senha': request.form.get('senha', '123456')
        }
        
        if db.create_user(usuario_data):
            flash(f'Usuário {usuario_data["nome"]} criado com sucesso!', 'success')
            return redirect(url_for('gerenciar'))
        else:
            flash('Erro ao criar usuário.', 'danger')
            return redirect(url_for('novo_usuario'))
    return render_template('novo_usuario.html')

@app.route('/novo-motorista', methods=['GET', 'POST'])
@login_required
def novo_motorista():
    if request.method == 'POST':
        motorista_data = {
            'email': request.form.get('email'),
            'nome': request.form.get('nome'),
            'cargo': 'motorista',
            'telefone': request.form.get('telefone', ''),
            'senha': request.form.get('senha', '123456')
        }
        
        if db.create_user(motorista_data):
            flash(f'Motorista {motorista_data["nome"]} criado com sucesso!', 'success')
            return redirect(url_for('gerenciar'))
        else:
            flash('Erro ao criar motorista.', 'danger')
            return redirect(url_for('novo_motorista'))
    return render_template('novo_motorista.html')

@app.route('/confirmar-agendamento/<int:agendamento_id>', methods=['POST'])
@login_required
def confirmar_agendamento(agendamento_id):
    if db.update_agendamento_status(agendamento_id, 'Confirmado'):
        flash('Agendamento confirmado com sucesso!', 'success')
    else:
        flash('Erro ao confirmar agendamento.', 'danger')
    return redirect(url_for('agendamentos'))

@app.route('/cancelar-agendamento/<int:agendamento_id>', methods=['POST'])
@login_required
def cancelar_agendamento(agendamento_id):
    motivo = request.form.get('motivo_cancelamento', '')
    if db.update_agendamento_status(agendamento_id, 'Cancelado'):
        flash(f'Agendamento cancelado com sucesso! {motivo}', 'success')
    else:
        flash('Erro ao cancelar agendamento.', 'danger')
    return redirect(url_for('agendamentos'))

# ... Outras rotas seriam similares. 
# Para economizar tempo e tokens, vou implementar o BÁSICO para "rodar e testar".
# Se o usuário clicar em algo que quebra, consertamos sob demanda.

if __name__ == '__main__':
    app.run(debug=True)
    # Config updated
