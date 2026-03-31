"""
Módulo FinaX Pay - FINAX OS
Geração de links de pagamento, QR codes e gestão de faturas
"""

import uuid
import qrcode
import io
import os
from datetime import datetime
from modules.logging_config import logger


class FinaXPay:
    """Gerenciador de pagamentos digitais com links e QR codes"""
    
    def __init__(self, supabase, instituicao_id):
        self.supabase = supabase
        self.instituicao_id = instituicao_id
        self.logger = logger
        self.base_url = "https://finax-os.streamlit.app"
    
    def gerar_pay_link(self, aluno_id, valor, mes=None, ano=None):
        """
        Gera link de pagamento único e QR code
        
        Args:
            aluno_id: ID do aluno
            valor: Valor a pagar
            mes: Mês (opcional)
            ano: Ano (opcional)
        
        Returns:
            Dict com pay_link, qr_code (bytes) e propina_id
        """
        try:
            # Buscar dados do aluno e instituição
            aluno = self.supabase.table('usuarios').select('nome').eq('id', aluno_id).execute()
            instituicao = self.supabase.table('instituicoes').select('iban, iban_nome').eq('id', self.instituicao_id).execute()
            
            if not aluno.data or not instituicao.data:
                self.logger.warning(f"Aluno {aluno_id} ou instituição {self.instituicao_id} não encontrados")
                return None
            
            # Usar data atual se não especificado
            if not mes or not ano:
                hoje = datetime.now()
                mes = mes or hoje.month
                ano = ano or hoje.year
            
            # Gerar link único
            link_id = uuid.uuid4().hex[:8]
            pay_link = f"{self.base_url}/pay?aluno={aluno_id}&valor={valor}&ref={link_id}"
            
            # Gerar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=2
            )
            qr.add_data(pay_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para bytes
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            qr_code_bytes = buf.getvalue()
            
            # Salvar no banco
            propina_id = str(uuid.uuid4())
            
            data_vencimento = datetime(ano, mes, 10).strftime("%Y-%m-%d")
            
            self.supabase.table('propinas').insert({
                "id": propina_id,
                "aluno_id": aluno_id,
                "instituicao_id": self.instituicao_id,
                "mes": mes,
                "ano": ano,
                "valor": valor,
                "data_vencimento": data_vencimento,
                "status": "PENDENTE",
                "pay_link": pay_link,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            self.logger.info(f"Pay link gerado para aluno {aluno_id}: {pay_link}")
            
            return {
                "pay_link": pay_link,
                "qr_code": qr_code_bytes,
                "propina_id": propina_id,
                "aluno_nome": aluno.data[0]['nome'],
                "valor": valor,
                "iban": instituicao.data[0]['iban'],
                "iban_nome": instituicao.data[0]['iban_nome']
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar pay link: {e}")
            return None
    
    def upload_comprovativo(self, propina_id, arquivo_path):
        """
        Faz upload do comprovativo para o Supabase Storage
        
        Args:
            propina_id: ID da propina
            arquivo_path: Caminho do arquivo no servidor
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            propina = self.supabase.table('propinas').select('aluno_id, mes, ano').eq('id', propina_id).execute()
            
            if not propina.data:
                self.logger.warning(f"Propina {propina_id} não encontrada")
                return False
            
            aluno_id = propina.data[0]['aluno_id']
            mes = propina.data[0]['mes']
            ano = propina.data[0]['ano']
            
            # Nome formatado: comprovativo_{instituicao}_{aluno}_{mes}_{ano}.pdf
            nome_arquivo = f"comprovativo_{self.instituicao_id[:8]}_{aluno_id[:8]}_{mes}_{ano}.pdf"
            
            # Atualizar registro
            self.supabase.table('propinas').update({
                "comprovativo_url": nome_arquivo,
                "status": "AGUARDANDO_CONFIRMACAO",
                "data_comprovativo": datetime.now().isoformat()
            }).eq('id', propina_id).execute()
            
            self.logger.info(f"Comprovativo enviado para propina {propina_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no upload de comprovativo: {e}")
            return False
    
    def confirmar_pagamento(self, propina_id):
        """
        Confirma o pagamento da propina
        
        Args:
            propina_id: ID da propina
        
        Returns:
            True se sucesso
        """
        try:
            self.supabase.table('propinas').update({
                "status": "PAGO",
                "data_pagamento": datetime.now().isoformat()
            }).eq('id', propina_id).execute()
            
            # Atualizar status do aluno (sem débito)
            propina = self.supabase.table('propinas').select('aluno_id').eq('id', propina_id).execute()
            if propina.data:
                aluno_id = propina.data[0]['aluno_id']
                
                # Verificar se ainda há débitos pendentes
                debitos = self.supabase.table('propinas').select('id').eq('aluno_id', aluno_id).eq('status', 'PENDENTE').execute()
                
                if not debitos.data:
                    self.supabase.table('usuarios').update({
                        "tem_divida": False
                    }).eq('id', aluno_id).execute()
            
            self.logger.info(f"Pagamento confirmado para propina {propina_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao confirmar pagamento: {e}")
            return False
    
    def listar_propinas_pendentes(self, aluno_id=None):
        """
        Lista propinas pendentes
        
        Args:
            aluno_id: ID do aluno (opcional)
        
        Returns:
            Lista de propinas pendentes
        """
        try:
            query = self.supabase.table('propinas').select('*').eq('instituicao_id', self.instituicao_id).eq('status', 'PENDENTE')
            
            if aluno_id:
                query = query.eq('aluno_id', aluno_id)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error(f"Erro ao listar propinas pendentes: {e}")
            return []
    
    def obter_relatorio_financeiro(self):
        """
        Gera relatório financeiro de pagamentos
        
        Returns:
            Dicionário com estatísticas de pagamentos
        """
        try:
            propinas = self.supabase.table('propinas').select('*').eq('instituicao_id', self.instituicao_id).execute()
            
            if not propinas.data:
                return {
                    "total_propinas": 0,
                    "total_recebido": 0,
                    "total_pendente": 0,
                    "taxa_inadimplencia": 0
                }
            
            total_propinas = len(propinas.data)
            total_recebido = sum(p['valor'] for p in propinas.data if p['status'] == 'PAGO')
            total_pendente = sum(p['valor'] for p in propinas.data if p['status'] == 'PENDENTE')
            taxa_inadimplencia = (total_pendente / (total_recebido + total_pendente) * 100) if (total_recebido + total_pendente) > 0 else 0
            
            self.logger.info(f"Relatório financeiro gerado - Recebido: {total_recebido}, Pendente: {total_pendente}")
            
            return {
                "total_propinas": total_propinas,
                "total_recebido": total_recebido,
                "total_pendente": total_pendente,
                "taxa_inadimplencia": round(taxa_inadimplencia, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório financeiro: {e}")
            return {}


__all__ = ['FinaXPay']
