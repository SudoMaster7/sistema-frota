from app import db, app
from models import Usuario, Veiculo, Agendamento, Viagem, Manutencao, Abastecimento, Auditoria

print(f"DB object: {db}")
print(f"DB metadata tables: {db.metadata.tables.keys()}")

app.app_context().push()
print("Creating all tables...")
db.create_all()

from sqlalchemy import text
result = db.session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
tables = [r[0] for r in result]
print(f"Tables in database: {tables}")
