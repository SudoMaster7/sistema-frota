"""
⚙️ Configuração de ambiente - Database, Cache, Logging

Gerencia todas as configurações da aplicação
"""

import os
from datetime import timedelta

class Config:
    """Configurações padrão"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Mostrar SQL gerado no console
    
    # Banco de dados - PostgreSQL em produção
    # IMPORTANTE: Configure a variável de ambiente DATABASE_URL antes de rodar em produção
    # Exemplo: postgresql://usuario:senha@localhost:5432/frota_globo
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/frota_globo'
    )
    
    # Flask-Login
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # True em HTTPS produção
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Cache - Redis
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
    CACHE_REDIS_URL = os.environ.get(
        'REDIS_URL',
        'redis://localhost:6379/0'
    )
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos padrão
    CACHE_KEY_PREFIX = 'frota_globo:'
    
    # Email - SMTP
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@frotaglobo.com')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get(
        'RATELIMIT_STORAGE_URL',
        'redis://localhost:6379/1'
    )
    
    # Google Sheets (se ainda usar para dados legados)
    GOOGLE_SHEETS_ID = os.environ.get(
        'GOOGLE_SHEETS_ID',
        '1ZjTYIRF_n91JSCI1OytRYaRFiGkZX2JgoqB0eRIwu8I'
    )


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostrar SQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///frota_globo_dev.db'  # SQLite para desenvolvimento local
    )
    SESSION_COOKIE_SECURE = False
    CACHE_TYPE = 'simple'  # Cache em memória para dev


class TestingConfig(Config):
    """Configurações de testes"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco em memória para testes
    WTF_CSRF_ENABLED = False  # Desabilitar CSRF em testes
    CACHE_TYPE = 'simple'


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    TESTING = False
    
    # Segurança em produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Usar PostgreSQL em produção (obrigatório)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError(
            "⚠️ ERRO: Configure a variável de ambiente DATABASE_URL em produção!\n"
            "Exemplo: postgresql://user:password@host:5432/frota_globo"
        )
    
    # Cache Redis em produção
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    if not CACHE_REDIS_URL:
        raise ValueError(
            "⚠️ ERRO: Configure a variável de ambiente REDIS_URL em produção!"
        )


# Selecionar configuração ativa
def get_config():
    """Retorna a configuração apropriada baseada no ambiente"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return configs.get(env, DevelopmentConfig)


# Configuração ativa
config = get_config()

print(f"""
╔════════════════════════════════════════════════════════════╗
║          ⚙️  CONFIGURAÇÃO CARREGADA                         ║
╠════════════════════════════════════════════════════════════╣
║  Ambiente: {os.environ.get('FLASK_ENV', 'development'):^47}║
║  Debug: {str(config.DEBUG):^52}║
║  Database: {config.SQLALCHEMY_DATABASE_URI[:45]:^45}║
║  Cache: {config.CACHE_TYPE:^51}║
╚════════════════════════════════════════════════════════════╝
""")
