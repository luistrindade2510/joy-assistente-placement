import re
import pandas as pd
import streamlit as st

# =========================
# CONFIGURAÇÕES BÁSICAS
# =========================
st.set_page_config(
    page_title="JOY – Assistente do time de Placement",
    page_icon="💬",
    layout="centered",
)

# =========================
# CSS (VISUAL PREMIUM)
# =========================
st.markdown(
    """
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 980px; }

.joy-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 18px 18px;
  background: rgba(255,255,255,.75);
  box-shadow: 0 10px 25px rgba(0,0,0,.06);
}

.joy-card-ans{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 16px;
  padding: 14px 14px;
  background: rgba(255,255,255,.92);
}

.joy-chip{
  display:inline-block;
  padding: 6px 10px;
  margin: 4px 6px 0 0;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.90);
  font-size: 13px;
}

.joy-muted{ color: rgba(0,0,0,.60); font-size: 14px; }
.joy-muted-2{ color: rgba(0,0,0,.55); font-size: 13px; }

.stChatInput{ margin-top: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# TOPO (CARD + IMAGEM + BOAS-VINDAS)
# =========================
st.markdown('<div class="joy-card">', unsafe_allow_html=True)

c1, c2 = st.columns([1, 3], vertical_alignment="center")

with c1:
    try:
        st.image("joy.png", use_container_width=True)
    except Exception:
        st.write("")

with c2:
    st.markdown("## 💬 JOY – Assistente do time de Placement")
    st.markdown(
        '<div class="joy-muted">J.O.Y. — Agilidade no acompanhamento, precisão na entrega</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Olá! Eu sou a **J.O.Y**, assistente do time de Placement.  \n"
        "Qual demanda vamos acompanhar hoje?"
    )

    st.markdown("**Exemplos de consulta:**")
    st.markdown(
        """
<span class="joy-chip">6163</span>
<span class="joy-chip">6163 histórico</span>
<span class="joy-chip">Leadace</span>
<span class="joy-chip">Leadace saúde</span>
<span class="joy-chip">Leadace odonto</span>
<span class="joy-chip">desde 10/01/2026</span>
""",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
st.write("")

# =========================
# FILTROS RÁPIDOS (CLIQUE PARA APLICAR)
# =========================
if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None  # SAÚDE | ODONTO | AMBOS | None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False

st.markdown("### 🎛️ Filtros rápidos")
st.markdown(
    '<div class="joy-muted-2">Clique para aplicar. Você pode combinar com o que digitar (ID/empresa + filtro).</div>',
    unsafe_allow_html=True
)

a1, a2, a3 = st.columns([1.2, 1.8, 3.0])

with a1:
    if st.button("🧽 Limpar filtros", use_container_width=True):
        st.session_state.quick_produto = None
        st.session_state.quick_hist = False

with a2:
    label = "✅ Modo: Histórico" if st.session_state.quick_hist else "🗂️ Modo: Última atualização"
    if st.button(label, use_container_width=True):
        st.session_state.quick_hist = not st.session_state.quick_hist

with a3:
    st.write("")

p1, p2, p3, p4 = st.columns([1, 1, 1, 1])

def chip(label: str, value: str):
    active = (st.session_state.quick_produto == value)
    text = f"✅ {label}" if active else label
    if st.button(text, use_container_width=True):
        st.session_state.quick_produto = value

with p1:
    chip("🩺 Saúde", "SAÚDE")
with p2:
    chip("🦷 Odonto", "ODONTO")
with p3:
    chip("🩺+🦷 Ambos", "AMBOS")
with p4:
    if st.button("🚫 Sem produto", use_container_width=True):
        st.session_state.quick_produto = None

prod_txt = st.session_state.quick_produto if st.session_state.quick_produto else "—"
modo_txt = "Histórico" if st.session_state.quick_hist else "Última atualização"

st.markdown(
    f"""
<div class="joy-card-ans" style="margin-top:10px;">
<b>Filtros ativos</b><br>
<span class="joy-chip">Produto: {prod_txt}</span>
<span class="joy-chip">Modo: {modo_txt}</span>
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="joy-muted-2" style="margin-top:8px;">
Dica: digite <b>6163</b> ou <b>Leadace</b> e use os filtros acima para refinar 😉
</div>
""",
    unsafe_allow_html=True
)

st.write("")

# =========================
# DADOS (SHEETS)
# =========================
SHEETS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7eJXK_IARZPmt6GdsQLDPX4sSI-aCWZK286Y4DtwhVXr3NOH22eTIPwkFSbF14rfdYReQndgU51st/pub?gid=0&single=true&output=csv"

COL_ID = "COD_ACRISURE"
COL_DATE = "DATA_ATUALIZACAO"
COL_EMPRESA = "EMPRESA"
COL_DEMANDA = "DEMANDA"
COL_PRODUTO = "PRODUTO"
COL_AUTOR = "AUTOR"
COL_STATUS = "STATUS"
COL_TEXTO = "TEXTO"


@st.cache_data(ttl=60)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]

    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce", dayfirst=True)
    df[COL_ID] = df[COL_ID].astype(str).str.strip()

    for c in [COL_EMPRESA, COL_DEMANDA, COL_PRODUTO, COL_AUTOR, COL_STATUS, COL_TEXTO]:
        if c in df.columns:
            df[c] = df[c].astype(str).fillna("").str.strip()

    return df


def parse_user_message(msg: str):
    m = msg.strip()

    historico = bool(re.search(r"\bhist(ó|o)rico\b|\bhist\b", m, flags=re.I))

    produto = None
    if re.search(r"\bambos\b|\bodonto\+sa(ú|u)de\b", m, flags=re.I):
        produto = "AMBOS"
    elif re.search(r"\bodonto\b", m, flags=re.I):
        produto = "ODONTO"
    elif re.search(r"\bsa(ú|u)de\b", m, flags=re.I):
        produto = "SAÚDE"

    date_exact = None
    mdate = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", m)
    if mdate:
        try:
            date_exact = pd.to_datetime(mdate.group(1), dayfirst=True)
        except Exception:
            date_exact = None

    date_since = None
    msince = re.search(r"desde\s+(\d{1,2}/\d{1,2}/\d{4})", m, flags=re.I)
    if msince:
        try:
            date_since = pd.to_datetime(msince.group(1), dayfirst=True)
        except Exception:
            date_since = None

    mid = re.search(r"\b(\d{3,})\b", m)
    demanda_id = mid.group(1) if mid else None

    empresa_term = None if demanda_id else m
    return demanda_id, empresa_term, produto, historico, date_exact, date_since


def filter_df(df: pd.DataFrame, demanda_id=None, empresa_term=None, produto=None, date_exact=None, date_since=None):
    out = df.copy()

    if demanda_id:
        out = out[out[COL_ID] == str(demanda_id)]

    if empresa_term:
        term = empresa_term.lower()
        out = out[out[COL_EMPRESA].str.lower().str.contains(term, na=False)]

    # "AMBOS" significa não filtrar por produto (pega tudo)
    if produto and produto != "AMBOS":
        out = out[out[COL_PRODUTO].str.lower().str.contains(produto.lower(), na=False)]

    if date_exact is not None:
        out = out[out[COL_DATE].dt.date == date_exact.date()]

    if date_since is not None:
        out = out[out[COL_DATE] >= date_since]

    out = out.sort_values(by=COL_DATE, ascending=False)
    return out


def render_last_update(row: pd.Series):
    d = row[COL_DATE]
    d_str = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"

    st.markdown('<div class="joy-card-ans">', unsafe_allow_html=True)
    st.markdown("**📌 Última atualização**")
    st.markdown(f"- **ID:** {row[COL_ID]}")
    st.markdown(f"- **Empresa:** {row[COL_EMPRESA]}")
    st.markdown(f"- **Demanda:** {row[COL_DEMANDA]}")
    st.markdown(f"- **Produto:** {row[COL_PRODUTO]}")
    st.markdown(f"- **Data:** {d_str}")
    st.markdown(f"- **Status:** {row[COL_STATUS]}")
    st.markdown(f"- **Autor:** {row[COL_AUTOR]}")
    st.markdown(f"**Texto:** {row[COL_TEXTO]}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_history_table(df_hist: pd.DataFrame):
    view = df_hist[[COL_DATE, COL_STATUS, COL_PRODUTO, COL_AUTOR, COL_TEXTO]].copy()
    view[COL_DATE] = view[COL_DATE].dt.strftime("%d/%m/%Y")
    view = view.rename(columns={
        COL_DATE: "Data",
        COL_STATUS: "Status",
        COL_PRODUTO: "Produto",
        COL_AUTOR: "Autor",
        COL_TEXTO: "Atualização",
    })

    st.markdown("**🗂️ Histórico (mais recente primeiro):**")
    st.dataframe(view, use_container_width=True, hide_index=True)


# =========================
# CHAT
# =========================
df = load_data(SHEETS_CSV_URL)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

hint_parts = []
if st.session_state.quick_produto:
    hint_parts.append(f"produto={st.session_state.quick_produto.lower()}")
hint_parts.append("modo=histórico" if st.session_state.quick_hist else "modo=última")
hint_txt = " | ".join(hint_parts)

user_msg = st.chat_input(
    f"Digite um ID (ex: 6163) ou empresa — filtros ativos: {hint_txt}. Ex: '6163' | 'Leadace desde 10/01/2026'"
)

if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    demanda_id, empresa_term, produto, historico, date_exact, date_since = parse_user_message(user_msg)

    # Aplica filtros rápidos se o usuário não informou explicitamente
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto

    # Se o usuário não pediu histórico explicitamente, usa o modo selecionado
    if not historico and st.session_state.quick_hist:
        historico = True

    result = filter_df(df, demanda_id, empresa_term, produto, date_exact, date_since)

    with st.chat_message("assistant"):
        if result.empty:
            st.markdown(
                "Não achei nada com esses critérios 😅  \n"
                "Tenta só o **ID** (ex: **6163**) ou só parte do nome da empresa."
            )
        else:
            if historico:
                render_history_table(result)
            else:
                render_last_update(result.iloc[0])
