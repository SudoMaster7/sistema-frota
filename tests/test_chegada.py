#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para registrar chegada com KM correto"""

from app import app, db
from models import Viagem
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

with app.app_context():
    viagem = db.session.query(Viagem).filter(Viagem.data_chegada == None).first()
    
    if viagem:
        print(f"Registrando chegada para viagem {viagem.id}")
        print(f"  KM saida: {viagem.km_saida}")
        
        # Registrar chegada com KM correto
        viagem.data_chegada = datetime.now(timezone.utc).astimezone(ZoneInfo('America/Sao_Paulo'))
        viagem.km_chegada = 55050.0  # 50 km rodados
        viagem.status = 'Finalizada'
        
        db.session.commit()
        
        print(f"  KM chegada: {viagem.km_chegada}")
        print(f"  KM rodados: {viagem.km_chegada - viagem.km_saida}")
        print("Chegada registrada com sucesso!")
    else:
        print("Nenhuma viagem em andamento encontrada")
