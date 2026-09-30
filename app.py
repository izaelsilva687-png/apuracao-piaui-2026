import streamlit as st
import pandas as pd
import requests

# Configuração da página e layout
st.set_page_config(
    page_title="Apuração Eleições 2026 - Piauí",
    page_icon="🗳️",
    layout="wide"
)

# Estilização do cabeçalho
st.title("🗳️ Painel de Apuração — Deputado Estadual (PI)")
st.caption("Projeção em tempo real da bancada de 30 cadeiras na Assembleia Legislativa do Piauí")

# -----------------------------------------------------------------------------
# DADOS DE SIMULAÇÃO (Substituídos pela API do TSE no dia)
# -----------------------------------------------------------------------------
DADOS_SIMULADOS = [
    {"nome": "Severo Eulálio", "partido": "MDB", "votos": 59133},
    {"nome": "Dr. Thales Coelho", "partido": "PP", "votos": 57761},
    {"nome": "Flávio Júnior", "partido": "PT", "votos": 55341},
    {"nome": "Ana Paula", "partido": "MDB", "votos": 50580},
    {"nome": "Janainna Marques", "partido": "PT", "votos": 49692},
    {"nome": "Limma", "partido": "PT", "votos": 46899},
    {"nome": "João Madison", "partido": "MDB", "votos": 43832},
    {"nome": "Gustavo Neiva", "partido": "PP", "votos": 42258},
    {"nome": "Firmino Paulo", "partido": "PT", "votos": 39854},
    {"nome": "Gracinha Mão Santa", "partido": "PP", "votos": 39515},
    {"nome": "Helio Isaias", "partido": "PT", "votos": 38984},
    {"nome": "Dr. Hélio", "partido": "MDB", "votos": 38029},
    {"nome": "Fábio Xavier", "partido": "PT", "votos": 37538},
    {"nome": "Marden Menezes", "partido": "PP", "votos": 36919},
    {"nome": "Henrique Pires", "partido": "MDB", "votos": 36407},
    {"nome": "Fábio Novo", "partido": "PT", "votos": 35510},
    {"nome": "Cel Carlos Augusto", "partido": "MDB", "votos": 34396},
    {"nome": "Nerinho", "partido": "PT", "votos": 33695},
    {"nome": "Dr. Vinicius", "partido": "PT", "votos": 33437},
    {"nome": "Wilson Brandão", "partido": "PP", "votos": 32100},
    {"nome": "Pastor Gessivaldo Isaias", "partido": "Republicanos", "votos": 29216},
    {"nome": "Rubens Vieira", "partido": "PT", "votos": 28835},
    {"nome": "Simone Pereira", "partido": "MDB", "votos": 27102},
    {"nome": "Dr. Gil Carlos", "partido": "PT", "votos": 23805},
    {"nome": "Warton Lacerda", "partido": "PT", "votos": 23454},
    {"nome": "Evaldo Gomes", "partido": "Solidariedade", "votos": 20920},
    {"nome": "Elisângela Moura", "partido": "PC do B", "votos": 20412},
    {"nome": "Hélio Rodrigues", "partido": "PT", "votos": 20231},
    {"nome": "Dr. Marcus Kalume", "partido": "PT", "votos": 19741},
    {"nome": "Elzuila Calisto", "partido": "PT", "votos": 18670},
]

# Configuração da Barra Lateral
st.sidebar.header("⚙️ Configurações da Fonte de Dados")
fonte = st.sidebar.radio("Selecione a Fonte de Dados:", ["Modo Simulação (Dados 2022)", "API Oficial do TSE (Ao Vivo)"])

pct_apurado = "100.0%"
if fonte == "Modo Simulação (Dados 2022)":
    pct = st.sidebar.slider("Simular % de Urnas Apuradas", 10, 100, 100, step=10)
    pct_apurado = f"{pct}.0%"
    df_cand = pd.DataFrame(DADOS_SIMULADOS)
    df_cand["votos"] = (df_cand["votos"] * (pct / 100)).astype(int)
else:
    url_tse = st.sidebar.text_input("URL da API do TSE", value="https://resultados.tse.jus.br/oficial/ele2026/divulgacao/oficial/pi/dados/pi-c0005-e002026-v.json")
    st.sidebar.info("Cole o link oficial do TSE no dia da eleição.")
    df_cand = pd.DataFrame(DADOS_SIMULADOS)

# -----------------------------------------------------------------------------
# CÁLCULO ELEITORAL (Quociente Eleitoral, Partidário e Sobras)
# -----------------------------------------------------------------------------
df_partidos = df_cand.groupby("partido")["votos"].sum().reset_index()
votos_validos = df_partidos["votos"].sum()
qe = max(1, int(votos_validos / 30))

df_partidos["qp_direto"] = df_partidos["votos"].apply(lambda v: int(v / qe))
df_partidos["sobras"] = 0
vagas_restantes = 30 - df_partidos["qp_direto"].sum()

for _ in range(vagas_restantes):
    maior_media = -1
    vencedor = None
    for idx, row in df_partidos.iterrows():
        if row["votos"] >= 0.80 * qe:
            media = row["votos"] / (row["qp_direto"] + row["sobras"] + 1)
            if media > maior_media:
                maior_media = media
                vencedor = row["partido"]
    if vencedor:
        df_partidos.loc[df_partidos["partido"] == vencedor, "sobras"] += 1

df_partidos["total_cadeiras"] = df_partidos["qp_direto"] + df_partidos["sobras"]

# Seleção dos Candidatos Eleitos
eleitos = []
for partido, group in df_cand.groupby("partido"):
    cand_ord = group.sort_values(by="votos", ascending=False)
    vagas = df_partidos.loc[df_partidos["partido"] == partido, "total_cadeiras"].values
    if vagas > 0:
        eleitos.append(cand_ord.head(vagas))

df_eleitos = pd.concat(eleitos).sort_values(by="votos", ascending=False).reset_index(drop=True)
df_eleitos.index += 1

# -----------------------------------------------------------------------------
# PAINEL VISUAL
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Urnas Apuradas", pct_apurado)
col2.metric("Votos Válidos", f"{votos_validos:,}".replace(",", "."))
col3.metric("Quociente Eleitoral (QE)", f"{qe:,}".replace(",", "."))
col4.metric("Total de Cadeiras", "30 Vagas")

st.markdown("---")

c_esq, c_dir = st.columns([1, 1.2])

with c_esq:
    st.subheader("📊 Divisão de Cadeiras por Partido")
    st.bar_chart(df_partidos.set_index("partido")["total_cadeiras"])
    st.dataframe(
        df_partidos.sort_values(by="total_cadeiras", ascending=False).rename(
            columns={"partido": "Partido", "votos": "Votos do Partido", "qp_direto": "Diretas", "sobras": "Sobras", "total_cadeiras": "Total Cadeiras"}
        ),
        hide_index=True,
        use_container_width=True
    )

with c_dir:
    st.subheader("🏆 30 Deputados Estaduais Projetados")
    st.dataframe(
        df_eleitos[["nome", "partido", "votos"]].rename(
            columns={"nome": "Candidato", "partido": "Partido", "votos": "Votos Individuais"}
        ),
        use_container_width=True
    )
