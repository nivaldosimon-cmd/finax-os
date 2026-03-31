"""
Módulo RH - FINAX OS
Gestão de recursos humanos e folha de pagamento
"""

import uuid
from datetime import datetime, timedelta
from modules.logging_config import logger


class RHManager:
    """Gerenciador de recursos humanos e folha salarial"""
    
    def __init__(self, supabase, instituicao_id):
        self.supabase = supabase
        self.instituicao_id = instituicao_id
        self.logger = logger
    
    def calcular_folha(self, mes, ano):
        """
        Calcula a folha de pagamento do mês
        
        Args:
            mes: Mês (1-12)
            ano: Ano
        
        Returns:
            Tupla (resultados, total_folha)
        """
        try:
            # Buscar todos os professores e funcionários
            funcionarios = self.supabase.table('usuarios').select('*').eq('instituicao_id', self.instituicao_id).in_('nivel', ['Professor', 'Funcionario']).execute()
            
            if not funcionarios.data:
                self.logger.info(f"Nenhum funcionário encontrado para {mes}/{ano}")
                return [], 0
            
            total_folha = 0
            resultados = []
            
            for f in funcionarios.data:
                salario_base = f.get('salario_base', 0)
                
                if salario_base <= 0:
                    self.logger.warning(f"Funcionário {f['nome']} sem salário base definido")
                    continue
                
                # Cálculos de benefícios e descontos
                subsidio_alimentacao = salario_base * 0.10
                subsidio_transporte = salario_base * 0.05
                horas_extras = f.get('horas_extras', 0) * (salario_base / 160)
                
                # Descontos
                descontos_irt = salario_base * 0.10 if salario_base > 70000 else 0
                descontos_inss = salario_base * 0.03
                
                # Cálculo do salário líquido
                salario_liquido = (
                    salario_base +
                    subsidio_alimentacao +
                    subsidio_transporte +
                    horas_extras -
                    descontos_irt -
                    descontos_inss
                )
                
                total_folha += salario_liquido
                
                resultados.append({
                    "funcionario_id": f['id'],
                    "nome": f['nome'],
                    "nivel": f['nivel'],
                    "salario_base": salario_base,
                    "subsidio_alimentacao": subsidio_alimentacao,
                    "subsidio_transporte": subsidio_transporte,
                    "horas_extras": horas_extras,
                    "descontos_irt": descontos_irt,
                    "descontos_inss": descontos_inss,
                    "salario_liquido": salario_liquido,
                    "status": "PENDENTE"
                })
            
            self.logger.info(f"Folha calculada para {mes}/{ano}: Total {total_folha:.2f} Kz - {len(resultados)} funcionários")
            return resultados, total_folha
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular folha: {e}")
            return [], 0
    
    def pagar_folha(self, mes, ano):
        """
        Processa o pagamento da folha de salário
        
        Args:
            mes: Mês
            ano: Ano
        
        Returns:
            Tupla (sucesso: bool, total_pago: float)
        """
        try:
            resultados, total_folha = self.calcular_folha(mes, ano)
            
            if not resultados:
                self.logger.warning(f"Nenhum funcionário para pagar em {mes}/{ano}")
                return False, 0
            
            # Registrar despesa no fluxo de caixa
            despesa_id = str(uuid.uuid4())
            self.supabase.table('despesas').insert({
                "id": despesa_id,
                "instituicao_id": self.instituicao_id,
                "tipo": "Salário",
                "valor": total_folha,
                "descricao": f"Folha salarial {mes}/{ano}",
                "data_pagamento": datetime.now().strftime("%Y-%m-%d"),
                "status": "PAGO"
            }).execute()
            
            # Registrar cada pagamento na folha salarial
            for r in resultados:
                self.supabase.table('folha_salarial').insert({
                    "id": str(uuid.uuid4()),
                    "funcionario_id": r['funcionario_id'],
                    "instituicao_id": self.instituicao_id,
                    "mes": mes,
                    "ano": ano,
                    "salario_base": r['salario_base'],
                    "subsidio_alimentacao": r['subsidio_alimentacao'],
                    "subsidio_transporte": r['subsidio_transporte'],
                    "horas_extras": r['horas_extras'],
                    "descontos_irt": r['descontos_irt'],
                    "descontos_inss": r['descontos_inss'],
                    "salario_liquido": r['salario_liquido'],
                    "status": "PAGO",
                    "data_pagamento": datetime.now().strftime("%Y-%m-%d")
                }).execute()
            
            self.logger.info(f"Folha de {mes}/{ano} paga com sucesso: {total_folha:.2f} Kz")
            return True, total_folha
            
        except Exception as e:
            self.logger.error(f"Erro ao pagar folha: {e}")
            return False, 0
    
    def alerta_proximo_pagamento(self):
        """
        Verifica se há pagamentos próximos
        
        Returns:
            Dicionário com informações do próximo pagamento
        """
        try:
            hoje = datetime.now()
            dia_pagamento = 25
            
            # Calcular dias até o próximo pagamento
            if hoje.day <= dia_pagamento:
                dias_restantes = dia_pagamento - hoje.day
                data_pagamento = datetime(hoje.year, hoje.month, dia_pagamento)
            else:
                # Próximo mês
                if hoje.month == 12:
                    data_pagamento = datetime(hoje.year + 1, 1, dia_pagamento)
                else:
                    data_pagamento = datetime(hoje.year, hoje.month + 1, dia_pagamento)
                dias_restantes = (data_pagamento - hoje).days
            
            if 0 <= dias_restantes <= 5:
                return {
                    "ativo": True,
                    "dias": dias_restantes,
                    "data": data_pagamento.strftime("%d/%m/%Y"),
                    "tipo": "ALERTA"
                }
            elif dias_restantes > 5:
                return {
                    "ativo": True,
                    "dias": dias_restantes,
                    "data": data_pagamento.strftime("%d/%m/%Y"),
                    "tipo": "INFO"
                }
            
            return {"ativo": False}
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alerta de pagamento: {e}")
            return {"ativo": False}
    
    def obter_historico_folha(self, funcionario_id=None, limite=12):
        """
        Obtém histórico de folhas de pagamento
        
        Args:
            funcionario_id: ID do funcionário (opcional)
            limite: Número de meses a retornar
        
        Returns:
            Lista de registros de folha
        """
        try:
            query = self.supabase.table('folha_salarial').select('*').eq('instituicao_id', self.instituicao_id).order('ano', desc=True).order('mes', desc=True).limit(limite * 5)
            
            result = query.execute()
            dados = result.data if result.data else []
            
            if funcionario_id:
                dados = [d for d in dados if d['funcionario_id'] == funcionario_id]
            
            return dados[:limite]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de folha: {e}")
            return []
    
    def gerar_relatorio_rh(self):
        """
        Gera relatório geral de RH
        
        Returns:
            Dicionário com estatísticas de RH
        """
        try:
            # Total de funcionários
            funcionarios = self.supabase.table('usuarios').select('*').eq('instituicao_id', self.instituicao_id).in_('nivel', ['Professor', 'Funcionario']).execute()
            
            if not funcionarios.data:
                return {
                    "total_funcionarios": 0,
                    "total_professores": 0,
                    "total_outros": 0,
                    "folha_mensal_estimada": 0
                }
            
            total_funcionarios = len(funcionarios.data)
            total_professores = sum(1 for f in funcionarios.data if f['nivel'] == 'Professor')
            total_outros = total_funcionarios - total_professores
            
            # Folha mensal estimada
            folha_estimada = sum(f.get('salario_base', 0) for f in funcionarios.data)
            
            self.logger.info(f"Relatório RH gerado - {total_funcionarios} funcionários")
            
            return {
                "total_funcionarios": total_funcionarios,
                "total_professores": total_professores,
                "total_outros": total_outros,
                "folha_mensal_estimada": folha_estimada,
                "proximo_pagamento": self.alerta_proximo_pagamento()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório RH: {e}")
            return {}
    
    def atualizar_salario(self, funcionario_id, novo_salario):
        """
        Atualiza o salário de um funcionário
        
        Args:
            funcionario_id: ID do funcionário
            novo_salario: Novo salário base
        
        Returns:
            True se sucesso
        """
        try:
            self.supabase.table('usuarios').update({
                "salario_base": novo_salario,
                "updated_at": datetime.now().isoformat()
            }).eq('id', funcionario_id).execute()
            
            self.logger.info(f"Salário atualizado para funcionário {funcionario_id}: {novo_salario:.2f} Kz")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar salário: {e}")
            return False


__all__ = ['RHManager']
