-- Frota Globo - Supabase Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  nome VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  telefone VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: veiculos
CREATE TABLE IF NOT EXISTS veiculos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  placa VARCHAR(20) UNIQUE NOT NULL,
  marca VARCHAR(100) NOT NULL,
  modelo VARCHAR(100) NOT NULL,
  ano INTEGER,
  cor VARCHAR(50),
  km_atual INTEGER DEFAULT 0,
  status VARCHAR(50) DEFAULT 'Disponível',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  usuario_email VARCHAR(255),
  placa VARCHAR(20) NOT NULL,
  data_agendamento TIMESTAMP DEFAULT NOW(),
  data_solicitada DATE NOT NULL,
  hora_inicio TIME,
  hora_fim TIME,
  passageiros VARCHAR(255),
  destinos TEXT,
  observacoes TEXT,
  status VARCHAR(50) DEFAULT 'Agendado',
  motivo_cancelamento TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: viagens
CREATE TABLE IF NOT EXISTS viagens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  motorista_email VARCHAR(255) NOT NULL,
  placa VARCHAR(20) NOT NULL,
  data_saida TIMESTAMP NOT NULL,
  data_chegada TIMESTAMP,
  km_saida INTEGER NOT NULL,
  km_chegada INTEGER,
  destino TEXT,
  observacoes TEXT,
  status VARCHAR(50) DEFAULT 'Em Andamento',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_veiculos_placa ON veiculos(placa);
CREATE INDEX IF NOT EXISTS idx_veiculos_status ON veiculos(status);
CREATE INDEX IF NOT EXISTS idx_agendamentos_placa ON agendamentos(placa);
CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(status);
CREATE INDEX IF NOT EXISTS idx_viagens_placa ON viagens(placa);
CREATE INDEX IF NOT EXISTS idx_viagens_status ON viagens(status);

-- Enable Row Level Security (RLS)
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE veiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE agendamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE viagens ENABLE ROW LEVEL SECURITY;

-- Policies (permitir todas operações para service_role/anon)
CREATE POLICY "Enable all for authenticated users" ON usuarios FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON veiculos FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON agendamentos FOR ALL USING (true);
CREATE POLICY "Enable all for authenticated users" ON viagens FOR ALL USING (true);
