"""
Módulo BI - FINAX OS
Business Intelligence com cálculo de KPIs e relatórios analíticos
"""

from datetime import datetime, timedelta
from modules.logging_config import logger


class BIManager:
    """Gerenciador de Business Intelligence e análise de dados"""
    
    def __init__(self, supabase, instituicao_id):
        self.supabase = supabase
        self.instituicao_id = instituicao_id
        self.logger = logger
    
    def calcular_kpis(self):
        """
        Calcula os principais indicadores-chave de desempenho
        
        Returns:
            Dicionário com todos os KPIs calculados
        """
        try:
            # ===== ALUNOS =====
            alunos = self.supabase.table('usuarios').select('*').eq('instituicao_id', self.instituicao_id).eq('nivel', 'Estudante').execute()
            total_alunos = len(alunos.data) if alunos.data else 0
            
            # Alunos devedores
            devedores = sum(1 for a in alunos.data if a.get('tem_divida', False)) if alunos.data else 0
            
            # Taxa de inadimplência
            taxa_inadimplencia = (devedores / total_alunos * 100) if total_alunos > 0 else 0
            
            # ===== FINANCEIRO =====
            receitas = self.supabase.table('receitas').select('valor').eq('instituicao_id', self.instituicao_id).execute()
            despesas = self.supabase.table('despesas').select('valor').eq('instituicao_id', self.instituicao_id).eq('status', 'PAGO').execute()
            
            total_receitas = sum(r['valor'] for r in receitas.data) if receitas.data else 0
            total_despesas = sum(d['valor'] for d in despesas.data) if despesas.data else 0
            saldo_atual = total_receitas - total_despesas
            
            # ===== PROPINAS =====
            propinas = self.supabase.table('propinas').select('valor').eq('instituicao_id', self.instituicao_id).eq('status', 'PENDENTE').execute()
            propinas_pendentes = sum(p['valor'] for p in propinas.data) if propinas.data else 0
            
            propinas_pagas = self.supabase.table('propinas').select('valor').eq('instituicao_id', self.instituicao_id).eq('status', 'PAGO').execute()
            propinas_pagas_total = sum(p['valor'] for p in propinas_pagas.data) if propinas_pagas.data else 0
            
            # ===== FOLHA SALARIAL =====
            folhas = self.supabase.table('folha_salarial').select('salario_liquido').eq('instituicao_id', self.instituicao_id).eq('status', 'PENDENTE').execute()
            salarios_pendentes = sum(f['salario_liquido'] for f in folhas.data) if folhas.data else 0
            
            # ===== PROJEÇÃO =====
            projecao_caixa = saldo_atual + propinas_pendentes - salarios_pendentes
            
            # ===== RENTABILIDADE =====
            margem_lucro = ((total_receitas - total_despesas) / total_receitas * 100) if total_receitas > 0 else 0
            
            self.logger.info(f"KPIs calculados: Inadimplência={taxa_inadimplencia:.1f}%, Saldo={saldo_atual:.2f}, Projeção={projecao_caixa:.2f}")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "alunos": {
                    "total": total_alunos,
                    "devedores": devedores,
                    "adimplentes": total_alunos - devedores
                },
                "financeiro": {
                    "total_receitas": total_receitas,
                    "total_despesas": total_despesas,
                    "saldo_atual": saldo_atual,
                    "margem_lucro": round(margem_lucro, 2)
                },
                "propinas": {
                    "pendentes": propinas_pendentes,
                    "pagas": propinas_pagas_total,
                    "total": propinas_pendentes + propinas_pagas_total
                },
                "salarios": {
                    "pendentes": salarios_pendentes
                },
                "indicadores": {
                    "taxa_inadimplencia": round(taxa_inadimplencia, 1),
                    "projecao_caixa": projecao_caixa,
                    "saude_financeira": self._calcular_saude_financeira(saldo_atual, salarios_pendentes)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular KPIs: {e}")
            return None
    
    def _calcular_saude_financeira(self, saldo, despesas_pendentes):
        """
        Calcula um score de saúde financeira (0-100)
        
        Args:
            saldo: Saldo atual
            despesas_pendentes: Despesas pendentes
        
        Returns:
            Score de 0-100
        """
        if saldo <= 0:
            return 0
        
        cobertura = saldo / despesas_pendentes if despesas_pendentes > 0 else 100
        
        if cobertura >= 3:
            return 100
        elif cobertura >= 2:
            return 80
        elif cobertura >= 1:
            return 60
        elif cobertura >= 0.5:
            return 30
        else:
            return 10
    
    def obter_relatorio_mensal(self, mes, ano):
        """
        Gera relatório detalhado do mês
        
        Args:
            mes: Mês (1-12)
            ano: Ano
        
        Returns:
            Dicionário com dados do mês
        """
        try:
            # Receitas do mês
            receitas = self.supabase.table('receitas').select('*').eq('instituicao_id', self.instituicao_id).execute()
            receitas_mes = [
                r for r in receitas.data
                if r['data_recebimento'][:7] == f"{ano}-{mes:02d}"
            ] if receitas.data else []
            
            total_receitas_mes = sum(r['valor'] for r in receitas_mes)
            
            # Despesas do mês
            despesas = self.supabase.table('despesas').select('*').eq('instituicao_id', self.instituicao_id).eq('status', 'PAGO').execute()
            despesas_mes = [
                d for d in despesas.data
                if d['data_pagamento'][:7] == f"{ano}-{mes:02d}"
            ] if despesas.data else []
            
            total_despesas_mes = sum(d['valor'] for d in despesas_mes)
            
            # Propinas do mês
            propinas = self.supabase.table('propinas').select('*').eq('instituicao_id', self.instituicao_id).eq('mes', mes).eq('ano', ano).execute()
            propinas_pendentes = sum(p['valor'] for p in propinas.data if p['status'] == 'PENDENTE') if propinas.data else 0
            propinas_pagas = sum(p['valor'] for p in propinas.data if p['status'] == 'PAGO') if propinas.data else 0
            
            # Lucro líquido
            lucro_liquido = total_receitas_mes - total_despesas_mes
            
            # Despesa por categoria
            categorias = {}
            for d in despesas_mes:
                tipo = d.get('tipo', 'Outros')
                categorias[tipo] = categorias.get(tipo, 0) + d['valor']
            
            self.logger.info(f"Relatório {mes}/{ano} gerado - Receita: {total_receitas_mes:.2f}, Despesa: {total_despesas_mes:.2f}")
            
            return {
                "periodo": f"{mes:02d}/{ano}",
                "receitas": {
                    "total": total_receitas_mes,
                    "quantidade": len(receitas_mes)
                },
                "despesas": {
                    "total": total_despesas_mes,
                    "quantidade": len(despesas_mes),
                    "por_categoria": categorias
                },
                "propinas": {
                    "pendentes": propinas_pendentes,
                    "pagas": propinas_pagas,
                    "total": propinas_pendentes + propinas_pagas
                },
                "lucro_liquido": lucro_liquido
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório mensal: {e}")
            return None
    
    def obter_tendencias(self, meses=6):
        """
        Analisa tendências dos últimos N meses
        
        Args:
            meses: Número de meses a analisar
        
        Returns:
            Dicionário com tendências
        """
        try:
            tendencias = []
            hoje = datetime.now()
            
            for i in range(meses):
                data = hoje - timedelta(days=30 * i)
                relatorio = self.obter_relatorio_mensal(data.month, data.year)
                if relatorio:
                    tendencias.insert(0, relatorio)
            
            # Calcular variação
            if len(tendencias) > 1:
                variacao_receita = (
                    (tendencias[-1]['receitas']['total'] - tendencias[-2]['receitas']['total']) / 
                    tendencias[-2]['receitas']['total'] * 100
                    if tendencias[-2]['receitas']['total'] > 0 else 0
                )
            else:
                variacao_receita = 0
            
            self.logger.info(f"Análise de tendências ({meses} meses): Variação receita={variacao_receita:.1f}%")
            
            return {
                "periodo": f"Últimos {meses} meses",
                "tendencias": tendencias,
                "variacao_receita": round(variacao_receita, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar tendências: {e}")
            return None
    
    def obter_ranking_turmas(self):
        """
        Cria ranking de turmas por desempenho acadêmico
        
        Returns:
            Lista de turmas com métricas
        """
        try:
            alunos = self.supabase.table('usuarios').select('*').eq('instituicao_id', self.instituicao_id).eq('nivel', 'Estudante').execute()
            
            if not alunos.data:
                return []
            
            # Agrupar por turma
            turmas = {}
            for aluno in alunos.data:
                turma = aluno.get('cargo', 'N/A')
                if turma not in turmas:
                    turmas[turma] = {
                        'total': 0,
                        'devedores': 0,
                        'notas': []
                    }
                turmas[turma]['total'] += 1
                if aluno.get('tem_divida'):
                    turmas[turma]['devedores'] += 1
            
            # Buscar notas
            notas = self.supabase.table('notas').select('*').execute()
            if notas.data:
                for nota in notas.data:
                    for turma in turmas.values():
                        turma['notas'].append(nota.get('media', 0))
            
            # Calcular métricas por turma
            ranking = []
            for turma_nome, dados in turmas.items():
                media_notas = sum(dados['notas']) / len(dados['notas']) if dados['notas'] else 0
                taxa_inadimplencia = (dados['devedores'] / dados['total'] * 100) if dados['total'] > 0 else 0
                
                ranking.append({
                    'turma': turma_nome,
                    'total_alunos': dados['total'],
                    'adimplentes': dados['total'] - dados['devedores'],
                    'taxa_inadimplencia': round(taxa_inadimplencia, 1),
                    'media_notas': round(media_notas, 2),
                    'score': round(
                        (media_notas / 20 * 60) + ((100 - taxa_inadimplencia) / 100 * 40), 2
                    )
                })
            
            # Ordenar por score
            ranking.sort(key=lambda x: x['score'], reverse=True)
            
            self.logger.info(f"Ranking de turmas gerado: {len(ranking)} turmas")
            return ranking
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar ranking de turmas: {e}")
            return []
    
    def gerar_alerta_financeiro(self):
        """
        Gera alertas automáticos baseado na saúde financeira
        
        Returns:
            Lista de alertas com severidade
        """
        try:
            kpis = self.calcular_kpis()
            alertas = []
            
            if not kpis:
                return alertas
            
            # Alerta de inadimplência
            if kpis['indicadores']['taxa_inadimplencia'] > 20:
                alertas.append({
                    'tipo': 'INADIMPLENCIA',
                    'severidade': 'CRÍTICA' if kpis['indicadores']['taxa_inadimplencia'] > 40 else 'ALTA',
                    'mensagem': f"Taxa de inadimplência em {kpis['indicadores']['taxa_inadimplencia']}%"
                })
            
            # Alerta de caixa
            if kpis['financeiro']['saldo_atual'] < kpis['salarios']['pendentes']:
                alertas.append({
                    'tipo': 'CAIXA_INSUFICIENTE',
                    'severidade': 'CRÍTICA',
                    'mensagem': f"Caixa insuficiente para pagar salários"
                })
            
            # Alerta de saldo baixo
            if kpis['financeiro']['saldo_atual'] < (kpis['salarios']['pendentes'] * 0.5):
                alertas.append({
                    'tipo': 'SALDO_BAIXO',
                    'severidade': 'ALTA',
                    'mensagem': f"Saldo crítico: {kpis['financeiro']['saldo_atual']:.2f} Kz"
                })
            
            # Alerta de propinas
            if kpis['propinas']['pendentes'] > (kpis['propinas']['pagas'] * 0.5):
                alertas.append({
                    'tipo': 'PROPINAS_ALTAS',
                    'severidade': 'MÉDIA',
                    'mensagem': f"Propinas pendentes: {kpis['propinas']['pendentes']:.2f} Kz"
                })
            
            if alertas:
                self.logger.warning(f"Alertas gerados: {len(alertas)} alertas")
            
            return alertas
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alertas: {e}")
            return []
    
    def exportar_dados_csv(self, tipo='relatorio'):
        """
        Exporta dados para CSV
        
        Args:
            tipo: 'relatorio' | 'kpis' | 'alunos'
        
        Returns:
            String em formato CSV
        """
        try:
            import csv
            from io import StringIO
            
            output = StringIO()
            
            if tipo == 'kpis':
                kpis = self.calcular_kpis()
                writer = csv.writer(output)
                writer.writerow(['Métrica', 'Valor'])
                for chave, valor in kpis['indicadores'].items():
                    writer.writerow([chave, valor])
            
            elif tipo == 'alunos':
                alunos = self.supabase.table('usuarios').select('*').eq('instituicao_id', self.instituicao_id).eq('nivel', 'Estudante').execute()
                writer = csv.DictWriter(output, fieldnames=['nome', 'email', 'telefone', 'tem_divida'])
                writer.writeheader()
                if alunos.data:
                    for aluno in alunos.data:
                        writer.writerow({
                            'nome': aluno.get('nome'),
                            'email': aluno.get('email'),
                            'telefone': aluno.get('telefone'),
                            'tem_divida': aluno.get('tem_divida')
                        })
            
            self.logger.info(f"Dados exportados em CSV: tipo={tipo}")
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar CSV: {e}")
            return None


__all__ = ['BIManager']
