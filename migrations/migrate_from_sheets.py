#!/usr/bin/env python3
"""
Script de Migração: Google Sheets → PostgreSQL
Frota Globo - Sprint 1
"""
import os
import sys
import gspread
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar contexto do Flask
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db
from models import Usuario, Veiculo, Agendamento, Viagem, Auditoria

TZ = ZoneInfo('America/Sao_Paulo')

class MigracaoGoogleSheets:
    def __init__(self):
        self.gc = None
        self.spreadsheet = None
        self.stats = {
            'usuarios_criados': 0,
            'usuarios_erro': 0,
            'veiculos_criados': 0,
            'veiculos_erro': 0,
            'agendamentos_criados': 0,
            'agendamentos_erro': 0,
            'viagens_criadas': 0,
            'viagens_erro': 0,
        }
    
    def conectar_sheets(self):
        """Conectar ao Google Sheets"""
        try:
            logger.info('🔐 Conectando ao Google Sheets...')
            
            # Verificar se arquivo de credenciais existe
            if not os.path.exists('credentials.json'):
                logger.error('❌ Arquivo credentials.json não encontrado!')
                logger.error('📖 Consulte CONFIGURAR_CREDENCIAIS.md para setup')
                raise FileNotFoundError('credentials.json')
            
            self.gc = gspread.service_account(filename='credentials.json')
            
            # Obter ID da planilha a partir de .env
            spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
            if not spreadsheet_id:
                logger.error('❌ GOOGLE_SHEETS_ID não configurado em .env')
                raise ValueError('GOOGLE_SHEETS_ID')
            
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            logger.info('✅ Conectado ao Google Sheets')
            return True
        except Exception as e:
            logger.error(f'❌ Erro ao conectar: {str(e)}')
            return False
    
    def migrar_usuarios(self):
        """Migrar Usuários"""
        try:
            logger.info('\n📝 Migrando Usuários...')
            
            worksheet = self.spreadsheet.worksheet('Usuários')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, 1):
                try:
                    # Verificar se já existe
                    if Usuario.query.filter_by(email=record['Email']).first():
                        logger.warning(f"⏭️  Usuário {record['Email']} já existe, pulando...")
                        continue
                    
                    usuario = Usuario(
                        email=record['Email'],
                        nome=record.get('Nome', 'Sem Nome'),
                        role=record.get('Cargo', 'Motorista'),
                        telefone=record.get('Telefone', ''),
                        ativo=record.get('Ativo', 'Sim').lower() in ['sim', 'true', '1']
                    )
                    
                    # Definir senha padrão (123456)
                    usuario.set_senha('123456')
                    
                    db.session.add(usuario)
                    self.stats['usuarios_criados'] += 1
                    logger.info(f"  ✅ {i}. {usuario.email} ({usuario.role})")
                
                except Exception as e:
                    logger.error(f"  ❌ Erro na linha {i}: {str(e)}")
                    self.stats['usuarios_erro'] += 1
            
            db.session.commit()
            logger.info(f"✅ Usuários: {self.stats['usuarios_criados']} criados, {self.stats['usuarios_erro']} erros")
        
        except Exception as e:
            logger.error(f'❌ Erro migrando usuários: {str(e)}')
    
    def migrar_veiculos(self):
        """Migrar Veículos"""
        try:
            logger.info('\n🚗 Migrando Veículos...')
            
            worksheet = self.spreadsheet.worksheet('Veículos')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, 1):
                try:
                    # Verificar se já existe
                    if Veiculo.query.filter_by(placa=record['Placa']).first():
                        logger.warning(f"⏭️  Veículo {record['Placa']} já existe, pulando...")
                        continue
                    
                    veiculo = Veiculo(
                        placa=record['Placa'],
                        marca=record.get('Marca', 'N/A'),
                        modelo=record.get('Modelo', 'N/A'),
                        ano=int(record.get('Ano', 2020)),
                        cor=record.get('Cor', 'N/A'),
                        tipo_combustivel=record.get('Combustível', 'Diesel'),
                        km_atual=float(record.get('KM Atual', 0)),
                        status=record.get('Status', 'Disponível')
                    )
                    
                    db.session.add(veiculo)
                    self.stats['veiculos_criados'] += 1
                    logger.info(f"  ✅ {i}. {veiculo.placa} - {veiculo.marca} {veiculo.modelo}")
                
                except Exception as e:
                    logger.error(f"  ❌ Erro na linha {i}: {str(e)}")
                    self.stats['veiculos_erro'] += 1
            
            db.session.commit()
            logger.info(f"✅ Veículos: {self.stats['veiculos_criados']} criados, {self.stats['veiculos_erro']} erros")
        
        except Exception as e:
            logger.error(f'❌ Erro migrando veículos: {str(e)}')
    
    def migrar_agendamentos(self):
        """Migrar Agendamentos"""
        try:
            logger.info('\n📅 Migrando Agendamentos...')
            
            worksheet = self.spreadsheet.worksheet('Agendamentos')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, 1):
                try:
                    # Buscar usuário
                    usuario = Usuario.query.filter_by(email=record.get('Email Solicitante', '')).first()
                    if not usuario:
                        logger.warning(f"  ⏭️  Usuário não encontrado, pulando...")
                        continue
                    
                    # Buscar veículo
                    veiculo = Veiculo.query.filter_by(placa=record.get('Placa', '')).first()
                    if not veiculo:
                        logger.warning(f"  ⏭️  Veículo não encontrado, pulando...")
                        continue
                    
                    agendamento = Agendamento(
                        usuario_id=usuario.id,
                        placa=veiculo.placa,
                        data_agendamento=datetime.now(TZ),
                        data_solicitada=datetime.fromisoformat(record.get('Data Solicitada', datetime.now(TZ).isoformat())),
                        hora_inicio=record.get('Hora Início', '08:00'),
                        hora_fim=record.get('Hora Fim', '17:00'),
                        destinos=record.get('Destinos', ''),
                        passageiros=int(record.get('Passageiros', 1)),
                        observacoes=record.get('Observações', ''),
                        producao_evento=record.get('Produção', 'Não').lower() in ['sim', 'yes'],
                        status=record.get('Status', 'Aguardando Aprovação')
                    )
                    
                    db.session.add(agendamento)
                    self.stats['agendamentos_criados'] += 1
                    logger.info(f"  ✅ {i}. Agendamento para {veiculo.placa} em {agendamento.data_solicitada.date()}")
                
                except Exception as e:
                    logger.error(f"  ❌ Erro na linha {i}: {str(e)}")
                    self.stats['agendamentos_erro'] += 1
            
            db.session.commit()
            logger.info(f"✅ Agendamentos: {self.stats['agendamentos_criados']} criados, {self.stats['agendamentos_erro']} erros")
        
        except Exception as e:
            logger.error(f'❌ Erro migrando agendamentos: {str(e)}')
    
    def migrar_viagens(self):
        """Migrar Viagens"""
        try:
            logger.info('\n🚕 Migrando Viagens...')
            
            worksheet = self.spreadsheet.worksheet('Viagens')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, 1):
                try:
                    # Buscar agendamento
                    agendamento = Agendamento.query.filter_by(placa=record.get('Placa', '')).first()
                    if not agendamento:
                        logger.warning(f"  ⏭️  Agendamento não encontrado, pulando...")
                        continue
                    
                    # Buscar motorista
                    motorista = Usuario.query.filter_by(email=record.get('Motorista', '')).first()
                    if not motorista:
                        logger.warning(f"  ⏭️  Motorista não encontrado, pulando...")
                        continue
                    
                    viagem = Viagem(
                        agendamento_id=agendamento.id,
                        motorista_id=motorista.id,
                        placa=agendamento.placa,
                        data_saida=datetime.fromisoformat(record.get('Data Saída', datetime.now(TZ).isoformat())),
                        data_chegada=datetime.fromisoformat(record.get('Data Chegada', datetime.now(TZ).isoformat())),
                        km_saida=float(record.get('KM Saída', 0)),
                        km_chegada=float(record.get('KM Chegada', 0)),
                        status=record.get('Status', 'Finalizada')
                    )
                    
                    db.session.add(viagem)
                    self.stats['viagens_criadas'] += 1
                    logger.info(f"  ✅ {i}. Viagem {viagem.placa} ({viagem.get_km_rodados()} km)")
                
                except Exception as e:
                    logger.error(f"  ❌ Erro na linha {i}: {str(e)}")
                    self.stats['viagens_erro'] += 1
            
            db.session.commit()
            logger.info(f"✅ Viagens: {self.stats['viagens_criadas']} criadas, {self.stats['viagens_erro']} erros")
        
        except Exception as e:
            logger.error(f'❌ Erro migrando viagens: {str(e)}')
    
    def executar(self):
        """Executar migração completa"""
        logger.info('='*50)
        logger.info('🔄 MIGRAÇÃO GOOGLE SHEETS → POSTGRESQL')
        logger.info('='*50)
        
        # Conectar ao Google Sheets
        if not self.conectar_sheets():
            return False
        
        # Executar migrações
        with app.app_context():
            self.migrar_usuarios()
            self.migrar_veiculos()
            self.migrar_agendamentos()
            self.migrar_viagens()
        
        # Resumo
        logger.info('\n' + '='*50)
        logger.info('📊 RESUMO DA MIGRAÇÃO')
        logger.info('='*50)
        total_sucesso = sum([
            self.stats['usuarios_criados'],
            self.stats['veiculos_criados'],
            self.stats['agendamentos_criados'],
            self.stats['viagens_criadas']
        ])
        total_erro = sum([
            self.stats['usuarios_erro'],
            self.stats['veiculos_erro'],
            self.stats['agendamentos_erro'],
            self.stats['viagens_erro']
        ])
        
        for chave, valor in self.stats.items():
            logger.info(f'  {chave}: {valor}')
        
        logger.info(f'\n✅ TOTAL MIGRADO: {total_sucesso} registros')
        logger.info(f'❌ TOTAL COM ERRO: {total_erro} registros')
        logger.info('='*50)
        
        return total_erro == 0


if __name__ == '__main__':
    migracao = MigracaoGoogleSheets()
    sucesso = migracao.executar()
    sys.exit(0 if sucesso else 1)
