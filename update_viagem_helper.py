# Helper method to update viagem
def update_viagem_chegada(self, placa, km_chegada, observacoes=''):
    """Update trip with arrival information"""
    ws = self._get_worksheet('Viagens')
    if not ws:
        return False
    
    try:
        records = ws.get_all_records()
        for idx, row in enumerate(records, start=2):  # Start at 2 because row 1 is header
            if row.get('Placa') == placa and row.get('Status') == 'Em Andamento':
                # Update the row (columns: Motorista Email, Placa, Data Saída, Data Chegada, KM Saída, KM Chegada, Destino, Observações, Status)
                ws.update_cell(idx, 4, datetime.now(TZ).isoformat())  # Data Chegada
                ws.update_cell(idx, 6, km_chegada)  # KM Chegada
                if observacoes:
                    current_obs = ws.cell(idx, 8).value or ''
                    ws.update_cell(idx, 8, current_obs + ' | ' + observacoes if current_obs else observacoes)
                ws.update_cell(idx, 9, 'Concluída')  # Status
                return True
        return False
    except Exception as e:
        logger.error(f"Erro ao atualizar viagem: {e}")
        return False
