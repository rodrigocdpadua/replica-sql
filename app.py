import streamlit as st

st.set_page_config(page_title="Gerador de SQL Multi-Schema", page_icon="🗄️", layout="wide")

st.title("🗄️ Gerador de SQL Multi-Schema (Oracle)")
st.caption(
    "Cole o SQL modelo usando `{schema}` no lugar do nome do schema. "
    "A ferramenta monta o UNION ALL para os schemas selecionados."
)

# --- Lista de schemas persistida na sessão ---
if "schemas" not in st.session_state:
    st.session_state.schemas = []

with st.sidebar:
    st.header("⚙️ Schemas cadastrados")

    novo = st.text_input("Adicionar schema(s) (separe por vírgula)")
    if st.button("➕ Adicionar", use_container_width=True):
        for s in novo.split(","):
            s = s.strip().upper()
            if s and s not in st.session_state.schemas:
                st.session_state.schemas.append(s)
        st.session_state.schemas.sort()

    st.divider()

    remover = st.multiselect("Remover schema(s)", st.session_state.schemas)
    if st.button("🗑️ Remover selecionados", use_container_width=True):
        st.session_state.schemas = [s for s in st.session_state.schemas if s not in remover]

    st.divider()
    st.caption("💾 Dica: cole aqui a lista completa de uma vez, ex: SCH_SP, SCH_RJ, SCH_MG")

st.subheader("1. SQL modelo")
sql_modelo = st.text_area(
    "Use `{schema}` onde normalmente entraria o nome do schema",
    height=180,
    placeholder=(
        "SELECT '{schema}' AS origem, t.*\n"
        "FROM {schema}.minha_tabela t\n"
        "WHERE t.data_referencia = TRUNC(SYSDATE)"
    ),
)

st.subheader("2. Escolha os schemas")

col_a, col_b, col_c = st.columns([1, 1, 3])
with col_a:
    marcar_todos = st.button("✅ Selecionar todos")
with col_b:
    limpar_todos = st.button("❌ Limpar seleção")

if "selecionados" not in st.session_state:
    st.session_state.selecionados = []

if marcar_todos:
    st.session_state.selecionados = st.session_state.schemas.copy()
if limpar_todos:
    st.session_state.selecionados = []

selecionados = st.multiselect(
    "Schemas que entrarão no UNION ALL",
    options=st.session_state.schemas,
    default=st.session_state.selecionados,
    key="ms_schemas",
)
st.session_state.selecionados = selecionados

st.subheader("3. Resultado")

if st.button("🚀 Gerar SQL", type="primary"):
    if not sql_modelo.strip():
        st.error("Cole o SQL modelo antes de gerar.")
    elif not selecionados:
        st.error("Selecione ao menos um schema.")
    elif "{schema}" not in sql_modelo:
        st.error("O SQL modelo precisa conter o marcador `{schema}`.")
    else:
        blocos = [sql_modelo.replace("{schema}", schema) for schema in selecionados]
        sql_final = "\n\nUNION ALL\n\n".join(blocos)

        st.success(f"SQL gerado para {len(selecionados)} schema(s).")
        st.code(sql_final, language="sql")

        st.download_button(
            label="⬇️ Baixar como .sql",
            data=sql_final,
            file_name="sql_multischema.sql",
            mime="text/plain",
        )
