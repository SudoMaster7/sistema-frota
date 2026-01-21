#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para criar viagem com motorista correto"""

from app import app, db
from models import Viagem, Agendamento, Usuario
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

with app.app_context():
    # Pegar um motorista (não admin)
    motorista = db.session.query(Usuario).filter(Usuario.role == 'motorista').first()
    if not motorista:
        print("Nenhum motorista encontrado")
    else:
        print(f"Usando motorista: {motorista.nome} ({motorista.email})")
        
        # Pegar um agendamento confirmado
        agendamento = db.session.query(Agendamento).filter(Agendamento.status == 'Confirmado').first()
        if not agendamento:
            print("Nenhum agendamento confirmado encontrado")
        else:
            print(f"Usando agendamento: {agendamento.id} - {agendamento.placa}")
            
            # Criar viagem com o motorista correto
            viagem = Viagem(
                agendamento_id=agendamento.id,
                motorista_id=motorista.id,
                placa=agendamento.placa,
                data_saida=datetime.now(timezone.utc).astimezone(ZoneInfo('America/Sao_Paulo')),
                km_saida=55000.0,
                destino=agendamento.destinos,
                observacoes='Test via script',
                status='Em Andamento'
            )
            
            agendamento.status = 'Em Uso'
            db.session.add(viagem)
            db.session.commit()
            
            print(f"Viagem criada com sucesso! ID: {viagem.id}")
            print(f"  Motorista ID: {viagem.motorista_id}")
            print(f"  Motorista Nome: {viagem.motorista.nome}")
