import warnings
warnings.filterwarnings('ignore')

import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import yfinance as yf
import requests
import streamlit as st
from datetime import date, timedelta
from pathlib import Path

st.set_page_config(page_title="Utah Research", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

BRAPI_TOKEN = st.secrets.get("BRAPI_TOKEN", "")

# ── Logo em base64 ────────────────────────────────────────────────────────────
def _img_b64(rel_path):
    try:
        p = Path(__file__).parent / rel_path
        return base64.b64encode(p.read_bytes()).decode()
    except:
        return ""

LOGO_B64        = _img_b64("assets/utah_logo_transparent.png")
LOGO_SQUARE_B64 = _img_b64("assets/utah_logo_transparent.png")

# ── Cores da marca Utah ───────────────────────────────────────────────────────
UTAH_NAVY   = "#1e2d4a"
UTAH_NAVY2  = "#2d3f63"
UTAH_NAVY3  = "#3a5080"
UTAH_WHITE  = "#f8fafc"
UTAH_SILVER = "#94a3b8"
UTAH_LINE   = "#2d3f63"
UTAH_GOLD   = "#c9a84c"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: {UTAH_NAVY}; }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {UTAH_NAVY} 0%, #162038 100%); border-right: 1px solid {UTAH_LINE}; }}
[data-testid="stSidebar"] * {{ color: {UTAH_WHITE} !important; }}
[data-testid="metric-container"] {{ background: {UTAH_NAVY2}; border: 1px solid {UTAH_LINE}; border-radius: 12px; padding: 16px 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.4); }}
[data-testid="metric-container"] label {{ color: {UTAH_SILVER} !important; font-size: 0.75rem !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; }}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{ color: {UTAH_WHITE} !important; font-size: 1.45rem !important; font-weight: 700 !important; }}
.hero {{ background: linear-gradient(135deg, #0f1c33 0%, {UTAH_NAVY} 40%, {UTAH_NAVY2} 100%); border: 1px solid {UTAH_NAVY3}; border-top: 3px solid {UTAH_GOLD}; border-radius: 16px; padding: 56px 48px; margin-bottom: 36px; text-align: center; position: relative; overflow: hidden; }}
.hero::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 50% 0%, rgba(201,168,76,0.06) 0%, transparent 70%); pointer-events: none; }}
.hero-logo {{ margin-bottom: 28px; }}
.hero h1 {{ font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 700; color: {UTAH_WHITE}; margin: 0 0 10px 0; letter-spacing: -0.5px; }}
.hero p {{ font-size: 1.1rem; color: {UTAH_SILVER}; margin: 0 0 28px 0; max-width: 560px; margin-left: auto; margin-right: auto; line-height: 1.7; }}
.hero-divider {{ width: 60px; height: 2px; background: {UTAH_GOLD}; margin: 0 auto 28px auto; border-radius: 2px; }}
.badge {{ display: inline-block; background: rgba(201,168,76,0.1); border: 1px solid rgba(201,168,76,0.35); color: {UTAH_GOLD}; border-radius: 20px; padding: 4px 14px; font-size: 0.78rem; margin: 0 4px 8px 4px; letter-spacing: 0.03em; }}
.chip-row {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 20px; }}
.chip {{ background: rgba(255,255,255,0.05); border: 1px solid {UTAH_NAVY3}; color: {UTAH_WHITE}; border-radius: 8px; padding: 6px 18px; font-size: 0.9rem; font-weight: 600; letter-spacing: 0.05em; }}
.section-header {{ display: flex; align-items: center; gap: 10px; margin: 36px 0 16px 0; padding-bottom: 10px; border-bottom: 1px solid {UTAH_LINE}; }}
.section-header h2 {{ color: {UTAH_WHITE}; font-size: 1.15rem; font-weight: 600; margin: 0; letter-spacing: 0.02em; text-transform: uppercase; }}
.company-card {{ background: linear-gradient(135deg, #0f1c33, {UTAH_NAVY2}); border: 1px solid {UTAH_LINE}; border-left: 4px solid {UTAH_GOLD}; border-radius: 14px; padding: 28px 32px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; }}
.company-name {{ color: {UTAH_WHITE}; font-size: 1.7rem; font-weight: 700; font-family: 'Playfair Display', serif; }}
.company-ticker {{ color: {UTAH_GOLD}; font-size: 0.95rem; font-weight: 600; letter-spacing: 0.08em; }}
.company-price {{ color: #4ade80; font-size: 2rem; font-weight: 700; }}
.company-date {{ color: {UTAH_SILVER}; font-size: 0.82rem; margin-top: 4px; }}
.divider {{ height: 1px; background: linear-gradient(90deg, transparent, {UTAH_LINE}, transparent); margin: 36px 0; }}
.info-box {{ background: rgba(45,63,99,0.4); border-left: 3px solid {UTAH_GOLD}; border-radius: 0 10px 10px 0; padding: 16px 20px; color: #cbd5e1; font-size: 0.93rem; margin: 16px 0; }}
.setor-title {{ background: linear-gradient(135deg, #0f1c33, {UTAH_NAVY2}); border: 1px solid {UTAH_LINE}; border-left: 4px solid {UTAH_GOLD}; border-radius: 14px; padding: 22px 28px; margin-bottom: 24px; }}
.setor-title h2 {{ font-family: 'Playfair Display', serif; color: {UTAH_WHITE}; font-size: 1.5rem; font-weight: 700; margin: 0 0 4px 0; }}
.setor-title p {{ color: {UTAH_SILVER}; margin: 0; font-size: 0.88rem; }}
.feat-card {{ background: {UTAH_NAVY2}; border: 1px solid {UTAH_LINE}; border-top: 2px solid {UTAH_GOLD}; border-radius: 12px; padding: 28px 24px; height: 100%; }}
.feat-card h3 {{ color: {UTAH_WHITE}; font-size: 1rem; font-weight: 600; margin: 8px 0; letter-spacing: 0.02em; }}
.feat-card p {{ color: {UTAH_SILVER}; font-size: 0.88rem; margin: 0; line-height: 1.6; }}
.sidebar-logo {{ text-align: center; padding: 8px 0 16px 0; }}
.utah-footer {{ color: {UTAH_SILVER}; font-size: 0.78rem; text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid {UTAH_LINE}; line-height: 1.8; }}
.rec-box {{ background: linear-gradient(135deg, #0f1c33, {UTAH_NAVY2}); border: 1px solid {UTAH_LINE}; border-left: 4px solid {UTAH_GOLD}; border-radius: 12px; padding: 28px 32px; line-height: 1.85; }}
.wa-wrap {{ position: fixed; bottom: 28px; right: 28px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }}
.wa-tooltip {{ background: #fff; color: #111; border-radius: 12px; padding: 12px 16px; font-size: 13px; line-height: 1.5; max-width: 210px; box-shadow: 0 8px 28px rgba(0,0,0,0.22); display: none; }}
.wa-tooltip strong {{ color: #128C7E; display: block; margin-bottom: 3px; font-size: 13px; }}
.wa-tooltip::after {{ content: ''; position: absolute; bottom: -6px; right: 26px; width: 12px; height: 12px; background: #fff; transform: rotate(45deg); }}
.wa-btn {{ width: 56px; height: 56px; border-radius: 50%; background: #25D366; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 18px rgba(37,211,102,0.45); transition: transform .15s, box-shadow .15s; text-decoration: none; }}
.wa-btn:hover {{ transform: scale(1.08); box-shadow: 0 6px 24px rgba(37,211,102,0.55); }}
</style>
""", unsafe_allow_html=True)

# ── Botão WhatsApp fixo ────────────────────────────────────────────────────────
st.markdown("""
<div class="wa-wrap">
  <div class="wa-tooltip" id="wa-tip">
    <strong>Fale com a Utah</strong>
    Tire suas dúvidas de investimentos com nosso time!
  </div>
  <a class="wa-btn"
     href="https://wa.me/5541996817327?text=Ol%C3%A1%21%20Tenho%20uma%20d%C3%BAvida%20sobre%20investimentos."
     target="_blank"
     onmouseenter="document.getElementById('wa-tip').style.display='block'"
     onmouseleave="document.getElementById('wa-tip').style.display='none'"
     title="Falar com a Utah Investimentos no WhatsApp"
     aria-label="Abrir WhatsApp da Utah Investimentos">
    <svg width="30" height="30" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
    </svg>
  </a>
</div>
""", unsafe_allow_html=True)

# ── Constantes ────────────────────────────────────────────────────────────────
DIAS_UTEIS   = 252
CDI_FALLBACK = 0.1065
DATA_FIM     = date.today().strftime("%Y-%m-%d")
DATA_INICIO  = (date.today() - timedelta(days=730)).strftime("%Y-%m-%d")

SETORES = {
    "Financeiro": {
        "tickers": ["ITUB4.SA","BBDC4.SA","BBAS3.SA","SANB11.SA","BBSE3.SA"],
        "nomes":   {"ITUB4.SA":"Itaú","BBDC4.SA":"Bradesco","BBAS3.SA":"Banco do Brasil","SANB11.SA":"Santander","BBSE3.SA":"BB Seguridade"},
        "variaveis": [("Taxa Selic","Queda de 2 p.p.","Aumento da volatilidade — pressão em margens de bancos","ITUB4, BBDC4"),("Inadimplência","Alta de 1 p.p.","Aumento da volatilidade — provisões sobem","BBDC4, SANB11"),("Câmbio BRL/USD","Desvalorização 15%","Leve aumento — impacto em carteiras dolarizadas","ITUB4")],
    },
    "Energia Elétrica": {
        "tickers": ["EQTL3.SA","CPFE3.SA","ENGI11.SA","TAEE11.SA","CMIG4.SA"],
        "nomes":   {"EQTL3.SA":"Equatorial","CPFE3.SA":"CPFL","ENGI11.SA":"Energisa","TAEE11.SA":"Taesa","CMIG4.SA":"Cemig"},
        "variaveis": [("Taxa Selic","Queda de 2 p.p.","Redução da volatilidade — setor de dividendos se valoriza","TAEE11, CMIG4"),("Nível dos Reservatórios","Abaixo de 30%","Aumento da volatilidade — risco hídrico","EQTL3, CMIG4"),("Regulação Aneel","Revisão tarifária","Aumento da volatilidade — incerteza nas margens","ENGI11, CPFE3")],
    },
    "Petróleo e Gás": {
        "tickers": ["PETR4.SA","PETR3.SA","PRIO3.SA","RECV3.SA","UGPA3.SA"],
        "nomes":   {"PETR4.SA":"Petrobras PN","PETR3.SA":"Petrobras ON","PRIO3.SA":"PRIO","RECV3.SA":"PetroReconcavo","UGPA3.SA":"Ultrapar"},
        "variaveis": [("Preço do Petróleo (Brent)","Alta de 20%","Redução da volatilidade — receitas mais previsíveis","PETR4, PRIO3"),("Câmbio BRL/USD","Desvalorização 15%","Redução — receitas em USD, custos em BRL","PETR4, RECV3"),("Risco Político","Intervenção governamental","Aumento forte da volatilidade","PETR4, PETR3")],
    },
    "Agronegócio e Alimentos": {
        "tickers": ["AGRO3.SA","SLCE3.SA","SMTO3.SA","TTEN3.SA","CAML3.SA"],
        "nomes":   {"AGRO3.SA":"BrasilAgro","SLCE3.SA":"SLC Agrícola","SMTO3.SA":"São Martinho","TTEN3.SA":"3tentos","CAML3.SA":"Camil"},
        "variaveis": [("Câmbio BRL/USD","Desvalorização 15%","Redução da volatilidade — exportadores ganham receita","AGRO3, SLCE3"),("Preço das Commodities","Queda de 15%","Aumento da volatilidade — margens comprimidas","SLCE3, SMTO3"),("El Niño / Clima","Seca severa","Aumento forte da volatilidade — quebra de safra","SLCE3, TTEN3")],
    },
    "Varejo": {
        "tickers": ["MGLU3.SA","VIVA3.SA","ALPA4.SA","SBFG3.SA","LREN3.SA"],
        "nomes":   {"MGLU3.SA":"Magazine Luiza","VIVA3.SA":"Vivara","ALPA4.SA":"Alpargatas","SBFG3.SA":"SBF Group","LREN3.SA":"Lojas Renner"},
        "variaveis": [("Taxa Selic","Queda de 2 p.p.","Redução da volatilidade — crédito mais barato, consumo sobe","MGLU3, LREN3"),("Desemprego","Alta de 1 p.p.","Aumento da volatilidade — queda no consumo discricionário","MGLU3, ALPA4"),("IPCA","Alta de 2 p.p.","Aumento — poder de compra reduzido, inadimplência sobe","LREN3, MGLU3")],
    },
    "Saúde e Farmácias": {
        "tickers": ["HAPV3.SA","RDOR3.SA","FLRY3.SA","PNVL3.SA","RADL3.SA"],
        "nomes":   {"HAPV3.SA":"Hapvida","RDOR3.SA":"Rede D'Or","FLRY3.SA":"Fleury","PNVL3.SA":"Dimed","RADL3.SA":"Raia Drogasil"},
        "variaveis": [("Taxa Selic","Queda de 2 p.p.","Redução da volatilidade — custo de dívida de expansão cai","HAPV3, RDOR3"),("Regulação ANS","Reajuste limitado","Aumento da volatilidade — pressão em margens de planos","HAPV3"),("Câmbio BRL/USD","Desvalorização 15%","Aumento — insumos e equipamentos médicos importados","RDOR3, FLRY3")],
    },
    "Tecnologia e Telecomunicações": {
        "tickers": ["TOTS3.SA","INTB3.SA","POSI3.SA","VIVT3.SA","TIMS3.SA","LWSA3.SA"],
        "nomes":   {"TOTS3.SA":"TOTVS","INTB3.SA":"Intelbras","POSI3.SA":"Positivo","VIVT3.SA":"Vivo","TIMS3.SA":"TIM","LWSA3.SA":"Locaweb"},
        "variaveis": [("Taxa Selic","Queda de 2 p.p.","Redução da volatilidade — valuation de crescimento melhora","TOTS3, LWSA3"),("Câmbio BRL/USD","Desvalorização 15%","Aumento — componentes importados encarecem","INTB3, POSI3"),("PIB","Desaceleração 1 p.p.","Aumento — empresas reduzem TI; telecom é mais resiliente","TOTS3, LWSA3")],
    },
    "Mineração": {
        "tickers": ["VALE3.SA","CMIN3.SA","CBAV3.SA","BRAP4.SA","FESA4.SA"],
        "nomes":   {"VALE3.SA":"Vale","CMIN3.SA":"CSN Mineração","CBAV3.SA":"CBA","BRAP4.SA":"Bradespar","FESA4.SA":"Ferbasa"},
        "variaveis": [("Preço do Minério de Ferro","Queda de 20%","Aumento forte da volatilidade — receitas caem","VALE3, CMIN3"),("Câmbio BRL/USD","Desvalorização 15%","Redução — exportações em USD","VALE3, CMIN3"),("Demanda China","Desaceleração 2 p.p.","Aumento da volatilidade — China consome ~70% do minério","VALE3, BRAP4")],
    },
    "Saneamento e Infraestrutura": {
        "tickers": ["SAPR11.SA","SBSP3.SA","CSMG3.SA","EGIE3.SA","SIMH3.SA"],
        "nomes":   {"SAPR11.SA":"Sanepar","SBSP3.SA":"Sabesp","CSMG3.SA":"Copasa","EGIE3.SA":"Engie","SIMH3.SA":"Simpar"},
        "variaveis": [("Taxa Selic","Queda de 2 p.p.","Redução da volatilidade — ativos regulados com dividendos sobem","SAPR11, CSMG3"),("Regulação ARSESP","Revisão tarifária negativa","Aumento da volatilidade — margem comprimida","SBSP3, CSMG3"),("Risco Hidrológico","Seca severa","Aumento — custos operacionais sobem","SAPR11, SBSP3")],
    },
    "Transportes e Logística": {
        "tickers": ["RAIL3.SA","TGMA3.SA","MOVI3.SA","AZUL3.SA","ECOR3.SA"],
        "nomes":   {"RAIL3.SA":"Rumo","TGMA3.SA":"Tegma","MOVI3.SA":"Movida","AZUL3.SA":"Azul","ECOR3.SA":"EcoRodovias"},
        "variaveis": [("Preço do Querosene (QAV)","Alta de 30%","Aumento forte da volatilidade — custo operacional das aéreas","AZUL3, MOVI3"),("Câmbio BRL/USD","Desvalorização 15%","Aumento — dívida e leasing de aeronaves em USD","AZUL3"),("Volume de Safra","Queda de 10%","Aumento — menos carga para ferrovias","RAIL3, TGMA3")],
    },
}

def retorno_acumulado(ret):  return (1 + ret).prod() - 1
def retorno_anualizado(ret): return (1 + retorno_acumulado(ret)) ** (DIAS_UTEIS / max(len(ret), 1)) - 1
def vol_anual(ret):          return ret.std() * np.sqrt(DIAS_UTEIS)
def sharpe(ret, rf):
    excesso = ret - rf
    return (excesso.mean() / excesso.std()) * np.sqrt(DIAS_UTEIS) if excesso.std() > 0 else 0.0
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

def section(icon, title):
    st.markdown(f'<div class="section-header"><span style="font-size:1.2rem">{icon}</span><h2>{title}</h2></div>', unsafe_allow_html=True)

def utah_fig(w=12, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#0f1c33")
    ax.set_facecolor("#0f1c33")
    ax.tick_params(colors=UTAH_SILVER)
    for sp in ax.spines.values(): sp.set_edgecolor(UTAH_LINE)
    return fig, ax

def parse_close(raw):
    if "Close" in raw.columns.get_level_values(0):
        close = raw["Close"]
    else:
        close = raw
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = close.columns.get_level_values(-1)
    return close.dropna(how="all")

@st.cache_data(ttl=900, show_spinner=False)
def buscar_dados(tickers):
    raw = yf.download(tickers + ["^BVSP"], period="2y", auto_adjust=True, progress=False)
    return parse_close(raw)

@st.cache_data(ttl=300, show_spinner=False)
def buscar_brapi(ticker_sa):
    ticker = ticker_sa.replace(".SA", "")
    try:
        url = f"https://brapi.dev/api/quote/{ticker}?token={BRAPI_TOKEN}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [{}])[0]
    except Exception:
        return {}

def _brapi_info(d):
    if not d: return {}
    return {
        "shortName":  d.get("shortName"),
        "longName":   d.get("longName"),
        "trailingPE": d.get("priceEarnings"),
        "trailingEps": d.get("earningsPerShare"),
        "marketCap":  d.get("marketCap"),
    }

def _brapi_cotacao(d):
    if not d: return None
    try:
        return {
            "preco":      round(float(d.get("regularMarketPrice", 0)), 2),
            "abertura":   round(float(d.get("regularMarketOpen", 0)), 2),
            "maxima":     round(float(d.get("regularMarketDayHigh", 0)), 2),
            "minima":     round(float(d.get("regularMarketDayLow", 0)), 2),
            "volume":     int(d.get("regularMarketVolume", 0)),
            "fechamento": round(float(d.get("regularMarketPreviousClose", 0)), 2),
        }
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_info(ticker_sa):
    try:
        return yf.Ticker(ticker_sa).info or {}
    except Exception:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_financials(ticker_sa):
    try:
        t = yf.Ticker(ticker_sa)
        return t.quarterly_financials, t.dividends
    except Exception:
        return None, None

@st.cache_data(ttl=300, show_spinner=False)
def cotacao_ao_vivo(ticker_sa):
    try:
        fi = yf.Ticker(ticker_sa).fast_info
        return {
            "preco":      round(float(fi.last_price), 2),
            "abertura":   round(float(fi.open), 2),
            "maxima":     round(float(fi.day_high), 2),
            "minima":     round(float(fi.day_low), 2),
            "volume":     int(fi.last_volume),
            "fechamento": round(float(fi.previous_close), 2),
        }
    except: return None

@st.cache_data(ttl=86400, show_spinner=False)
def buscar_cdi(data_inicio, data_fim):
    try:
        di  = pd.to_datetime(data_inicio).strftime("%d/%m/%Y")
        df_ = pd.to_datetime(data_fim).strftime("%d/%m/%Y")
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={di}&dataFinal={df_}"
        df  = pd.DataFrame(requests.get(url, timeout=10).json())
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        return df.set_index("data")["valor"].astype(float) / 100
    except: return None

def calcular_rf(cdi_serie, idx):
    if cdi_serie is not None and len(cdi_serie) > 0:
        al = cdi_serie.reindex(idx).ffill().bfill().dropna()
        if len(al) > 0:
            return al.mean()
    return (1 + CDI_FALLBACK) ** (1 / DIAS_UTEIS) - 1

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f'<div class="sidebar-logo"><img src="data:image/png;base64,{LOGO_B64}" style="width:160px"/></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<p style="color:#f8fafc;font-weight:700;text-align:center;letter-spacing:0.1em">UTAH INVESTIMENTOS</p>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2d3f63;margin:0 0 16px'>", unsafe_allow_html=True)
    modo = st.radio("", ["🏠  Início", "🔍  Empresa", "📂  Setor"], label_visibility="collapsed")
    st.markdown("<hr style='border-color:#2d3f63;margin:16px 0 12px'>", unsafe_allow_html=True)
    st.markdown("<small style='color:#64748b'>Dados: Yahoo Finance · BCB<br>Cotações com delay de 15 min</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA INICIAL
# ══════════════════════════════════════════════════════════════════════════════
if "Início" in modo:
    logo_html = (
        f'<div class="hero-logo"><img src="data:image/png;base64,{LOGO_B64}" style="height:110px"/></div>'
        if LOGO_B64 else ""
    )
    st.markdown(f"""
    <div class="hero">
        {logo_html}
        <h1>Utah Research</h1>
        <div class="hero-divider"></div>
        <p>Pesquise fundamentos, desempenho histórico e análise de portfólio de qualquer empresa listada na Bolsa brasileira</p>
        <div>
            <span class="badge">Análise Fundamentalista</span>
            <span class="badge">Dividendos</span>
            <span class="badge">Retorno vs IBOVESPA</span>
            <span class="badge">Portfólio por Setor</span>
            <span class="badge">Cotação em Tempo Real</span>
        </div>
        <div class="chip-row">
            <span class="chip">PETR4</span>
            <span class="chip">VALE3</span>
            <span class="chip">ITUB4</span>
            <span class="chip">BBDC4</span>
            <span class="chip">WEGE3</span>
            <span class="chip">MGLU3</span>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    cards = [
        ("🔍", "Empresa Individual", "Digite qualquer ticker da B3 e acesse indicadores fundamentalistas, balanço trimestral, histórico de dividendos e análise técnica completa."),
        ("📂", "Análise por Setor",  "Escolha um dos 10 setores, compare portfólios, analise correlação, volatilidade e desempenho histórico com benchmark IBOVESPA."),
        ("📈", "Benchmarking",       "Todos os resultados são comparados ao IBOVESPA e à taxa CDI (Banco Central do Brasil) como referências de mercado."),
    ]
    for col, (icon, titulo, desc) in zip([c1, c2, c3], cards):
        col.markdown(f'<div class="feat-card"><div style="font-size:1.8rem">{icon}</div><h3>{titulo}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="utah-footer">Utah Investimentos · Parceiro XP · Dados com fins educacionais · Não constitui recomendação de investimento<br><span style="font-size:0.72rem;color:#475569">Atualizado em {DATA_FIM}</span></div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# EMPRESA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════
if "Empresa" in modo:
    st.markdown(f'<div style="margin-bottom:24px"><h1 style="color:{UTAH_WHITE};font-size:1.9rem;font-weight:700;margin:0 0 4px;font-family:\'Playfair Display\',serif">Pesquisar Empresa</h1><p style="color:{UTAH_SILVER};margin:0;font-size:0.9rem">Análise fundamentalista e técnica · B3</p></div>', unsafe_allow_html=True)

    ticker_input = st.text_input("", placeholder="Digite o ticker — ex: PETR4, VALE3, ITUB4...", label_visibility="collapsed").strip().upper()

    if not ticker_input:
        st.markdown('<div class="info-box">💡 <strong>Exemplos:</strong> PETR4 (Petrobras), VALE3 (Vale), ITUB4 (Itaú), WEGE3 (WEG), BBDC4 (Bradesco), MGLU3 (Magazine Luiza)</div>', unsafe_allow_html=True)
        st.stop()

    ticker_sa = ticker_input if ticker_input.endswith(".SA") else ticker_input + ".SA"

    with st.spinner(f"Carregando {ticker_input}..."):
        try:
            _raw    = yf.download([ticker_sa, "^BVSP"], period="2y", auto_adjust=True, progress=False)
            raw_ind = parse_close(_raw)
        except Exception as e:
            st.error(f"Erro ao buscar preços: {e}"); st.stop()
        brapi_raw = buscar_brapi(ticker_sa)
        brapi_info_d = _brapi_info(brapi_raw)
        info_yf  = buscar_info(ticker_sa)
        # Merge: Brapi values take precedence when non-None
        info = {**info_yf, **{k: v for k, v in brapi_info_d.items() if v is not None}}
        qfin, divs_raw = buscar_financials(ticker_sa)
        vivo_brapi = _brapi_cotacao(brapi_raw)
        vivo_yf    = cotacao_ao_vivo(ticker_sa)
        vivo       = vivo_brapi if (vivo_brapi and vivo_brapi["preco"] > 0) else vivo_yf

    if ticker_sa not in raw_ind.columns or raw_ind[ticker_sa].dropna().empty:
        st.error(f"Ticker **{ticker_input}** não encontrado. Verifique o código."); st.stop()

    preco_ind  = raw_ind[ticker_sa].dropna()
    preco_ibov = raw_ind["^BVSP"].dropna() if "^BVSP" in raw_ind.columns else None
    ret_ind    = preco_ind.pct_change().dropna()

    cdi_s = buscar_cdi(DATA_INICIO, DATA_FIM)
    rf_i  = calcular_rf(cdi_s, ret_ind.index)

    nome_empresa = info.get("shortName") or info.get("longName") or ticker_input

    if vivo and vivo["preco"] > 0:
        cotacao_atual = vivo["preco"]
        var_dia       = (vivo["preco"] / vivo["fechamento"] - 1) * 100 if vivo["fechamento"] else 0
        preco_label   = "Tempo real (15 min delay)"
    else:
        cotacao_atual = preco_ind.iloc[-1]
        var_dia       = ret_ind.iloc[-1] * 100
        preco_label   = f"Fechamento {preco_ind.index[-1].date()}"

    cor_var = "#4ade80" if var_dia >= 0 else "#f87171"
    sinal   = "▲" if var_dia >= 0 else "▼"

    st.markdown(f"""
    <div class="company-card">
        <div>
            <div class="company-name">{nome_empresa}</div>
            <div class="company-ticker">{ticker_input} · B3</div>
            <div class="company-date">{preco_label}</div>
        </div>
        <div style="text-align:right">
            <div class="company-price">R$ {cotacao_atual:.2f}</div>
            <div style="color:{cor_var};font-size:1rem;font-weight:600;margin-top:4px">{sinal} {abs(var_dia):.2f}% no dia</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if vivo:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Abertura",        f"R$ {vivo['abertura']:.2f}")
        c2.metric("Máxima do dia",   f"R$ {vivo['maxima']:.2f}")
        c3.metric("Mínima do dia",   f"R$ {vivo['minima']:.2f}")
        c4.metric("Fechamento ant.", f"R$ {vivo['fechamento']:.2f}")
        vol = vivo['volume']
        c5.metric("Volume", f"{vol/1e6:.1f}M" if vol >= 1e6 else f"{vol/1e3:.0f}K")
    st.markdown("<br>", unsafe_allow_html=True)

    section("📊", "Indicadores Fundamentalistas")
    st.markdown("**Valuation**")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("P/L",        num(info.get("trailingPE")))
    c2.metric("P/VP",       num(info.get("priceToBook")))
    c3.metric("EV/EBITDA",  num(info.get("enterpriseToEbitda")))
    dy_raw = float(info.get("dividendYield") or 0)
    dy_val = dy_raw / 100 if dy_raw > 1 else dy_raw
    c4.metric("Div. Yield", pct(dy_val))
    c5.metric("LPA",        f"R$ {num(info.get('trailingEps'))}")

    st.markdown("<br>**Rentabilidade**", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("ROE",            pct(info.get("returnOnEquity")))
    c2.metric("ROA",            pct(info.get("returnOnAssets")))
    c3.metric("Margem Líquida", pct(info.get("profitMargins")))
    c4.metric("Margem EBITDA",  pct(info.get("ebitdaMargins")))
    c5.metric("Margem Bruta",   pct(info.get("grossMargins")))

    st.markdown("<br>**Saúde Financeira**", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Dívida/PL",       num(info.get("debtToEquity")))
    c2.metric("Liquidez Corr.",  num(info.get("currentRatio")))
    c3.metric("Liquidez Rápida", num(info.get("quickRatio")))
    c4.metric("Cres. Receita",   pct(info.get("revenueGrowth")))
    c5.metric("Valor de Mercado",fmt_bi(info.get("marketCap")))

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**DRE — últimos 12 meses**")
        st.table(pd.DataFrame({"Receita Líquida":[fmt_bi(info.get("totalRevenue"))],"EBITDA":[fmt_bi(info.get("ebitda"))],"Lucro Líquido":[fmt_bi(info.get("netIncomeToCommon"))]}).T.rename(columns={0:"Valor"}))
    with col_b:
        st.markdown("**Estrutura de Capital**")
        st.table(pd.DataFrame({"Dívida Total":[fmt_bi(info.get("totalDebt"))],"Caixa":[fmt_bi(info.get("totalCash"))],"VPA":[f"R$ {num(info.get('bookValue'))}"]}).T.rename(columns={0:"Valor"}))

    st.markdown("**DRE Trimestral**")
    try:
        if qfin is not None and not qfin.empty:
            mapa = {"Total Revenue":"Receita Líquida","EBITDA":"EBITDA","Net Income":"Lucro Líquido","Net Income Common Stockholders":"Lucro Líquido"}
            vistas = set(); sel = []
            for l in mapa:
                if l in qfin.index and mapa[l] not in vistas:
                    sel.append(l); vistas.add(mapa[l])
            qf = qfin.loc[sel, qfin.columns[:4]].copy()
            qf.index = [mapa[i] for i in qf.index]
            qf.columns = [str(c)[:10] for c in qf.columns]
            st.dataframe(qf.map(lambda v: fmt_bi(v) if pd.notna(v) else "—"), use_container_width=True)
        else:
            st.info("DRE trimestral não disponível.")
    except Exception:
        st.info("DRE trimestral não disponível.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    section("💰", "Histórico de Dividendos")
    try:
        divs = divs_raw
        if divs is not None and len(divs) > 0:
            divs.index = divs.index.tz_convert(None) if divs.index.tz is not None else divs.index
            div_12m = divs[divs.index >= (divs.index[-1] - pd.DateOffset(years=1))].sum()
            dy_calc = div_12m / cotacao_atual * 100 if cotacao_atual > 0 else 0
            n_pag   = len(divs[divs.index >= (divs.index[-1] - pd.DateOffset(years=1))])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total pago (12m)",  f"R$ {div_12m:.4f}")
            c2.metric("Dividend Yield",    f"{dy_calc:.2f}%")
            c3.metric("Pagamentos (12m)",  str(n_pag))
            divs_graf = divs[divs.index >= pd.Timestamp("2022-01-01")]
            fig_d, ax_d = utah_fig(12, 3.5)
            ax_d.bar(divs_graf.index, divs_graf.values, color=UTAH_GOLD, alpha=0.85, width=20)
            ax_d.set_title(f"Dividendos Pagos — {ticker_input}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
            ax_d.set_ylabel("R$/ação", color=UTAH_SILVER)
            plt.tight_layout(); st.pyplot(fig_d); plt.close()
        else:
            st.info("Nenhum dividendo registrado para este ativo.")
    except Exception as e:
        st.warning(f"Histórico de dividendos indisponível: {e}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    section("📈", "Análise Técnica")

    if preco_ibov is not None:
        ret_ib  = preco_ibov.pct_change().dropna()
        idx_com = ret_ind.index.intersection(ret_ib.index)
        ret_ind_c, ret_ib_c = ret_ind.loc[idx_com], ret_ib.loc[idx_com]
    else:
        ret_ind_c = ret_ind; ret_ib_c = None

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Retorno Acumulado",  f"{retorno_acumulado(ret_ind_c):.2%}")
    c2.metric("Retorno Anualizado", f"{retorno_anualizado(ret_ind_c):.2%}")
    c3.metric("Volatilidade Anual", f"{vol_anual(ret_ind_c):.2%}")
    c4.metric("Sharpe (CDI)",       f"{sharpe(ret_ind_c, rf_i):.3f}")
    c5.metric("Máx. Drawdown",      f"{max_dd(ret_ind_c):.2%}")

    curva_ind = (1 + ret_ind_c).cumprod() - 1
    fig_r, ax_r = utah_fig(12, 5)
    ax_r.plot(curva_ind.index, curva_ind * 100, label=ticker_input, color=UTAH_GOLD, linewidth=2.5)
    if ret_ib_c is not None:
        curva_ib = (1 + ret_ib_c).cumprod() - 1
        ax_r.plot(curva_ib.index, curva_ib * 100, label="IBOVESPA", color=UTAH_SILVER, linewidth=1.5, linestyle="--")
        ax_r.fill_between(curva_ind.index, curva_ind*100, curva_ib*100, where=(curva_ind>=curva_ib), alpha=0.12, color="#4ade80")
        ax_r.fill_between(curva_ind.index, curva_ind*100, curva_ib*100, where=(curva_ind<curva_ib),  alpha=0.12, color="#f87171")
    ax_r.axhline(0, color="#475569", linewidth=0.8)
    ax_r.set_title(f"Retorno Acumulado — {ticker_input} vs IBOVESPA", fontsize=13, fontweight="bold", color=UTAH_WHITE)
    ax_r.set_ylabel("Retorno Acumulado (%)", color=UTAH_SILVER)
    ax_r.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax_r.legend(fontsize=11, facecolor="#0f1c33", edgecolor=UTAH_LINE, labelcolor=UTAH_WHITE)
    plt.tight_layout(); st.pyplot(fig_r); plt.close()

    curva_p  = (1 + ret_ind_c).cumprod()
    dd_serie = (curva_p - curva_p.cummax()) / curva_p.cummax() * 100
    fig_dd, ax_dd = utah_fig(12, 3)
    ax_dd.fill_between(dd_serie.index, dd_serie.values, 0, color="#f87171", alpha=0.4)
    ax_dd.plot(dd_serie.index, dd_serie.values, color="#f87171", linewidth=1)
    ax_dd.set_title(f"Drawdown — {ticker_input}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
    ax_dd.set_ylabel("Drawdown (%)", color=UTAH_SILVER)
    ax_dd.yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.tight_layout(); st.pyplot(fig_dd); plt.close()

    fig_h, ax_h = utah_fig(10, 4)
    ax_h.hist(ret_ind_c * 100, bins=60, color=UTAH_NAVY3, edgecolor="#0f1c33", linewidth=0.3, alpha=0.9)
    ax_h.axvline(ret_ind_c.mean()*100, color=UTAH_GOLD, linestyle="--", linewidth=2, label=f"Média: {ret_ind_c.mean()*100:.3f}%")
    ax_h.axvline(0, color=UTAH_SILVER, linewidth=1, alpha=0.6)
    ax_h.set_title(f"Distribuição de Retornos Diários — {ticker_input}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
    ax_h.set_xlabel("Retorno Diário (%)", color=UTAH_SILVER)
    ax_h.set_ylabel("Frequência", color=UTAH_SILVER)
    ax_h.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax_h.legend(facecolor="#0f1c33", edgecolor=UTAH_LINE, labelcolor=UTAH_WHITE)
    plt.tight_layout(); st.pyplot(fig_h); plt.close()

    st.markdown(f'<div class="utah-footer">Utah Investimentos · Parceiro XP · Fontes: Yahoo Finance · BCB · Não constitui recomendação de investimento</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SETOR
# ══════════════════════════════════════════════════════════════════════════════
setor_escolhido = st.sidebar.selectbox("Setor:", list(SETORES.keys()))
info_setor = SETORES[setor_escolhido]
tickers    = info_setor["tickers"]
nomes      = info_setor["nomes"]

st.markdown(f'<div class="setor-title"><h2>📂 {setor_escolhido}</h2><p>Análise de portfólio · últimos 2 anos · {DATA_FIM} · Benchmark: IBOVESPA</p></div>', unsafe_allow_html=True)

with st.spinner("Baixando dados..."):
    precos_raw = buscar_dados(tickers)

precos_raw.columns = [nomes.get(c, c) for c in precos_raw.columns]
# filtra só ativos com dados suficientes (≥ 80% dos dias)
nomes_ativos = [
    nomes[t] for t in tickers
    if nomes[t] in precos_raw.columns
    and precos_raw[nomes[t]].notna().mean() >= 0.8
]
precos = precos_raw[nomes_ativos].ffill().bfill().dropna(how="all")
ibov_precos  = precos_raw["^BVSP"].dropna() if "^BVSP" in precos_raw.columns else precos_raw.iloc[:, -1].dropna()
retornos     = precos.pct_change().dropna()
ret_ibov     = ibov_precos.pct_change().dropna()
ret_ibov.name = "IBOVESPA"

cdi_serie = buscar_cdi(DATA_INICIO, DATA_FIM)
rf_diario = calcular_rf(cdi_serie, retornos.index)
if cdi_serie is not None and len(cdi_serie) > 0:
    al = cdi_serie.reindex(retornos.index).ffill().bfill().dropna()
    cdi_anual = (1 + al).prod() ** (DIAS_UTEIS / max(len(al), 1)) - 1 if len(al) > 0 else CDI_FALLBACK
    cdi_fonte = f"CDI anualizado: {cdi_anual:.2%} (API BCB)"
else:
    cdi_fonte = f"CDI fallback: {CDI_FALLBACK:.2%} a.a."

st.caption(f"Taxa livre de risco — {cdi_fonte}")

section("📋", "Retornos e Estatísticas")
col1, col2 = st.columns([1, 3])
with col1:
    st.metric("Dias úteis", len(retornos))
    st.metric("Ativos",     len(nomes_ativos))
with col2:
    st.dataframe(retornos.describe().T.style.format("{:.4f}"), use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
section("⚡", "Volatilidade e Variáveis Sensíveis")
vol_anualizada = retornos.std() * np.sqrt(DIAS_UTEIS)
vol_df = vol_anualizada.sort_values(ascending=False) * 100
fig_v, ax_v = utah_fig(10, 4)
n_bars = len(vol_df)
cores_bars = [UTAH_NAVY3, "#4a6090", "#5870a8", "#6680b8", UTAH_GOLD, UTAH_GOLD][:n_bars]
bars = ax_v.bar(vol_df.index, vol_df.values, color=cores_bars[:n_bars], edgecolor="#0f1c33", linewidth=0.5)
ax_v.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=10, color=UTAH_WHITE)
ax_v.set_title(f"Volatilidade Anualizada — {setor_escolhido}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
ax_v.set_ylabel("Volatilidade (%)", color=UTAH_SILVER)
ax_v.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout(); st.pyplot(fig_v); plt.close()

st.markdown("**Variáveis Sensíveis e Cenários Prospectivos**")
st.dataframe(pd.DataFrame(info_setor["variaveis"], columns=["Variável Sensível","Cenário","Efeito na volatilidade","Ativos impactados"]), use_container_width=True, hide_index=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
section("🔗", "Correlação e Diversificação")
matriz_corr = retornos.corr()
fig_hm, ax_hm = plt.subplots(figsize=(8, 6))
fig_hm.patch.set_facecolor("#0f1c33"); ax_hm.set_facecolor("#0f1c33")
sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap="RdYlGn", vmin=-1, vmax=1, center=0,
            linewidths=0.5, ax=ax_hm, annot_kws={"size":10,"color":"#0f1c33"})
ax_hm.set_title(f"Matriz de Correlação — {setor_escolhido}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
ax_hm.tick_params(colors=UTAH_SILVER)
plt.tight_layout(); st.pyplot(fig_hm); plt.close()

corr_pairs = matriz_corr.where(np.tril(np.ones(matriz_corr.shape), k=-1).astype(bool)).stack().sort_values()
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Menor correlação**")
    st.dataframe(corr_pairs.head(3).to_frame("Correlação").style.format("{:.3f}"), use_container_width=True)
with col_b:
    st.markdown("**Maior correlação**")
    st.dataframe(corr_pairs.tail(3).to_frame("Correlação").style.format("{:.3f}"), use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
section("⚖️", "Dois Portfólios")
n = len(retornos.columns)
pesos_ewp = pd.Series({a: 1/n for a in retornos.columns})
inv_vol   = 1 / vol_anualizada
corr_med  = matriz_corr.mean()
score     = np.sqrt(inv_vol * (1 / corr_med.clip(lower=0.01)))
pesos_B   = (score / score.sum()).round(4)
pesos_B.iloc[-1] += round(1 - pesos_B.sum(), 4)

st.dataframe(pd.DataFrame({
    "Portfólio A (EWP)":  pesos_ewp.map("{:.2%}".format),
    "Portfólio B":        pesos_B.map("{:.2%}".format),
    "Vol. Anualizada":    (vol_anualizada*100).map("{:.2f}%".format),
    "Corr. Média":        corr_med.map("{:.3f}".format),
}), use_container_width=True)

fig_p, ax_p = utah_fig(11, 4)
x = np.arange(n); w = 0.35
b1 = ax_p.bar(x-w/2, pesos_ewp.values*100, w, label="Portfólio A (EWP)", color=UTAH_NAVY3, edgecolor="#0f1c33")
b2 = ax_p.bar(x+w/2, pesos_B.values*100,   w, label="Portfólio B",        color=UTAH_GOLD,  edgecolor="#0f1c33")
ax_p.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=8, color=UTAH_WHITE)
ax_p.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=8, color=UTAH_WHITE)
ax_p.set_xticks(x); ax_p.set_xticklabels(retornos.columns, fontsize=10, color=UTAH_SILVER)
ax_p.set_ylabel("Peso (%)", color=UTAH_SILVER)
ax_p.set_title(f"Comparação de Pesos — {setor_escolhido}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
ax_p.yaxis.set_major_formatter(mtick.PercentFormatter())
ax_p.legend(facecolor="#0f1c33", edgecolor=UTAH_LINE, labelcolor=UTAH_WHITE)
plt.tight_layout(); st.pyplot(fig_p); plt.close()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
section("🏆", "Comparação de Desempenho")
ret_A = retornos.dot(pesos_ewp); ret_A.name = "Portfólio A (EWP)"
ret_B = retornos.dot(pesos_B);   ret_B.name = "Portfólio B"
idx   = ret_A.index.intersection(ret_ibov.index)
ret_A, ret_B, ibov_al = ret_A.loc[idx], ret_B.loc[idx], ret_ibov.loc[idx]
metricas = {}
for nome_m, serie in [("Portfólio A (EWP)", ret_A), ("Portfólio B", ret_B), ("IBOVESPA", ibov_al)]:
    metricas[nome_m] = {
        "Retorno Acumulado":  f"{retorno_acumulado(serie):.2%}",
        "Retorno Anualizado": f"{retorno_anualizado(serie):.2%}",
        "Volatilidade":       f"{vol_anual(serie):.2%}",
        "Sharpe (CDI)":       f"{sharpe(serie, rf_diario):.3f}",
        "Máx. Drawdown":      f"{max_dd(serie):.2%}",
    }
st.dataframe(pd.DataFrame(metricas).T, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
section("📉", "Retorno Acumulado")
curva_A    = (1 + ret_A).cumprod() - 1
curva_B    = (1 + ret_B).cumprod() - 1
curva_ibov = (1 + ibov_al).cumprod() - 1
fig_r, ax_r = utah_fig(13, 5)
ax_r.plot(curva_A.index,    curva_A*100,    label="Portfólio A (EWP)", color=UTAH_NAVY3,  linewidth=2)
ax_r.plot(curva_B.index,    curva_B*100,    label="Portfólio B",        color=UTAH_GOLD,   linewidth=2.5)
ax_r.plot(curva_ibov.index, curva_ibov*100, label="IBOVESPA",           color=UTAH_SILVER, linewidth=1.5, linestyle="--")
ax_r.axhline(0, color="#475569", linewidth=0.8)
ax_r.fill_between(curva_B.index, curva_B*100, curva_A*100, where=(curva_B>=curva_A), alpha=0.1, color="#4ade80")
ax_r.fill_between(curva_B.index, curva_B*100, curva_A*100, where=(curva_B<curva_A),  alpha=0.1, color="#f87171")
ax_r.set_title(f"Retorno Acumulado — {setor_escolhido}", fontsize=13, fontweight="bold", color=UTAH_WHITE)
ax_r.set_ylabel("Retorno Acumulado (%)", color=UTAH_SILVER)
ax_r.yaxis.set_major_formatter(mtick.PercentFormatter())
ax_r.legend(fontsize=11, facecolor="#0f1c33", edgecolor=UTAH_LINE, labelcolor=UTAH_WHITE)
plt.tight_layout(); st.pyplot(fig_r); plt.close()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
section("🎯", "Recomendação ao Cliente")
sh_A = sharpe(ret_A, rf_diario); sh_B = sharpe(ret_B, rf_diario)
ra_B = retorno_acumulado(ret_B);  ra_ibov = retorno_acumulado(ibov_al)
ativo_def = vol_df.index[-1]
melhor  = "entregou" if sh_B > sh_A else "não entregou"
vs_ibov = "superou" if ra_B > ra_ibov else "ficou abaixo d"
st.markdown(f"""
<div class="rec-box">
<p style="color:#e2e8f0;margin:0">
A estratégia do <strong style="color:{UTAH_GOLD}">Portfólio B</strong>
<strong style="color:{'#4ade80' if sh_B > sh_A else '#f87171'}">{melhor}</strong>
melhor Sharpe Ratio que o EWP (<strong style="color:{UTAH_WHITE}">{sh_B:.3f}</strong> vs <strong style="color:{UTAH_WHITE}">{sh_A:.3f}</strong>).
O setor <strong style="color:{UTAH_WHITE}">{vs_ibov}</strong>o IBOVESPA no período
(<strong style="color:{UTAH_WHITE}">{ra_B:.2%}</strong> vs <strong style="color:{UTAH_WHITE}">{ra_ibov:.2%}</strong>).
Para um cliente com <strong style="color:{UTAH_GOLD}">perfil moderado</strong>, destacamos
<strong style="color:#4ade80">{ativo_def}</strong> como o ativo mais defensivo do setor,
com a menor volatilidade histórica anualizada ({vol_df[ativo_def]:.1f}%).
</p>
</div>""", unsafe_allow_html=True)

st.markdown(f'<div class="utah-footer">Utah Investimentos · Parceiro XP · Fontes: Yahoo Finance · Banco Central do Brasil<br>Não constitui recomendação de investimento · Atualizado em {DATA_FIM}</div>', unsafe_allow_html=True)
