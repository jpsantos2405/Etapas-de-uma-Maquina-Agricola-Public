import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier


def preprocessar_dados(df_bruto):
    """Padroniza as colunas e converte valores textuais para numéricos."""
    df = df_bruto.copy()
    # Força os nomes das colunas para minúsculo
    df.columns = df.columns.str.lower()

    # Tratamento de booleanos textuais para 1 e 0
    bool_cols = ['n', 'p', 'k', 'chuva']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().map({'true': 1, 'false': 0, '1': 1, '0': 0})

    return df


def gerar_analise_exploratoria(df):
    """Gera e retorna 5 figuras distintas para a rubrica."""
    figs = []
    df_clean = preprocessar_dados(df)

    # Gráfico 1: Histograma de Umidade por Chuva
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    sns.histplot(data=df_clean, x='umidade', kde=True, hue='chuva',
                 multiple='stack', palette='Blues', ax=ax1)
    ax1.set_title('Distribuição da Umidade do Solo por Chuva')
    figs.append(fig1)

    # Gráfico 2: Boxplot do pH por Chuva
    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    sns.boxplot(data=df_clean, x='chuva', y='ph', palette='Set2', ax=ax2)
    ax2.set_title('Impacto da Chuva no pH do Solo')
    ax2.set_xticklabels(['Sem Chuva', 'Com Chuva'])
    figs.append(fig2)

    # Gráfico 3: Heatmap de Correlação — FIX #1
    fig3, ax3 = plt.subplots(figsize=(6, 4.5))
    # Filtra apenas colunas numéricas para evitar erro com colunas de texto
    df_numeric = df_clean.select_dtypes(include='number')
    sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm',
                fmt='.2f', linewidths=0.5, ax=ax3)
    ax3.set_title('Matriz de Correlação das Variáveis')
    figs.append(fig3)

    # Gráfico 4: Countplot de N por Chuva
    fig4, ax4 = plt.subplots(figsize=(6, 3.5))
    sns.countplot(data=df_clean, x='n', hue='chuva', palette='viridis', ax=ax4)
    ax4.set_title('Relação entre Nitrogênio (N) e Chuva')
    ax4.set_xticklabels(['Ausente', 'Presente'])
    figs.append(fig4)

    # Gráfico 5: Dispersão Umidade vs pH
    fig5, ax5 = plt.subplots(figsize=(6, 3.5))
    sns.scatterplot(data=df_clean, x='umidade', y='ph', hue='chuva',
                    palette='deep', ax=ax5)
    ax5.set_title('Dispersão: Umidade vs pH')
    figs.append(fig5)

    return figs


def obter_perfis_solo(df):
    """Gera dados consolidados para a discussão de 3 perfis de solo/clima."""
    df_clean = preprocessar_dados(df)

    perfis = {
        "Perfil N+K (Rico em Nitrogênio e Potássio)": df_clean[(df_clean['n'] == 1) & (df_clean['k'] == 1)],
        "Perfil P+K (Rico em Fósforo e Potássio)": df_clean[(df_clean['p'] == 1) & (df_clean['k'] == 1)],
        "Perfil Geral (Média de Todo o Ecossistema)": df_clean
    }

    resumo = []
    for nome, sub_df in perfis.items():
        if not sub_df.empty:
            resumo.append({
                "Perfil": nome,
                "Umidade Média (%)": round(sub_df['umidade'].mean(), 2),
                "pH Médio": round(sub_df['ph'].mean(), 2),
                "Frequência de Chuva (%)": round(sub_df['chuva'].mean() * 100, 2)
            })

    return pd.DataFrame(resumo)


def treinar_e_avaliar_modelos(df):
    """Treina 5 algoritmos distintos e retorna o relatório e o gráfico de comparação."""
    df_clean = preprocessar_dados(df)

    # FIX #2 — Seleciona apenas as colunas originais do banco como features
    # Evita data leakage de colunas derivadas (ex: "Sugestão de Irrigação")
    feature_cols = ['umidade', 'ph', 'n', 'p', 'k']
    X = df_clean[feature_cols]
    y = df_clean['chuva']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    modelos = {
        "Regressão Logística": LogisticRegression(),
        "Árvore de Decisão": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "KNN (K-Vizinhos)": KNeighborsClassifier(n_neighbors=5)
    }

    resultados = []
    for nome, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        preds = modelo.predict(X_test)
        resultados.append({
            "Modelo": nome,
            "Acurácia": accuracy_score(y_test, preds),
            "Precisão": precision_score(y_test, preds, zero_division=0),
            "Recall": recall_score(y_test, preds, zero_division=0),
            "F1-Score": f1_score(y_test, preds, zero_division=0)
        })

    df_res = pd.DataFrame(resultados)

    # FIX #3 — Arredonda métricas para 4 casas decimais (visual mais limpo)
    for col in ['Acurácia', 'Precisão', 'Recall', 'F1-Score']:
        df_res[col] = df_res[col].round(4)

    # Gráfico de barras comparativo
    fig_comp, ax = plt.subplots(figsize=(8, 4))
    df_res.set_index('Modelo')[['Acurácia', 'F1-Score']].plot(
        kind='bar', ax=ax, color=['#3498db', '#e74c3c']
    )
    ax.set_title('Performance dos 5 Modelos de Machine Learning')
    ax.set_ylabel('Score')
    plt.xticks(rotation=30, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    return df_res, fig_comp