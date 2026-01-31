import gspread
import os
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from zoneinfo import ZoneInfo
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TZ = ZoneInfo('America/Sao_Paulo')

class SheetsDB:
    def __init__(self):
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.creds = None
        self.client = None
        self.spreadsheet = None
        self._connect()

    def _connect(self):
        """Estabelece conexão com o Google Sheets"""
        try:
            # Tenta carregar credenciais do arquivo local first
            if os.path.exists('credentials.json'):
                self.creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', self.scope)
            # Tenta carregar da variável de ambiente (para Vercel/Prod)
            elif os.getenv('GOOGLE_CREDENTIALS_JSON'):
                creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
                self.creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            else:
                logger.error("Credenciais não encontradas (arquivo ou variável de ambiente)")
                return

            self.client = gspread.authorize(self.creds)
            
            # Tenta abrir a planilha pelo ID ou Nome
            sheet_id = os.getenv('GOOGLE_SHEETS_ID')
            logger.info(f"Tentando conectar planilha ID: {sheet_id}")
            
            if sheet_id:
                self.spreadsheet = self.client.open_by_key(sheet_id)
            else:
                # Fallback para nome fixo se ID não estiver no .env (para testes locais rápidos)
                # O ideal é sempre usar o ID
                self.spreadsheet = self.client.open_by_key('1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I')
            
            logger.info("Conexão com Google Sheets estabelecida com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao Google Sheets: {e}")

    def _get_worksheet(self, name):
        if not self.spreadsheet:
            self._connect()
        try:
            return self.spreadsheet.worksheet(name)
        except Exception as e:
            logger.error(f"Erro ao acessar aba {name}: {e}")
            return None

    # ================= USUÁRIOS =================
    def get_users(self):
        ws = self._get_worksheet('Usuários')
        if not ws: return []
        return ws.get_all_records()

    def get_user_by_email(self, email):
        users = self.get_users()
        for user in users:
            if user.get('Email') == email:
                return user
        return None

    def get_user_by_id(self, user_id):
        # Na planilha antiga não tinha ID, usava Email. Vamos adaptar.
        # Se user_id parecer um email, busca por email.
        if '@' in user_id:
            return self.get_user_by_email(user_id)
        # Se não, busca por um campo ID se existir, ou retorna None
        users = self.get_users()
        for user in users:
            if str(user.get('ID', '')) == str(user_id):
                return user
        return None

    def create_user(self, user_data):
        ws = self._get_worksheet('Usuários')
        if not ws: return False
        
        # Mapear campos do objeto Usuario para colunas da planilha
        row = [
            user_data.get('email'),
            user_data.get('nome'),
            user_data.get('role', 'motorista'),
            user_data.get('telefone', ''),
            'Sim' if user_data.get('ativo', True) else 'Não',
            '123456' # Senha padrão, já que planilha não guarda hash seguro idealmente
        ]
        ws.append_row(row)
        return True

    # ================= VEÍCULOS =================
    def get_veiculos(self):
        ws = self._get_worksheet('Veículos')
        if not ws: return []
        return ws.get_all_records()

    def get_veiculo_by_placa(self, placa):
        veiculos = self.get_veiculos()
        for v in veiculos:
            if v.get('Placa') == placa:
                return v
        return None

    def update_veiculo_status(self, placa, novo_status):
        ws = self._get_worksheet('Veículos')
        cell = ws.find(placa)
        if cell:
            # Assumindo que Status é a coluna 8 (H) com base no migrate script
            # Mas é mais seguro buscar o header
            headers = ws.row_values(1)
            try:
                col_idx = headers.index('Status') + 1
                ws.update_cell(cell.row, col_idx, novo_status)
                return True
            except ValueError:
                pass
        return False

    # ================= AGENDAMENTOS =================
    def get_agendamentos(self):
        ws = self._get_worksheet('Agendamentos')
        if not ws: return []
        return ws.get_all_records()

    def create_agendamento(self, data):
        ws = self._get_worksheet('Agendamentos')
        if not ws: return False
        
        row = [
            data.get('usuario_email'),
            data.get('placa'),
            data.get('data_solicitada'), # YYYY-MM-DD
            data.get('hora_inicio'),
            data.get('hora_fim'),
            data.get('destinos'),
            data.get('passageiros'),
            data.get('observacoes'),
            data.get('producao', 'Não'),
            data.get('status', 'Agendado'),
            datetime.now(TZ).isoformat() # Data Criação
        ]
        ws.append_row(row)
        return True
    

    # ================= VIAGENS =================

    # ================= VIAGENS =================
    def get_viagens(self):
        ws = self._get_worksheet('Viagens')
        if not ws: return []
        return ws.get_all_records()

    def create_viagem(self, data):
        ws = self._get_worksheet('Viagens')
        if not ws: return False
        
        row = [
            data.get('motorista_email'),
            data.get('placa'),
            data.get('data_saida'),
            '', # Data Chegada
            data.get('km_saida'),
            '', # KM Chegada
            data.get('destino'),
            data.get('observacoes', ''),
            'Em Andamento'
        ]
        ws.append_row(row)
        
        # Update vehicle status to 'Em Uso'
        placa = data.get('placa')
        if placa:
            self.update_veiculo_status(placa, 'Em Uso')
        
        # Update agendamento status to 'Em Uso' if agendamento_id provided
        agendamento_id = data.get('agendamento_id')
        if agendamento_id:
            self.update_agendamento_status(int(agendamento_id), 'Em Uso')
        
        return True

    def finaliza_viagem(self, placa, km_chegada, observacoes=None):
        ws = self._get_worksheet('Viagens')
        if not ws: return False
        
        # Encontrar a viagem em aberto para este veículo
        # Isso é ineficiente em planilhas grandes, mas ok para testes
        records = ws.get_all_records()
        headers = ws.row_values(1)
        
        status_col = headers.index('Status') + 1
        placa_col = headers.index('Placa') + 1
        data_chegada_col = headers.index('Data Chegada') + 1
        km_chegada_col = headers.index('KM Chegada') + 1
        obs_col = headers.index('Observações') + 1 # Assumindo que existe
        
        for i, viagem in enumerate(records):
            if viagem.get('Placa') == placa and viagem.get('Status') == 'Em Andamento':
                row_num = i + 2 # +2 por causa do header e 0-based index
                
                # Atualizar campos
                ws.update_cell(row_num, status_col, 'Finalizada')
                ws.update_cell(row_num, data_chegada_col, datetime.now(TZ).isoformat())
                ws.update_cell(row_num, km_chegada_col, km_chegada)
                if observacoes:
                     # Nota: Se observações já tiver texto, pode sobrescrever.
                     # Para simplicidade, vamos sobrescrever ou concatenar se possível, mas update_cell sobrescreve.
                     ws.update_cell(row_num, obs_col, observacoes)
                
                # Update vehicle status back to 'Disponível'
                self.update_veiculo_status(placa, 'Disponível')
                
                # Update agendamento status to 'Realizado'
                self.update_agendamento_status_by_placa(placa, 'Realizado')
                
                return True
        return False

    # ================= LEADS =================
    def create_lead(self, data):
        ws = self._get_worksheet('Leads')
        if not ws:
            # Tentar criar a aba se não existir
            try:
                if self.spreadsheet:
                    ws = self.spreadsheet.add_worksheet(title="Leads", rows=1000, cols=10)
                    # Adicionar header
                    ws.append_row(['Data Criação', 'Nome', 'Email', 'Telefone', 'Empresa', 'Senha', 'Status'])
                else:
                    return False
            except Exception as e:
                logger.error(f"Erro ao criar aba Leads: {e}")
                return False
        
        row = [
            datetime.now(TZ).isoformat(),
            data.get('nome'),
            data.get('email'),
            data.get('telefone'),
            data.get('empresa'),
            data.get('password'), # Plain text as requested
            'Pendente'
        ]
        ws.append_row(row)
        return True

    # =================== VEICULO CRUD ===================
    def create_veiculo(self, data):
        """Create a new vehicle"""
        ws = self._get_worksheet('Veículos')
        if not ws:
            return False
        
        row = [
            data.get('placa'),
            data.get('marca'),
            data.get('modelo'),
            data.get('ano'),
            data.get('cor'),
            data.get('km_atual', 0),
            'Disponível',  # Status padrão
            data.get('observacoes', '')
        ]
        ws.append_row(row)
        return True
    
    def update_veiculo(self, placa, data):
        """Update vehicle data"""
        ws = self._get_worksheet('Veículos')
        if not ws:
            return False
        
        try:
            records = ws.get_all_records()
            for idx, row in enumerate(records, start=2):
                if row.get('Placa') == placa:
                    # Update columns: Placa, Marca, Modelo, Ano, Cor, KM Atual, Status, Observações
                    if 'marca' in data: ws.update_cell(idx, 2, data['marca'])
                    if 'modelo' in data: ws.update_cell(idx, 3, data['modelo'])
                    if 'ano' in data: ws.update_cell(idx, 4, data['ano'])
                    if 'cor' in data: ws.update_cell(idx, 5, data['cor'])
                    if 'km_atual' in data: ws.update_cell(idx, 6, data['km_atual'])
                    return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar veículo: {e}")
            return False
    
    # =================== USER CRUD ===================
    def create_user(self, data):
        """Create a new user"""
        ws = self._get_worksheet('Usuários')
        if not ws:
            return False
        
        row = [
            data.get('email'),
            data.get('nome'),
            data.get('cargo', 'usuario'),
            data.get('telefone', ''),
            'Sim',  # Ativo
            data.get('senha', '123456')
        ]
        ws.append_row(row)
        return True
    
    def update_user(self, email, data):
        """Update user data"""
        ws = self._get_worksheet('Usuários')
        if not ws:
            return False
        
        try:
            records = ws.get_all_records()
            for idx, row in enumerate(records, start=2):
                if row.get('Email') == email:
                    # Update columns: Email, Nome, Cargo, Telefone, Ativo, Senha
                    if 'nome' in data: ws.update_cell(idx, 2, data['nome'])
                    if 'telefone' in data: ws.update_cell(idx, 4, data['telefone'])
                    if 'senha' in data: ws.update_cell(idx, 6, data['senha'])
                    return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            return False
    
    def update_agendamento_status(self, row_index, new_status):
        """Update agendamento status by row index (1-indexed from data, not including header)"""
        ws = self._get_worksheet('Agendamentos')
        if not ws:
            return False
        
        try:
            # Row index needs +1 because row 1 is header, so data starts at row 2
            actual_row = row_index + 1
            # Status is column 10 (J) in the Agendamentos sheet
            ws.update_cell(actual_row, 10, new_status)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar status do agendamento: {e}")
            return False
    
    def update_agendamento_status_by_placa(self, placa, new_status):
        """Update agendamento status by finding the most recent agendamento for a given placa"""
        ws = self._get_worksheet('Agendamentos')
        if not ws:
            return False
        
        try:
            records = ws.get_all_records()
            headers = ws.row_values(1)
            status_col = headers.index('Status') + 1
            
            # Find the most recent agendamento for this placa with status 'Em Uso' or 'Confirmado'
            for i in range(len(records) - 1, -1, -1):  # Search from bottom (most recent)
                agend = records[i]
                if agend.get('Placa') == placa and agend.get('Status') in ['Em Uso', 'Confirmado']:
                    row_num = i + 2  # +2 for header and 0-based index
                    ws.update_cell(row_num, status_col, new_status)
                    return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar status do agendamento por placa: {e}")
            return False

