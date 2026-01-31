import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sheets_db import SheetsDB

# Load environment variables
load_dotenv()

def seed_database():
    print("Connecting to database...")
    db = SheetsDB()
    if not db.spreadsheet:
        print("Failed to connect to spreadsheet.")
        return

    # ================= 1. USUÁRIOS =================
    print("\n[1/5] Checking 'Usuários'...")
    ws_users = db._get_worksheet('Usuários')
    if not ws_users:
        ws_users = db.spreadsheet.add_worksheet(title="Usuários", rows=100, cols=10)
        ws_users.append_row(['Email', 'Nome', 'Cargo', 'Telefone', 'Ativo', 'Senha'])
        print(" -> Created 'Usuários' worksheet.")
    
    # Check if driver exists
    users = ws_users.get_all_records()
    driver_email = "motorista1@frota.globo"
    driver_exists = any(u.get('Email') == driver_email for u in users)
    
    if not driver_exists:
        ws_users.append_row([
            driver_email,
            "João Motorista",
            "motorista",
            "5521999999999",
            "Sim",
            "mot123"
        ])
        print(f" -> Created driver: {driver_email}")
    else:
        print(f" -> Driver {driver_email} already exists.")

    # ================= 2. VEÍCULOS =================
    print("\n[2/5] Checking 'Veículos'...")
    ws_veiculos = db._get_worksheet('Veículos')
    if not ws_veiculos:
        ws_veiculos = db.spreadsheet.add_worksheet(title="Veículos", rows=100, cols=10)
        # Assuming schema: Placa, Marca, Modelo, Ano, Cor, KM Atual, Status, Observações
        ws_veiculos.append_row(['Placa', 'Marca', 'Modelo', 'Ano', 'Cor', 'KM Atual', 'Status', 'Observações'])
        print(" -> Created 'Veículos' worksheet.")

    veiculos_data = [
        ['ABC-1234', 'Toyota', 'Corolla', '2023', 'Branco', 15000, 'Disponível', ''],
        ['XYZ-9876', 'Honda', 'Civic', '2022', 'Preto', 28500, 'Em Uso', ''],
        ['FRO-2024', 'Fiat', 'Ducato', '2024', 'Prata', 5000, 'Manutenção', 'Revisão agendada']
    ]
    
    existing_veiculos = ws_veiculos.get_all_records()
    existing_placas = [v.get('Placa') for v in existing_veiculos]
    
    for v in veiculos_data:
        if v[0] not in existing_placas:
            ws_veiculos.append_row(v)
            print(f" -> Added vehicle: {v[0]}")

    # ================= 3. AGENDAMENTOS =================
    print("\n[3/5] Checking 'Agendamentos'...")
    ws_agendamentos = db._get_worksheet('Agendamentos')
    if not ws_agendamentos:
        ws_agendamentos = db.spreadsheet.add_worksheet(title="Agendamentos", rows=100, cols=15)
        # Header based on sheets_db.py create_agendamento
        ws_agendamentos.append_row([
            'Usuario Email', 'Placa', 'Data Solicitada', 'Hora Início', 'Hora Fim', 
            'Destinos', 'Passageiros', 'Observações', 'Produção', 'Status', 'Data Criação'
        ])
        print(" -> Created 'Agendamentos' worksheet.")

    # Add a sample schedule if empty
    if len(ws_agendamentos.get_all_values()) <= 1:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        ws_agendamentos.append_row([
            'admin@frota.globo', 'ABC-1234', tomorrow, '08:00', '12:00',
            'Centro de Convenções', 'Diretoria', 'Reunião Externa', 'Sim', 'Agendado',
            datetime.now().isoformat()
        ])
        print(" -> Added sample schedule.")

    # ================= 4. VIAGENS =================
    print("\n[4/5] Checking 'Viagens'...")
    ws_viagens = db._get_worksheet('Viagens')
    if not ws_viagens:
        ws_viagens = db.spreadsheet.add_worksheet(title="Viagens", rows=100, cols=15)
        # Header based on sheets_db.py create_viagem
        ws_viagens.append_row([
            'Motorista Email', 'Placa', 'Data Saída', 'Data Chegada', 
            'KM Saída', 'KM Chegada', 'Destino', 'Observações', 'Status'
        ])
        print(" -> Created 'Viagens' worksheet.")

    # Add an active trip for 'XYZ-9876' (which is 'Em Uso')
    # Check if there is already an active trip
    viagens = ws_viagens.get_all_records()
    active_trip = any(v.get('Status') == 'Em Andamento' for v in viagens)
    
    if not active_trip:
        ws_viagens.append_row([
            driver_email, 'XYZ-9876', datetime.now().isoformat(), '',
            28000, '', 'Aeroporto Galeão', 'Transfer equipe', 'Em Andamento'
        ])
        print(" -> Added active trip for XYZ-9876.")

    # ================= 5. LEADS =================
    print("\n[5/5] Checking 'Leads'...")
    ws_leads = db._get_worksheet('Leads')
    if not ws_leads:
        ws_leads = db.spreadsheet.add_worksheet(title="Leads", rows=100, cols=10)
        ws_leads.append_row(['Data Criação', 'Nome', 'Email', 'Telefone', 'Empresa', 'Senha', 'Status'])
        print(" -> Created 'Leads' worksheet.")
        
    print("\nDatabase seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
