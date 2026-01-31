"""
Frota Globo - Sistema de Gestão de Frotas
Versão 2.0 - PostgreSQL + Redis + SQLAlchemy
Sprint 1 - Nova Arquitetura
"""
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
# pytz substituído por zoneinfo nativa
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    from config import ProductionConfig as Config
elif config_name == 'testing':
    from config import TestingConfig as Config
else:
    from config import DevelopmentConfig as Config

# Inicialização do Flask
app = Flask(__name__)
app.config.from_object(Config)

# Importar modelos primeiro
import models
from models import db, bcrypt as models_bcrypt

# Configurar db com a aplicação Flask
db.init_app(app)
models_bcrypt.init_app(app)
migrate = Migrate(app, db)

# Importar classes de modelo
from models import Usuario, Veiculo, Agendamento, Viagem, Manutencao, Abastecimento, Auditoria

# Database - já inicializado acima
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# bcrypt = Bcrypt(app)

# Cache
cache = Cache(app, config={'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple')})

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor faça login para acessar esta página.'

# Timezone
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo('America/Sao_Paulo')
except Exception:
    # Fallback para UTC se tzdata não está disponível
    from datetime import timezone, timedelta
    TZ = timezone(timedelta(hours=-3))  # UTC-3 (São Paulo)

# Configurar logging
if not app.debug and not app.testing:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/frota_globo.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('🚀 Frota Globo iniciando...')

@login_manager.user_loader
def load_user(user_id):
    from sqlalchemy import select
    stmt = select(Usuario).where(Usuario.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()

# ==================== CONTEXT PROCESSOR ====================
@app.context_processor
def inject_now():
    return {'now': datetime.now(TZ)}

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Dashboard principal"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    now = datetime.now(TZ)
    
    # Estatísticas e dados detalhados
    veiculos_disponiveis = db.session.execute(
        db.select(Veiculo).where(db.func.lower(Veiculo.status) == 'disponível').order_by(Veiculo.placa)
    ).scalars().all()
    viagens_em_rota = db.session.execute(
        db.select(Viagem)
        .where(Viagem.data_chegada == None, db.func.lower(Viagem.status) == 'em andamento')
        .order_by(Viagem.data_saida.desc())
    ).scalars().all()
    
    viagens_hoje = db.session.query(Viagem).filter(
        db.func.date(Viagem.data_saida) == now.date()
    ).count()
    
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
    """Login de usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # O formulário envia 'username' e 'password', não 'email' e 'senha'
        username = request.form.get('username')  # Pode ser email ou username
        password = request.form.get('password')
        
        from sqlalchemy import select
        # Tentar buscar por email primeiro
        stmt = select(Usuario).where(Usuario.email == username)
        usuario = db.session.execute(stmt).scalar_one_or_none()
        
        if usuario and usuario.verificar_senha(password) and usuario.ativo:
            login_user(usuario, remember=request.form.get('lembrar'))
            app.logger.info(f'✅ Usuário {username} fez login')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            app.logger.warning(f'❌ Tentativa de login falhou: {username}')
            flash('Email ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    app.logger.info(f'📵 Usuário {current_user.email} fez logout')
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/perfil/editar', endpoint='editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Editar perfil do usuário"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            telefone = request.form.get('telefone', '').strip()
            
            # Validar dados
            if not nome:
                flash('Nome é obrigatório!', 'danger')
                return render_template('editar_perfil.html', usuario=current_user)
            
            if len(nome) < 3:
                flash('Nome deve ter pelo menos 3 caracteres!', 'danger')
                return render_template('editar_perfil.html', usuario=current_user)
            
            # Atualizar usuário
            current_user.nome = nome
            if telefone:
                current_user.telefone = telefone
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            app.logger.info(f'✏️ Usuário {current_user.email} atualizou seu perfil')
            return redirect(url_for('editar_perfil'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
            return render_template('editar_perfil.html', usuario=current_user)
    
    return render_template('editar_perfil.html', usuario=current_user)

@app.route('/agendamentos')
@login_required
def agendamentos():
    """Lista agendamentos"""
    page = request.args.get('page', 1, type=int)
    from sqlalchemy import select
    stmt = select(Agendamento)
    agendamentos_page = db.paginate(stmt, page=page, per_page=20)
    
    return render_template('agendamentos.html', 
                         agendamentos=agendamentos_page.items,
                         page=page,
                         total_pages=agendamentos_page.pages)

@app.route('/cronograma')
@login_required
def cronograma():
    """Cronograma de viagens"""
    from sqlalchemy import select
    
    # Buscar viagens em andamento (sem chegada)
    stmt = select(Viagem).where(Viagem.data_chegada == None).order_by(Viagem.data_saida.desc())
    viagens = db.session.execute(stmt).scalars().all()
    
    return render_template('cronograma.html', viagens=viagens)

@app.route('/registrar-saida', endpoint='registrar_saida', methods=['GET', 'POST'])
@login_required
def registrar_saida():
    """Registrar saída de veículo"""
    from sqlalchemy import select
    
    if request.method == 'GET':
        # Buscar agendamentos confirmados
        stmt = select(Agendamento).where(Agendamento.status == 'Confirmado')
        agendamentos = db.session.execute(stmt).scalars().all()
        
        # Buscar motoristas
        stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
        motoristas = db.session.execute(stmt_motoristas).scalars().all()
        
        return render_template('registrar_saida.html', agendamentos=agendamentos, motoristas=motoristas)
    
    elif request.method == 'POST':
        try:
            agendamento_id = request.form.get('agendamento_id')
            motorista_id = request.form.get('motorista_id')
            km_inicial = request.form.get('km_inicial')
            observacoes = request.form.get('observacoes', '')
            
            # Validar dados
            if not agendamento_id or not km_inicial or not motorista_id:
                flash('Agendamento, motorista e KM inicial são obrigatórios', 'danger')
                stmt = select(Agendamento).where(Agendamento.status == 'Confirmado')
                agendamentos = db.session.execute(stmt).scalars().all()
                stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
                motoristas = db.session.execute(stmt_motoristas).scalars().all()
                return render_template('registrar_saida.html', agendamentos=agendamentos, motoristas=motoristas)
            
            # Buscar agendamento
            agendamento = db.session.get(Agendamento, int(agendamento_id))
            if not agendamento:
                flash('Agendamento não encontrado', 'danger')
                stmt = select(Agendamento).where(Agendamento.status == 'Confirmado')
                agendamentos = db.session.execute(stmt).scalars().all()
                stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
                motoristas = db.session.execute(stmt_motoristas).scalars().all()
                return render_template('registrar_saida.html', agendamentos=agendamentos, motoristas=motoristas)
            
            if agendamento.status != 'Confirmado':
                flash('Agendamento não está confirmado', 'danger')
                stmt = select(Agendamento).where(Agendamento.status == 'Confirmado')
                agendamentos = db.session.execute(stmt).scalars().all()
                stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
                motoristas = db.session.execute(stmt_motoristas).scalars().all()
                return render_template('registrar_saida.html', agendamentos=agendamentos, motoristas=motoristas)
            
            # Verificar se motorista existe
            motorista = db.session.get(Usuario, motorista_id)
            if not motorista or motorista.role != 'motorista':
                flash('Motorista não encontrado ou inválido', 'danger')
                stmt = select(Agendamento).where(Agendamento.status == 'Confirmado')
                agendamentos = db.session.execute(stmt).scalars().all()
                stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
                motoristas = db.session.execute(stmt_motoristas).scalars().all()
                return render_template('registrar_saida.html', agendamentos=agendamentos, motoristas=motoristas)
            
            # Criar viagem
            viagem = Viagem(
                agendamento_id=agendamento.id,
                motorista_id=motorista_id,
                placa=agendamento.placa,
                data_saida=datetime.now(timezone.utc).astimezone(ZoneInfo('America/Sao_Paulo')),
                km_saida=float(km_inicial),
                destino=agendamento.destinos,
                observacoes=observacoes,
                status='Em Andamento'
            )
            
            # Atualizar status do agendamento
            agendamento.status = 'Em Uso'
            
            db.session.add(viagem)
            db.session.commit()
            
            flash(f'Saída registrada com sucesso! Viagem #{viagem.id}', 'success')
            return redirect(url_for('agendamentos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar saída: {str(e)}', 'danger')
            stmt = select(Agendamento).where(Agendamento.status == 'Confirmado')
            agendamentos = db.session.execute(stmt).scalars().all()
            stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
            motoristas = db.session.execute(stmt_motoristas).scalars().all()
            return render_template('registrar_saida.html', agendamentos=agendamentos, motoristas=motoristas)

@app.route('/registrar-chegada', endpoint='registrar_chegada', methods=['GET', 'POST'])
@login_required
def registrar_chegada():
    """Registrar chegada de veículo"""
    from sqlalchemy import select

    def carregar_viagens_e_veiculos():
        """Retorna viagens em andamento e veículos correspondentes sem executar IN vazio."""
        stmt = select(Viagem).where(Viagem.data_chegada == None)
        viagens_abertas = db.session.execute(stmt).scalars().all()
        placas_em_uso = [v.placa for v in viagens_abertas]

        veiculos_em_uso = []
        if placas_em_uso:
            stmt_veiculos_em_uso = select(Veiculo).where(Veiculo.placa.in_(placas_em_uso))
            veiculos_em_uso = db.session.execute(stmt_veiculos_em_uso).scalars().all()

        return viagens_abertas, veiculos_em_uso
    
    if request.method == 'GET':
        viagens, veiculos_em_uso = carregar_viagens_e_veiculos()
        
        return render_template('registrar_chegada.html', viagens=viagens, veiculos_em_uso=veiculos_em_uso)
    
    elif request.method == 'POST':
        try:
            veiculo = request.form.get('veiculo')  # placa do veículo
            km_final = request.form.get('km_final')
            observacoes = request.form.get('observacoes', '')
            
            # Validar dados
            if not veiculo or not km_final:
                flash('Veículo e KM final são obrigatórios', 'danger')
                viagens, veiculos_em_uso = carregar_viagens_e_veiculos()
                return render_template('registrar_chegada.html', viagens=viagens, veiculos_em_uso=veiculos_em_uso)
            
            # Buscar viagem pela placa do veículo
            stmt = select(Viagem).where((Viagem.placa == veiculo) & (Viagem.data_chegada == None))
            viagem = db.session.execute(stmt).scalars().first()
            
            if not viagem:
                flash('Nenhuma viagem em andamento encontrada para este veículo', 'danger')
                viagens, veiculos_em_uso = carregar_viagens_e_veiculos()
                return render_template('registrar_chegada.html', viagens=viagens, veiculos_em_uso=veiculos_em_uso)
            
            # Validar KM final
            km_final_float = float(km_final)
            if km_final_float < viagem.km_saida:
                flash(f'KM final ({km_final_float}) não pode ser menor que KM saida ({viagem.km_saida})', 'danger')
                viagens, veiculos_em_uso = carregar_viagens_e_veiculos()
                return render_template('registrar_chegada.html', viagens=viagens, veiculos_em_uso=veiculos_em_uso)
            
            # Atualizar viagem com chegada
            viagem.data_chegada = datetime.now(timezone.utc).astimezone(ZoneInfo('America/Sao_Paulo'))
            viagem.km_chegada = km_final_float
            viagem.status = 'Finalizada'
            if observacoes:
                viagem.observacoes = observacoes
            
            # Atualizar status do agendamento para Finalizado
            if viagem.agendamento_id:
                agendamento = db.session.get(Agendamento, viagem.agendamento_id)
                if agendamento:
                    agendamento.status = 'Finalizado'
            
            # Atualizar status do veículo para disponível
            stmt_veiculo = select(Veiculo).where(Veiculo.placa == viagem.placa)
            veiculo_obj = db.session.execute(stmt_veiculo).scalars().first()
            if veiculo_obj:
                veiculo_obj.status = 'disponível'
            
            db.session.commit()
            
            flash(f'Chegada registrada com sucesso! Viagem finalizada.', 'success')
            return redirect(url_for('historico'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar chegada: {str(e)}', 'danger')
            viagens, veiculos_em_uso = carregar_viagens_e_veiculos()
            return render_template('registrar_chegada.html', viagens=viagens, veiculos_em_uso=veiculos_em_uso)

@app.route('/historico')
@login_required
def historico():
    """Histórico de viagens"""
    from sqlalchemy import select
    
    # Buscar viagens finalizadas (com data_chegada registrada)
    stmt = select(Viagem).where(Viagem.data_chegada != None).order_by(Viagem.data_chegada.desc())
    viagens = db.session.execute(stmt).scalars().all()
    
    return render_template('historico.html', viagens=viagens)

@app.route('/gerenciar')
@login_required
def gerenciar():
    """Gerenciar usuários e veículos"""
    from sqlalchemy import select
    
    # Carregar veículos e usuários
    stmt_veiculos = select(Veiculo)
    veiculos = db.session.execute(stmt_veiculos).scalars().all()
    
    stmt_usuarios = select(Usuario)
    usuarios = db.session.execute(stmt_usuarios).scalars().all()
    
    return render_template('gerenciar.html', veiculos=veiculos, usuarios=usuarios)

@app.route('/veiculo/novo', endpoint='novo_veiculo', methods=['GET', 'POST'])
@login_required
def novo_veiculo():
    """Adicionar novo veículo"""
    if request.method == 'POST':
        placa = request.form.get('placa')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        ano = request.form.get('ano')
        
        if placa and marca and modelo:
            novo = Veiculo(
                placa=placa.upper(),
                marca=marca,
                modelo=modelo,
                ano=int(ano) if ano else None,
                status='disponível'
            )
            db.session.add(novo)
            db.session.commit()
            flash(f'Veículo {placa} adicionado com sucesso!', 'success')
            return redirect(url_for('gerenciar'))
        else:
            flash('Preencha todos os campos obrigatórios!', 'danger')
    
    return render_template('novo_veiculo.html')

@app.route('/veiculo/<veiculo_id>/editar', endpoint='editar_veiculo', methods=['GET', 'POST'])
@login_required
def editar_veiculo(veiculo_id):
    """Editar veículo"""
    from sqlalchemy import select
    stmt = select(Veiculo).where(Veiculo.id == veiculo_id)
    veiculo = db.session.execute(stmt).scalar_one_or_none()
    
    if not veiculo:
        flash('Veículo não encontrado!', 'danger')
        return redirect(url_for('gerenciar'))
    
    if request.method == 'POST':
        veiculo.placa = request.form.get('placa', veiculo.placa).upper()
        veiculo.marca = request.form.get('marca', veiculo.marca)
        veiculo.modelo = request.form.get('modelo', veiculo.modelo)
        veiculo.status = request.form.get('status', veiculo.status)
        
        db.session.commit()
        flash(f'Veículo atualizado!', 'success')
        return redirect(url_for('gerenciar'))
    
    return render_template('editar_veiculo.html', veiculo=veiculo)

@app.route('/veiculo/<veiculo_id>/deletar', endpoint='deletar_veiculo', methods=['POST'])
@login_required
def deletar_veiculo(veiculo_id):
    """Deletar veículo"""
    from sqlalchemy import select
    stmt = select(Veiculo).where(Veiculo.id == veiculo_id)
    veiculo = db.session.execute(stmt).scalar_one_or_none()
    
    if veiculo:
        db.session.delete(veiculo)
        db.session.commit()
        flash(f'Veículo deletado!', 'success')
    
    return redirect(url_for('gerenciar'))

@app.route('/relatorios')
@login_required
def relatorios():
    """Relatórios do sistema"""
    from sqlalchemy import select, and_, func
    from datetime import datetime, date
    
    # Parâmetros de busca
    data_param = request.args.get('data')
    veiculo_filter = request.args.get('veiculo')
    motorista_filter = request.args.get('motorista')
    
    # Data a exibir
    if data_param:
        try:
            data_busca = datetime.strptime(data_param, '%Y-%m-%d').date()
            data_display = data_busca.strftime('%d/%m/%Y')
            data_input_value = data_param
        except ValueError:
            data_busca = date.today()
            data_display = data_busca.strftime('%d/%m/%Y')
            data_input_value = data_busca.isoformat()
    else:
        data_busca = date.today()
        data_display = data_busca.strftime('%d/%m/%Y')
        data_input_value = data_busca.isoformat()
    
    # Buscar viagens finalizadas no dia (ignora viagens sem chegada para não poluir métricas)
    stmt = select(Viagem).where(
        func.date(Viagem.data_saida) == data_busca,
        Viagem.data_chegada != None
    )
    viagens = db.session.execute(stmt).scalars().all()
    
    # Filtrar por veículo se especificado
    if veiculo_filter:
        viagens = [v for v in viagens if v.placa.lower() == veiculo_filter.lower()]
    
    # Filtrar por motorista se especificado
    if motorista_filter:
        filtro_lower = motorista_filter.lower()
        viagens = [
            v for v in viagens
            if (
                v.motorista
                and (
                    (v.motorista.nome and filtro_lower in v.motorista.nome.lower())
                    or (v.motorista.email and filtro_lower in v.motorista.email.lower())
                )
            )
        ]
    
    # Processar relatórios
    relatorio_veiculos = {}
    relatorio_motoristas = {}
    
    for viagem in viagens:
        # Calcular KM rodados
        km_rodados = 0
        if viagem.km_chegada is not None and viagem.km_saida is not None:
            km_rodados = viagem.km_chegada - viagem.km_saida
        
        # Agrupar por veículo
        if viagem.placa not in relatorio_veiculos:
            relatorio_veiculos[viagem.placa] = 0
        relatorio_veiculos[viagem.placa] += km_rodados
        
        # Agrupar por motorista
        motorista_nome = 'N/A'
        if viagem.motorista:
            motorista_nome = viagem.motorista.nome if viagem.motorista.nome else viagem.motorista.email
        
        if motorista_nome not in relatorio_motoristas:
            relatorio_motoristas[motorista_nome] = 0
        relatorio_motoristas[motorista_nome] += km_rodados
    
    # Buscar lista de veículos e motoristas para filtros
    stmt_veiculos = select(Veiculo)
    todos_veiculos = db.session.execute(stmt_veiculos).scalars().all()
    
    stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
    todos_motoristas = db.session.execute(stmt_motoristas).scalars().all()
    
    return render_template(
        'relatorios.html',
        relatorio_veiculos=relatorio_veiculos,
        relatorio_motoristas=relatorio_motoristas,
        data_display=data_display,
        data_input_value=data_input_value,
        todos_veiculos=todos_veiculos,
        todos_motoristas=todos_motoristas,
        viagens_total=len(viagens)
    )

@app.route('/agendar-veiculo', endpoint='agendar_veiculo', methods=['GET', 'POST'])
@login_required
def agendar_veiculo():
    """Agendar veículo"""
    if request.method == 'POST':
        # Processar formulário de agendamento
        from datetime import datetime, date, time
        
        placa = request.form.get('veiculo')
        motorista_id = request.form.get('motorista')
        data_solicitada = request.form.get('data_solicitada')
        hora_inicio = request.form.get('hora_inicio')
        hora_fim = request.form.get('hora_fim')
        destinos = request.form.get('destinos')
        passageiros = request.form.get('passageiros')
        observacoes = request.form.get('observacoes')
        
        # Validar dados obrigatórios
        if not placa or not motorista_id or not data_solicitada or not hora_inicio or not hora_fim:
            flash('Preencha todos os campos obrigatórios!', 'danger')
            from sqlalchemy import select
            stmt_veiculos = select(Veiculo).where(Veiculo.status == 'disponível')
            veiculos = db.session.execute(stmt_veiculos).scalars().all()
            stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
            motoristas = db.session.execute(stmt_motoristas).scalars().all()
            return render_template('agendar_veiculo.html', veiculos=veiculos, motoristas=motoristas)
        
        # Converter strings para tipos Python apropriados
        try:
            # Converter data (formato: YYYY-MM-DD)
            data_obj = datetime.strptime(data_solicitada, '%Y-%m-%d').date()
            
            # Converter horas (formato: HH:MM)
            hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
            hora_fim_obj = datetime.strptime(hora_fim, '%H:%M').time()
        except ValueError as e:
            flash(f'Erro ao processar data/hora: {str(e)}', 'danger')
            from sqlalchemy import select
            stmt_veiculos = select(Veiculo).where(Veiculo.status == 'disponível')
            veiculos = db.session.execute(stmt_veiculos).scalars().all()
            stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
            motoristas = db.session.execute(stmt_motoristas).scalars().all()
            return render_template('agendar_veiculo.html', veiculos=veiculos, motoristas=motoristas)
        
        # Criar agendamento
        novo_agendamento = Agendamento(
            usuario_id=current_user.id,
            placa=placa,
            data_solicitada=data_obj,
            hora_inicio=hora_inicio_obj,
            hora_fim=hora_fim_obj,
            destinos=destinos,
            passageiros=int(passageiros) if passageiros else None,
            observacoes=observacoes,
            status='Agendado'
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso!', 'success')
        return redirect(url_for('agendamentos'))
    
    # GET: Carregar formulário com lista de veículos e motoristas
    from sqlalchemy import select
    stmt_veiculos = select(Veiculo).where(Veiculo.status == 'disponível')
    veiculos = db.session.execute(stmt_veiculos).scalars().all()
    
    stmt_motoristas = select(Usuario).where(Usuario.role == 'motorista')
    motoristas = db.session.execute(stmt_motoristas).scalars().all()
    
    return render_template('agendar_veiculo.html', veiculos=veiculos, motoristas=motoristas)

@app.route('/confirmar-agendamento/<agendamento_id>', endpoint='confirmar_agendamento', methods=['POST'])
@login_required
def confirmar_agendamento(agendamento_id):
    """Confirmar agendamento"""
    from sqlalchemy import select
    stmt = select(Agendamento).where(Agendamento.id == agendamento_id)
    agendamento = db.session.execute(stmt).scalar_one_or_none()
    
    if not agendamento:
        flash('Agendamento não encontrado!', 'danger')
        return redirect(url_for('agendamentos'))
    
    agendamento.status = 'Confirmado'
    db.session.commit()
    flash('Agendamento confirmado com sucesso!', 'success')
    return redirect(url_for('agendamentos'))

@app.route('/cancelar-agendamento/<agendamento_id>', endpoint='cancelar_agendamento', methods=['POST'])
@login_required
def cancelar_agendamento(agendamento_id):
    """Cancelar agendamento"""
    from sqlalchemy import select
    stmt = select(Agendamento).where(Agendamento.id == agendamento_id)
    agendamento = db.session.execute(stmt).scalar_one_or_none()
    
    if not agendamento:
        flash('Agendamento não encontrado!', 'danger')
        return redirect(url_for('agendamentos'))
    
    # Verificar permissão
    if current_user.id != agendamento.usuario_id and current_user.role != 'admin':
        flash('Você não tem permissão para cancelar este agendamento!', 'danger')
        return redirect(url_for('agendamentos'))
    
    agendamento.status = 'Cancelado'
    agendamento.motivo_cancelamento = request.form.get('motivo_cancelamento', '')
    db.session.commit()
    flash('Agendamento cancelado com sucesso!', 'success')
    return redirect(url_for('agendamentos'))

@app.route('/usuario/novo', endpoint='novo_usuario', methods=['GET', 'POST'])
@login_required
def novo_usuario():
    """Adicionar novo usuário"""
    if request.method == 'POST':
        email = request.form.get('email')
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')
        role = request.form.get('role', 'motorista')
        
        # Validar inputs
        if not email or not nome or not senha:
            flash('Preencha todos os campos obrigatórios!', 'danger')
            return render_template('novo_usuario.html')
        
        # Verificar se email já existe
        from sqlalchemy import select
        stmt = select(Usuario).where(Usuario.email == email)
        usuario_existe = db.session.execute(stmt).scalar_one_or_none()
        
        if usuario_existe:
            flash('Email já cadastrado!', 'danger')
            return render_template('novo_usuario.html')
        
        # Criar novo usuário
        import uuid
        novo_user = Usuario(
            id=str(uuid.uuid4())[:8].upper(),
            email=email,
            nome=nome,
            telefone=telefone,
            role=role.lower() if role else 'motorista',
            ativo=True
        )
        novo_user.set_senha(senha)
        
        db.session.add(novo_user)
        db.session.commit()
        
        flash(f'Usuário {nome} criado com sucesso!', 'success')
        return redirect(url_for('gerenciar'))
    
    return render_template('novo_usuario.html')

@app.route('/motorista/novo', endpoint='novo_motorista', methods=['GET', 'POST'])
@login_required
def novo_motorista():
    """Adicionar novo motorista"""
    if request.method == 'POST':
        email = request.form.get('email')
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')
        
        # Validar inputs
        if not email or not nome or not senha:
            flash('Preencha todos os campos obrigatórios!', 'danger')
            return render_template('novo_motorista.html')
        
        # Verificar se email já existe
        from sqlalchemy import select
        stmt = select(Usuario).where(Usuario.email == email)
        usuario_existe = db.session.execute(stmt).scalar_one_or_none()
        
        if usuario_existe:
            flash('Email já cadastrado!', 'danger')
            return render_template('novo_motorista.html')
        
        # Criar novo motorista
        import uuid
        novo_mot = Usuario(
            id=str(uuid.uuid4())[:8].upper(),
            email=email,
            nome=nome,
            telefone=telefone,
            role='motorista',
            ativo=True
        )
        novo_mot.set_senha(senha)
        
        db.session.add(novo_mot)
        db.session.commit()
        
        flash(f'Motorista {nome} criado com sucesso!', 'success')
        return redirect(url_for('gerenciar'))
    
    return render_template('novo_motorista.html')

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'❌ Erro 500: {str(error)}')
    return render_template('500.html'), 500

# ==================== SHELL CONTEXT ====================

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Usuario': Usuario,
        'Veiculo': Veiculo,
        'Agendamento': Agendamento,
        'Viagem': Viagem,
    }

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
