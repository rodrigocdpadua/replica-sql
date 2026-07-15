import json
import os

import streamlit as st

# ------------------------------------------------------------------
# Configuração da página e paleta de cores da empresa
# ------------------------------------------------------------------
AZUL_MARINHO = "#2A5599"
LARANJA = "#F26B2E"
AZUL_CLARO = "#4FB3E0"

st.set_page_config(page_title="Gerador de SQL", page_icon=None, layout="wide")

st.markdown(
    f"""
    <style>
        /* Título principal */
        h1 {{
            color: {AZUL_MARINHO};
        }}

        /* Botões primários */
        .stButton > button, .stDownloadButton > button {{
            background-color: {LARANJA};
            color: white;
            border: none;
            border-radius: 6px;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: {AZUL_MARINHO};
            color: white;
        }}

        /* Barra lateral */
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
            color: #FFFFFF;
        }}

        /* Correção de alinhamento: título/label alinhado com a caixa do campo */
        div[data-testid="stWidgetLabel"] {{
            padding-left: 0rem;
            margin-left: 0rem;
        }}
        div[data-testid="stWidgetLabel"] label {{
            padding-left: 0rem;
            margin-left: 0rem;
        }}
        div[data-baseweb="input"], div[data-baseweb="select"] {{
            margin-left: 0rem;
        }}
        .stTextInput, .stMultiSelect, .stSelectbox, .stTextArea {{
            padding-left: 0rem;
            margin-left: 0rem;
        }}

        /* Destaque de seleção do multiselect com azul claro da marca */
        span[data-baseweb="tag"] {{
            background-color: {AZUL_CLARO} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Gerador de SQL")
st.caption(
    "Cole o SQL modelo usando {schema} no lugar do nome do schema. "
    "A ferramenta monta o UNION ALL para os schemas selecionados."
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "schemas_config.json")


def carregar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


if "config" not in st.session_state:
    st.session_state.config = carregar_config()

if "selecionados" not in st.session_state:
    st.session_state.selecionados = []

# ------------------------------------------------------------------
# Barra lateral: gestão de bancos de dados e schemas
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Bancos de dados e schemas")

    bancos = list(st.session_state.config.keys())

    if not bancos:
        st.info("Nenhum banco de dados cadastrado. Adicione um no arquivo schemas_config.json.")

    banco_atual = st.selectbox("Banco de dados", options=bancos) if bancos else None

# ------------------------------------------------------------------
# Área principal: montagem do SQL
# ------------------------------------------------------------------
st.subheader("1. SQL modelo")
sql_modelo = st.text_area(
    "Use {schema} onde normalmente entraria o nome do schema",
    height=180,
    placeholder=(
        "SELECT '{schema}' AS origem, t.*\n"
        "FROM {schema}.minha_tabela t\n"
        "WHERE t.data_referencia = TRUNC(SYSDATE)"
    ),
)

st.subheader("2. Escolha os schemas")

if not banco_atual:
    st.warning("Cadastre um banco de dados na barra lateral para continuar.")
else:
    schemas_disponiveis = st.session_state.config[banco_atual]

    col_a, col_b, _ = st.columns([1, 1, 3])
    with col_a:
        marcar_todos = st.button("Selecionar todos")
    with col_b:
        limpar_todos = st.button("Limpar seleção")

    if marcar_todos:
        st.session_state.selecionados = schemas_disponiveis.copy()
    if limpar_todos:
        st.session_state.selecionados = []

    selecionados = st.multiselect(
        f"Schemas de {banco_atual} que entrarão no UNION ALL",
        options=schemas_disponiveis,
        default=[s for s in st.session_state.selecionados if s in schemas_disponiveis],
    )
    st.session_state.selecionados = selecionados

    st.subheader("3. Resultado")

    if st.button("Gerar SQL", type="primary"):
        if not sql_modelo.strip():
            st.error("Cole o SQL modelo antes de gerar.")
        elif not selecionados:
            st.error("Selecione ao menos um schema.")
        elif "{schema}" not in sql_modelo:
            st.error("O SQL modelo precisa conter o marcador {schema}.")
        else:
            blocos = [sql_modelo.replace("{schema}", schema) for schema in selecionados]
            sql_final = "\n\nUNION ALL\n\n".join(blocos)

            st.success(f"SQL gerado para {len(selecionados)} schema(s) em {banco_atual}.")
            st.code(sql_final, language="sql")

            st.download_button(
                label="Baixar como .sql",
                data=sql_final,
                file_name="sql_multischema.sql",
                mime="text/plain",
            )