"""
UMBRELLA AI - SISTEMA DE GESTÃO ESCOLAR
Frontend Streamlit Moderno com QR Code Visual
Versão corrigida - sem erros de elementos duplicados
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import uuid
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database_config import db_config
from modules.super_perfil import iniciar_login_simples
from utils.qr_utils import gerar_qr_code_aluno, gerar_qr_code_pagamento, listar_qr_codes

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Umbrella AI - Gestão Escolar",
    page_icon="☂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ESTILOS CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 700; }
    
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    
    .metric-card {
        text-align: center;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        border-radius: 20px;
        padding: 1.2rem;
        color: white;
    }
    
    .metric-value { font-size: 2.2rem; font-weight: 800; }
    .metric-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.3rem; }
    
    .stButton button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }
    
    .stButton button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(30,58,138,0.4); }
    
    .badge-success { background: #10B981; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-warning { background: #F59E0B; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-danger { background: #EF4444; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    
    .qr-container { background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAÇÃO
# ============================================
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "supabase" not in st.session_state:
        st.session_state.supabase = db_config.get_client()
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

init_session_state()
supabase = st.session_state.supabase

# ============================================
# TELA DE LOGIN
# ============================================
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>☂️ UMBRELLA AI</h1>
        <p>Sistema Inteligente de Gestão Escolar</p>
        <p style="font-size: 0.9rem; opacity: 0.9;">✨ Tecnologia | Inovação | Eficiência ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Acesso ao Sistema")
        
        username = st.text_input("Username", placeholder="Digite seu username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Digite sua senha", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🎯 Entrar", key="login_btn", use_container_width=True):
                if username and password:
                    user = iniciar_login_simples(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Username ou password incorretos!")
                else:
                    st.warning("Preencha todos os campos!")
        with col_btn2:
            if st.button("📝 Criar Conta", key="signup_btn_main", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# TELA DE CADASTRO
# ============================================
def signup_page():
    st.markdown("""
    <div class="main-header">
        <h1>📝 Criar Nova Conta</h1>
        <p>Junte-se ao Umbrella AI e modernize sua escola</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏢 Sou Administrador", "🎓 Sou Estudante"])
    
    # ==================== TAB ADMIN ====================
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🏫 Criar Nova Escola")
        
        col1, col2 = st.columns(2)
        with col1:
            escola_nome = st.text_input("Nome da Escola", key="signup_escola_nome")
            escola_endereco = st.text_input("Endereço", key="signup_escola_endereco")
        with col2:
            escola_telefone = st.text_input("Telefone da Escola", key="signup_escola_telefone")
            escola_email = st.text_input("Email da Escola", key="signup_escola_email")
        
        st.markdown("---")
        st.markdown("### 👤 Dados do Administrador")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo", key="signup_admin_nome")
            username = st.text_input("Username", key="signup_admin_username")
        with col2:
            password = st.text_input("Password", type="password", key="signup_admin_password")
            email = st.text_input("Email", key="signup_admin_email")
        
        telefone = st.text_input("Telefone", key="signup_admin_telefone")
        
        st.markdown("---")
        st.markdown("### 🏦 Dados Bancários (IBAN)")
        
        iban = st.text_input("IBAN (ex: AO06.0066.0000.1234.5678.9012.3)", key="signup_iban")
        iban_nome = st.text_input("Nome do Titular da Conta", key="signup_iban_nome")
        
        if st.button("🚀 Criar Escola e Conta", key="signup_create_btn", use_container_width=True):
            if all([escola_nome, nome, username, password, email, telefone, iban, iban_nome]):
                try:
                    escola_id = f"ESC_{uuid.uuid4().hex[:8].upper()}"
                    admin_id = str(uuid.uuid4())
                    senha_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    dados_admin = {
                        "id": admin_id, "username": username.lower(), "password": senha_hash,
                        "nivel": "Administrador", "sub_nivel": "SuperAdmin", "nome": nome,
                        "email": email, "telefone": telefone, "escola_id": escola_id,
                        "classe": "DIREÇÃO", "turma": "GERAL", "curso": "ADMINISTRAÇÃO",
                        "tem_divida": False, "status_conta": "Ativa", "iban": iban,
                        "iban_nome": iban_nome, "created_at": datetime.now().isoformat()
                    }
                    
                    supabase.table('usuarios').insert(dados_admin).execute()
                    
                    st.success("✅ Conta criada com sucesso!")
                    st.info(f"🏛️ ID da Escola: `{escola_id}`")
                    st.info(f"👤 Username: `{username}`")
                    st.info(f"🏦 IBAN: `{iban[:15]}...`")
                    st.warning("Guarde estas informações!")
                    
                    if st.button("🔐 Fazer Login Agora", key="login_after_signup_admin"):
                        st.session_state.user = dados_admin
                        st.session_state.authenticated = True
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("Preencha todos os campos obrigatórios!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ==================== TAB ESTUDANTE ====================
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎓 Juntar-se a uma Escola")
        
        escola_id = st.text_input("ID da Escola", placeholder="EX: ESC_ABC123", key="signup_estudante_escola_id")
        
        st.markdown("---")
        st.markdown("### 👤 Dados Pessoais")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo", key="signup_estudante_nome")
            username = st.text_input("Username", key="signup_estudante_username")
        with col2:
            password = st.text_input("Password", type="password", key="signup_estudante_password")
            email = st.text_input("Email", key="signup_estudante_email")
        
        telefone = st.text_input("Telefone", key="signup_estudante_telefone")
        data_nascimento = st.text_input("Data de Nascimento (dd/mm/aaaa)", key="signup_estudante_data")
        
        st.markdown("---")
        st.markdown("### 📚 Dados Académicos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            classe = st.text_input("Classe (ex: 10ª, 11ª, 12ª)", key="signup_estudante_classe")
        with col2:
            turma = st.text_input("Turma (ex: A, B, C)", key="signup_estudante_turma")
        with col3:
            curso = st.text_input("Curso (ex: Ciências, Humanidades)", key="signup_estudante_curso")
        
        st.markdown("---")
        st.markdown("### 👨‍👩‍👧 Encarregados de Educação (Opcional)")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_pai = st.text_input("Nome do Pai", key="signup_estudante_nome_pai")
            telefone_pai = st.text_input("Telefone do Pai", key="signup_estudante_telefone_pai")
        with col2:
            nome_mae = st.text_input("Nome da Mãe", key="signup_estudante_nome_mae")
            telefone_mae = st.text_input("Telefone da Mãe", key="signup_estudante_telefone_mae")
        
        nome_responsavel = st.text_input("Nome do Responsável (se diferente)", key="signup_estudante_responsavel")
        telefone_responsavel = st.text_input("Telefone do Responsável", key="signup_estudante_telefone_responsavel")
        
        if st.button("📝 Cadastrar Estudante", key="signup_estudante_btn", use_container_width=True):
            if all([escola_id, nome, username, password, email, telefone, classe, turma, curso]):
                try:
                    # Verificar se escola existe
                    escola_existe = supabase.table('usuarios').select('escola_id').eq('escola_id', escola_id).limit(1).execute()
                    if not escola_existe.data:
                        st.error("Escola não encontrada! Verifique o ID.")
                    else:
                        estudante_id = str(uuid.uuid4())
                        senha_hash = hashlib.sha256(password.encode()).hexdigest()
                        
                        # Gerar QR Code ID
                        ultimo = supabase.table('usuarios').select('qrcode_id').eq('escola_id', escola_id).not_.is_('qrcode_id', 'null').order('qrcode_id', desc=True).limit(1).execute()
                        if ultimo.data and ultimo.data[0]['qrcode_id']:
                            qrcode_id = str(int(ultimo.data[0]['qrcode_id']) + 1)
                        else:
                            qrcode_id = "1001"
                        
                        dados = {
                            "id": estudante_id, "username": username.lower(), "password": senha_hash,
                            "nivel": "Estudante", "nome": nome, "email": email, "telefone": telefone,
                            "escola_id": escola_id, "classe": classe, "turma": turma, "curso": curso,
                            "tem_divida": True, "status_conta": "Ativa", "qrcode_id": qrcode_id,
                            "data_nascimento": data_nascimento, "created_at": datetime.now().isoformat(),
                            "nome_pai": nome_pai, "telefone_pai": telefone_pai, "nome_mae": nome_mae,
                            "telefone_mae": telefone_mae, "nome_responsavel": nome_responsavel,
                            "telefone_responsavel": telefone_responsavel
                        }
                        
                        supabase.table('usuarios').insert(dados).execute()
                        
                        # Gerar QR Code visual
                        turma_completa = f"{classe} {turma}".strip()
                        try:
                            from utils.qr_utils import gerar_qr_code_aluno
                            qr_path = gerar_qr_code_aluno(estudante_id, nome, turma_completa, qrcode_id)
                        except:
                            qr_path = None
                        
                        st.success(f"✅ Estudante {nome} cadastrado com sucesso!")
                        st.info(f"Username: {username}")
                        st.info(f"QR Code ID: {qrcode_id}")
                        if qr_path:
                            st.info(f"QR Code salvo em: {qr_path}")
                        
                        if st.button("🔐 Fazer Login Agora", key="login_after_signup_estudante"):
                            st.session_state.user = dados
                            st.session_state.authenticated = True
                            st.rerun()
                        
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("Preencha todos os campos obrigatórios!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Voltar ao Login", key="back_to_login"):
        st.session_state.show_signup = False
        st.rerun()

# ============================================
# DASHBOARD PRINCIPAL
# ============================================
def dashboard():
    user = st.session_state.user
    escola_id = user['escola']
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
                        border-radius: 50%; width: 80px; height: 80px; 
                        margin: 0 auto 1rem; display: flex; align-items: center; 
                        justify-content: center;">
                <span style="font-size: 2.5rem;">{'👨‍💼' if user['nivel'] == 'Administrador' else '🎓'}</span>
            </div>
            <h3>{user['nome'][:20]}</h3>
            <p style="color: #9CA3AF;">@{user['username']}</p>
            <p><span class="{'badge-success' if user['nivel'] == 'Administrador' else 'badge-warning'}">{user['nivel']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        menu_items = {
            "dashboard": "📊 Dashboard",
            "presencas": "📍 Presenças",
            "alunos": "👥 Alunos",
            "notas": "📝 Notas",
            "ranking": "🏆 Ranking",
            "financeiro": "💰 Financeiro",
            "material": "📚 Biblioteca",
            "denuncias": "🕊️ Ética",
            "qrcodes": "📱 QR Codes",
            "config": "⚙️ Configurações"
        }
        
        if user['nivel'] == 'Administrador':
            menu = menu_items
        else:
            menu = {k: v for k, v in menu_items.items() if k in ['dashboard', 'presencas', 'notas', 'ranking', 'material', 'denuncias', 'qrcodes']}
        
        for key, label in menu.items():
            if st.sidebar.button(label, key=f"menu_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Sair", key="logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    page = st.session_state.get('page', 'dashboard')
    
    if page == "dashboard":
        dashboard_home(user, supabase, escola_id)
    elif page == "presencas":
        presencas_page(user, supabase, escola_id)
    elif page == "alunos":
        alunos_page(user, supabase, escola_id)
    elif page == "notas":
        notas_page(user, supabase, escola_id)
    elif page == "ranking":
        ranking_page(user, supabase, escola_id)
    elif page == "financeiro":
        financeiro_page(user, supabase, escola_id)
    elif page == "material":
        material_page(user, supabase, escola_id)
    elif page == "denuncias":
        denuncias_page(user, supabase, escola_id)
    elif page == "qrcodes":
        qrcodes_page(user, supabase, escola_id)
    elif page == "config":
        config_page(user, supabase, escola_id)

# ============================================
# PÁGINA DASHBOARD
# ============================================
def dashboard_home(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Visão geral da sua escola em tempo real</p>
    </div>
    """, unsafe_allow_html=True)
    
    alunos = supabase.table('usuarios').select('*').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
    total_alunos = len(alunos.data) if alunos.data else 0
    
    hoje = datetime.now().strftime("%Y-%m-%d")
    presencas = supabase.table('presencas').select('*').eq('escola_id', escola_id).eq('data', hoje).execute()
    total_presencas = len(presencas.data) if presencas.data else 0
    
    alunos_debito = sum(1 for a in alunos.data if a.get('tem_divida', False)) if alunos.data else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_alunos}</div><div class='metric-label'>👥 Total de Alunos</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_presencas}</div><div class='metric-label'>📍 Presenças Hoje</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{alunos_debito}</div><div class='metric-label'>💰 Alunos com Débito</div></div>", unsafe_allow_html=True)
    with col4:
        percentual = (total_presencas / total_alunos * 100) if total_alunos > 0 else 0
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{percentual:.0f}%</div><div class='metric-label'>📈 % Presença</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Distribuição por Classe/Turma")
        if alunos.data:
            turmas = {}
            for a in alunos.data:
                chave = f"{a.get('classe', 'N/A')} {a.get('turma', '')}"
                turmas[chave] = turmas.get(chave, 0) + 1
            df = pd.DataFrame(list(turmas.items()), columns=['Classe/Turma', 'Quantidade'])
            fig = px.bar(df, x='Classe/Turma', y='Quantidade', color='Quantidade', color_continuous_scale='Viridis')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum aluno cadastrado.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Status Financeiro")
        if alunos.data:
            fig = go.Figure(data=[go.Pie(labels=['Em dia', 'Débito'], values=[total_alunos - alunos_debito, alunos_debito], marker_colors=['#10B981', '#EF4444'], hole=0.4, textinfo='label+percent')])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado financeiro.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📋 Últimas Atividades")
    ultimas = supabase.table('presencas').select('*').eq('escola_id', escola_id).order('data', desc=True).limit(5).execute()
    if ultimas.data:
        for p in ultimas.data:
            st.markdown(f"✅ **{p.get('nome_aluno', 'Aluno')}** - Entrada registada em {p.get('data', 'N/A')} às {p.get('hora_entrada', 'N/A')}")
    else:
        st.info("Nenhuma atividade recente.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# PÁGINA QR CODES
# ============================================
def qrcodes_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>📱 QR Codes</h1>
        <p>Gere QR codes com ID numérico único para os alunos</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🎓 QR Code do Aluno", "📁 QR Codes Gerados"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎓 Gerar QR Code do Aluno")
        
        alunos = supabase.table('usuarios').select('id, nome, username, classe, turma, qrcode_id').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
        
        if alunos.data:
            aluno_opcoes = {}
            for a in alunos.data:
                if a.get('qrcode_id'):
                    display = f"{a['nome']} (ID: {a['qrcode_id']})"
                else:
                    display = f"{a['nome']} (sem QR)"
                aluno_opcoes[display] = a
            
            aluno_selecionado = st.selectbox("Selecione o aluno", list(aluno_opcoes.keys()), key="qr_aluno_select")
            aluno = aluno_opcoes[aluno_selecionado]
            
            if st.button("🆕 Gerar Novo ID", key="qr_gen_id", use_container_width=True):
                ultimo_id = supabase.table('usuarios').select('qrcode_id').eq('escola_id', escola_id).not_.is_('qrcode_id', 'null').order('qrcode_id', desc=True).limit(1).execute()
                if ultimo_id.data and ultimo_id.data[0]['qrcode_id']:
                    novo_id = str(int(ultimo_id.data[0]['qrcode_id']) + 1)
                else:
                    novo_id = "1001"
                supabase.table('usuarios').update({"qrcode_id": novo_id}).eq('id', aluno['id']).execute()
                st.success(f"✅ ID {novo_id} gerado para {aluno['nome']}")
                st.rerun()
            
            if aluno.get('qrcode_id'):
                if st.button("📱 Gerar QR Code", key="qr_generate", use_container_width=True):
                    with st.spinner("Gerando QR code..."):
                        turma_completa = f"{aluno.get('classe', '')} {aluno.get('turma', '')}".strip()
                        caminho = gerar_qr_code_aluno(
                            aluno_id=aluno['id'],
                            nome=aluno['nome'],
                            turma=turma_completa,
                            qrcode_id=aluno['qrcode_id']
                        )
                        if os.path.exists(caminho):
                            st.markdown('<div class="qr-container">', unsafe_allow_html=True)
                            st.image(caminho, caption=f"QR Code de {aluno['nome']} - ID: {aluno['qrcode_id']}", use_container_width=True)
                            st.success(f"✅ QR Code gerado para {aluno['nome']}")
                            with open(caminho, "rb") as file:
                                st.download_button(label="📥 Baixar QR Code", data=file, file_name=f"qr_{aluno['qrcode_id']}.png", mime="image/png", key="qr_download")
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Primeiro gere um ID para este aluno!")
        else:
            st.info("Nenhum aluno cadastrado.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📁 QR Codes Gerados")
        
        qrcodes = listar_qr_codes()
        if qrcodes:
            for i, qr in enumerate(qrcodes):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📱 **{qr}**")
                with col2:
                    caminho = os.path.join("qrcodes", qr)
                    if os.path.exists(caminho):
                        with open(caminho, "rb") as file:
                            st.download_button(label="📥 Download", data=file, file_name=qr, mime="image/png", key=f"qr_download_{i}")
                st.divider()
        else:
            st.info("Nenhum QR code gerado ainda.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# DEMAIS PÁGINAS (SIMPLIFICADAS)
# ============================================
def presencas_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>📍 Controlo de Presenças</h1>
        <p>Registe a entrada dos alunos</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📷 Registrar Entrada")
        qr_code = st.text_input("Código QR (username ou ID)", key="presenca_qr")
        if st.button("Registrar Entrada", key="presenca_btn", use_container_width=True):
            if qr_code:
                aluno = supabase.table('usuarios').select('*').eq('qrcode_id', qr_code).eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
                if not aluno.data:
                    aluno = supabase.table('usuarios').select('*').eq('username', qr_code).eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
                if aluno.data:
                    aluno_data = aluno.data[0]
                    agora = datetime.now()
                    hora = agora.strftime("%H:%M:%S")
                    data = agora.strftime("%Y-%m-%d")
                    status = "ATRASADO" if agora.hour > 7 or (agora.hour == 7 and agora.minute > 30) else "PRESENTE"
                    
                    presenca_id = str(uuid.uuid4())
                    supabase.table('presencas').insert({
                        "id": presenca_id, "aluno_id": aluno_data['id'], "aluno_username": aluno_data['username'],
                        "nome_aluno": aluno_data['nome'], "escola_id": escola_id,
                        "data": data, "hora_entrada": hora, "status": status
                    }).execute()
                    st.success(f"✅ {aluno_data['nome']} - {status} às {hora}")
                else:
                    st.error("Aluno não encontrado!")
            else:
                st.warning("Digite o código QR!")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Presenças de Hoje")
        hoje = datetime.now().strftime("%Y-%m-%d")
        presencas = supabase.table('presencas').select('*').eq('escola_id', escola_id).eq('data', hoje).execute()
        if presencas.data:
            df = pd.DataFrame(presencas.data)
            df = df[['nome_aluno', 'hora_entrada', 'status']]
            df.columns = ['Aluno', 'Hora', 'Status']
            st.dataframe(df, use_container_width=True)
            st.info(f"Total: {len(presencas.data)} registos")
        else:
            st.info("Nenhuma presença registada hoje.")
        st.markdown('</div>', unsafe_allow_html=True)

def alunos_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>👥 Gestão de Alunos</h1>
        <p>Cadastre e gerencie os alunos</p>
    </div>
    """, unsafe_allow_html=True)
    
    alunos = supabase.table('usuarios').select('*').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
    if alunos.data:
        df = pd.DataFrame(alunos.data)
        df = df[['id', 'nome', 'classe', 'turma', 'curso', 'tem_divida', 'qrcode_id']]
        df.columns = ['ID', 'Nome', 'Classe', 'Turma', 'Curso', 'Débito', 'QR ID']
        df['Status'] = df['Débito'].apply(lambda x: "🔴 Débito" if x else "🟢 Em dia")
        st.dataframe(df, use_container_width=True)
        st.info(f"Total: {len(alunos.data)} alunos")
    
    with st.expander("➕ Cadastrar Novo Aluno"):
        with st.form("cadastro_aluno_form"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome completo", key="cad_nome")
                username = st.text_input("Username", key="cad_username")
                password = st.text_input("Password", type="password", key="cad_password")
            with col2:
                email = st.text_input("Email", key="cad_email")
                telefone = st.text_input("Telefone", key="cad_telefone")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                classe = st.text_input("Classe", key="cad_classe")
            with col2:
                turma = st.text_input("Turma", key="cad_turma")
            with col3:
                curso = st.text_input("Curso", key="cad_curso")
            
            if st.form_submit_button("Cadastrar"):
                if nome and username and password and classe and turma and curso:
                    aluno_id = str(uuid.uuid4())
                    senha_hash = hashlib.sha256(password.encode()).hexdigest()
                    # Gerar QR Code ID
                    ultimo = supabase.table('usuarios').select('qrcode_id').eq('escola_id', escola_id).not_.is_('qrcode_id', 'null').order('qrcode_id', desc=True).limit(1).execute()
                    if ultimo.data and ultimo.data[0]['qrcode_id']:
                        qrcode_id = str(int(ultimo.data[0]['qrcode_id']) + 1)
                    else:
                        qrcode_id = "1001"
                    
                    dados = {
                        "id": aluno_id, "username": username.lower(), "password": senha_hash,
                        "nivel": "Estudante", "nome": nome, "email": email, "telefone": telefone,
                        "escola_id": escola_id, "classe": classe, "turma": turma, "curso": curso,
                        "tem_divida": True, "status_conta": "Ativa", "qrcode_id": qrcode_id,
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table('usuarios').insert(dados).execute()
                    st.success(f"✅ Aluno {nome} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos!")

def notas_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>📝 Gestão de Notas</h1>
        <p>Lançamento de notas e boletim</p>
    </div>
    """, unsafe_allow_html=True)
    
    alunos = supabase.table('usuarios').select('id, nome, classe, turma').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
    if not alunos.data:
        st.info("Nenhum aluno cadastrado.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Lançar Notas")
        aluno_nome = st.selectbox("Aluno", [a['nome'] for a in alunos.data], key="notas_aluno")
        aluno = next(a for a in alunos.data if a['nome'] == aluno_nome)
        disciplina = st.text_input("Disciplina", key="notas_disciplina")
        
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            nota1 = st.number_input("Nota 1", min_value=0.0, max_value=20.0, step=0.5, key="nota1")
        with col_n2:
            nota2 = st.number_input("Nota 2", min_value=0.0, max_value=20.0, step=0.5, key="nota2")
        with col_n3:
            nota3 = st.number_input("Nota 3", min_value=0.0, max_value=20.0, step=0.5, key="nota3")
        
        faltas = st.number_input("Faltas", min_value=0, step=1, key="notas_faltas")
        
        if st.button("Lançar Notas", key="lancar_notas_btn", use_container_width=True):
            if disciplina and (nota1 > 0 or nota2 > 0 or nota3 > 0):
                media = (nota1 + nota2 + nota3) / 3
                dados = {
                    "nota_1": nota1, "nota_2": nota2, "nota_3": nota3, "faltas": faltas,
                    "media": media, "disciplina": disciplina, "aluno_id": aluno['id'],
                    "aluno_username": aluno['nome'].lower().replace(' ', '.'),
                    "escola_id": escola_id, "id": str(uuid.uuid4())
                }
                supabase.table('notas').insert(dados).execute()
                st.success(f"✅ Notas de {disciplina} lançadas! Média: {media:.1f}")
            else:
                st.warning("Preencha a disciplina e pelo menos uma nota!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Boletim do Aluno")
        aluno_boletim = st.selectbox("Aluno", [a['nome'] for a in alunos.data], key="boletim_aluno")
        aluno = next(a for a in alunos.data if a['nome'] == aluno_boletim)
        notas = supabase.table('notas').select('*').eq('aluno_id', aluno['id']).execute()
        if notas.data:
            df = pd.DataFrame(notas.data)
            df = df[['disciplina', 'nota_1', 'nota_2', 'nota_3', 'media', 'faltas']]
            df.columns = ['Disciplina', 'N1', 'N2', 'N3', 'Média', 'Faltas']
            st.dataframe(df, use_container_width=True)
            media_geral = df['Média'].mean()
            st.metric("Média Geral", f"{media_geral:.1f}", delta="Aprovado" if media_geral >= 10 else "Reprovado")
        else:
            st.info("Nenhuma nota registada.")
        st.markdown('</div>', unsafe_allow_html=True)

def ranking_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Ranking de Alunos</h1>
        <p>Os melhores alunos da escola</p>
    </div>
    """, unsafe_allow_html=True)
    
    alunos = supabase.table('usuarios').select('id, nome, classe, turma').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
    ranking_data = []
    for aluno in alunos.data:
        notas = supabase.table('notas').select('media').eq('aluno_id', aluno['id']).execute()
        media = sum(n['media'] for n in notas.data) / len(notas.data) if notas.data else 0
        ranking_data.append({"Nome": aluno['nome'], "Turma": f"{aluno.get('classe', '')} {aluno.get('turma', '')}", "Média": media})
    ranking_data.sort(key=lambda x: x['Média'], reverse=True)
    df = pd.DataFrame(ranking_data)
    medalhas = []
    for i in range(len(df)):
        if i == 0: medalhas.append("🥇 1º")
        elif i == 1: medalhas.append("🥈 2º")
        elif i == 2: medalhas.append("🥉 3º")
        else: medalhas.append(f"{i+1}º")
    df.insert(0, "Posição", medalhas)
    st.dataframe(df, use_container_width=True)
    fig = px.bar(df.head(10), x='Nome', y='Média', title="Top 10 Alunos", color='Média', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

def financeiro_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>💰 Gestão Financeira</h1>
        <p>Controle de pagamentos e receitas</p>
    </div>
    """, unsafe_allow_html=True)
    
    alunos = supabase.table('usuarios').select('*').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
    total_alunos = len(alunos.data) if alunos.data else 0
    alunos_debito = sum(1 for a in alunos.data if a.get('tem_divida', False)) if alunos.data else 0
    
    col1, col2 = st.columns(2)
    with col1: st.metric("Total de Alunos", total_alunos)
    with col2: st.metric("Alunos com Débito", alunos_debito)
    
    st.markdown("---")
    st.markdown("### 💵 Processar Pagamento")
    
    alunos_debito_list = supabase.table('usuarios').select('id, nome').eq('escola_id', escola_id).eq('nivel', 'Estudante').eq('tem_divida', True).execute()
    if alunos_debito_list.data:
        aluno_opcoes = {a['nome']: a['id'] for a in alunos_debito_list.data}
        aluno_selecionado = st.selectbox("Aluno com débito", list(aluno_opcoes.keys()), key="financeiro_aluno")
        valor = st.number_input("Valor da propina (Kz)", min_value=1000, step=5000, value=50000, key="financeiro_valor")
        if st.button("Registrar Pagamento", key="financeiro_pagar", use_container_width=True):
            aluno_id = aluno_opcoes[aluno_selecionado]
            lucro = valor * 0.02
            supabase.table('receitas').insert({"id": str(uuid.uuid4()), "aluno_id": aluno_id, "valor_pago": valor, "lucro_finax": lucro, "data_pagamento": datetime.now().isoformat()}).execute()
            supabase.table('usuarios').update({"tem_divida": False}).eq('id', aluno_id).execute()
            st.success(f"✅ Pagamento registado! Lucro FinaX: {lucro:,.2f} Kz")
            st.rerun()
    else:
        st.info("Nenhum aluno com débito pendente.")

def material_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>📚 Biblioteca Digital</h1>
        <p>Materiais didáticos disponíveis</p>
    </div>
    """, unsafe_allow_html=True)
    
    materiais = supabase.table('materiais').select('*').eq('escola_id', escola_id).execute()
    if materiais.data:
        for m in materiais.data:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{m['titulo']}**")
                    st.caption(f"📖 {m['disciplina']} | {m['tipo']}")
                with col2:
                    st.caption(m['data_upload'][:10] if m['data_upload'] else '')
                with col3:
                    st.markdown(f'<a href="{m["url_acesso"]}" target="_blank"><button style="background: #1E3A8A; color: white; border: none; border-radius: 8px; padding: 0.3rem 1rem;">🔗 Abrir</button></a>', unsafe_allow_html=True)
                st.divider()
    else:
        st.info("Nenhum material disponível.")
    
    if user['nivel'] == 'Administrador':
        with st.expander("➕ Adicionar Material"):
            with st.form("upload_material_form"):
                titulo = st.text_input("Título", key="mat_titulo")
                disciplina = st.text_input("Disciplina", key="mat_disciplina")
                tipo = st.selectbox("Tipo", ["PDF", "Link", "Vídeo"], key="mat_tipo")
                url = st.text_input("URL/Link", key="mat_url")
                if st.form_submit_button("Publicar"):
                    if titulo and disciplina and url:
                        supabase.table('materiais').insert({"id": str(uuid.uuid4()), "titulo": titulo, "disciplina": disciplina, "tipo": tipo, "url_acesso": url, "escola_id": escola_id, "data_upload": datetime.now().isoformat()}).execute()
                        st.success("Material publicado!")
                        st.rerun()
                    else:
                        st.warning("Preencha todos os campos!")

def denuncias_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>🕊️ Canal de Ética</h1>
        <p>Espaço seguro para denúncias anónimas</p>
    </div>
    """, unsafe_allow_html=True)
    
    if user['nivel'] == 'Estudante':
        st.info("🔒 A sua identidade será PRESERVADA. Use este canal com responsabilidade.")
        with st.form("denuncia_form"):
            tipo = st.selectbox("Tipo", ["Bullying", "Infraestrutura", "Assédio", "Outros"], key="den_tipo")
            titulo = st.text_input("Título", key="den_titulo")
            descricao = st.text_area("Descrição detalhada", key="den_descricao")
            if st.form_submit_button("Enviar Denúncia Anónima"):
                if titulo and descricao:
                    supabase.table('denuncias').insert({"id": str(uuid.uuid4()), "titulo": titulo, "descricao": descricao, "tipo": tipo, "status": "Pendente", "escola_id": escola_id, "data": datetime.now().isoformat()}).execute()
                    st.success("✅ Denúncia registada com sucesso!")
                else:
                    st.warning("Preencha título e descrição!")
    else:
        denuncias = supabase.table('denuncias').select('*').eq('escola_id', escola_id).order('data', desc=True).execute()
        if denuncias.data:
            df = pd.DataFrame(denuncias.data)
            df = df[['titulo', 'tipo', 'data', 'status']]
            df.columns = ['Título', 'Tipo', 'Data', 'Status']
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            st.markdown("### 📄 Detalhes da Denúncia")
            denuncia_selecionada = st.selectbox("Selecione", [d['titulo'] for d in denuncias.data], key="den_select")
            denuncia = next(d for d in denuncias.data if d['titulo'] == denuncia_selecionada)
            st.markdown(f"**Título:** {denuncia['titulo']}")
            st.markdown(f"**Tipo:** {denuncia['tipo']}")
            st.markdown(f"**Data:** {denuncia['data'][:19] if denuncia['data'] else 'N/A'}")
            st.markdown(f"**Status:** {denuncia['status']}")
            st.markdown(f"**Descrição:** {denuncia['descricao']}")
            novos_status = ["Pendente", "Em Análise", "Resolvido"]
            novo_status = st.selectbox("Alterar status", novos_status, index=novos_status.index(denuncia['status']), key="den_status")
            if novo_status != denuncia['status']:
                if st.button("Atualizar Status", key="den_update"):
                    supabase.table('denuncias').update({"status": novo_status}).eq('id', denuncia['id']).execute()
                    st.success("Status atualizado!")
                    st.rerun()
        else:
            st.info("Nenhuma denúncia registada.")

def config_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Configurações</h1>
        <p>Gerencie o seu perfil</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 👤 Meu Perfil")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nome", value=user['nome'], disabled=True, key="config_nome")
        st.text_input("Username", value=user['username'], disabled=True, key="config_username")
    with col2:
        st.text_input("Email", value=user.get('email', 'Não definido'), disabled=True, key="config_email")
        st.text_input("Telefone", value=user.get('telefone', 'Não definido'), disabled=True, key="config_telefone")
    
    if user.get('iban'):
        st.markdown("### 🏦 Dados Bancários")
        st.text_input("IBAN", value=user.get('iban', ''), disabled=True, key="config_iban")
        st.text_input("Titular", value=user.get('iban_nome', ''), disabled=True, key="config_iban_nome")
    
    st.markdown("---")
    st.markdown("### 🔑 Alterar Senha")
    nova_senha = st.text_input("Nova senha", type="password", key="nova_senha")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password", key="confirmar_senha")
    if st.button("Atualizar Senha", key="atualizar_senha"):
        if nova_senha and nova_senha == confirmar_senha:
            senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
            supabase.table('usuarios').update({"password": senha_hash}).eq('id', user['id']).execute()
            st.success("Senha alterada com sucesso!")
        else:
            st.warning("As senhas não coincidem!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================
def main():
    if not st.session_state.authenticated:
        if st.session_state.get("show_signup", False):
            signup_page()
        else:
            login_page()
    else:
        dashboard()

if __name__ == "__main__":
    main()

    # Versão corrigida - 30/03/2026