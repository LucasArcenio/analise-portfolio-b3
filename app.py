import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import yfinance as yf
import requests
import streamlit as st

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análise de Portfólio B3",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Setores e tickers ─────────────────────────────────────────────────────────
SETORES = {
    "Financeiro": {
        "tickers": ["ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "BBSE3.SA"],
        "nomes":   {"ITUB4.SA": "Itaú", "BBDC4.SA": "Bradesco", "BBAS3.SA": "Banco do Brasil",
                    "SANB11.SA": "Santander", "BBSE3.SA": "BB Seguridade"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Aumento da volatilidade — pressão em margens de bancos", "ITUB4, BBDC4"),
            ("Inadimplência (IPCA)", "Alta de 1 p.p.", "Aumento da volatilidade — provisões sobem", "BBDC4, SANB11"),
            ("Câmbio BRL/USD", "Desvalorização 15%", "Leve aumento — impacto em carteiras dolarizadas", "ITUB4"),
        ]
    },
    "Energia Elétrica": {
        "tickers": ["ELET3.SA", "CPFE3.SA", "ENGI11.SA", "TAEE11.SA", "CMIG4.SA"],
        "nomes":   {"ELET3.SA": "Eletrobras", "CPFE3.SA": "CPFL", "ENGI11.SA": "Energisa",
                    "TAEE11.SA": "Taesa", "CMIG4.SA": "Cemig"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Redução da volatilidade — setor de dividendos se valoriza", "TAEE11, CMIG4"),
            ("Nível dos Reservatórios", "Abaixo de 30%", "Aumento da volatilidade — risco hídrico", "ELET3, CMIG4"),
            ("Regulação Aneel", "Revisão tarifária", "Aumento da volatilidade — incerteza nas margens", "ENGI11, CPFE3"),
        ]
    },
    "Petróleo e Gás": {
        "tickers": ["PETR4.SA", "PETR3.SA", "PRIO3.SA", "RECV3.SA", "UGPA3.SA"],
        "nomes":   {"PETR4.SA": "Petrobras PN", "PETR3.SA": "Petrobras ON", "PRIO3.SA": "PRIO",
                    "RECV3.SA": "PetroReconcavo", "UGPA3.SA": "Ultrapar"},
        "variaveis": [
            ("Preço do Petróleo (Brent)", "Alta de 20%", "Redução da volatilidade — receitas mais previsíveis", "PETR4, PRIO3"),
            ("Câmbio BRL/USD", "Desvalorização 15%", "Redução — receitas em USD, custos em BRL", "PETR4, RECV3"),
            ("Risco Político", "Intervenção governamental", "Aumento forte da volatilidade", "PETR4, PETR3"),
        ]
    },
    "Agronegócio e Alimentos": {
        "tickers": ["AGRO3.SA", "SLCE3.SA", "SMTO3.SA", "TTEN3.SA", "CAML3.SA"],
        "nomes":   {"AGRO3.SA": "BrasilAgro", "SLCE3.SA": "SLC Agrícola", "SMTO3.SA": "São Martinho",
                    "TTEN3.SA": "3tentos", "CAML3.SA": "Camil"},
        "variaveis": [
            ("Câmbio BRL/USD", "Desvalorização 15%", "Redução da volatilidade — exportadores ganham receita", "AGRO3, SLCE3"),
            ("Preço das Commodities", "Queda de 15%", "Aumento da volatilidade — margens comprimidas", "SLCE3, SMTO3"),
            ("El Niño / Clima", "Seca severa", "Aumento forte da volatilidade — quebra de safra", "SLCE3, TTEN3"),
        ]
    },
    "Varejo": {
        "tickers": ["MGLU3.SA", "VIVA3.SA", "SOMA3.SA", "SBFG3.SA", "LREN3.SA"],
        "nomes":   {"MGLU3.SA": "Magazine Luiza", "VIVA3.SA": "Vivara", "SOMA3.SA": "Grupo Soma",
                    "SBFG3.SA": "SBF Group", "LREN3.SA": "Lojas Renner"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Redução da volatilidade — crédito mais barato, consumo sobe", "MGLU3, LREN3"),
            ("Desemprego", "Alta de 1 p.p.", "Aumento da volatilidade — queda no consumo discricionário", "MGLU3, SOMA3"),
            ("IPCA", "Alta de 2 p.p.", "Aumento — poder de compra reduzido, inadimplência sobe", "LREN3, MGLU3"),
        ]
    },
    "Saúde e Farmácias": {
        "tickers": ["HAPV3.SA", "RDOR3.SA", "FLRY3.SA", "PNVL3.SA", "RAIA3.SA"],
        "nomes":   {"HAPV3.SA": "Hapvida", "RDOR3.SA": "Rede D'Or", "FLRY3.SA": "Fleury",
                    "PNVL3.SA": "Dimed", "RAIA3.SA": "Raia Drogasil"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Redução da volatilidade — custo de dívida de expansão cai", "HAPV3, RDOR3"),
            ("Regulação ANS", "Reajuste limitado", "Aumento da volatilidade — pressão em margens de planos", "HAPV3"),
            ("Câmbio BRL/USD", "Desvalorização 15%", "Aumento — insumos e equipamentos médicos importados", "RDOR3, FLRY3"),
        ]
    },
    "Tecnologia e Telecomunicações": {
        "tickers": ["TOTVS3.SA", "INTB3.SA", "POSI3.SA", "VIVO3.SA", "TIMS3.SA", "LWSA3.SA"],
        "nomes":   {"TOTVS3.SA": "TOTVS", "INTB3.SA": "Intelbras", "POSI3.SA": "Positivo",
                    "VIVO3.SA": "Vivo", "TIMS3.SA": "TIM", "LWSA3.SA": "Locaweb"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Redução da volatilidade — valuation de crescimento melhora", "TOTVS3, LWSA3"),
            ("Câmbio BRL/USD", "Desvalorização 15%", "Aumento — componentes importados encarecem", "INTB3, POSI3"),
            ("PIB", "Desaceleração 1 p.p.", "Aumento — empresas reduzem TI; telecom é mais resiliente", "TOTVS3, LWSA3"),
        ]
    },
    "Mineração": {
        "tickers": ["VALE3.SA", "CMIN3.SA", "CBAV3.SA", "BRAP4.SA", "FESA4.SA"],
        "nomes":   {"VALE3.SA": "Vale", "CMIN3.SA": "CSN Mineração", "CBAV3.SA": "CBA",
                    "BRAP4.SA": "Bradespar", "FESA4.SA": "Ferbasa"},
        "variaveis": [
            ("Preço do Minério de Ferro", "Queda de 20%", "Aumento forte da volatilidade — receitas caem", "VALE3, CMIN3"),
            ("Câmbio BRL/USD", "Desvalorização 15%", "Redução — exportações em USD", "VALE3, CMIN3"),
            ("Demanda China", "Desaceleração 2 p.p.", "Aumento da volatilidade — China consome ~70% do minério", "VALE3, BRAP4"),
        ]
    },
    "Saneamento e Infraestrutura": {
        "tickers": ["SAPR11.SA", "SBSP3.SA", "CSMG3.SA", "EGIE3.SA", "CCRO3.SA"],
        "nomes":   {"SAPR11.SA": "Sanepar", "SBSP3.SA": "Sabesp", "CSMG3.SA": "Copasa",
                    "EGIE3.SA": "Engie", "CCRO3.SA": "CCR"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Redução da volatilidade — ativos regulados com dividendos sobem", "SAPR11, CSMG3"),
            ("Regulação ARSESP", "Revisão tarifária negativa", "Aumento da volatilidade — margem comprimida", "SBSP3, CSMG3"),
            ("Risco Hidrológico", "Seca severa", "Aumento — custos operacionais sobem", "SAPR11, SBSP3"),
        ]
    },
    "Transportes e Logística": {
        "tickers": ["RAIL3.SA", "RDNI3.SA", "GOL4.SA", "AZUL4.SA", "ECOR3.SA"],
        "nomes":   {"RAIL3.SA": "Rumo", "RDNI3.SA": "Rodonitro", "GOL4.SA": "Gol",
                    "AZUL4.SA": "Azul", "ECOR3.SA": "EcoRodovias"},
        "variaveis": [
            ("Preço do Querosene (QAV)", "Alta de 30%", "Aumento forte da volatilidade — custo operacional das aéreas", "GOL4, AZUL4"),
            ("Câmbio BRL/USD", "Desvalorização 15%", "Aumento — dívida e leasing de aeronaves em USD", "GOL4, AZUL4"),
            ("Volume de Safra", "Queda de 10%", "Aumento — menos carga para ferrovias", "RAIL3"),
        ]
    },
}

DIAS_UTEIS = 252
DATA_INICIO = "2024-05-01"
DATA_FIM    = "2026-05-01"
CDI_FALLBACK = 0.1065

# ── Funções de métricas ───────────────────────────────────────────────────────
def retorno_acumulado(ret):   return (1 + ret).prod() - 1
def retorno_anualizado(ret):  return (1 + retorno_acumulado(ret)) ** (DIAS_UTEIS / len(ret)) - 1
def vol_anual(ret):           return ret.std() * np.sqrt(DIAS_UTEIS)
def sharpe(ret, rf):          return ((ret - rf).mean() / (ret - rf).std()) * np.sqrt(DIAS_UTEIS)
def max_dd(ret):
    curva = (1 + ret).cumprod()
    return ((curva - curva.cummax()) / curva.cummax()).min()

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados(tickers, data_inicio, data_fim):
    raw = yf.download(tickers + ["^BVSP"], start=data_inicio, end=data_fim,
                      auto_adjust=True, progress=False)
    return raw["Close"].dropna()

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_cdi():
    try:
        url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
               f"?formato=json&dataInicial=01/05/2024&dataFinal=01/05/2026")
        df = pd.DataFrame(requests.get(url, timeout=10).json())
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        serie = df.set_index("data")["valor"].astype(float) / 100
        return serie
    except:
        return None

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("📊 Análise de Portfólio B3")
st.sidebar.markdown("---")
setor_escolhido = st.sidebar.selectbox("Escolha o setor:", list(SETORES.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Período:** {DATA_INICIO} → {DATA_FIM}")
st.sidebar.markdown("**Benchmark:** IBOVESPA")
st.sidebar.markdown("**Taxa livre:** CDI (API BCB)")

info = SETORES[setor_escolhido]
tickers = info["tickers"]
nomes   = info["nomes"]

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.title(f"📈 {setor_escolhido}")
st.markdown(f"Análise de portfólio — dados de **{DATA_INICIO}** a **{DATA_FIM}**")
st.markdown("---")

# ── Carregamento de dados ─────────────────────────────────────────────────────
with st.spinner("Baixando dados do Yahoo Finance..."):
    precos_raw = buscar_dados(tickers, DATA_INICIO, DATA_FIM)

precos_raw.columns = [nomes.get(c, c) for c in precos_raw.columns]
ibov_precos = precos_raw.get("^BVSP", precos_raw.iloc[:, -1])
nomes_ativos = [nomes[t] for t in tickers if nomes[t] in precos_raw.columns]
precos = precos_raw[nomes_ativos].dropna()
ibov_precos = precos_raw["^BVSP"].dropna() if "^BVSP" in precos_raw.columns else precos_raw.iloc[:, -1].dropna()

retornos     = precos.pct_change().dropna()
ret_ibov     = ibov_precos.pct_change().dropna()
ret_ibov.name = "IBOVESPA"

# CDI
with st.spinner("Buscando CDI via Banco Central..."):
    cdi_serie = buscar_cdi()

if cdi_serie is not None:
    cdi_diario = cdi_serie.reindex(retornos.index).ffill().bfill()
    rf_diario  = cdi_diario.mean()
    cdi_anual  = (1 + cdi_diario).prod() ** (DIAS_UTEIS / len(cdi_diario)) - 1
    cdi_fonte  = f"API BCB — CDI anualizado: {cdi_anual:.2%}"
else:
    rf_diario = (1 + CDI_FALLBACK) ** (1 / DIAS_UTEIS) - 1
    cdi_anual = CDI_FALLBACK
    cdi_fonte = f"Fallback manual — CDI: {CDI_FALLBACK:.2%} a.a."

st.caption(f"💰 Taxa livre de risco: {cdi_fonte}")

# ── Etapa 1 — Estatísticas descritivas ────────────────────────────────────────
st.header("Etapa 1 — Retornos e Estatísticas")
col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Dias úteis analisados", len(retornos))
    st.metric("Ativos", len(nomes_ativos))
with col2:
    st.dataframe(
        retornos.describe().T.style.format("{:.4f}"),
        use_container_width=True
    )

# ── Etapa 2 — Volatilidade ────────────────────────────────────────────────────
st.header("Etapa 2 — Volatilidade e Variáveis Sensíveis")

vol_anualizada = retornos.std() * np.sqrt(DIAS_UTEIS)
vol_df = vol_anualizada.sort_values(ascending=False) * 100

fig_vol, ax_vol = plt.subplots(figsize=(10, 4))
cores = sns.color_palette("Reds_r", n_colors=len(vol_df))
bars = ax_vol.bar(vol_df.index, vol_df.values, color=cores, edgecolor="black", linewidth=0.5)
ax_vol.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=10)
ax_vol.set_title(f"Volatilidade Anualizada — {setor_escolhido}", fontsize=13, fontweight="bold")
ax_vol.set_ylabel("Volatilidade Anualizada (%)")
ax_vol.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
st.pyplot(fig_vol)
plt.close()

st.subheader("Variáveis Sensíveis e Cenários Prospectivos (2027)")
df_vars = pd.DataFrame(info["variaveis"],
                       columns=["Variável Sensível", "Cenário", "Efeito esperado na volatilidade", "Ativos mais impactados"])
st.dataframe(df_vars, use_container_width=True, hide_index=True)

# ── Etapa 3 — Correlação ──────────────────────────────────────────────────────
st.header("Etapa 3 — Correlação e Diversificação")

matriz_corr = retornos.corr()
fig_heat, ax_heat = plt.subplots(figsize=(8, 6))
sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap="RdYlGn",
            vmin=-1, vmax=1, center=0, linewidths=0.5, ax=ax_heat, annot_kws={"size": 10})
ax_heat.set_title(f"Matriz de Correlação — {setor_escolhido}", fontsize=13, fontweight="bold")
plt.tight_layout()
st.pyplot(fig_heat)
plt.close()

corr_pairs = (matriz_corr
              .where(np.tril(np.ones(matriz_corr.shape), k=-1).astype(bool))
              .stack()
              .sort_values())
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Menor correlação (melhor diversificação)**")
    st.dataframe(corr_pairs.head(3).to_frame("Correlação").style.format("{:.3f}"), use_container_width=True)
with col_b:
    st.markdown("**Maior correlação (menos diversificação)**")
    st.dataframe(corr_pairs.tail(3).to_frame("Correlação").style.format("{:.3f}"), use_container_width=True)

# ── Etapa 4 — Portfólios ──────────────────────────────────────────────────────
st.header("Etapa 4 — Dois Portfólios")

n = len(retornos.columns)
pesos_ewp = pd.Series({a: 1/n for a in retornos.columns})

inv_vol   = 1 / vol_anualizada
corr_med  = matriz_corr.mean()
inv_corr  = 1 / corr_med.clip(lower=0.01)
score     = np.sqrt(inv_vol * inv_corr)
pesos_B   = (score / score.sum()).round(4)
pesos_B.iloc[-1] += round(1 - pesos_B.sum(), 4)

tabela_pesos = pd.DataFrame({
    "Portfólio A — EWP": pesos_ewp.map("{:.2%}".format),
    "Portfólio B — Estratégia": pesos_B.map("{:.2%}".format),
    "Vol. Anualizada": (vol_anualizada * 100).map("{:.2f}%".format),
    "Corr. Média": corr_med.map("{:.3f}".format),
    "Justificativa": ["Sobrepeso: baixa vol/corr" if pesos_B[a] > 1/n else "Subpeso: alta vol/corr"
                      for a in retornos.columns]
})
st.dataframe(tabela_pesos, use_container_width=True)

fig_pesos, ax_pesos = plt.subplots(figsize=(10, 4))
x = np.arange(n)
w = 0.35
b1 = ax_pesos.bar(x - w/2, pesos_ewp.values * 100, w, label="Portfólio A (EWP)", color="steelblue", edgecolor="black", linewidth=0.5)
b2 = ax_pesos.bar(x + w/2, pesos_B.values * 100,   w, label="Portfólio B (Estratégia)", color="coral", edgecolor="black", linewidth=0.5)
ax_pesos.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=8)
ax_pesos.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=8)
ax_pesos.set_xticks(x)
ax_pesos.set_xticklabels(retornos.columns, fontsize=10)
ax_pesos.set_ylabel("Peso (%)")
ax_pesos.set_title(f"Comparação de Pesos — {setor_escolhido}", fontsize=13, fontweight="bold")
ax_pesos.yaxis.set_major_formatter(mtick.PercentFormatter())
ax_pesos.legend()
plt.tight_layout()
st.pyplot(fig_pesos)
plt.close()

# ── Etapa 5 — Métricas ────────────────────────────────────────────────────────
st.header("Etapa 5 — Comparação de Desempenho")

ret_A = retornos.dot(pesos_ewp)
ret_A.name = "Portfólio A (EWP)"
ret_B = retornos.dot(pesos_B)
ret_B.name = "Portfólio B (Estratégia)"
idx = ret_A.index.intersection(ret_ibov.index)
ret_A, ret_B, ibov_al = ret_A.loc[idx], ret_B.loc[idx], ret_ibov.loc[idx]

metricas = {}
for nome, serie in [("Portfólio A (EWP)", ret_A), ("Portfólio B (Estratégia)", ret_B), ("IBOVESPA", ibov_al)]:
    metricas[nome] = {
        "Retorno Acumulado":      f"{retorno_acumulado(serie):.2%}",
        "Retorno Anualizado":     f"{retorno_anualizado(serie):.2%}",
        "Volatilidade Anualizada":f"{vol_anual(serie):.2%}",
        "Sharpe Ratio (CDI)":     f"{sharpe(serie, rf_diario):.3f}",
        "Máximo Drawdown":        f"{max_dd(serie):.2%}",
    }

st.dataframe(pd.DataFrame(metricas).T, use_container_width=True)

# ── Etapa 6 — Gráfico de retorno acumulado ────────────────────────────────────
st.header("Etapa 6 — Visualizações")

curva_A    = (1 + ret_A).cumprod() - 1
curva_B    = (1 + ret_B).cumprod() - 1
curva_ibov = (1 + ibov_al).cumprod() - 1

fig_ret, ax_ret = plt.subplots(figsize=(12, 5))
ax_ret.plot(curva_A.index,    curva_A    * 100, label="Portfólio A (EWP)",        color="steelblue",  linewidth=2)
ax_ret.plot(curva_B.index,    curva_B    * 100, label="Portfólio B (Estratégia)", color="coral",      linewidth=2.5)
ax_ret.plot(curva_ibov.index, curva_ibov * 100, label="IBOVESPA",                 color="dimgray",    linewidth=1.5, linestyle="--")
ax_ret.axhline(0, color="black", linewidth=0.8, alpha=0.4)
ax_ret.fill_between(curva_B.index, curva_B * 100, curva_A * 100,
                    where=(curva_B >= curva_A), alpha=0.1, color="green")
ax_ret.fill_between(curva_B.index, curva_B * 100, curva_A * 100,
                    where=(curva_B < curva_A), alpha=0.1, color="red")
ax_ret.set_title(f"Retorno Acumulado — {setor_escolhido}", fontsize=13, fontweight="bold")
ax_ret.set_ylabel("Retorno Acumulado (%)")
ax_ret.yaxis.set_major_formatter(mtick.PercentFormatter())
ax_ret.legend(fontsize=11)
plt.tight_layout()
st.pyplot(fig_ret)
plt.close()

# ── Etapa 7 — Recomendação ────────────────────────────────────────────────────
st.header("Etapa 7 — Recomendação ao Cliente")

ra_A    = retorno_acumulado(ret_A)
ra_B    = retorno_acumulado(ret_B)
ra_ibov = retorno_acumulado(ibov_al)
sh_A    = sharpe(ret_A, rf_diario)
sh_B    = sharpe(ret_B, rf_diario)
melhor_sharpe = "Portfólio B (Estratégia)" if sh_B > sh_A else "Portfólio A (EWP)"
vs_ibov = "superou" if ra_B > ra_ibov else "ficou abaixo do"
ativo_defensivo = vol_df.index[-1]

st.info(f"""
**Relatório de Análise — {setor_escolhido}**

A estratégia de alocação do **Portfólio B** {('entregou' if sh_B > sh_A else 'não entregou')} melhor
Sharpe Ratio que o EWP ({sh_B:.3f} vs {sh_A:.3f}), indicando que a abordagem de baixa volatilidade
e baixa correlação {('melhorou' if sh_B > sh_A else 'não melhorou')} o retorno ajustado ao risco.

O setor **{vs_ibov}** o IBOVESPA no período ({ra_B:.2%} vs {ra_ibov:.2%}).

Dado o cenário prospectivo para 2027 identificado na análise de variáveis sensíveis, a exposição
ao setor deve ser avaliada considerando as variáveis descritas na Etapa 2.

Para um cliente com **perfil moderado**, destacamos o ativo **{ativo_defensivo}** como o mais
adequado, por apresentar a menor volatilidade histórica anualizada do setor ({vol_df[ativo_defensivo]:.1f}%),
combinando menor risco com potencial de retorno consistente.
""")

st.caption("Análise elaborada com dados públicos. Não constitui recomendação formal de investimento.")
