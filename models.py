"""
📦 Modelos do banco de dados - SQLAlchemy ORM

Este arquivo define todos os modelos do sistema Frota Globo
Migrado de Google Sheets para PostgreSQL
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from zoneinfo import ZoneInfo

# Criar instâncias globais que serão inicializadas em app.py
db = SQLAlchemy()
bcrypt = Bcrypt()

# Timezone padrão
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo('America/Sao_Paulo')
except Exception:
    # Fallback para UTC se tzdata não está disponível
    from datetime import timezone, timedelta
    TZ = timezone(timedelta(hours=-3))  # UTC-3 (São Paulo)

class Usuario(UserMixin, db.Model):
    """Modelo de usuário do sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.String(50), primary_key=True)
    nome = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='motorista')  # 'admin' ou 'motorista'
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(TZ))
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='usuario_agendador', lazy=True)
    viagens = db.relationship('Viagem', backref='motorista', lazy=True)
    logs_auditoria = db.relationship('Auditoria', backref='usuario_acao', lazy=True)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return bcrypt.check_password_hash(self.password_hash, senha)
    
    def set_senha(self, senha):
        """Define a senha com hash"""
        self.password_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
    
    def __repr__(self):
        return f'<Usuario {self.id}>'


class Veiculo(db.Model):
    """Modelo de veículo"""
    __tablename__ = 'veiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False, index=True)
    marca = db.Column(db.String(50), nullable=True)
    modelo = db.Column(db.String(50), nullable=True)
    ano = db.Column(db.Integer, nullable=True)
    cor = db.Column(db.String(30), nullable=True)
    tipo_combustivel = db.Column(db.String(20), nullable=True, default='Gasolina')  # Gasolina, Diesel, Etanol
    km_atual = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Disponível')  # Disponível, Em Uso, Manutenção
    
    # Manutenção
    km_proxima_revisao = db.Column(db.Float, nullable=True)
    data_proxima_revisao = db.Column(db.Date, nullable=True)
    
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(TZ))
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(TZ), onupdate=lambda: datetime.now(TZ))
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='veiculo', lazy=True)
    viagens = db.relationship('Viagem', backref='veiculo', lazy=True)
    manutencoes = db.relationship('Manutencao', backref='veiculo', lazy=True)
    abastecimentos = db.relationship('Abastecimento', backref='veiculo', lazy=True)
    
    def __repr__(self):
        return f'<Veiculo {self.placa}>'


class Agendamento(db.Model):
    """Modelo de agendamento de veículo"""
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    data_agendamento = db.Column(db.DateTime, default=lambda: datetime.now(TZ))
    usuario_id = db.Column(db.String(50), db.ForeignKey('usuarios.id'), nullable=False)
    placa = db.Column(db.String(10), db.ForeignKey('veiculos.placa'), nullable=False)
    data_solicitada = db.Column(db.Date, nullable=False, index=True)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    destinos = db.Column(db.Text, nullable=True)
    passageiros = db.Column(db.Integer, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    producao_evento = db.Column(db.String(100), nullable=True)  # Novo campo
    
    status = db.Column(db.String(20), default='Agendado')  # Agendado, Aprovado, Cancelado
    motivo_cancelamento = db.Column(db.Text, nullable=True)
    data_cancelamento = db.Column(db.DateTime, nullable=True)
    observacoes_admin = db.Column(db.Text, nullable=True)
    
    ultima_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(TZ), onupdate=lambda: datetime.now(TZ))
    
    # Relacionamento com viagem
    viagem = db.relationship('Viagem', backref='agendamento', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - {self.placa}>'


class Viagem(db.Model):
    """Modelo de viagem realizada"""
    __tablename__ = 'viagens'
    
    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=True)
    motorista_id = db.Column(db.String(50), db.ForeignKey('usuarios.id'), nullable=False)
    placa = db.Column(db.String(10), db.ForeignKey('veiculos.placa'), nullable=False)
    
    data_saida = db.Column(db.DateTime, nullable=False, index=True)
    data_chegada = db.Column(db.DateTime, nullable=True)
    
    km_saida = db.Column(db.Float, nullable=False)
    km_chegada = db.Column(db.Float, nullable=True)
    
    destino = db.Column(db.String(200), nullable=True)
    motivo = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    producao_evento = db.Column(db.String(100), nullable=True)
    
    status = db.Column(db.String(20), default='Em Andamento')  # Em Andamento, Finalizada
    
    # Campos calculados
    def get_km_rodados(self):
        """Calcula KM rodados"""
        if self.km_chegada:
            return self.km_chegada - self.km_saida
        return None
    
    def get_duracao(self):
        """Calcula duração da viagem"""
        if self.data_chegada:
            delta = self.data_chegada - self.data_saida
            return delta.total_seconds() / 3600  # em horas
        return None
    
    def __repr__(self):
        return f'<Viagem {self.id} - {self.placa}>'


class Manutencao(db.Model):
    """Modelo de manutenção de veículo"""
    __tablename__ = 'manutencoes'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), db.ForeignKey('veiculos.placa'), nullable=False)
    
    data_manutencao = db.Column(db.Date, nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)  # Preventiva, Corretiva
    descricao = db.Column(db.Text, nullable=False)
    
    pecas = db.Column(db.Text, nullable=True)  # Peças trocadas
    custo = db.Column(db.Float, nullable=True)
    oficina = db.Column(db.String(100), nullable=True)
    
    km_manutencao = db.Column(db.Float, nullable=True)
    proxima_revisao_km = db.Column(db.Float, nullable=True)
    proxima_revisao_data = db.Column(db.Date, nullable=True)
    
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(TZ))
    
    def __repr__(self):
        return f'<Manutencao {self.id} - {self.placa}>'


class Abastecimento(db.Model):
    """Modelo de abastecimento de combustível"""
    __tablename__ = 'abastecimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), db.ForeignKey('veiculos.placa'), nullable=False)
    
    data_abastecimento = db.Column(db.DateTime, nullable=False, index=True)
    litros = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    valor_litro = db.Column(db.Float, nullable=True)
    
    km_atual = db.Column(db.Float, nullable=False)
    tipo_combustivel = db.Column(db.String(20), nullable=True)
    posto = db.Column(db.String(100), nullable=True)
    
    # Campo calculado para consumo
    def get_consumo_km_litro(self):
        """Calcula consumo em km/l desde último abastecimento"""
        abastecimentos_anteriores = Abastecimento.query.filter(
            Abastecimento.placa == self.placa,
            Abastecimento.id < self.id
        ).order_by(Abastecimento.id.desc()).first()
        
        if abastecimentos_anteriores:
            km_rodados = self.km_atual - abastecimentos_anteriores.km_atual
            return km_rodados / self.litros if self.litros > 0 else None
        return None
    
    def __repr__(self):
        return f'<Abastecimento {self.id} - {self.placa}>'


class Auditoria(db.Model):
    """Modelo de log de auditoria - rastreia todas as ações"""
    __tablename__ = 'auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(TZ), index=True)
    usuario_id = db.Column(db.String(50), db.ForeignKey('usuarios.id'), nullable=False)
    
    acao = db.Column(db.String(100), nullable=False)  # Login, Criar Agendamento, Editar Veículo, etc
    entidade = db.Column(db.String(50), nullable=False)  # Usuario, Veiculo, Agendamento, Viagem, etc
    entidade_id = db.Column(db.Integer, nullable=True)  # ID da entidade afetada
    
    detalhes = db.Column(db.Text, nullable=True)  # JSON com antes/depois ou detalhes
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Auditoria {self.id} - {self.acao}>'


# Índices para melhor performance
db.Index('idx_agendamento_data', Agendamento.data_solicitada)
db.Index('idx_agendamento_status', Agendamento.status)
db.Index('idx_viagem_data_saida', Viagem.data_saida)
db.Index('idx_veiculo_status', Veiculo.status)
db.Index('idx_auditoria_timestamp', Auditoria.timestamp)
