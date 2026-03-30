"""
FINAX OS - SISTEMA DE GESTÃO ESCOLAR
Frontend Streamlit Moderno com QR Code Visual
Versão com campos personalizáveis (Turma, Curso, ID Escola)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# CONFIGURAÇÃO DAS CREDENCIAIS
# ============================================
def get_supabase_creds():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            return url, key
    except:
        pass
    
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return url, key
    except:
        pass
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return url, key

SUPABASE_URL, SUPABASE_KEY = get_supabase_creds()

with open("temp_config.py", "w") as f:
    f.write(f"""
SUPABASE_URL = "{SUPABASE_URL}"
SUPABASE_KEY = "{SUPABASE_KEY}"
""")

from modules.database_config import db_config
from modules.super_perfil import iniciar_login_simples
from utils.qr_utils import gerar_qr_code_aluno, gerar_qr_code_pagamento, listar_qr_codes

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="FinaX OS - Gestão Escolar",
    page_icon="🏫",
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 700; }
    
    .card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 1.2rem;
        color: white;
    }
    
    .metric-value { font-size: 2.2rem; font-weight: 800; }
    .metric-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.3rem; }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }
    
    .stButton button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
    
    .badge-success { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-warning { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-danger { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    
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
        <h1>🏫 FINAX OS</h1>
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
            if st.button("🎯 Entrar", use_container_width=True):
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
            if st.button("📝 Criar Conta", use_container_width=True):
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
        <p>Junte-se ao FinaX OS e modernize sua escola</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏢 Sou Administrador", "🎓 Sou Estudante"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🏫 Criar Nova Escola")
        
        col1, col2 = st.columns(2)
        with col1:
            escola_nome = st.text_input("Nome da Escola")
            escola_endereco = st.text_input("Endereço")
        with col2:
            escola_telefone = st.text_input("Telefone")
            escola_email = st.text_input("Email da Escola")
        
        st.markdown("---")
        st.markdown("### 👤 Dados do Administrador")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo")
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
        
        telefone = st.text_input("Telefone")
        
        if st.button("🚀 Criar Escola e Conta", use_container_width=True):
            if all([escola_nome, nome, username, password, email]):
                try:
                    escola_id = f"ESC_{uuid.uuid4().hex[:8].upper()}"
                    admin_id = str(uuid.uuid4())
                    dados_admin = {
                        "id": admin_id,
                        "username": username.lower(),
                        "password": password,
                        "nivel": "Administrador",
                        "nome": nome,
                        "escola_id": escola_id,
                        "classe": "DIREÇÃO",
                        "turma": "GERAL",
                        "curso": "ADMINISTRAÇÃO",
                        "tem_divida": False,
                        "status_conta": "Ativa",
                        "email": email,
                        "telefone": telefone
                    }
                    supabase.table('usuarios').insert(dados_admin).execute()
                    st.success("✅ Conta criada com sucesso!")
                    st.info(f"🏛️ ID da Escola: `{escola_id}`")
                    st.info(f"👤 Username: `{username}`")
                    if st.button("🔐 Fazer Login Agora"):
                        st.session_state.user = dados_admin
                        st.session_state.authenticated = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("Preencha todos os campos obrigatórios!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎓 Juntar-se a uma Escola")
        
        escola_id = st.text_input("ID da Escola", placeholder="EX: ESC_ABC123 (fornecido pelo administrador)")
        
        st.markdown("---")
        st.markdown("### 👤 Dados Pessoais")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo")
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
        
        telefone = st.text_input("Telefone")
        
        st.markdown("---")
        st.markdown("### 📚 Dados Académicos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            classe = st.text_input("Classe", placeholder="Ex: 10ª, 11ª, 12ª")
        with col2:
            turma = st.text_input("Turma", placeholder="Ex: A, B, C (ou outra)")
        with col3:
            curso = st.text_input("Curso", placeholder="Ex: Ciências, Humanidades, Técnico")
        
        if st.button("📝 Cadastrar Estudante", use_container_width=True):
            if all([escola_id, nome, username, password, classe, turma, curso]):
                try:
                    estudante_id = str(uuid.uuid4())
                    dados = {
                        "id": estudante_id,
                        "username": username.lower(),
                        "password": password,
                        "nivel": "Estudante",
                        "nome": nome,
                        "escola_id": escola_id,
                        "classe": classe,
                        "turma": turma,
                        "curso": curso,
                        "tem_divida": True,
                        "status_conta": "Ativa",
                        "email": email,
                        "telefone": telefone
                    }
                    supabase.table('usuarios').insert(dados).execute()
                    st.success("✅ Cadastro realizado com sucesso!")
                    if st.button("🔐 Fazer Login Agora", key="estudante_login"):
                        st.session_state.user = dados
                        st.session_state.authenticated = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("Preencha todos os campos!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Voltar ao Login"):
        st.session_state.show_signup = False
        st.rerun()

# ============================================
# DASHBOARD PRINCIPAL (MESMO CÓDIGO ANTERIOR)
# ============================================
def dashboard():
    user = st.session_state.user
    escola_id = user['escola']
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
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
        if st.button("🚪 Sair", use_container_width=True):
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
# PÁGINA ALUNOS (COM CAMPOS PERSONALIZÁVEIS)
# ============================================
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
        df = df[['id', 'nome', 'classe', 'turma', 'curso', 'tem_divida']]
        df.columns = ['ID', 'Nome', 'Classe', 'Turma', 'Curso', 'Débito']
        df['Status'] = df['Débito'].apply(lambda x: "🔴 Débito" if x else "🟢 Em dia")
        st.dataframe(df, use_container_width=True)
        st.info(f"Total: {len(alunos.data)} alunos")
    
    with st.expander("➕ Cadastrar Novo Aluno"):
        with st.form("cadastro_aluno"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome completo")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
            with col2:
                email = st.text_input("Email")
                telefone = st.text_input("Telefone")
            
            st.markdown("---")
            st.markdown("### 📚 Dados Académicos")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                classe = st.text_input("Classe", placeholder="Ex: 10ª, 11ª, 12ª")
            with col2:
                turma = st.text_input("Turma", placeholder="Ex: A, B, C (ou outra)")
            with col3:
                curso = st.text_input("Curso", placeholder="Ex: Ciências, Humanidades, Técnico")
            
            if st.form_submit_button("Cadastrar"):
                if nome and username and password and classe and turma and curso:
                    aluno_id = str(uuid.uuid4())
                    dados = {
                        "id": aluno_id,
                        "username": username.lower(),
                        "password": password,
                        "nivel": "Estudante",
                        "nome": nome,
                        "escola_id": escola_id,
                        "classe": classe,
                        "turma": turma,
                        "curso": curso,
                        "tem_divida": True,
                        "status_conta": "Ativa",
                        "email": email,
                        "telefone": telefone
                    }
                    supabase.table('usuarios').insert(dados).execute()
                    st.success(f"✅ Aluno {nome} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos (Nome, Username, Password, Classe, Turma, Curso)!")

# ============================================
# PÁGINA RANKING (ATUALIZADA)
# ============================================
def ranking_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Ranking de Alunos</h1>
        <p>Os melhores alunos da escola</p>
    </div>
    """, unsafe_allow_html=True)
    
    alunos = supabase.table('usuarios').select('id, nome, classe, turma, curso').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
    
    ranking_data = []
    for aluno in alunos.data:
        notas = supabase.table('notas').select('media').eq('aluno_id', aluno['id']).execute()
        media = sum(n['media'] for n in notas.data) / len(notas.data) if notas.data else 0
        ranking_data.append({
            "Nome": aluno['nome'],
            "Classe": aluno.get('classe', 'N/A'),
            "Turma": aluno.get('turma', 'N/A'),
            "Curso": aluno.get('curso', 'N/A'),
            "Média": media
        })
    
    ranking_data.sort(key=lambda x: x['Média'], reverse=True)
    df = pd.DataFrame(ranking_data)
    
    medalhas = []
    for i in range(len(df)):
        if i == 0:
            medalhas.append("🥇 1º")
        elif i == 1:
            medalhas.append("🥈 2º")
        elif i == 2:
            medalhas.append("🥉 3º")
        else:
            medalhas.append(f"{i+1}º")
    
    df.insert(0, "Posição", medalhas)
    st.dataframe(df, use_container_width=True)
    
    fig = px.bar(df.head(10), x='Nome', y='Média', title="Top 10 Alunos", color='Média', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# DEMAIS PÁGINAS (MESMO CÓDIGO ANTERIOR)
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
        qr_code = st.text_input("Código QR (username do aluno)")
        if st.button("Registrar Entrada", use_container_width=True):
            if qr_code:
                aluno = supabase.table('usuarios').select('*').eq('username', qr_code).eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
                if aluno.data:
                    aluno_data = aluno.data[0]
                    agora = datetime.now()
                    hora = agora.strftime("%H:%M:%S")
                    data = agora.strftime("%Y-%m-%d")
                    status = "ATRASADO" if agora.hour > 7 or (agora.hour == 7 and agora.minute > 30) else "PRESENTE"
                    presenca_id = str(uuid.uuid4())
                    supabase.table('presencas').insert({
                        "id": presenca_id, "aluno_id": aluno_data['id'], "aluno_username": qr_code,
                        "nome_aluno": aluno_data['nome'], "escola_id": escola_id,
                        "data": data, "hora_entrada": hora, "status": status
                    }).execute()
                    if status == "PRESENTE":
                        supabase.table('usuarios').update({"total_presencas": aluno_data.get('total_presencas', 0) + 1}).eq('id', aluno_data['id']).execute()
                    else:
                        supabase.table('usuarios').update({"total_atrasos": aluno_data.get('total_atrasos', 0) + 1}).eq('id', aluno_data['id']).execute()
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
        aluno_nome = st.selectbox("Aluno", [a['nome'] for a in alunos.data])
        aluno = next(a for a in alunos.data if a['nome'] == aluno_nome)
        disciplina = st.text_input("Disciplina")
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            nota1 = st.number_input("Nota 1", min_value=0.0, max_value=20.0, step=0.5)
        with col_n2:
            nota2 = st.number_input("Nota 2", min_value=0.0, max_value=20.0, step=0.5)
        with col_n3:
            nota3 = st.number_input("Nota 3", min_value=0.0, max_value=20.0, step=0.5)
        faltas = st.number_input("Faltas", min_value=0, step=1)
        if st.button("Lançar Notas", use_container_width=True):
            if disciplina and (nota1 > 0 or nota2 > 0 or nota3 > 0):
                media = (nota1 + nota2 + nota3) / 3
                dados = {"nota_1": nota1, "nota_2": nota2, "nota_3": nota3, "faltas": faltas, "media": media, "disciplina": disciplina, "aluno_id": aluno['id'], "aluno_username": aluno['nome'].lower().replace(' ', '.'), "escola_id": escola_id}
                existente = supabase.table('notas').select('*').eq('aluno_id', aluno['id']).eq('disciplina', disciplina).execute()
                if existente.data:
                    supabase.table('notas').update(dados).eq('id', existente.data[0]['id']).execute()
                    st.success(f"✅ Notas de {disciplina} atualizadas!")
                else:
                    dados["id"] = str(uuid.uuid4())
                    supabase.table('notas').insert(dados).execute()
                    st.success(f"✅ Notas de {disciplina} lançadas!")
            else:
                st.warning("Preencha a disciplina e pelo menos uma nota!")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Boletim do Aluno")
        aluno_boletim = st.selectbox("Aluno", [a['nome'] for a in alunos.data], key="boletim")
        aluno = next(a for a in alunos.data if a['nome'] == aluno_boletim)
        notas = supabase.table('notas').select('*').eq('aluno_id', aluno['id']).execute()
        if notas.data:
            df = pd.DataFrame(notas.data)
            df = df[['disciplina', 'nota_1', 'nota_2', 'nota_3', 'media', 'faltas']]
            df.columns = ['Disciplina', 'N1', 'N2', 'N3', 'Média', 'Faltas']
            def color_media(val): return 'color: #10B981' if val >= 10 else 'color: #EF4444'
            st.dataframe(df.style.applymap(color_media, subset=['Média']), use_container_width=True)
            media_geral = df['Média'].mean()
            st.metric("Média Geral", f"{media_geral:.1f}", delta="Aprovado" if media_geral >= 10 else "Reprovado")
        else:
            st.info("Nenhuma nota registada.")
        st.markdown('</div>', unsafe_allow_html=True)

def financeiro_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>💰 Gestão Financeira</h1>
        <p>Controle de pagamentos e receitas</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "💵 Processar Pagamento", "📜 Histórico"])
    with tab1:
        alunos = supabase.table('usuarios').select('*').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
        total_alunos = len(alunos.data) if alunos.data else 0
        alunos_debito = sum(1 for a in alunos.data if a.get('tem_divida', False)) if alunos.data else 0
        col1, col2 = st.columns(2)
        with col1: st.metric("Total de Alunos", total_alunos)
        with col2: st.metric("Alunos com Débito", alunos_debito)
        receitas = supabase.table('receitas').select('*').execute()
        if receitas.data:
            total_recebido = sum(r['valor_pago'] for r in receitas.data)
            total_lucro = sum(r['lucro_finax'] for r in receitas.data)
            st.metric("Total Recebido", f"{total_recebido:,.0f} Kz")
            st.metric("Lucro FinaX (2%)", f"{total_lucro:,.0f} Kz")
    with tab2:
        alunos_debito_list = supabase.table('usuarios').select('id, nome').eq('escola_id', escola_id).eq('nivel', 'Estudante').eq('tem_divida', True).execute()
        if alunos_debito_list.data:
            aluno_opcoes = {a['nome']: a['id'] for a in alunos_debito_list.data}
            aluno_selecionado = st.selectbox("Aluno com débito", list(aluno_opcoes.keys()))
            valor = st.number_input("Valor da propina (Kz)", min_value=1000, step=5000, value=50000)
            if st.button("Registrar Pagamento", use_container_width=True):
                aluno_id = aluno_opcoes[aluno_selecionado]
                lucro = valor * 0.02
                supabase.table('receitas').insert({"id": str(uuid.uuid4()), "aluno_id": aluno_id, "valor_pago": valor, "lucro_finax": lucro, "data_pagamento": datetime.now().isoformat()}).execute()
                supabase.table('usuarios').update({"tem_divida": False}).eq('id', aluno_id).execute()
                st.success(f"✅ Pagamento registado!")
                st.info(f"💰 Lucro FinaX: {lucro:,.2f} Kz")
                st.rerun()
        else:
            st.info("Nenhum aluno com débito pendente.")
    with tab3:
        alunos_list = supabase.table('usuarios').select('id, nome').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
        if alunos_list.data:
            aluno_historico = st.selectbox("Aluno", [a['nome'] for a in alunos_list.data])
            aluno_id = next(a['id'] for a in alunos_list.data if a['nome'] == aluno_historico)
            pagamentos = supabase.table('receitas').select('*').eq('aluno_id', aluno_id).order('data_pagamento', desc=True).execute()
            if pagamentos.data:
                df = pd.DataFrame(pagamentos.data)
                df = df[['data_pagamento', 'valor_pago', 'lucro_finax']]
                df.columns = ['Data', 'Valor Pago', 'Lucro FinaX']
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum pagamento registado.")

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
                    st.markdown(f'<a href="{m["url_acesso"]}" target="_blank"><button style="background: #667eea; color: white; border: none; border-radius: 8px; padding: 0.3rem 1rem;">🔗 Abrir</button></a>', unsafe_allow_html=True)
                st.divider()
    else:
        st.info("Nenhum material disponível.")
    
    if user['nivel'] == 'Administrador':
        with st.expander("➕ Adicionar Material"):
            with st.form("upload"):
                titulo = st.text_input("Título")
                disciplina = st.text_input("Disciplina")
                tipo = st.selectbox("Tipo", ["PDF", "Link", "Vídeo"])
                url = st.text_input("URL/Link")
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
        with st.form("denuncia"):
            tipo = st.selectbox("Tipo", ["Bullying", "Infraestrutura", "Assédio", "Outros"])
            titulo = st.text_input("Título")
            descricao = st.text_area("Descrição detalhada")
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
            denuncia_selecionada = st.selectbox("Selecione", [d['titulo'] for d in denuncias.data])
            denuncia = next(d for d in denuncias.data if d['titulo'] == denuncia_selecionada)
            st.markdown(f"**Título:** {denuncia['titulo']}")
            st.markdown(f"**Tipo:** {denuncia['tipo']}")
            st.markdown(f"**Data:** {denuncia['data'][:19] if denuncia['data'] else 'N/A'}")
            st.markdown(f"**Status:** {denuncia['status']}")
            st.markdown(f"**Descrição:** {denuncia['descricao']}")
            novos_status = ["Pendente", "Em Análise", "Resolvido"]
            novo_status = st.selectbox("Alterar status", novos_status, index=novos_status.index(denuncia['status']))
            if novo_status != denuncia['status']:
                if st.button("Atualizar Status"):
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
        st.text_input("Nome", value=user['nome'], disabled=True)
        st.text_input("Username", value=user['username'], disabled=True)
    with col2:
        st.text_input("Email", value=user.get('email', 'Não definido'), disabled=True)
        st.text_input("Telefone", value=user.get('telefone', 'Não definido'), disabled=True)
    st.markdown("---")
    st.markdown("### 🔑 Alterar Senha")
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password")
    if st.button("Atualizar Senha"):
        if nova_senha and nova_senha == confirmar_senha:
            supabase.table('usuarios').update({"password": nova_senha}).eq('id', user['id']).execute()
            st.success("Senha alterada com sucesso!")
        else:
            st.warning("As senhas não coincidem!")
    st.markdown('</div>', unsafe_allow_html=True)

def qrcodes_page(user, supabase, escola_id):
    st.markdown("""
    <div class="main-header">
        <h1>📱 QR Codes</h1>
        <p>Gere QR codes visuais para alunos e pagamentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎓 QR Code do Aluno", "💰 QR Code de Pagamento", "📁 QR Codes Gerados"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎓 Gerar QR Code do Aluno")
        alunos = supabase.table('usuarios').select('id, nome, username, classe, turma').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
        if alunos.data:
            aluno_selecionado = st.selectbox("Selecione o aluno", [a['nome'] for a in alunos.data])
            aluno = next(a for a in alunos.data if a['nome'] == aluno_selecionado)
            if st.button("📱 Gerar QR Code", use_container_width=True):
                with st.spinner("Gerando QR code..."):
                    caminho = gerar_qr_code_aluno(username=aluno['username'], nome=aluno['nome'], turma=f"{aluno.get('classe', '')} {aluno.get('turma', '')}", escola_id=escola_id)
                    if os.path.exists(caminho):
                        st.markdown('<div class="qr-container">', unsafe_allow_html=True)
                        st.image(caminho, caption=f"QR Code de {aluno['nome']}", use_container_width=True)
                        st.success(f"✅ QR Code gerado para {aluno['nome']}")
                        with open(caminho, "rb") as file:
                            st.download_button(label="📥 Baixar QR Code", data=file, file_name=f"qr_{aluno['username']}.png", mime="image/png")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("Erro ao gerar QR code")
        else:
            st.info("Nenhum aluno cadastrado.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💰 Gerar QR Code de Pagamento")
        alunos = supabase.table('usuarios').select('id, nome, username').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
        if alunos.data:
            aluno_selecionado = st.selectbox("Selecione o aluno", [a['nome'] for a in alunos.data], key="pagamento_aluno")
            aluno = next(a for a in alunos.data if a['nome'] == aluno_selecionado)
            col1, col2 = st.columns(2)
            with col1:
                valor = st.number_input("Valor (Kz)", min_value=1000, step=5000, value=50000)
            with col2:
                referencia = st.text_input("Referência", value=f"REF_{datetime.now().strftime('%Y%m%d%H%M')}")
            if st.button("💳 Gerar QR Code de Pagamento", use_container_width=True):
                with st.spinner("Gerando QR code..."):
                    caminho = gerar_qr_code_pagamento(username=aluno['username'], nome=aluno['nome'], valor=valor, referencia=referencia)
                    if os.path.exists(caminho):
                        st.markdown('<div class="qr-container">', unsafe_allow_html=True)
                        st.image(caminho, caption=f"QR Code de Pagamento - {aluno['nome']}", use_container_width=True)
                        st.success(f"✅ QR Code de pagamento gerado para {aluno['nome']}")
                        with open(caminho, "rb") as file:
                            st.download_button(label="📥 Baixar QR Code de Pagamento", data=file, file_name=f"qr_pagamento_{aluno['username']}.png", mime="image/png")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("Erro ao gerar QR code")
        else:
            st.info("Nenhum aluno cadastrado.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📁 QR Codes Gerados")
        qrcodes = listar_qr_codes()
        if qrcodes:
            for qr in qrcodes:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📱 **{qr}**")
                with col2:
                    caminho = os.path.join("qrcodes", qr)
                    if os.path.exists(caminho):
                        with open(caminho, "rb") as file:
                            st.download_button(label="📥 Download", data=file, file_name=qr, mime="image/png", key=f"download_{qr}")
                st.divider()
        else:
            st.info("Nenhum QR code gerado ainda.")
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