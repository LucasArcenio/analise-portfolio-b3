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

st.set_page_config(
    page_title="B3 Research",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; }
[data-testid="stSidebar"] hr { border-color: #334155; }

/* Cards de métricas */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 0.78rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border: 1px solid #1e40af;
    border-radius: 20px;
    padding: 60px 48px;
    margin-bottom: 32px;
    text-align: center;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0 0 12px 0;
    letter-spacing: -1px;
}
.hero p {
    font-size: 1.2rem;
    color: #94a3b8;
    margin: 0 0 32px 0;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}
.badge {
    display: inline-block;
    background: #1e40af22;
    border: 1px solid #3b82f6;
    color: #93c5fd;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    margin: 0 4px 8px 4px;
}

/* Chips de exemplos */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 16px; }
.chip {
    background: #0f2744;
    border: 1px solid #1e40af;
    color: #60a5fa;
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
}

/* Seção header */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #1e40af;
}
.section-header h2 {
    color: #f1f5f9;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0;
}

/* Company header card */
.company-card {
    background: linear-gradient(135deg, #0f2744, #1e293b);
    border: 1px solid #1e40af;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.company-name { color: #f8fafc; font-size: 1.8rem; font-weight: 700; }
.company-ticker { color: #60a5fa; font-size: 1rem; font-weight: 600; }
.company-price { color: #34d399; font-size: 2rem; font-weight: 700; }
.company-date { color: #94a3b8; font-size: 0.85rem; }

/* Tabela customizada */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #334155, transparent);
    margin: 32px 0;
}

/* Info box */
.info-box {
    background: #0f2744;
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    color: #93c5fd;
    font-size: 0.95rem;
    margin: 16px 0;
}

/* Setor card */
.setor-title {
    background: linear-gradient(135deg, #0f2744, #1e293b);
    border: 1px solid #1e40af;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.setor-title h2 { color: #f8fafc; font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0; }
.setor-title p { color: #94a3b8; margin: 0; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Dados ─────────────────────────────────────────────────────────────────────
SETORES = {
    "Financeiro": {
        "tickers": ["ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "BBSE3.SA"],
        "nomes":   {"ITUB4.SA": "Itaú", "BBDC4.SA": "Bradesco", "BBAS3.SA": "Banco do Brasil",
                    "SANB11.SA": "Santander", "BBSE3.SA": "BB Seguridade"},
        "variaveis": [
            ("Taxa Selic", "Queda de 2 p.p.", "Aumento da volatilidade — pressão em margens de bancos", "ITUB4, BBDC4"),
            ("Inadimplência", "Alta de 1 p.p.", "Aumento da volatilidade — provisões sobem", "BBDC4, SANB11"),
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

DIAS_UTEIS   = 252
CDI_FALLBACK = 0.1065

from datetime import date, timedelta
DATA_FIM    = date.today().strftime("%Y-%m-%d")
DATA_INICIO = (date.today() - timedelta(days=730)).strftime("%Y-%m-%d")

# ── Funções ───────────────────────────────────────────────────────────────────
def retorno_acumulado(ret):   return (1 + ret).prod() - 1
def retorno_anualizado(ret):  return (1 + retorno_acumulado(ret)) ** (DIAS_UTEIS / len(ret)) - 1
def vol_anual(ret):           return ret.std() * np.sqrt(DIAS_UTEIS)
def sharpe(ret, rf):          return ((ret - rf).mean() / (ret - rf).std()) * np.sqrt(DIAS_UTEIS)
def max_dd(ret):
    curva = (1 + ret).cumprod()
    return ((curva - curva.cummax()) / curva.cummax()).min()

def fmt_bi(v):
    try:
        n = float(v)
        if abs(n) >= 1e9: return f"R$ {n/1e9:.2f} bi"
        if abs(n) >= 1e6: return f"R$ {n/1e6:.2f} mi"
        return f"R$ {n:,.0f}"
    except: return "—"

def pct(v):
    try:    return f"{float(v)*100:.2f}%"
    except: return "—"

def num(v, dec=2):
    try:    return f"{float(v):.{dec}f}"
    except: return "—"

@st.cache_data(ttl=900, show_spinner=False)  # cache de 15 min — mesma latência do Google Finance
def buscar_dados(tickers, data_inicio, data_fim):
    # Usa period="2y" para garantir dados sempre até hoje, ignorando end date
    raw = yf.download(tickers + ["^BVSP"], period="2y",
                      auto_adjust=True, progress=False)
    close = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = close.columns.get_level_values(-1)
    return close.dropna(how="all")

@st.cache_data(ttl=300, show_spinner=False)  # cache de 5 min para cotação ao vivo
def cotacao_ao_vivo(ticker_sa):
    try:
        fi = yf.Ticker(ticker_sa).fast_info
        return {
            "preco":        round(float(fi.last_price), 2),
            "abertura":     round(float(fi.open), 2),
            "maxima":       round(float(fi.day_high), 2),
            "minima":       round(float(fi.day_low), 2),
            "volume":       int(fi.last_volume),
            "fechamento":   round(float(fi.previous_close), 2),
        }
    except:
        return None

@st.cache_data(ttl=86400, show_spinner=False)  # cache de 24h
def buscar_cdi(data_inicio, data_fim):
    try:
        di = pd.to_datetime(data_inicio).strftime("%d/%m/%Y")
        df_ = pd.to_datetime(data_fim).strftime("%d/%m/%Y")
        url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
               f"?formato=json&dataInicial={di}&dataFinal={df_}")
        df = pd.DataFrame(requests.get(url, timeout=10).json())
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        return df.set_index("data")["valor"].astype(float) / 100
    except:
        return None

def section(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <span style="font-size:1.4rem">{icon}</span>
        <h2>{title}</h2>
    </div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 B3 Research")
    st.markdown("<hr style='border-color:#334155;margin:8px 0 16px'>", unsafe_allow_html=True)
    modo = st.radio("", ["🏠  Início", "🔍  Empresa", "📂  Setor"], label_visibility="collapsed")
    st.markdown("<hr style='border-color:#334155;margin:16px 0 12px'>", unsafe_allow_html=True)
    st.markdown(f"<small style='color:#64748b'>Dados: Yahoo Finance · BCB<br>Período: últimos 2 anos · Atualizado diariamente</small>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA INICIAL
# ══════════════════════════════════════════════════════════════════════════════
if "Início" in modo:
    st.markdown("""
    <div class="hero">
        <h1>📊 B3 Research</h1>
        <p>Pesquise informações fundamentalistas e técnicas de qualquer empresa listada na Bolsa brasileira</p>
        <div>
            <span class="badge">Análise Fundamentalista</span>
            <span class="badge">Histórico de Dividendos</span>
            <span class="badge">Retorno vs IBOVESPA</span>
            <span class="badge">Portfólio por Setor</span>
        </div>
        <div class="chip-row">
            <span class="chip">PETR4</span>
            <span class="chip">VALE3</span>
            <span class="chip">ITUB4</span>
            <span class="chip">BBDC4</span>
            <span class="chip">WEGE3</span>
            <span class="chip">MGLU3</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px">
        <div style="font-size:2rem;margin-bottom:8px">🔍</div>
        <h3 style="color:#f1f5f9;margin:0 0 8px">Empresa Individual</h3>
        <p style="color:#94a3b8;font-size:0.9rem;margin:0">
        Digite qualquer ticker da B3 e veja indicadores fundamentalistas, balanço, dividendos e análise técnica completa.
        </p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px">
        <div style="font-size:2rem;margin-bottom:8px">📂</div>
        <h3 style="color:#f1f5f9;margin:0 0 8px">Análise por Setor</h3>
        <p style="color:#94a3b8;font-size:0.9rem;margin:0">
        Escolha um dos 10 setores da B3 e compare portfólios, correlação, volatilidade e desempenho histórico.
        </p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px">
        <div style="font-size:2rem;margin-bottom:8px">📈</div>
        <h3 style="color:#f1f5f9;margin:0 0 8px">Benchmarking</h3>
        <p style="color:#94a3b8;font-size:0.9rem;margin:0">
        Todos os resultados são comparados ao IBOVESPA e à taxa CDI como referências de mercado.
        </p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;text-align:center;font-size:0.85rem'>Selecione um modo na barra lateral para começar · Dados com fins educacionais · Não constitui recomendação de investimento</p>",
                unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# EMPRESA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════
if "Empresa" in modo:
    st.markdown("""
    <div style="margin-bottom:24px">
        <h1 style="color:#f8fafc;font-size:2rem;font-weight:700;margin:0 0 4px">🔍 Pesquisar Empresa</h1>
        <p style="color:#94a3b8;margin:0">Análise fundamentalista e técnica de qualquer ação da B3</p>
    </div>""", unsafe_allow_html=True)

    ticker_input = st.text_input(
        "", placeholder="Digite o ticker — ex: PETR4, VALE3, ITUB4, WEGE3...",
        label_visibility="collapsed"
    ).strip().upper()

    if not ticker_input:
        st.markdown("""
        <div class="info-box">
            💡 <strong>Exemplos de tickers:</strong> PETR4 (Petrobras), VALE3 (Vale), ITUB4 (Itaú),
            WEGE3 (WEG), BBDC4 (Bradesco), MGLU3 (Magazine Luiza), RENT3 (Localiza)
        </div>""", unsafe_allow_html=True)
        st.stop()

    ticker_sa = ticker_input if ticker_input.endswith(".SA") else ticker_input + ".SA"

    with st.spinner(f"Carregando {ticker_input}..."):
        try:
            _raw = yf.download([ticker_sa, "^BVSP"], period="2y",
                               auto_adjust=True, progress=False)
            raw_ind = _raw["Close"] if "Close" in _raw.columns.get_level_values(0) else _raw
            if isinstance(raw_ind.columns, pd.MultiIndex):
                raw_ind.columns = raw_ind.columns.get_level_values(-1)
            raw_ind = raw_ind.dropna(how="all")
        except Exception as e:
            st.error(f"Erro ao buscar preços: {e}")
            st.stop()
        yf_ticker  = yf.Ticker(ticker_sa)
        info_yf    = yf_ticker.info or {}
        vivo       = cotacao_ao_vivo(ticker_sa)

    if ticker_sa not in raw_ind.columns or raw_ind[ticker_sa].dropna().empty:
        st.error(f"Ticker **{ticker_input}** não encontrado. Verifique o código.")
        st.stop()

    preco_ind  = raw_ind[ticker_sa].dropna()
    preco_ibov = raw_ind["^BVSP"].dropna()
    ret_ind    = preco_ind.pct_change().dropna()
    ret_ib     = preco_ibov.pct_change().dropna()
    idx_i      = ret_ind.index.intersection(ret_ib.index)
    ret_ind, ret_ib = ret_ind.loc[idx_i], ret_ib.loc[idx_i]

    cdi_s = buscar_cdi(DATA_INICIO, DATA_FIM)
    if cdi_s is not None and len(cdi_s) > 0:
        _cdi_al = cdi_s.reindex(ret_ind.index).ffill().bfill().dropna()
        rf_i = _cdi_al.mean() if len(_cdi_al) > 0 else (1 + CDI_FALLBACK) ** (1 / DIAS_UTEIS) - 1
    else:
        rf_i = (1 + CDI_FALLBACK) ** (1 / DIAS_UTEIS) - 1

    nome_empresa  = info_yf.get("shortName") or info_yf.get("longName") or ticker_input

    # Cotação ao vivo tem prioridade; fallback para último fechamento histórico
    if vivo and vivo["preco"] > 0:
        cotacao_atual = vivo["preco"]
        var_dia       = (vivo["preco"] / vivo["fechamento"] - 1) * 100 if vivo["fechamento"] else 0
        preco_label   = "Tempo real (15min delay)"
    else:
        cotacao_atual = preco_ind.iloc[-1]
        var_dia       = ret_ind.iloc[-1] * 100
        preco_label   = f"Fechamento {preco_ind.index[-1].date()}"

    cor_var = "#34d399" if var_dia >= 0 else "#f87171"
    sinal   = "▲" if var_dia >= 0 else "▼"

    # Company card
    st.markdown(f"""
    <div class="company-card">
        <div>
            <div class="company-name">{nome_empresa}</div>
            <div class="company-ticker">{ticker_input} · B3</div>
            <div class="company-date" style="margin-top:4px">{preco_label}</div>
        </div>
        <div style="text-align:right">
            <div class="company-price">R$ {cotacao_atual:.2f}</div>
            <div style="color:{cor_var};font-size:1rem;font-weight:600">{sinal} {abs(var_dia):.2f}% no dia</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Dados intraday do dia
    if vivo:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Abertura",       f"R$ {vivo['abertura']:.2f}")
        c2.metric("Máxima do dia",  f"R$ {vivo['maxima']:.2f}")
        c3.metric("Mínima do dia",  f"R$ {vivo['minima']:.2f}")
        c4.metric("Fechamento ant.", f"R$ {vivo['fechamento']:.2f}")
        vol = vivo['volume']
        vol_fmt = f"{vol/1e6:.1f}M" if vol >= 1e6 else f"{vol/1e3:.0f}K"
        c5.metric("Volume",         vol_fmt)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Indicadores fundamentalistas ─────────────────────────────────────────
    section("📊", "Indicadores Fundamentalistas")

    st.markdown("**Valuation**")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("P/L",         num(info_yf.get("trailingPE")))
    c2.metric("P/VP",        num(info_yf.get("priceToBook")))
    c3.metric("EV/EBITDA",   num(info_yf.get("enterpriseToEbitda")))
    dy_raw = float(info_yf.get("dividendYield") or 0)
    dy_val = dy_raw / 100 if dy_raw > 1 else dy_raw  # normaliza para decimal
    c4.metric("Div. Yield",  pct(dy_val))
    c5.metric("LPA",         f"R$ {num(info_yf.get('trailingEps'))}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Rentabilidade**")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("ROE",            pct(info_yf.get("returnOnEquity")))
    c2.metric("ROA",            pct(info_yf.get("returnOnAssets")))
    c3.metric("Margem Líquida", pct(info_yf.get("profitMargins")))
    c4.metric("Margem EBITDA",  pct(info_yf.get("ebitdaMargins")))
    c5.metric("Margem Bruta",   pct(info_yf.get("grossMargins")))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Saúde Financeira**")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Dívida/PL",        num(info_yf.get("debtToEquity")))
    c2.metric("Liquidez Corr.",    num(info_yf.get("currentRatio")))
    c3.metric("Liquidez Rápida",   num(info_yf.get("quickRatio")))
    c4.metric("Cres. Receita",     pct(info_yf.get("revenueGrowth")))
    c5.metric("Valor de Mercado",  fmt_bi(info_yf.get("marketCap")))

    # Balanço + DRE
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**DRE — últimos 12 meses**")
        st.table(pd.DataFrame({
            "Receita Líquida": [fmt_bi(info_yf.get("totalRevenue"))],
            "EBITDA":          [fmt_bi(info_yf.get("ebitda"))],
            "Lucro Líquido":   [fmt_bi(info_yf.get("netIncomeToCommon"))],
        }).T.rename(columns={0: "Valor"}))
    with col_b:
        st.markdown("**Estrutura de Capital**")
        st.table(pd.DataFrame({
            "Dívida Total":          [fmt_bi(info_yf.get("totalDebt"))],
            "Caixa e Equivalentes":  [fmt_bi(info_yf.get("totalCash"))],
            "Valor Patrimonial/ação":[f"R$ {num(info_yf.get('bookValue'))}"],
        }).T.rename(columns={0: "Valor"}))

    # DRE trimestral
    st.markdown("**DRE Trimestral**")
    try:
        qfin = yf_ticker.quarterly_financials
        if qfin is not None and not qfin.empty:
            linhas_pt = {
                "Total Revenue": "Receita Líquida",
                "EBITDA": "EBITDA",
                "Net Income": "Lucro Líquido",
                "Net Income Common Stockholders": "Lucro Líquido",
            }
            presentes = [l for l in linhas_pt if l in qfin.index]
            # remove duplicatas mantendo a primeira ocorrência de cada tradução
            vistas = set(); presentes_uniq = []
            for l in presentes:
                if linhas_pt[l] not in vistas:
                    presentes_uniq.append(l); vistas.add(linhas_pt[l])
            qfin_f = qfin.loc[presentes_uniq, qfin.columns[:4]]
            qfin_f.index = [linhas_pt[i] for i in qfin_f.index]
            qfin_f.columns = [str(c)[:10] for c in qfin_f.columns]
            st.dataframe(qfin_f.map(lambda v: fmt_bi(v) if pd.notna(v) else "—"),
                         use_container_width=True)
        else:
            st.info("DRE trimestral não disponível.")
    except Exception:
        st.info("DRE trimestral não disponível.")

    # ── Dividendos ────────────────────────────────────────────────────────────
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    section("💰", "Histórico de Dividendos")

    try:
        divs = yf_ticker.dividends
        if divs is not None and len(divs) > 0:
            divs.index = divs.index.tz_convert(None) if divs.index.tz is not None else divs.index
            div_12m = divs[divs.index >= (divs.index[-1] - pd.DateOffset(years=1))].sum()
            dy_calc = div_12m / cotacao_atual * 100 if cotacao_atual > 0 else 0
            n_pag   = len(divs[divs.index >= (divs.index[-1] - pd.DateOffset(years=1))])

            c1, c2, c3 = st.columns(3)
            c1.metric("Total pago (12 meses)",  f"R$ {div_12m:.4f}")
            c2.metric("Dividend Yield",          f"{dy_calc:.2f}%")
            c3.metric("Pagamentos (12 meses)",   str(n_pag))

            divs_graf = divs[divs.index >= pd.Timestamp("2022-01-01")]
            fig_div, ax_div = plt.subplots(figsize=(12, 3.5))
            fig_div.patch.set_facecolor("#0f172a")
            ax_div.set_facecolor("#0f172a")
            ax_div.bar(divs_graf.index, divs_graf.values, color="#34d399", alpha=0.85, width=20)
            ax_div.set_title(f"Dividendos Pagos — {ticker_input}", fontsize=13, fontweight="bold", color="#f1f5f9")
            ax_div.set_ylabel("R$/ação", color="#94a3b8")
            ax_div.tick_params(colors="#94a3b8")
            for spine in ax_div.spines.values(): spine.set_edgecolor("#334155")
            plt.tight_layout()
            st.pyplot(fig_div)
            plt.close()
        else:
            st.info("Nenhum dividendo registrado para este ativo.")
    except Exception as e:
        st.warning(f"Histórico de dividendos indisponível: {e}")

    # ── Análise técnica ───────────────────────────────────────────────────────
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    section("📈", "Análise Técnica")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Retorno Acumulado",  f"{retorno_acumulado(ret_ind):.2%}")
    c2.metric("Retorno Anualizado", f"{retorno_anualizado(ret_ind):.2%}")
    c3.metric("Volatilidade Anual", f"{vol_anual(ret_ind):.2%}")
    c4.metric("Sharpe (CDI)",       f"{sharpe(ret_ind, rf_i):.3f}")
    c5.metric("Máx. Drawdown",      f"{max_dd(ret_ind):.2%}")

    curva_ind = (1 + ret_ind).cumprod() - 1
    curva_ib  = (1 + ret_ib).cumprod()  - 1

    def dark_fig(w=12, h=4.5):
        fig, ax = plt.subplots(figsize=(w, h))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors="#94a3b8")
        for sp in ax.spines.values(): sp.set_edgecolor("#334155")
        return fig, ax

    fig_i, ax_i = dark_fig()
    ax_i.plot(curva_ind.index, curva_ind * 100, label=ticker_input, color="#60a5fa", linewidth=2.5)
    ax_i.plot(curva_ib.index,  curva_ib  * 100, label="IBOVESPA",   color="#94a3b8", linewidth=1.5, linestyle="--")
    ax_i.axhline(0, color="#475569", linewidth=0.8)
    ax_i.fill_between(curva_ind.index, curva_ind*100, curva_ib*100,
                      where=(curva_ind >= curva_ib), alpha=0.12, color="#34d399")
    ax_i.fill_between(curva_ind.index, curva_ind*100, curva_ib*100,
                      where=(curva_ind < curva_ib),  alpha=0.12, color="#f87171")
    ax_i.set_title(f"Retorno Acumulado — {ticker_input} vs IBOVESPA", fontsize=13, fontweight="bold", color="#f1f5f9")
    ax_i.set_ylabel("Retorno Acumulado (%)", color="#94a3b8")
    ax_i.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax_i.legend(fontsize=11, facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0")
    plt.tight_layout()
    st.pyplot(fig_i); plt.close()

    curva_p  = (1 + ret_ind).cumprod()
    dd_serie = (curva_p - curva_p.cummax()) / curva_p.cummax() * 100
    fig_dd, ax_dd = dark_fig(12, 3)
    ax_dd.fill_between(dd_serie.index, dd_serie.values, 0, color="#f87171", alpha=0.4)
    ax_dd.plot(dd_serie.index, dd_serie.values, color="#f87171", linewidth=1)
    ax_dd.set_title(f"Drawdown — {ticker_input}", fontsize=13, fontweight="bold", color="#f1f5f9")
    ax_dd.set_ylabel("Drawdown (%)", color="#94a3b8")
    ax_dd.yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.tight_layout()
    st.pyplot(fig_dd); plt.close()

    fig_h, ax_h = dark_fig(10, 4)
    ax_h.hist(ret_ind * 100, bins=60, color="#3b82f6", edgecolor="#0f172a", linewidth=0.3, alpha=0.85)
    ax_h.axvline(ret_ind.mean()*100, color="#34d399", linestyle="--", linewidth=2,
                 label=f"Média: {ret_ind.mean()*100:.3f}%")
    ax_h.axvline(0, color="#94a3b8", linewidth=1, alpha=0.6)
    ax_h.set_title(f"Distribuição de Retornos Diários — {ticker_input}", fontsize=13, fontweight="bold", color="#f1f5f9")
    ax_h.set_xlabel("Retorno Diário (%)", color="#94a3b8")
    ax_h.set_ylabel("Frequência", color="#94a3b8")
    ax_h.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax_h.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0")
    plt.tight_layout()
    st.pyplot(fig_h); plt.close()

    st.markdown("<p style='color:#475569;font-size:0.8rem;text-align:center;margin-top:24px'>Fontes: Yahoo Finance · Banco Central do Brasil · Não constitui recomendação de investimento</p>",
                unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISE POR SETOR
# ══════════════════════════════════════════════════════════════════════════════
setor_escolhido = st.sidebar.selectbox("Setor:", list(SETORES.keys()))
info_setor = SETORES[setor_escolhido]
tickers    = info_setor["tickers"]
nomes      = info_setor["nomes"]

st.markdown(f"""
<div class="setor-title">
    <h2>📂 {setor_escolhido}</h2>
    <p>Análise de portfólio · últimos 2 anos · Atualizado em {DATA_FIM} · Benchmark: IBOVESPA</p>
</div>""", unsafe_allow_html=True)

with st.spinner("Baixando dados..."):
    precos_raw = buscar_dados(tickers, DATA_INICIO, DATA_FIM)

precos_raw.columns = [nomes.get(c, c) for c in precos_raw.columns]
nomes_ativos = [nomes[t] for t in tickers if nomes[t] in precos_raw.columns]
precos       = precos_raw[nomes_ativos].dropna()
ibov_precos  = precos_raw["^BVSP"].dropna() if "^BVSP" in precos_raw.columns else precos_raw.iloc[:, -1].dropna()
retornos     = precos.pct_change().dropna()
ret_ibov     = ibov_precos.pct_change().dropna()
ret_ibov.name = "IBOVESPA"

cdi_serie = buscar_cdi(DATA_INICIO, DATA_FIM)
if cdi_serie is not None and len(cdi_serie) > 0:
    cdi_diario = cdi_serie.reindex(retornos.index).ffill().bfill()
    cdi_diario = cdi_diario.dropna()
    if len(cdi_diario) > 0:
        rf_diario = cdi_diario.mean()
        cdi_anual = (1 + cdi_diario).prod() ** (DIAS_UTEIS / len(cdi_diario)) - 1
        cdi_fonte = f"CDI anualizado: {cdi_anual:.2%} (API BCB)"
    else:
        rf_diario = (1 + CDI_FALLBACK) ** (1 / DIAS_UTEIS) - 1
        cdi_fonte = f"CDI fallback: {CDI_FALLBACK:.2%} a.a."
else:
    rf_diario = (1 + CDI_FALLBACK) ** (1 / DIAS_UTEIS) - 1
    cdi_fonte = f"CDI fallback: {CDI_FALLBACK:.2%} a.a."

st.caption(f"💰 Taxa livre de risco — {cdi_fonte}")

def dark_fig_s(w=10, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    ax.tick_params(colors="#94a3b8")
    for sp in ax.spines.values(): sp.set_edgecolor("#334155")
    return fig, ax

# Etapa 1
section("📋", "Retornos e Estatísticas")
col1, col2 = st.columns([1, 3])
with col1:
    st.metric("Dias úteis", len(retornos))
    st.metric("Ativos",     len(nomes_ativos))
with col2:
    st.dataframe(retornos.describe().T.style.format("{:.4f}"), use_container_width=True)

# Etapa 2
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
section("⚡", "Volatilidade e Variáveis Sensíveis")

vol_anualizada = retornos.std() * np.sqrt(DIAS_UTEIS)
vol_df = vol_anualizada.sort_values(ascending=False) * 100

fig_vol, ax_vol = dark_fig_s(10, 4)
cores = ["#3b82f6","#60a5fa","#93c5fd","#bfdbfe","#dbeafe","#eff6ff"][:len(vol_df)]
bars  = ax_vol.bar(vol_df.index, vol_df.values, color=cores, edgecolor="#0f172a", linewidth=0.5)
ax_vol.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=10, color="#e2e8f0")
ax_vol.set_title(f"Volatilidade Anualizada — {setor_escolhido}", fontsize=13, fontweight="bold", color="#f1f5f9")
ax_vol.set_ylabel("Volatilidade (%)", color="#94a3b8")
ax_vol.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
st.pyplot(fig_vol); plt.close()

st.markdown("**Variáveis Sensíveis e Cenários Prospectivos (2027)**")
df_vars = pd.DataFrame(info_setor["variaveis"],
                       columns=["Variável Sensível","Cenário","Efeito na volatilidade","Ativos impactados"])
st.dataframe(df_vars, use_container_width=True, hide_index=True)

# Etapa 3
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
section("🔗", "Correlação e Diversificação")

matriz_corr = retornos.corr()
fig_heat, ax_heat = plt.subplots(figsize=(8, 6))
fig_heat.patch.set_facecolor("#0f172a")
ax_heat.set_facecolor("#0f172a")
sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap="RdYlGn",
            vmin=-1, vmax=1, center=0, linewidths=0.5, ax=ax_heat,
            annot_kws={"size": 10, "color": "#0f172a"})
ax_heat.set_title(f"Matriz de Correlação — {setor_escolhido}", fontsize=13, fontweight="bold", color="#f1f5f9")
ax_heat.tick_params(colors="#94a3b8")
plt.tight_layout()
st.pyplot(fig_heat); plt.close()

corr_pairs = (matriz_corr
              .where(np.tril(np.ones(matriz_corr.shape), k=-1).astype(bool))
              .stack().sort_values())
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Menor correlação (melhor diversificação)**")
    st.dataframe(corr_pairs.head(3).to_frame("Correlação").style.format("{:.3f}"), use_container_width=True)
with col_b:
    st.markdown("**Maior correlação**")
    st.dataframe(corr_pairs.tail(3).to_frame("Correlação").style.format("{:.3f}"), use_container_width=True)

# Etapa 4
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
section("⚖️", "Dois Portfólios")

n = len(retornos.columns)
pesos_ewp = pd.Series({a: 1/n for a in retornos.columns})
inv_vol   = 1 / vol_anualizada
corr_med  = matriz_corr.mean()
inv_corr  = 1 / corr_med.clip(lower=0.01)
score     = np.sqrt(inv_vol * inv_corr)
pesos_B   = (score / score.sum()).round(4)
pesos_B.iloc[-1] += round(1 - pesos_B.sum(), 4)

tabela_pesos = pd.DataFrame({
    "Portfólio A (EWP)":        pesos_ewp.map("{:.2%}".format),
    "Portfólio B (Estratégia)": pesos_B.map("{:.2%}".format),
    "Vol. Anualizada":          (vol_anualizada * 100).map("{:.2f}%".format),
    "Corr. Média":              corr_med.map("{:.3f}".format),
})
st.dataframe(tabela_pesos, use_container_width=True)

fig_p, ax_p = dark_fig_s(11, 4)
x = np.arange(n); w = 0.35
b1 = ax_p.bar(x - w/2, pesos_ewp.values*100, w, label="Portfólio A (EWP)",        color="#3b82f6", edgecolor="#0f172a")
b2 = ax_p.bar(x + w/2, pesos_B.values*100,   w, label="Portfólio B (Estratégia)", color="#f97316", edgecolor="#0f172a")
ax_p.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=8, color="#e2e8f0")
ax_p.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=8, color="#e2e8f0")
ax_p.set_xticks(x); ax_p.set_xticklabels(retornos.columns, fontsize=10, color="#94a3b8")
ax_p.set_ylabel("Peso (%)", color="#94a3b8")
ax_p.set_title(f"Comparação de Pesos — {setor_escolhido}", fontsize=13, fontweight="bold", color="#f1f5f9")
ax_p.yaxis.set_major_formatter(mtick.PercentFormatter())
ax_p.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0")
plt.tight_layout()
st.pyplot(fig_p); plt.close()

# Etapa 5
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
section("🏆", "Comparação de Desempenho")

ret_A = retornos.dot(pesos_ewp); ret_A.name = "Portfólio A (EWP)"
ret_B = retornos.dot(pesos_B);   ret_B.name = "Portfólio B (Estratégia)"
idx   = ret_A.index.intersection(ret_ibov.index)
ret_A, ret_B, ibov_al = ret_A.loc[idx], ret_B.loc[idx], ret_ibov.loc[idx]

metricas = {}
for nome, serie in [("Portfólio A (EWP)", ret_A), ("Portfólio B (Estratégia)", ret_B), ("IBOVESPA", ibov_al)]:
    metricas[nome] = {
        "Retorno Acumulado":       f"{retorno_acumulado(serie):.2%}",
        "Retorno Anualizado":      f"{retorno_anualizado(serie):.2%}",
        "Volatilidade Anualizada": f"{vol_anual(serie):.2%}",
        "Sharpe Ratio (CDI)":      f"{sharpe(serie, rf_diario):.3f}",
        "Máximo Drawdown":         f"{max_dd(serie):.2%}",
    }
st.dataframe(pd.DataFrame(metricas).T, use_container_width=True)

# Etapa 6 — Gráficos
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
section("📉", "Visualizações")

curva_A    = (1 + ret_A).cumprod() - 1
curva_B    = (1 + ret_B).cumprod() - 1
curva_ibov = (1 + ibov_al).cumprod() - 1

fig_r, ax_r = dark_fig_s(13, 5)
ax_r.plot(curva_A.index,    curva_A    * 100, label="Portfólio A (EWP)",        color="#3b82f6",  linewidth=2)
ax_r.plot(curva_B.index,    curva_B    * 100, label="Portfólio B (Estratégia)", color="#f97316",  linewidth=2.5)
ax_r.plot(curva_ibov.index, curva_ibov * 100, label="IBOVESPA",                 color="#94a3b8",  linewidth=1.5, linestyle="--")
ax_r.axhline(0, color="#475569", linewidth=0.8)
ax_r.fill_between(curva_B.index, curva_B*100, curva_A*100,
                  where=(curva_B >= curva_A), alpha=0.1, color="#34d399")
ax_r.fill_between(curva_B.index, curva_B*100, curva_A*100,
                  where=(curva_B < curva_A),  alpha=0.1, color="#f87171")
ax_r.set_title(f"Retorno Acumulado — {setor_escolhido}", fontsize=13, fontweight="bold", color="#f1f5f9")
ax_r.set_ylabel("Retorno Acumulado (%)", color="#94a3b8")
ax_r.yaxis.set_major_formatter(mtick.PercentFormatter())
ax_r.legend(fontsize=11, facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0")
plt.tight_layout()
st.pyplot(fig_r); plt.close()

# Etapa 7
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
section("🎯", "Recomendação ao Cliente")

sh_A = sharpe(ret_A, rf_diario); sh_B = sharpe(ret_B, rf_diario)
ra_B = retorno_acumulado(ret_B);  ra_ibov = retorno_acumulado(ibov_al)
ativo_def = vol_df.index[-1]

st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f2744,#1e293b);border:1px solid #1e40af;
border-radius:12px;padding:28px 32px;line-height:1.8">
<p style="color:#e2e8f0;margin:0">
A estratégia do <strong style="color:#f97316">Portfólio B</strong>
{"<strong style='color:#34d399'>entregou</strong>" if sh_B > sh_A else "<strong style='color:#f87171'>não entregou</strong>"}
melhor Sharpe Ratio que o EWP
(<strong style="color:#f1f5f9">{sh_B:.3f}</strong> vs <strong style="color:#f1f5f9">{sh_A:.3f}</strong>).
O setor <strong style="color:#f1f5f9">{'superou' if ra_B > ra_ibov else 'ficou abaixo d'}</strong>o IBOVESPA no período
(<strong style="color:#f1f5f9">{ra_B:.2%}</strong> vs <strong style="color:#f1f5f9">{ra_ibov:.2%}</strong>).
Para um cliente com <strong style="color:#60a5fa">perfil moderado</strong>, destacamos
<strong style="color:#34d399">{ativo_def}</strong> como o ativo mais defensivo do setor,
com a menor volatilidade histórica anualizada ({vol_df[ativo_def]:.1f}%).
</p>
</div>""", unsafe_allow_html=True)

st.markdown("<p style='color:#475569;font-size:0.8rem;text-align:center;margin-top:24px'>Fontes: Yahoo Finance · Banco Central do Brasil · Não constitui recomendação de investimento</p>",
            unsafe_allow_html=True)
