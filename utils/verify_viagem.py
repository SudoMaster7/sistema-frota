#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificar dados de viagem"""

from app import app, db
from models import Viagem

with app.app_context():
    viagens = db.session.query(Viagem).all()
    print(f'Total de viagens: {len(viagens)}\n')
    
    for v in viagens:
        print(f'Viagem {v.id}:')
        print(f'  Motorista ID: {v.motorista_id}')
        nome = v.motorista.nome if v.motorista else 'None'
        email = v.motorista.email if v.motorista else 'None'
        print(f'  Motorista Nome: {nome}')
        print(f'  Motorista Email: {email}')
        print()
