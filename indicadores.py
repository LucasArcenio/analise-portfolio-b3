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

IND_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');
.ind-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:12px;margin:6px 0 6px}
.ind-card{background:linear-gradient(160deg,#0f1c33,#15263f);border:1px solid #2d3f63;border-radius:12px;padding:13px 16px;transition:border-color .2s,transform .2s}
.ind-card:hover{border-color:#3a5080;transform:translateY(-2px)}
.ind-label{color:#94a3b8;font-size:0.72rem;font-weight:600;letter-spacing:.5px;margin-bottom:7px;text-transform:uppercase}
.ind-value{color:#f8fafc;font-size:1.28rem;font-weight:700;font-family:'Orbitron',sans-serif;line-height:1.1}
.ind-delta{font-size:0.8rem;font-weight:700;margin-top:7px;font-family:'Orbitron',sans-serif}
.ind-up{color:#39ff14;text-shadow:0 0 8px rgba(57,255,20,.35)}
.ind-down{color:#ff2e63;text-shadow:0 0 8px rgba(255,46,99,.35)}
</style>"""


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


def _pct_br(v):
    return f"{abs(float(v)):.2f}".replace(".", ",")


def _secao(titulo):
    st.markdown(
        f'<div style="margin:20px 0 2px"><h3 style="color:{UTAH_WHITE};font-size:1.05rem;'
        f'font-weight:700;margin:0;font-family:\'Playfair Display\',serif">{titulo}</h3></div>',
        unsafe_allow_html=True,
    )


def _card(label, value, var):
    """Card de dashboard: navy com borda lateral verde (sobe) / vermelha (cai)."""
    if var is None:
        accent, delta_html = "#3a5080", ""
    else:
        up = float(var) >= 0
        accent = "#39ff14" if up else "#ff2e63"
        cls = "ind-up" if up else "ind-down"
        seta = "▲" if up else "▼"
        delta_html = f'<div class="ind-delta {cls}">{seta} {_pct_br(var)}%</div>'
    return (f'<div class="ind-card" style="border-left:3px solid {accent}">'
            f'<div class="ind-label">{label}</div>'
            f'<div class="ind-value">{value}</div>'
            f'{delta_html}</div>')


def _grid_cards(itens):
    cards = "".join(_card(l, v, d) for l, v, d in itens)
    st.markdown(f'<div class="ind-grid">{cards}</div>', unsafe_allow_html=True)


def render_indicadores(autorefresh=False):
    """Renderiza o painel de indicadores. Se autorefresh, recarrega a cada 60s."""
    if autorefresh and _HAS_AUTOREFRESH:
        st_autorefresh(interval=60_000, key="indicadores_auto")

    dados = buscar_indicadores()
    if not dados:
        st.warning("Não foi possível carregar os indicadores de mercado agora. Tente novamente em instantes.")
        return

    st.markdown(IND_CSS, unsafe_allow_html=True)

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
    _grid_cards([
        ("Ibovespa",        f"{_br(ibov_p, 0)} pts", ibov_v),
        ("IFIX",            f"{_br(ifix_p, 0)} pts", ifix_v),
        ("Dólar (USD/BRL)", f"R$ {_br(usd_p, 4)}",   usd_v),
        ("Euro (EUR/BRL)",  f"R$ {_br(eur_p, 4)}",   eur_v),
        ("Selic",           f"{_br(taxes.get('selic'), 2)}% a.a.", None),
        ("CDI",             f"{_br(taxes.get('cdi'), 2)}% a.a.",   None),
    ])

    # ── Internacional ─────────────────────────────────────────────────────────
    _secao("🌎 Internacional")
    nas_p, nas_v = stk("NASDAQ")
    dow_p, dow_v = stk("DOWJONES")
    cac_p, cac_v = stk("CAC")
    nik_p, nik_v = stk("NIKKEI")
    _grid_cards([
        ("Nasdaq",    f"{_br(nas_p, 0)} pts", nas_v),
        ("Dow Jones", f"{_br(dow_p, 0)} pts", dow_v),
        ("CAC 40",    f"{_br(cac_p, 0)} pts", cac_v),
        ("Nikkei",    f"{_br(nik_p, 0)} pts", nik_v),
    ])

    # ── Cripto ────────────────────────────────────────────────────────────────
    _secao("₿ Cripto")
    btc_usd = btc.get("blockchain_info") or btc.get("bitstamp") or {}
    btc_brl = btc.get("mercadobitcoin") or btc.get("foxbit") or {}
    _grid_cards([
        ("Bitcoin (USD)", f"US$ {_br(btc_usd.get('last'), 0)}", btc_usd.get('variation')),
        ("Bitcoin (BRL)", f"R$ {_br(btc_brl.get('last'), 0)}",  btc_brl.get('variation')),
    ])

    st.markdown(
        '<div style="font-size:0.72rem;color:#64748b;margin-top:14px">'
        'Fonte: HG Brasil · atualização automática a cada 60s · valores podem ter pequena defasagem · não constitui recomendação de investimento</div>',
        unsafe_allow_html=True,
    )
