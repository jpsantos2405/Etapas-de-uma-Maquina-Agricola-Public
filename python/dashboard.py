import streamlit as st
import pandas as pd
import oracledb
import configparser

# ---------------- CONFIG BANCO ----------------

config = configparser.ConfigParser()
config.read("config.ini")

db_user = config.get("database", "user")
db_password = config.get("database", "password")
db_dsn = config.get("database", "dsn")

# ---------------- CONEXÃO ----------------

@st.cache_data
def carregar_dados():
    try:
        conn = oracledb.connect(
            user=db_user,
            password=db_password,
            dsn=db_dsn
        )

        query = """
            SELECT
                umidade,
                ph,
                N,
                P,
                K,
                chuva
            FROM dados_sensores
        """

        df = pd.read_sql(query, conn)
        conn.close()

        return df

    except Exception as e:
        st.error(f"Erro ao conectar no banco: {e}")
        return pd.DataFrame()


# ---------------- REGRA DE IRRIGAÇÃO ----------------

def sugestao_irrigacao(umidade, chuva):
    if chuva == "true":
        return "Não irrigar (há previsão/registro de chuva)"

    if umidade < 30:
        return "Irrigação URGENTE"

    elif umidade < 50:
        return "Irrigação recomendada"

    else:
        return "Solo com boa umidade"


# ---------------- DASHBOARD ----------------

st.set_page_config(
    page_title="Dashboard Sensores Agrícolas",
    layout="wide"
)

st.title("🌱 Dashboard de Sensores Agrícolas")

df = carregar_dados()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# padronização
df["CHUVA"] = df["CHUVA"].astype(str).str.lower()
df["N"] = df["N"].astype(str).str.lower()
df["P"] = df["P"].astype(str).str.lower()
df["K"] = df["K"].astype(str).str.lower()

# sugestão automática
df["Sugestão de Irrigação"] = df.apply(
    lambda row: sugestao_irrigacao(row["UMIDADE"], row["CHUVA"]),
    axis=1
)

# ---------------- MÉTRICAS ----------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Umidade Média", f"{df['UMIDADE'].mean():.2f}")

with col2:
    st.metric("pH Médio", f"{df['PH'].mean():.2f}")

with col3:
    total_chuva = (df["CHUVA"] == "true").sum()
    st.metric("Registros com Chuva", total_chuva)

with col4:
    irrigacao_urgente = (
        df["Sugestão de Irrigação"] == "Irrigação URGENTE"
    ).sum()
    st.metric("Irrigação Urgente", irrigacao_urgente)


st.divider()

# ---------------- GRÁFICOS ----------------

st.subheader("📊 Níveis dos Sensores")

st.line_chart(df[["UMIDADE"]])

st.line_chart(df[["PH"]])

st.subheader("🧪 Nutrientes (N, P e K)")

nutrientes = pd.DataFrame({
    "Nutriente": ["N", "P", "K"],
    "Quantidade Ativa": [
        (df["N"] == "true").sum(),
        (df["P"] == "true").sum(),
        (df["K"] == "true").sum()
    ]
})

st.bar_chart(
    nutrientes.set_index("Nutriente")
)

st.divider()

# ---------------- STATUS IRRIGAÇÃO ----------------

st.subheader("💧 Sugestões de Irrigação")

filtro = st.selectbox(
    "Filtrar por status",
    [
        "Todos",
        "Irrigação URGENTE",
        "Irrigação recomendada",
        "Solo com boa umidade",
        "Não irrigar (há previsão/registro de chuva)"
    ]
)

if filtro != "Todos":
    df = df[df["Sugestão de Irrigação"] == filtro]

st.dataframe(df, use_container_width=True)

st.success("Dashboard carregada com sucesso.")