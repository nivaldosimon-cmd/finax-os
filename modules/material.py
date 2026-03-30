"""
MÓDULO MATERIAL - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Partilha de materiais didáticos entre professores e alunos
- Upload de links de materiais (PDF, Vídeo, Link)
- Visualização e acesso aos materiais via navegador
"""

import sys
import os
import uuid
import webbrowser
from datetime import datetime

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config


# ============================================
# IMPORTAÇÕES DE TERCEIROS
# ============================================
from tabulate import tabulate

# ============================================
# CONSTANTES
# ============================================

# Tipos de materiais suportados
TIPOS_MATERIAIS = ["PDF", "Link", "Vídeo"]

# Mensagens
MSG_TIPO_INVALIDO = f"Tipo inválido. Escolha: {', '.join(TIPOS_MATERIAIS)}"


# ============================================
# CLASSE PRINCIPAL DE GESTÃO DE MATERIAL
# ============================================

class GestaoMaterial:
    """
    Classe responsável pela gestão de materiais didáticos.
    
    Funcionalidades:
    - Upload de materiais (PDF, Link, Vídeo)
    - Listagem de materiais disponíveis
    - Abertura automática de links no navegador
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        
    
    # ============================================
    # 1. UPLOAD DE MATERIAL (ADMIN/PROFESSOR)
    # ============================================
    
    def upload_material(self, escola_id):
        """
        Regista um novo material didático no sistema.
        
        Args:
            escola_id (str): ID da escola do administrador
        
        Returns:
            dict or None: Dados do material registado
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📤 UPLOAD DE MATERIAL - FINAX OS")
        self.interface.mostrar_info("Partilhe materiais didáticos com os alunos.")
        
        try:
            # Coletar dados do material
            print(f"\n{self.interface.cores.AZUL}📌 DADOS DO MATERIAL{self.interface.cores.RESET}")
            
            titulo = self.interface.input_com_validação(
                "Título do material: ",
                obrigatorio=True
            )
            
            disciplina = self.interface.input_com_validação(
                "Disciplina: ",
                obrigatorio=True
            )
            
            # Escolher tipo de material
            print(f"\n{self.interface.cores.AZUL}📁 TIPO DE MATERIAL{self.interface.cores.RESET}")
            for i, tipo in enumerate(TIPOS_MATERIAIS, 1):
                print(f"   {i} - {tipo}")
            
            tipo_escolha = self.interface.input_com_validação(
                "\nEscolha o tipo (1-3): ",
                obrigatorio=True,
                tipo="numero"
            )
            
            try:
                tipo_idx = int(tipo_escolha) - 1
                if tipo_idx < 0 or tipo_idx >= len(TIPOS_MATERIAIS):
                    raise ValueError
                tipo = TIPOS_MATERIAIS[tipo_idx]
            except ValueError:
                self.interface.exibir_mensagem(MSG_TIPO_INVALIDO, tipo="erro")
                return None
            
            # Coletar URL/link
            print(f"\n{self.interface.cores.AZUL}🔗 LINK DE ACESSO{self.interface.cores.RESET}")
            self.interface.mostrar_info("   Exemplos:")
            print("   • Google Drive: https://drive.google.com/file/d/...")
            print("   • YouTube: https://youtu.be/... ou https://www.youtube.com/watch?v=...")
            print("   • Link direto: https://...")
            
            url_acesso = self.interface.input_com_validação(
                "URL do material: ",
                obrigatorio=True
            )
            
            # Validar URL (básico)
            if not url_acesso.startswith(('http://', 'https://')):
                self.interface.exibir_mensagem("URL inválida! Deve começar com http:// ou https://", tipo="erro")
                return None
            
            # Confirmar dados
            self.interface.mostrar_info("\n📋 CONFIRMAÇÃO")
            print(f"   Título: {titulo}")
            print(f"   Disciplina: {disciplina}")
            print(f"   Tipo: {tipo}")
            print(f"   Link: {url_acesso[:60]}{'...' if len(url_acesso) > 60 else ''}")
            
            if not self.interface.confirmar("\nDeseja publicar este material?"):
                self.interface.mostrar_info("Upload cancelado.")
                return None
            
            # Registrar no banco
            material_id = str(uuid.uuid4())
            data_upload = datetime.now().isoformat()
            
            dados_material = {
                "id": material_id,
                "titulo": titulo,
                "disciplina": disciplina,
                "tipo": tipo,
                "url_acesso": url_acesso,
                "escola_id": escola_id,
                "data_upload": data_upload
            }
            
            resultado = self.supabase.table('materiais').insert(dados_material).execute()
            
            if resultado.data:
                self.interface.mostrar_sucesso("Material publicado com sucesso!")
                print(f"\n{self.interface.cores.CIANO}📎 ID do material: {material_id}{self.interface.cores.RESET}")
                return resultado.data[0]
            else:
                self.interface.exibir_mensagem("Erro ao publicar material.", tipo="erro")
                return None
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao fazer upload: {e}", tipo="erro")
            return None
    
    # ============================================
    # 2. LISTAR MATERIAIS (PARA ALUNOS/ADMIN)
    # ============================================
    
    def listar_materiais_aluno(self, escola_id, disciplina=None):
        """
        Lista todos os materiais disponíveis para a escola.
        
        Args:
            escola_id (str): ID da escola
            disciplina (str, optional): Filtrar por disciplina
        
        Returns:
            list: Lista de materiais
        """
        self.interface.limpar_tela()
        
        if disciplina:
            self.interface.mostrar_titulo(f"📚 MATERIAIS - {disciplina.upper()}")
        else:
            self.interface.mostrar_titulo("📚 BIBLIOTECA DIGITAL - FINAX OS")
        
        try:
            # Construir query
            query = self.supabase.table('materiais')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .order('data_upload', desc=True)
            
            if disciplina:
                query = query.eq('disciplina', disciplina)
            
            resultado = query.execute()
            materiais = resultado.data
            
            if not materiais:
                self.interface.exibir_mensagem(
                    "Nenhum material disponível no momento.",
                    tipo="info"
                )
                return []
            
            # Preparar dados para a tabela
            dados_tabela = []
            for i, mat in enumerate(materiais, 1):
                # Ícone conforme tipo
                if mat['tipo'] == 'PDF':
                    icone = "📄"
                elif mat['tipo'] == 'Vídeo':
                    icone = "🎬"
                else:
                    icone = "🔗"
                
                # Data formatada
                try:
                    data_obj = datetime.fromisoformat(mat['data_upload'])
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                except:
                    data_formatada = mat['data_upload'][:10] if mat['data_upload'] else "N/A"
                
                dados_tabela.append([
                    i,
                    f"{icone} {mat['tipo']}",
                    mat['disciplina'],
                    mat['titulo'][:40] + ("..." if len(mat['titulo']) > 40 else ""),
                    data_formatada,
                    mat['id']  # Guardar ID para acesso
                ])
            
            # Exibir tabela
            print("\n")
            tabela = tabulate(
                [[d[0], d[1], d[2], d[3], d[4]] for d in dados_tabela],
                headers=["#", "TIPO", "DISCIPLINA", "TÍTULO", "DATA"],
                tablefmt="grid"
            )
            print(tabela)
            
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"📊 Total de materiais: {len(materiais)}")
            
            return materiais
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao listar materiais: {e}", tipo="erro")
            return []
    
    # ============================================
    # 3. ABRIR MATERIAL NO NAVEGADOR
    # ============================================
    
    def abrir_material(self, material_id):
        """
        Abre o link do material no navegador padrão.
        
        Args:
            material_id (str): ID do material
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            # Buscar material
            resultado = self.supabase.table('materiais')\
                .select('titulo, tipo, url_acesso')\
                .eq('id', material_id)\
                .execute()
            
            if not resultado.data:
                self.interface.exibir_mensagem("Material não encontrado!", tipo="erro")
                return False
            
            material = resultado.data[0]
            titulo = material['titulo']
            url = material['url_acesso']
            tipo = material['tipo']
            
            # Confirmar abertura
            self.interface.mostrar_info(f"\n📎 Abrindo: {titulo}")
            print(f"   Tipo: {tipo}")
            print(f"   Link: {url[:80]}{'...' if len(url) > 80 else ''}")
            
            if self.interface.confirmar("\nAbrir no navegador?"):
                webbrowser.open(url)
                self.interface.mostrar_sucesso("Material aberto no navegador!")
                return True
            else:
                self.interface.mostrar_info("Acesso cancelado.")
                return False
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao abrir material: {e}", tipo="erro")
            return False
    
    # ============================================
    # 4. LISTAR MATERIAIS COM INTERATIVIDADE
    # ============================================
    
    def menu_materiais_aluno(self, escola_id):
        """
        Menu interativo para alunos visualizarem e acederem a materiais.
        
        Args:
            escola_id (str): ID da escola
        """
        while True:
            # Listar materiais
            materiais = self.listar_materiais_aluno(escola_id)
            
            if not materiais:
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para voltar..." + self.interface.cores.RESET)
                break
            
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print("1 - 🔍 Abrir um material")
            print("2 - 📁 Filtrar por disciplina")
            print("3 - 🔄 Atualizar lista")
            print("4 - ⬅️ Voltar")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                try:
                    idx = int(self.interface.input_com_validação(
                        "Número do material: ",
                        obrigatorio=True,
                        tipo="numero"
                    ))
                    if 1 <= idx <= len(materiais):
                        material_id = materiais[idx-1]['id']
                        self.abrir_material(material_id)
                    else:
                        self.interface.exibir_mensagem("Número inválido!", tipo="erro")
                except ValueError:
                    self.interface.exibir_mensagem("Número inválido!", tipo="erro")
                
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                disciplina = self.interface.input_com_validação(
                    "Nome da disciplina: ",
                    obrigatorio=True
                )
                self.listar_materiais_aluno(escola_id, disciplina)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                continue
                
            elif opcao == "4":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
    
    # ============================================
    # 5. MENU ADMIN (GESTÃO DE MATERIAIS)
    # ============================================
    
    def menu_admin(self, escola_id):
        """
        Menu interativo para administradores gerirem materiais.
        
        Args:
            escola_id (str): ID da escola
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("📚 FINAX MATERIAL - GESTÃO DE MATERIAIS")
            
            print("1 - 📤 Publicar novo material")
            print("2 - 📖 Ver todos os materiais")
            print("3 - 🗑️ Remover material (em breve)")
            print("4 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.upload_material(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                self.listar_materiais_aluno(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                self.interface.exibir_mensagem("Funcionalidade em desenvolvimento.", tipo="info")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "4":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
    
    # ============================================
    # 6. FUNÇÃO DE INTEGRAÇÃO COM PERFIL
    # ============================================
    
    def iniciar_por_perfil(self, sessao):
        """
        Inicia o módulo conforme o perfil do utilizador.
        
        Args:
            sessao (dict): Dados da sessão do utilizador logado
        """
        nivel = sessao.get('nivel')
        escola_id = sessao.get('escola')
        
        if nivel == 'Administrador':
            self.menu_admin(escola_id)
        else:
            self.menu_materiais_aluno(escola_id)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_material(sessao):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        sessao (dict): Dados da sessão do utilizador logado
    """
    material = GestaoMaterial()
    material.iniciar_por_perfil(sessao)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Gestão de Material")
    print("⚠️ Para testar, execute o main.py com um utilizador logado.")
    print("   Ou utilize: material = GestaoMaterial()")
    print("   material.upload_material('ESC_001')")