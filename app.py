import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="Apuração Eleições 2026 - Piauí", page_icon="🗳️", layout="wide"
)

# -----------------------------------------------------------------------------
# PALETA DE CORES OFICIAIS DOS PARTIDOS
# -----------------------------------------------------------------------------
CORES_PARTIDOS = {
    "PT": "#CC0000",  # Vermelho
    "MDB": "#008000",  # Laranja
    "PP": "#004080",  # Azul Claro
    "PSD": "#FF9900",  # Azul
    "PL": "#223B72",  # Azul Marinho
    "Republicanos": "#00A896",  # Verde Água
    "PV": "#2E7D32",  # Verde
    "Solidariedade": "#FF5722",  # Laranja Vivo
    "PC do B": "#8B0000",  # Vermelho Escuro
    "PSB": "#E53935",  # Vermelho Claro
    "PDT": "#1E88E5",  # Azul
    "PSOL": "#FFD600",  # Amarelo
    "UNIÃO": "#002B49",  # Azul Escuro
}

# -----------------------------------------------------------------------------
# BARRA LATERAL: SELEÇÃO DO CARGO E DA FONTE DE DADOS
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Opções da Eleição")

cargo_selecionado = st.sidebar.selectbox(
    "Selecione o Cargo:",
    ["Deputado Estadual (30 vagas)", "Deputado Federal (10 vagas)"],
)

if "Estadual" in cargo_selecionado:
  total_vagas = 30
  codigo_cargo = "c0005"
  titulo_cargo = "Deputado Estadual"
else:
  total_vagas = 10
  codigo_cargo = "c0006"
  titulo_cargo = "Deputado Federal"

st.title(f"🗳️ Painel de Apuração — {titulo_cargo} (PI)")
st.caption(
    f"Projeção em tempo real das {total_vagas} cadeiras do Piauí com base nas"
    " regras oficiais do TSE"
)

fonte = st.sidebar.radio(
    "Selecione a Fonte de Dados:",
    ["Modo Simulação (Dados 2022)", "API Oficial do TSE (Ao Vivo)"],
)

# -----------------------------------------------------------------------------
# DADOS DE SIMULAÇÃO (2022)
# -----------------------------------------------------------------------------
DADOS_ESTADUAL = [
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
]

DADOS_FEDERAL = [
    {"nome": "Wilson Martins", "partido": "PSD", "votos": 48863},
    {"nome": "Georgiano Neto", "partido": "PSD", "votos": 200863},
    {"nome": "Francisco Costa", "partido": "PT", "votos": 129229},
    {"nome": "Delegado Charles", "partido": "PV", "votos": 134863},
    {"nome": "Castro Neto", "partido": "MDB", "votos": 127753},
    {"nome": "Merlong Solano", "partido": "PT", "votos": 125774},
    {"nome": "Flávio Nogueira", "partido": "PT", "votos": 114140},
    {"nome": "Florentino Neto", "partido": "PT", "votos": 105739},
    {"nome": "Capitão Fábio Abreu", "partido": "Republicanos", "votos": 20863},
    {"nome": "Jadyel Alencar", "partido": "PV", "votos": 83175},
    {"nome": "Átila Lira", "partido": "PP", "votos": 92049},
    {"nome": "Júlio Arcoverde", "partido": "PP", "votos": 66085},
    {"nome": "Marcos Aurélio Sampaio", "partido": "PSD", "votos": 66310},
]

pct_apurado = "100.0%"
dados_base = DADOS_ESTADUAL if total_vagas == 30 else DADOS_FEDERAL

if fonte == "Modo Simulação (Dados 2022)":
  pct = st.sidebar.slider("Simular % de Urnas Apuradas", 10, 100, 100, step=10)
  pct_apurado = f"{pct}.0%"
  df_cand = pd.DataFrame(dados_base)
  df_cand["votos"] = (df_cand["votos"] * (pct / 100)).astype(int)
else:
  url_default = f"https://resultados.tse.jus.br/oficial/ele2026/6259/dados/pi/pi-{codigo_cargo}-e006259-u.json"
  url_tse = st.sidebar.text_input("URL da API do TSE", value=url_default)

  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url_tse, headers=headers, timeout=5)
    dados = res.json()
    pct_apurado = f"{dados.get('pst', '0,00')}%"
    candidatos = []
    for carg in dados.get("carg", []):
      for agr in carg.get("agr", []):
        for par in agr.get("par", []):
          partido = par.get("sg", "")
          for cand in par.get("cand", []):
            candidatos.append({
                "nome": cand.get("nmu", cand.get("nm", "")),
                "partido": partido,
                "votos": int(cand.get("vap", 0)),
            })
    df_cand = (
        pd.DataFrame(candidatos) if candidatos else pd.DataFrame(dados_base)
    )
  except Exception:
    st.sidebar.warning("Aguardando transmissão oficial do TSE...")
    df_cand = pd.DataFrame(dados_base)

# -----------------------------------------------------------------------------
# CÁLCULO ELEITORAL
# -----------------------------------------------------------------------------
df_partidos = df_cand.groupby("partido")["votos"].sum().reset_index()
votos_validos = df_partidos["votos"].sum()
qe = max(1, int(votos_validos / total_vagas))

df_partidos["qp_direto"] = df_partidos["votos"].apply(lambda v: int(v / qe))
df_partidos["sobras"] = 0
vagas_restantes = total_vagas - df_partidos["qp_direto"].sum()

if vagas_restantes > 0:
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

df_partidos["total_cadeiras"] = (
    df_partidos["qp_direto"] + df_partidos["sobras"]
)

# Seleção dos Candidatos Eleitos
eleitos = []
for partido, group in df_cand.groupby("partido"):
  cand_ord = group.sort_values(by="votos", ascending=False)
  vagas_vals = df_partidos.loc[
      df_partidos["partido"] == partido, "total_cadeiras"
  ].values
  vagas_num = int(vagas_vals[0]) if len(vagas_vals) > 0 else 0
  if vagas_num > 0:
    eleitos.append(cand_ord.head(vagas_num))

if eleitos:
  df_eleitos = (
      pd.concat(eleitos)
      .sort_values(by="votos", ascending=False)
      .reset_index(drop=True)
  )
  df_eleitos.index += 1
else:
  df_eleitos = pd.DataFrame(columns=["nome", "partido", "votos"])

# -----------------------------------------------------------------------------
# PAINEL VISUAL
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Urnas Apuradas", pct_apurado)
col2.metric("Votos Válidos", f"{votos_validos:,}".replace(",", "."))
col3.metric("Quociente Eleitoral (QE)", f"{qe:,}".replace(",", "."))
col4.metric("Cadeiras em Disputa", f"{total_vagas} Vagas")

st.markdown("---")

col_grafico, col_tabela = st.columns([1, 1.2])

with col_grafico:
  st.subheader(f"📊 Cadeiras de {titulo_cargo} por Partido")

  # Gráfico Colorido com Plotly
  df_partidos_ord = df_partidos.sort_values(
      by="total_cadeiras", ascending=False
  )

  fig = px.bar(
      df_partidos_ord,
      x="partido",
      y="total_cadeiras",
      color="partido",
      color_discrete_map=CORES_PARTIDOS,
      text="total_cadeiras",
      labels={"partido": "Partido", "total_cadeiras": "Cadeiras"},
  )
  fig.update_traces(textposition="outside")
  fig.update_layout(
      showlegend=False,
      xaxis_title="",
      yaxis_title="Nº de Cadeiras",
      height=380,
  )

  st.plotly_chart(fig, use_container_width=True)

  st.dataframe(
      df_partidos_ord.rename(
          columns={
              "partido": "Partido",
              "votos": "Votos do Partido",
              "qp_direto": "Diretas",
              "sobras": "Sobras",
              "total_cadeiras": "Total Cadeiras",
          }
      ),
      hide_index=True,
      use_container_width=True,
  )

with col_tabela:
  st.subheader(f"🏆 {total_vagas} Deputados Projetados")
  st.dataframe(
      df_eleitos[["nome", "partido", "votos"]].rename(
          columns={
              "nome": "Candidato",
              "partido": "Partido",
              "votos": "Votos Individuais",
          }
      ),
      use_container_width=True,
  )
