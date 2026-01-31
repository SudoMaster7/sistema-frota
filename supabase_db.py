"""
Supabase Database Layer for Frota Globo
Replaces Google Sheets with PostgreSQL via Supabase
"""

import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Timezone
TZ = ZoneInfo('America/Sao_Paulo')

logger = logging.getLogger(__name__)

class SupabaseDB:
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized successfully")
    
    # ============ USERS ============
    
    def get_users(self):
        """Get all users"""
        try:
            response = self.client.table('usuarios').select('*').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            response = self.client.table('usuarios').select('*').eq('email', email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def create_user(self, user_data):
        """Create a new user"""
        try:
            response = self.client.table('usuarios').insert(user_data).execute()
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    # ============ VEICULOS ============
    
    def get_veiculos(self):
        """Get all vehicles"""
        try:
            response = self.client.table('veiculos').select('*').execute()
            # Convert to dict format for compatibility
            return [dict(v) for v in response.data]
        except Exception as e:
            logger.error(f"Error getting vehicles: {e}")
            return []
    
    def get_veiculo_by_placa(self, placa):
        """Get vehicle by placa"""
        try:
            response = self.client.table('veiculos').select('*').eq('placa', placa).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting vehicle: {e}")
            return None
    
    def update_veiculo_status(self, placa, novo_status):
        """Update vehicle status"""
        try:
            response = self.client.table('veiculos').update({
                'status': novo_status
            }).eq('placa', placa).execute()
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error updating vehicle status: {e}")
            return False
    
    # ============ AGENDAMENTOS ============
    
    def get_agendamentos(self):
        """Get all agendamentos"""
        try:
            response = self.client.table('agendamentos').select('*').order('created_at', desc=True).execute()
            # Convert to dict format for compatibility
            result = []
            for item in response.data:
                # Convert to match Google Sheets format
                formatted = {
                    'Usuario Email': item.get('usuario_email'),
                    'Placa': item.get('placa'),
                    'Data Agendamento': item.get('data_agendamento'),
                    'Data Solicitada': item.get('data_solicitada'),
                    'Hora Inicio': item.get('hora_inicio'),
                    'Hora Fim': item.get('hora_fim'),
                    'Passageiros': item.get('passageiros'),
                    'Destinos': item.get('destinos'),
                    'Observações': item.get('observacoes'),
                    'Status': item.get('status'),
                    'Motivo Cancelamento': item.get('motivo_cancelamento'),
                    '_id': item.get('id')  # Keep UUID for reference
                }
                result.append(formatted)
            return result
        except Exception as e:
            logger.error(f"Error getting agendamentos: {e}")
            return []
    
    def create_agendamento(self, data):
        """Create new agendamento"""
        try:
            agend_data = {
                'usuario_email': data.get('usuario_email'),
                'placa': data.get('placa'),
                'data_solicitada': data.get('data_solicitada'),
                'hora_inicio': data.get('hora_inicio'),
                'hora_fim': data.get('hora_fim'),
                'passageiros': data.get('passageiros'),
                'destinos': data.get('destinos'),
                'observacoes': data.get('observacoes'),
                'status': data.get('status', 'Agendado')
            }
            response = self.client.table('agendamentos').insert(agend_data).execute()
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error creating agendamento: {e}")
            return False
    
    def update_agendamento_status(self, agendamento_id, new_status):
        """Update agendamento status by ID"""
        try:
            # If agendamento_id is numeric (from old system), get by index
            # Otherwise treat as UUID
            if isinstance(agendamento_id, int) or (isinstance(agendamento_id, str) and agendamento_id.isdigit()):
                # Get by position (for backwards compatibility)
                all_agendamentos = self.get_agendamentos()
                idx = int(agendamento_id) - 1  # Convert to 0-based
                if 0 <= idx < len(all_agendamentos):
                    uuid = all_agendamentos[idx].get('_id')
                    if uuid:
                        response = self.client.table('agendamentos').update({
                            'status': new_status
                        }).eq('id', uuid).execute()
                        return True if response.data else False
            else:
                # Direct UUID update
                response = self.client.table('agendamentos').update({
                    'status': new_status
                }).eq('id', agendamento_id).execute()
                return True if response.data else False
            return False
        except Exception as e:
            logger.error(f"Error updating agendamento status: {e}")
            return False
    
    def update_agendamento_status_by_placa(self, placa, new_status):
        """Update most recent agendamento for a placa"""
        try:
            # Find most recent agendamento with this placa and status in ['Em Uso', 'Confirmado']
            response = self.client.table('agendamentos')\
                .select('*')\
                .eq('placa', placa)\
                .in_('status', ['Em Uso', 'Confirmado'])\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                agend_id = response.data[0]['id']
                update_response = self.client.table('agendamentos').update({
                    'status': new_status
                }).eq('id', agend_id).execute()
                return True if update_response.data else False
            return False
        except Exception as e:
            logger.error(f"Error updating agendamento by placa: {e}")
            return False
    
    def cancelar_agendamento(self, agendamento_id, motivo=None):
        """Cancel agendamento"""
        try:
            update_data = {'status': 'Cancelado'}
            if motivo:
                update_data['motivo_cancelamento'] = motivo
            
            # Handle numeric ID (backwards compatibility)
            if isinstance(agendamento_id, int) or (isinstance(agendamento_id, str) and agendamento_id.isdigit()):
                all_agendamentos = self.get_agendamentos()
                idx = int(agendamento_id) - 1
                if 0 <= idx < len(all_agendamentos):
                    uuid = all_agendamentos[idx].get('_id')
                    if uuid:
                        response = self.client.table('agendamentos').update(update_data).eq('id', uuid).execute()
                        return True if response.data else False
            else:
                response = self.client.table('agendamentos').update(update_data).eq('id', agendamento_id).execute()
                return True if response.data else False
            return False
        except Exception as e:
            logger.error(f"Error cancelling agendamento: {e}")
            return False
    
    # ============ VIAGENS ============
    
    def get_viagens(self):
        """Get all trips"""
        try:
            response = self.client.table('viagens').select('*').order('created_at', desc=True).execute()
            # Convert to dict format for compatibility
            result = []
            for item in response.data:
                formatted = {
                    'Motorista Email': item.get('motorista_email'),
                    'Placa': item.get('placa'),
                    'Data Saida': item.get('data_saida'),
                    'Data Chegada': item.get('data_chegada'),
                    'KM Saida': item.get('km_saida'),
                    'KM Chegada': item.get('km_chegada'),
                    'Destino': item.get('destino'),
                    'Observações': item.get('observacoes'),
                    'Status': item.get('status'),
                    '_id': item.get('id')
                }
                result.append(formatted)
            return result
        except Exception as e:
            logger.error(f"Error getting viagens: {e}")
            return []
    
    def create_viagem(self, data):
        """Create new trip"""
        try:
            viagem_data = {
                'motorista_email': data.get('motorista_email'),
                'placa': data.get('placa'),
                'data_saida': data.get('data_saida'),
                'km_saida': data.get('km_saida'),
                'destino': data.get('destino'),
                'observacoes': data.get('observacoes'),
                'status': 'Em Andamento'
            }
            
            response = self.client.table('viagens').insert(viagem_data).execute()
            
            if response.data:
                # Update vehicle status
                placa = data.get('placa')
                if placa:
                    self.update_veiculo_status(placa, 'Em Uso')
                
                # Update agendamento status if provided
                agendamento_id = data.get('agendamento_id')
                if agendamento_id:
                    self.update_agendamento_status(int(agendamento_id), 'Em Uso')
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error creating viagem: {e}")
            return False
    
    def finaliza_viagem(self, placa, km_chegada, observacoes=None):
        """Finalize trip"""
        try:
            # Find active trip for this vehicle
            response = self.client.table('viagens')\
                .select('*')\
                .eq('placa', placa)\
                .eq('status', 'Em Andamento')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                viagem_id = response.data[0]['id']
                
                # Update trip
                update_data = {
                    'status': 'Finalizada',
                    'data_chegada': datetime.now(TZ).isoformat(),
                    'km_chegada': km_chegada
                }
                if observacoes:
                    update_data['observacoes'] = observacoes
                
                update_response = self.client.table('viagens').update(update_data).eq('id', viagem_id).execute()
                
                if update_response.data:
                    # Update vehicle status back to available
                    self.update_veiculo_status(placa, 'Disponível')
                    
                    # Update agendamento status
                    self.update_agendamento_status_by_placa(placa, 'Realizado')
                    
                    return True
            return False
        except Exception as e:
            logger.error(f"Error finalizing viagem: {e}")
            return False
