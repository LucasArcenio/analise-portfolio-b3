"""Indicadores de Mercado — painel HG Brasil para o app Utah Research."""
import requests
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except Exception:
    _HAS_AUTOREFRESH = False

HG_KEY = st.secrets.get("HG_KEY", "")
HG_URL = "https://api.hgbrasil.com/finance?format=json&key={}"

UTAH_WHITE = "#f8fafc"


@st.cache_data(ttl=60, show_spinner=False)
def buscar_indicadores():
    """Busca todos os indicadores num único endpoint da HG Brasil (cache 60s)."""
    try:
        r = requests.get(HG_URL.format(HG_KEY), timeout=10)
        r.raise_for_status()
        return r.json().get("results", {})
    except Exception:
        return {}


def _br(v, dec=2):
    """Formata número no padrão brasileiro (1.234,56)."""
    try:
        return f"{float(v):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "—"


def _delta(v):
    """Variação como string com sinal (st.metric colore verde/vermelho)."""
    try:
        return f"{float(v):+.2f}%".replace(".", ",")
    except (TypeError, ValueError):
        return None


def _secao(titulo):
    st.markdown(
        f'<div style="margin:18px 0 2px"><h3 style="color:{UTAH_WHITE};font-size:1.05rem;'
        f'font-weight:700;margin:0;font-family:\'Playfair Display\',serif">{titulo}</h3></div>',
        unsafe_allow_html=True,
    )


def _grid(itens, ncols):
    cols = st.columns(ncols)
    for i, (label, value, delta) in enumerate(itens):
        cols[i % ncols].metric(label, value, delta)


def render_indicadores(autorefresh=False):
    """Renderiza o painel de indicadores. Se autorefresh, recarrega a cada 60s."""
    if autorefresh and _HAS_AUTOREFRESH:
        st_autorefresh(interval=60_000, key="indicadores_auto")

    dados = buscar_indicadores()
    if not dados:
        st.warning("Não foi possível carregar os indicadores de mercado agora. Tente novamente em instantes.")
        return

    stocks = dados.get("stocks", {}) or {}
    cur    = dados.get("currencies", {}) or {}
    taxes  = (dados.get("taxes") or [{}])[0]
    btc    = dados.get("bitcoin", {}) or {}

    def stk(k):
        s = stocks.get(k) or {}
        return s.get("points"), s.get("variation")

    def moe(k):
        m = cur.get(k) or {}
        return m.get("buy"), m.get("variation")

    # ── Mercado Brasileiro ────────────────────────────────────────────────────
    _secao("🇧🇷 Mercado Brasileiro")
    ibov_p, ibov_v = stk("IBOVESPA")
    ifix_p, ifix_v = stk("IFIX")
    usd_p, usd_v   = moe("USD")
    eur_p, eur_v   = moe("EUR")
    _grid([
        ("Ibovespa",        f"{_br(ibov_p, 0)} pts", _delta(ibov_v)),
        ("IFIX",            f"{_br(ifix_p, 0)} pts", _delta(ifix_v)),
        ("Dólar (USD/BRL)", f"R$ {_br(usd_p, 4)}",   _delta(usd_v)),
        ("Euro (EUR/BRL)",  f"R$ {_br(eur_p, 4)}",   _delta(eur_v)),
        ("Selic",           f"{_br(taxes.get('selic'), 2)}% a.a.", None),
        ("CDI",             f"{_br(taxes.get('cdi'), 2)}% a.a.",   None),
    ], ncols=3)

    # ── Internacional ─────────────────────────────────────────────────────────
    _secao("🌎 Internacional")
    nas_p, nas_v = stk("NASDAQ")
    dow_p, dow_v = stk("DOWJONES")
    cac_p, cac_v = stk("CAC")
    nik_p, nik_v = stk("NIKKEI")
    _grid([
        ("Nasdaq",    f"{_br(nas_p, 0)} pts", _delta(nas_v)),
        ("Dow Jones", f"{_br(dow_p, 0)} pts", _delta(dow_v)),
        ("CAC 40",    f"{_br(cac_p, 0)} pts", _delta(cac_v)),
        ("Nikkei",    f"{_br(nik_p, 0)} pts", _delta(nik_v)),
    ], ncols=4)

    # ── Cripto ────────────────────────────────────────────────────────────────
    _secao("₿ Cripto")
    btc_usd = btc.get("blockchain_info") or btc.get("bitstamp") or {}
    btc_brl = btc.get("mercadobitcoin") or btc.get("foxbit") or {}
    _grid([
        ("Bitcoin (USD)", f"US$ {_br(btc_usd.get('last'), 0)}", _delta(btc_usd.get('variation'))),
        ("Bitcoin (BRL)", f"R$ {_br(btc_brl.get('last'), 0)}",  _delta(btc_brl.get('variation'))),
    ], ncols=4)

    st.markdown(
        '<div style="font-size:0.72rem;color:#64748b;margin-top:14px">'
        'Fonte: HG Brasil · atualização automática a cada 60s · valores podem ter pequena defasagem · não constitui recomendação de investimento</div>',
        unsafe_allow_html=True,
    )
