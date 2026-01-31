from dotenv import load_dotenv
from sheets_db import SheetsDB

load_dotenv()
db = SheetsDB()

print("=" * 60)
print("VERIFICANDO DADOS PARA REGISTRAR SAÍDA")
print("=" * 60)

# Verificar agendamentos
agendamentos = db.get_agendamentos()
print(f"\n✅ Total de agendamentos: {len(agendamentos)}")
confirmados = [a for a in agendamentos if a.get('Status') == 'Confirmado']
print(f"✅ Agendamentos confirmados: {len(confirmados)}")
for idx, a in enumerate(confirmados, start=1):
    print(f"   {idx}. Placa: {a.get('Placa')} | Data: {a.get('Data Solicitada')} | Destinos: {a.get('Destinos', 'N/A')[:50]}")

# Verificar motoristas  
usuarios = db.get_users()
motoristas = [u for u in usuarios if u.get('Cargo', '').lower() == 'motorista']
print(f"\n✅ Total de motoristas: {len(motoristas)}")
for m in motoristas:
    print(f"   - {m.get('Nome')} ({m.get('Email')})")

# Verificar admin
admin = db.get_user_by_email('admin@frota.globo')
print(f"\n✅ Admin: {admin.get('Email')} - Cargo: {admin.get('Cargo')}")

if len(confirmados) == 0:
    print("\n⚠️  PROBLEMA: Não há agendamentos confirmados!")
    print("   Solução: Vá para Agendamentos e confirme pelo menos um")
    
if len(motoristas) == 0:
    print("\n⚠️  PROBLEMA: Não há motoristas cadastrados!")
    print("   Solução: Cadastre um motorista em Gerenciar > Novo Motorista")
