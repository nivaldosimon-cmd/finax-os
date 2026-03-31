"""
FINAX OS - SISTEMA PROFISSIONAL DE GESTÃO ESCOLAR
VERSÃO: 5.0 ENTERPRISE - CORRIGIDA
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import uuid
import hashlib
import re
import io
import qrcode
import json
import time
from PIL import Image
from typing import Optional, Dict, List, Any, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database_config import db_config

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="FINAX OS - Gestão Escolar",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CORES
# ============================================
COLORS = {
    "primary": "#1E3A8A",
    "secondary": "#3B82F6",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "info": "#3B82F6",
    "dark": "#1F2937",
    "light": "#F9FAFB"
}

# ============================================
# ESTILOS CSS
# ============================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}
    
    .main-header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 700; }}
    .main-header p {{ font-size: 1rem; opacity: 0.9; }}
    
    .card {{
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }}
    
    .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
    
    .metric-card {{
        text-align: center;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        border-radius: 20px;
        padding: 1.2rem;
        color: white;
    }}
    
    .metric-value {{ font-size: 2.2rem; font-weight: 800; }}
    .metric-label {{ font-size: 0.9rem; opacity: 0.9; margin-top: 0.3rem; }}
    
    .stButton button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }}
    
    .stButton button:hover {{ transform: scale(1.02); box-shadow: 0 5px 15px rgba(30,58,138,0.4); }}
    
    .badge-success {{ background: {COLORS['success']}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }}
    .badge-warning {{ background: {COLORS['warning']}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }}
    .badge-danger {{ background: {COLORS['danger']}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }}
    
    .qr-container {{ background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
    .pay-link {{ background: #f0f9ff; padding: 1rem; border-radius: 10px; font-family: monospace; word-break: break-all; }}
    
    .divider {{ height: 1px; background: linear-gradient(90deg, transparent, #e5e7eb, transparent); margin: 1rem 0; }}
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def validar_email(email: str) -> bool:
    if not email: return False
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validar_telefone(telefone: str) -> bool:
    if not telefone: return False
    return telefone.isdigit() and len(telefone) == 9

def validar_username(username: str) -> bool:
    if not username: return False
    return re.match(r'^[a-zA-Z0-9._]+$', username) is not None

def validar_senha(senha: str) -> bool:
    return senha and len(senha) >= 4

def validar_bi(bi: str) -> bool:
    if not bi: return True
    return re.match(r'^\d{9,12}[A-Z]{2}\d{2}$', bi) is not None

def validar_iban(iban: str) -> bool:
    if not iban: return True
    return iban.startswith('AO') and len(iban) >= 25

def limpar_texto(texto: str) -> str:
    if not texto: return ""
    return str(texto).strip()

def validar_campos(campos: Dict[str, Any]) -> List[str]:
    return [nome for nome, valor in campos.items() if not valor or not str(valor).strip()]

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def formatar_moeda(valor: float) -> str:
    return f"{valor:,.2f} Kz"

def formatar_data(data: str) -> str:
    if not data: return "N/A"
    try:
        if 'T' in data:
            dt = datetime.fromisoformat(data)
        else:
            dt = datetime.strptime(data, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return data

def gerar_qr_code(dados: str) -> Optional[bytes]:
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(dados)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    except:
        return None

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
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

init_session_state()
supabase = st.session_state.supabase

# ============================================
# FUNÇÃO DE LOGIN
# ============================================
def fazer_login(username: str, password: str) -> Optional[Dict]:
    try:
        resultado = supabase.table('usuarios').select('*').eq('username', username.lower()).execute()
        if not resultado.data:
            return None
        usuario = resultado.data[0]
        if hash_senha(password) != usuario.get('password', ''):
            return None
        if usuario.get('status_conta') == "Bloqueada":
            return None
        return {
            "id": usuario.get('id'),
            "nome": usuario.get('nome'),
            "username": usuario.get('username'),
            "nivel": usuario.get('nivel'),
            "sub_nivel": usuario.get('sub_nivel', ''),
            "instituicao_id": usuario.get('instituicao_id'),
            "cargo": usuario.get('cargo', ''),
            "email": usuario.get('email', ''),
            "telefone": usuario.get('telefone', ''),
            "tem_divida": usuario.get('tem_divida', False),
            "qrcode_id": usuario.get('qrcode_id', '')
        }
    except Exception as e:
        return None

# ============================================
# TELA DE LOGIN
# ============================================
def login_page():
    st.markdown(f"""
    <div class="main-header">
        <h1>🏫 FINAX OS</h1>
        <p>Sistema Profissional de Gestão Escolar</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Acesso ao Sistema")
        
        username = st.text_input("Username", placeholder="Digite seu username", key="login_username_unique")
        password = st.text_input("Password", type="password", placeholder="Digite sua senha", key="login_password_unique")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🎯 Entrar", key="login_btn_unique", use_container_width=True):
                if username and password:
                    user = fazer_login(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Username ou password incorretos!")
                else:
                    st.warning("Preencha username e password!")
        with col_btn2:
            if st.button("📝 Criar Conta", key="signup_btn_unique", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# TELA DE CADASTRO DE INSTITUIÇÃO
# ============================================
def signup_instituicao():
    st.markdown(f"""
    <div class="main-header">
        <h1>🏫 Criar Nova Instituição</h1>
        <p>Escola | Universidade | Centro de Formação</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("cadastro_instituicao_form"):
        st.markdown("### 📋 Dados da Instituição")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Instituição", ["Escola", "Universidade", "Centro de Formação"], key="tipo_select")
            nome = st.text_input("Nome da Instituição", key="inst_nome")
            endereco = st.text_input("Endereço", key="inst_endereco")
        with col2:
            telefone = st.text_input("Telefone", key="inst_telefone")
            email = st.text_input("Email", key="inst_email")
            nif = st.text_input("NIF (Opcional)", placeholder="9 ou 14 dígitos", key="inst_nif")
        
        st.markdown("### 🏦 Dados Bancários")
        col1, col2 = st.columns(2)
        with col1:
            iban = st.text_input("IBAN", placeholder="AO06.0066.0000.1234.5678.9012.3", key="inst_iban")
        with col2:
            iban_nome = st.text_input("Nome do Titular da Conta", key="inst_iban_nome")
        
        st.markdown("### 👤 Dados do Administrador Principal")
        col1, col2 = st.columns(2)
        with col1:
            admin_nome = st.text_input("Nome completo", key="admin_nome")
            admin_username = st.text_input("Username", key="admin_username")
            admin_password = st.text_input("Password", type="password", key="admin_password")
        with col2:
            admin_email = st.text_input("Email", key="admin_email")
            admin_telefone = st.text_input("Telefone", key="admin_telefone")
            admin_bi = st.text_input("BI (Opcional)", placeholder="000123456LA012", key="admin_bi")
        
        submitted = st.form_submit_button("🚀 Criar Instituição", use_container_width=True)
        
        if submitted:
            nome_clean = limpar_texto(nome)
            admin_nome_clean = limpar_texto(admin_nome)
            admin_username_clean = limpar_texto(admin_username).lower()
            admin_password_clean = limpar_texto(admin_password)
            admin_email_clean = limpar_texto(admin_email)
            admin_telefone_clean = limpar_texto(admin_telefone)
            iban_clean = limpar_texto(iban)
            iban_nome_clean = limpar_texto(iban_nome)
            
            campos = {
                "Nome da Instituição": nome_clean,
                "Nome do Administrador": admin_nome_clean,
                "Username": admin_username_clean,
                "Password": admin_password_clean,
                "Email": admin_email_clean,
                "Telefone": admin_telefone_clean
            }
            
            vazios = validar_campos(campos)
            
            if vazios:
                st.error(f"❌ Campos obrigatórios não preenchidos: {', '.join(vazios)}")
            elif not validar_telefone(admin_telefone_clean):
                st.error("❌ Telefone inválido! Use 9 dígitos")
            elif not validar_email(admin_email_clean):
                st.error("❌ Email inválido!")
            elif not validar_username(admin_username_clean):
                st.error("❌ Username inválido!")
            elif not validar_senha(admin_password_clean):
                st.error("❌ Password deve ter pelo menos 4 caracteres!")
            elif admin_bi and not validar_bi(admin_bi):
                st.error("❌ BI inválido!")
            elif iban_clean and not validar_iban(iban_clean):
                st.error("❌ IBAN inválido!")
            else:
                try:
                    instituicao_id = str(uuid.uuid4())
                    dados_instituicao = {
                        "id": instituicao_id,
                        "nome": nome_clean,
                        "tipo": tipo,
                        "endereco": limpar_texto(endereco),
                        "telefone": limpar_texto(telefone),
                        "email": limpar_texto(email),
                        "nif": nif if nif else None,
                        "iban": iban_clean if iban_clean else None,
                        "iban_nome": iban_nome_clean if iban_nome_clean else None,
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table('instituicoes').insert(dados_instituicao).execute()
                    
                    admin_id = str(uuid.uuid4())
                    senha_hash = hash_senha(admin_password_clean)
                    
                    dados_admin = {
                        "id": admin_id,
                        "instituicao_id": instituicao_id,
                        "username": admin_username_clean,
                        "password": senha_hash,
                        "nivel": "Administrador",
                        "sub_nivel": "SuperAdmin",
                        "cargo": "Diretor",
                        "nome": admin_nome_clean,
                        "email": admin_email_clean,
                        "telefone": admin_telefone_clean,
                        "bi": admin_bi if admin_bi else None,
                        "status_conta": "Ativa",
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table('usuarios').insert(dados_admin).execute()
                    
                    st.success(f"✅ {tipo} criada com sucesso!")
                    st.info(f"🏛️ ID da Instituição: `{instituicao_id}`")
                    st.info(f"👤 Username: `{admin_username_clean}`")
                    st.warning("Guarde estas informações!")
                    
                    if st.button("🔐 Fazer Login Agora", key="admin_login_after_unique"):
                        st.session_state.user = dados_admin
                        st.session_state.authenticated = True
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Erro ao criar instituição: {e}")

# ============================================
# TELA DE CADASTRO (SIGNUP)
# ============================================
def signup_page():
    st.markdown(f"""
    <div class="main-header">
        <h1>📝 Criar Nova Conta</h1>
        <p>Junte-se ao FINAX OS e modernize sua instituição</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏢 Sou Administrador", "🎓 Sou Estudante"])
    
    with tab1:
        signup_instituicao()
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎓 Juntar-se a uma Instituição")
        
        instituicao_id = st.text_input("ID da Instituição", placeholder="EX: 11111111-1111-1111-1111-111111111111", key="estudante_inst_id")
        
        st.markdown("---")
        st.markdown("### 👤 Dados Pessoais")
        
        col1, col2 = st.columns(2)
        with col1:
            estudante_nome = st.text_input("Nome completo", key="estudante_nome")
            estudante_username = st.text_input("Username", key="estudante_username")
        with col2:
            estudante_password = st.text_input("Password", type="password", key="estudante_password")
            estudante_email = st.text_input("Email", key="estudante_email")
        
        estudante_telefone = st.text_input("Telefone", key="estudante_telefone")
        estudante_data = st.text_input("Data de Nascimento (dd/mm/aaaa)", key="estudante_data")
        
        st.markdown("---")
        st.markdown("### 📚 Dados Académicos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            estudante_curso = st.text_input("Curso", key="estudante_curso")
        with col2:
            estudante_ano = st.text_input("Ano/Classe", key="estudante_ano")
        with col3:
            estudante_turma = st.text_input("Turma", key="estudante_turma")
        
        st.markdown("---")
        st.markdown("### 👨‍👩‍👧 Encarregados de Educação (Opcional)")
        
        col1, col2 = st.columns(2)
        with col1:
            estudante_pai_nome = st.text_input("Nome do Pai", key="estudante_pai_nome")
            estudante_pai_telefone = st.text_input("Telefone do Pai", key="estudante_pai_telefone")
        with col2:
            estudante_mae_nome = st.text_input("Nome da Mãe", key="estudante_mae_nome")
            estudante_mae_telefone = st.text_input("Telefone da Mãe", key="estudante_mae_telefone")
        
        if st.button("📝 Cadastrar Estudante", key="estudante_register_btn", use_container_width=True):
            inst_id_clean = limpar_texto(instituicao_id)
            nome_clean = limpar_texto(estudante_nome)
            username_clean = limpar_texto(estudante_username).lower()
            password_clean = limpar_texto(estudante_password)
            email_clean = limpar_texto(estudante_email)
            telefone_clean = limpar_texto(estudante_telefone)
            curso_clean = limpar_texto(estudante_curso)
            ano_clean = limpar_texto(estudante_ano)
            turma_clean = limpar_texto(estudante_turma)
            
            campos = {
                "ID da Instituição": inst_id_clean,
                "Nome completo": nome_clean,
                "Username": username_clean,
                "Password": password_clean,
                "Email": email_clean,
                "Telefone": telefone_clean,
                "Curso": curso_clean,
                "Ano/Classe": ano_clean,
                "Turma": turma_clean
            }
            
            vazios = validar_campos(campos)
            
            if vazios:
                st.error(f"❌ Campos obrigatórios não preenchidos: {', '.join(vazios)}")
            elif not validar_telefone(telefone_clean):
                st.error("❌ Telefone inválido! Use 9 dígitos")
            elif not validar_email(email_clean):
                st.error("❌ Email inválido!")
            elif not validar_username(username_clean):
                st.error("❌ Username inválido!")
            elif not validar_senha(password_clean):
                st.error("❌ Password deve ter pelo menos 4 caracteres!")
            else:
                try:
                    instituicao_existe = supabase.table('instituicoes').select('id').eq('id', inst_id_clean).limit(1).execute()
                    if not instituicao_existe.data:
                        st.error("❌ Instituição não encontrada! Verifique o ID.")
                    else:
                        estudante_id = str(uuid.uuid4())
                        senha_hash = hash_senha(password_clean)
                        
                        ultimo = supabase.table('usuarios').select('qrcode_id').eq('instituicao_id', inst_id_clean).not_.is_('qrcode_id', 'null').order('qrcode_id', desc=True).limit(1).execute()
                        if ultimo.data and ultimo.data[0]['qrcode_id']:
                            qrcode_id = str(int(ultimo.data[0]['qrcode_id']) + 1)
                        else:
                            qrcode_id = "1001"
                        
                        dados = {
                            "id": estudante_id,
                            "instituicao_id": inst_id_clean,
                            "username": username_clean,
                            "password": senha_hash,
                            "nivel": "Estudante",
                            "cargo": f"{ano_clean} {turma_clean}",
                            "nome": nome_clean,
                            "email": email_clean,
                            "telefone": telefone_clean,
                            "especialidade": curso_clean,
                            "tem_divida": True,
                            "status_conta": "Ativa",
                            "qrcode_id": qrcode_id,
                            "data_nascimento": limpar_texto(estudante_data) or None,
                            "created_at": datetime.now().isoformat(),
                            "nome_pai": limpar_texto(estudante_pai_nome) or "",
                            "telefone_pai": limpar_texto(estudante_pai_telefone) or "",
                            "nome_mae": limpar_texto(estudante_mae_nome) or "",
                            "telefone_mae": limpar_texto(estudante_mae_telefone) or ""
                        }
                        supabase.table('usuarios').insert(dados).execute()
                        
                        st.success(f"✅ Estudante {nome_clean} cadastrado com sucesso!")
                        st.info(f"Username: {username_clean}")
                        st.info(f"QR Code ID: {qrcode_id}")
                        
                        if st.button("🔐 Fazer Login Agora", key="estudante_login_after_unique"):
                            st.session_state.user = dados
                            st.session_state.authenticated = True
                            st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar estudante: {e}")
    
    if st.button("⬅️ Voltar ao Login", key="signup_back_to_login_unique"):
        st.session_state.show_signup = False
        st.rerun()

# ============================================
# DASHBOARD ADMINISTRATIVO
# ============================================
def dashboard_admin():
    user = st.session_state.user
    instituicao_id = user.get('instituicao_id')
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 Dashboard Executivo</h1>
        <p>Visão estratégica da sua instituição</p>
        <p style="font-size: 0.8rem; margin-top: 10px;">🏛️ ID da Instituição: <strong>{instituicao_id}</strong></p>
        <p style="font-size: 0.8rem;">👤 {user['nome']} | {user['nivel']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        alunos = supabase.table('usuarios').select('*').eq('instituicao_id', instituicao_id).eq('nivel', 'Estudante').execute()
        total_alunos = len(alunos.data) if alunos.data else 0
        
        professores = supabase.table('usuarios').select('*').eq('instituicao_id', instituicao_id).eq('nivel', 'Professor').execute()
        total_professores = len(professores.data) if professores.data else 0
        
        receitas = supabase.table('receitas').select('valor').eq('instituicao_id', instituicao_id).execute()
        total_receitas = sum(r['valor'] for r in receitas.data) if receitas.data else 0
        
        despesas = supabase.table('despesas').select('valor').eq('instituicao_id', instituicao_id).eq('status', 'PAGO').execute()
        total_despesas = sum(d['valor'] for d in despesas.data) if despesas.data else 0
        
        alunos_debito = sum(1 for a in alunos.data if a.get('tem_divida', False)) if alunos.data else 0
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        presencas = supabase.table('presencas').select('*').eq('instituicao_id', instituicao_id).eq('data', hoje).execute()
        total_presencas = len(presencas.data) if presencas.data else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_alunos}</div><div class='metric-label'>👥 Alunos</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_professores}</div><div class='metric-label'>👨‍🏫 Professores</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_presencas}</div><div class='metric-label'>📍 Presenças Hoje</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{alunos_debito}</div><div class='metric-label'>⚠️ Débitos</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Receitas", formatar_moeda(total_receitas))
        with col2:
            st.metric("📉 Despesas", formatar_moeda(total_despesas))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📊 Distribuição por Turma")
            if alunos.data:
                turmas = {}
                for a in alunos.data:
                    cargo = a.get('cargo', 'N/A')
                    turmas[cargo] = turmas.get(cargo, 0) + 1
                df = pd.DataFrame(list(turmas.items()), columns=['Turma', 'Quantidade'])
                fig = px.bar(df, x='Turma', y='Quantidade', color='Quantidade', color_continuous_scale='Viridis')
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
        ultimas = supabase.table('presencas').select('*').eq('instituicao_id', instituicao_id).order('created_at', desc=True).limit(10).execute()
        if ultimas.data:
            for p in ultimas.data:
                st.markdown(f"✅ **{p.get('nome_aluno', 'Aluno')}** - Entrada registada em {formatar_data(p.get('data', 'N/A'))} às {p.get('hora_entrada', 'N/A')}")
        else:
            st.info("Nenhuma atividade recente.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")

# ============================================
# PÁGINA DO ESTUDANTE
# ============================================
def estudante_page():
    user = st.session_state.user
    instituicao_id = user.get('instituicao_id')
    aluno_id = user['id']
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🎓 Área do Estudante</h1>
        <p>Bem-vindo, {user['nome']}!</p>
        <p style="font-size: 0.8rem;">QR Code ID: {user.get('qrcode_id', 'Não definido')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Minhas Notas", "💰 FinaX Pay"])
    
    with tab1:
        st.markdown("### 📝 Boletim Escolar")
        notas = supabase.table('notas').select('*').eq('aluno_id', aluno_id).execute()
        if notas.data:
            df = pd.DataFrame(notas.data)
            df = df[['disciplina', 'trimestre', 'nota_1', 'nota_2', 'nota_3', 'prova_final', 'media', 'faltas']]
            df.columns = ['Disciplina', 'Trimestre', 'N1', 'N2', 'N3', 'Final', 'Média', 'Faltas']
            st.dataframe(df, use_container_width=True)
            media_geral = df['Média'].mean()
            st.metric("Média Geral", f"{media_geral:.1f}")
        else:
            st.info("Nenhuma nota registada.")
    
    with tab2:
        st.markdown("### 💰 FinaX Pay - Pagamentos")
        tem_divida = user.get('tem_divida', True)
        if tem_divida:
            st.warning("⚠️ Atenção: Existem pagamentos pendentes!")
        else:
            st.success("✅ Em dia! Nenhum débito pendente.")
        
        st.markdown("---")
        st.markdown("### 🔗 Gerar Pay Link")
        valor_pagamento = st.number_input("Valor a pagar (Kz)", min_value=1000, step=5000, value=50000, key="pay_link_valor")
        
        if st.button("💰 Gerar Link de Pagamento", use_container_width=True, key="gerar_pay_link_btn"):
            link_id = uuid.uuid4().hex[:8]
            pay_link = f"https://finax-os.streamlit.app/pay?aluno={aluno_id}&valor={valor_pagamento}&ref={link_id}"
            st.markdown(f"""
            <div class="pay-link">
                <strong>🔗 Seu Link de Pagamento:</strong><br>
                <code>{pay_link}</code>
            </div>
            """, unsafe_allow_html=True)
            qr_img = gerar_qr_code(pay_link)
            if qr_img:
                st.image(qr_img, caption="QR Code de Pagamento", width=200)
            st.info("💡 Instruções: 1. Escaneie o QR code ou abra o link. 2. Faça a transferência para o IBAN indicado. 3. Envie o comprovativo.")

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
        user = st.session_state.user
        nivel = user.get('nivel')
        if nivel == 'Administrador':
            dashboard_admin()
        elif nivel == 'Estudante':
            estudante_page()
        else:
            dashboard_admin()

if __name__ == "__main__":
    main()