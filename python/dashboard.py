import ml_utils as ml
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


# ---------------- SEÇÃO MACHINE LEARNING (PROGRAMA IR ALÉM) ----------------
st.divider()
st.header("🧠 Inteligência Artificial & Análise de Solo")

aba_eda, aba_perfis, aba_ml = st.tabs([
    "📊 Análise Exploratória", 
    "🌱 Perfis Ideais de Solo", 
    "🤖 Modelagem Preditiva"
])

with aba_eda:
    st.subheader("Análise de Variáveis Orientada por Gráficos")
    st.markdown("Confira as distribuições e correlações físicas e químicas capturadas pelos sensores:")
    
    # função que gera os gráficos 
    figuras = ml.gerar_analise_exploratoria(df)
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.pyplot(figuras[0])
        st.caption("**Análise Descritiva:** Há uma clara separação na umidade quando há ocorrência de chuva, indicando forte fator preditivo.")
        st.pyplot(figuras[2])
        st.caption("**Análise Descritiva:** O mapa de calor destaca forte correlação positiva entre umidade e chuva.")
        st.pyplot(figuras[4])
        st.caption("**Análise Descritiva:** Dispersão mapeia zonas químicas ideais de pH e umidade onde ocorrem variações.")
    
    with col_g2:
        st.pyplot(figuras[1])
        st.caption("**Análise Descritiva:** O boxplot mostra que o pH do solo varia sutilmente em períodos chuvosos devido à acidez da água.")
        st.pyplot(figuras[3])
        st.caption("**Análise Descritiva:** Distribuição de Nitrogênio em relação a eventos climáticos.")

with aba_perfis:
    st.subheader("Discussão sobre o Perfil Ideal de Solo/Clima")
    st.markdown("Estudo comparativo focado em entender a resiliência e as características de 3 recortes de ambientes:")
    
    df_perfis = ml.obter_perfis_solo(df)
    st.dataframe(df_perfis, use_container_width=True)
    
    st.info(
        "💡 **Conclusão Agronômica:** Solos ricos em N+K apresentam dinâmicas distintas de retenção "
        "de umidade comparados ao perfil P+K, servindo como base técnica para mapear o ambiente ideal "
        "para diferentes tipos de cultivares."
    )

with aba_ml:
    st.subheader("Modelagem Preditiva e Avaliação de Performance")
    st.markdown("Resultados do treinamento de **5 algoritmos distintos** para previsão de eventos:")
    
    # Executa a pipeline retorna as métricas 
    df_metricas, fig_comparativa = ml.treinar_e_avaliar_modelos(df)
    
    col_m1, col_m2 = st.columns([3, 2])
    with col_m1:
        st.markdown("**Tabela Comparativa de Métricas:**")
        st.dataframe(df_metricas, use_container_width=True)
    
    with col_m2:
        st.pyplot(fig_comparativa)
        
    # Identifica o algoritmo vencedor 
    melhor_modelo = df_metricas.sort_values(by='Acurácia', ascending=False).iloc[0]['Modelo']
    st.success(f"🏆 **Conclusão:** O algoritmo com melhor performance geral para o dataset foi o **{melhor_modelo}**.")

st.success("Dashboard carregada com sucesso.")