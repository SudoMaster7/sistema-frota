"""
Migrate data from Google Sheets to Supabase
Run this script once to transfer all existing data
"""

import sys
from sheets_db import SheetsDB
from supabase_db import SupabaseDB

def migrate_users(sheets_db, supabase_db):
    """Migrate users from Sheets to Supabase"""
    print("Migrating users...")
    users = sheets_db.get_users()
    
    for user in users:
        user_data = {
            'email': user.get('Email'),
            'senha': user.get('Senha'),
            'nome': user.get('Nome'),
            'role': user.get('Role', 'user'),
            'telefone': user.get('Telefone', '')
        }
        
        if user_data['email'] and user_data['senha'] and user_data['nome']:
            try:
                supabase_db.create_user(user_data)
                print(f"  ✓ Migrated user: {user_data['nome']}")
            except Exception as e:
                print(f"  ✗ Error migrating user {user_data['email']}: {e}")
    
    print(f"Users migration complete!\n")

def migrate_veiculos(sheets_db, supabase_db):
    """Migrate vehicles from Sheets to Supabase"""
    print("Migrating vehicles...")
    veiculos = sheets_db.get_veiculos()
    
    for veiculo in veiculos:
        veiculo_data = {
            'placa': veiculo.get('Placa'),
            'marca': veiculo.get('Marca'),
            'modelo': veiculo.get('Modelo'),
            'ano': veiculo.get('Ano'),
            'cor': veiculo.get('Cor'),
            'km_atual': veiculo.get('KM Atual', 0),
            'status': veiculo.get('Status', 'Disponível')
        }
        
        if veiculo_data['placa'] and veiculo_data['marca'] and veiculo_data['modelo']:
            try:
                response = supabase_db.client.table('veiculos').insert(veiculo_data).execute()
                print(f"  ✓ Migrated vehicle: {veiculo_data['placa']} - {veiculo_data['modelo']}")
            except Exception as e:
                print(f"  ✗ Error migrating vehicle {veiculo_data['placa']}: {e}")
    
    print(f"Vehicles migration complete!\n")

def migrate_agendamentos(sheets_db, supabase_db):
    """Migrate agendamentos from Sheets to Supabase"""
    print("Migrating agendamentos...")
    agendamentos = sheets_db.get_agendamentos()
    
    for agend in agendamentos:
        agend_data = {
            'usuario_email': agend.get('Usuario Email'),
            'placa': agend.get('Placa'),
            'data_solicitada': agend.get('Data Solicitada'),
            'hora_inicio': agend.get('Hora Inicio'),
            'hora_fim': agend.get('Hora Fim'),
            'passageiros': agend.get('Passageiros'),
            'destinos': agend.get('Destinos'),
            'observacoes': agend.get('Observações'),
            'status': agend.get('Status', 'Agendado'),
            'motivo_cancelamento': agend.get('Motivo Cancelamento')
        }
        
        if agend_data['placa'] and agend_data['data_solicitada']:
            try:
                response = supabase_db.client.table('agendamentos').insert(agend_data).execute()
                print(f"  ✓ Migrated agendamento: {agend_data['placa']} - {agend_data['data_solicitada']}")
            except Exception as e:
                print(f"  ✗ Error migrating agendamento: {e}")
    
    print(f"Agendamentos migration complete!\n")

def migrate_viagens(sheets_db, supabase_db):
    """Migrate viagens from Sheets to Supabase"""
    print("Migrating viagens...")
    viagens = sheets_db.get_viagens()
    
    for viagem in viagens:
        viagem_data = {
            'motorista_email': viagem.get('Motorista Email'),
            'placa': viagem.get('Placa'),
            'data_saida': viagem.get('Data Saida'),
            'data_chegada': viagem.get('Data Chegada'),
            'km_saida': viagem.get('KM Saida'),
            'km_chegada': viagem.get('KM Chegada'),
            'destino': viagem.get('Destino'),
            'observacoes': viagem.get('Observações'),
            'status': viagem.get('Status', 'Em Andamento')
        }
        
        if viagem_data['motorista_email'] and viagem_data['placa'] and viagem_data['data_saida']:
            try:
                response = supabase_db.client.table('viagens').insert(viagem_data).execute()
                print(f"  ✓ Migrated viagem: {viagem_data['placa']} - {viagem_data['status']}")
            except Exception as e:
                print(f"  ✗ Error migrating viagem: {e}")
    
    print(f"Viagens migration complete!\n")

def main():
    print("="*60)
    print("  MIGRAÇÃO GOOGLE SHEETS → SUPABASE")
    print("="*60)
    print()
    
    try:
        # Initialize databases
        print("Connecting to databases...")
        sheets_db = SheetsDB()
        supabase_db = SupabaseDB()
        print("✓ Connected successfully!\n")
        
        # Run migrations
        migrate_users(sheets_db, supabase_db)
        migrate_veiculos(sheets_db, supabase_db)
        migrate_agendamentos(sheets_db, supabase_db)
        migrate_viagens(sheets_db, supabase_db)
        
        print("="*60)
        print("  MIGRATION COMPLETE!")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Verify data in Supabase dashboard")
        print("2. Update app_sheets.py to use supabase_db")
        print("3. Test the application")
        print()
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    response = input("This will migrate all data from Google Sheets to Supabase. Continue? (yes/no): ")
    if response.lower() == 'yes':
        main()
    else:
        print("Migration cancelled.")
