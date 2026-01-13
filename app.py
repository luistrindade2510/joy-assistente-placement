import re
import pandas as pd
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="JOY – Assistente Placement Jr",
    page_icon="💬",
    layout="centered",
)

VIDEO_TOP = "joy_idle.mp4"
VIDEO_RESULT = "joy_success.mp4"

SHEETS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7eJXK_IARZPmt6GdsQLDPX4sSI-aCWZK286Y4DtwhVXr3NOH22eTIPwkFSbF14rfdYReQndgU51st/pub?gid=0&single=true&output=csv"

COL_ID = "COD_ACRISURE"
COL_DATE = "DATA_ATUALIZACAO"
COL_EMPRESA = "EMPRESA"
COL_DEMANDA = "DEMANDA"
COL_PRODUTO = "PRODUTO"
COL_AUTOR = "AUTOR"
COL_STATUS = "STATUS"
COL_TEXTO = "TEXTO"

# =========================
# STATE
# =========================
if "query" not in st.session_state:
    st.session_state.query = ""
if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False

# =========================
# CSS PREMIUM
# =========================
st.markdown(
    """
<style>
.block-container{
  max-width: 1040px;
  padding-top: 1.1rem;
  padding-bottom: 2.2rem;
}

/* ====== HERO ====== */
.joy-hero{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 22px;
  padding: 18px 18px;
  background: linear-gradient(180deg, rgba(255,255,255,.97), rgba(255,255,255,.90));
  box-shadow: 0 18px 44px rgba(0,0,0,.07);
  margin-bottom: 14px;
}

.joy-title{
  font-size: 28px;
  font-weight: 860;
  line-height: 1.1;
  margin: 0;
}

.joy-sub{
  margin-top: 6px;
  color: rgba(0,0,0,.62);
  font-size: 13.5px;
}

.joy-help{
  margin-top: 12px;
  color: rgba(0,0,0,.86);
  font-size: 14px;
  line-height: 1.5;
}

.joy-help b{ font-weight: 820; }

.joy-divider{
  margin: 14px 0 8px 0;
  border-bottom: 1px solid rgba(0,0,0,.08);
}

/* ====== SEARCH ====== */
.joy-search-label{
  font-size: 13px;
  color: rgba(0,0,0,.62);
  margin-bottom: 6px;
}

div[data-testid="stTextInput"] input{
  border-radius: 16px !important;
  border: 1px solid rgba(0,0,0,.12) !important;
  padding: 12px 14px !important;
  font-size: 14px !important;
}

div[data-testid="stTextInput"] input:focus{
  border: 1px solid rgba(0,0,0,.22) !important;
  box-shadow: 0 0 0 4px rgba(0,0,0,.06) !important;
}

.joy-primary > button{
  border-radius: 16px !important;
  padding: 10px 14px !important;
  border: 1px solid rgba(0,0,0,.12) !important;
  font-weight: 760 !important;
}

/* ====== CHIPS ====== */
.joy-chiprow{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.joy-chipbtn > button{
  border-radius: 999px !important;
  padding: 6px 10px !important;
  border: 1px solid rgba(0,0,0,.12) !important;
  font-size: 12.8px !important;
}

/* ====== FILTER CARD ====== */
.joy-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 14px 14px;
  background: rgba(255,255,255,.94);
  box-shadow: 0 14px 34px rgba(0,0,0,.05);
  margin-top: 12px;
}

.joy-card-title{
  font-weight: 850;
  font-size: 14px;
  margin: 0;
}

.joy-muted{
  color: rgba(0,0,0,.58);
  font-size: 12.8px;
  margin-top: 4px;
}

.joy-pilltag{
  display:inline-block;
  padding: 6px 10px;
  margin: 8px 8px 0 0;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(0,0,0,.03);
  font-size: 12px;
}

/* ====== RESULT HEADER ====== */
.joy-head{
  display:flex;
  justify-content: space-between;
  align-items:flex-start;
  gap: 14px;
}

.joy-badge{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.12);
  background: rgba(0,0,0,.03);
  font-size: 12px;
  font-weight: 700;
}

/* ====== RESULT GRID ====== */
.joy-grid{
  display:grid;
  grid-template-columns: 120px 1fr;
  gap: 6px 10px;
  font-size: 13.6px;
  margin-top: 10px;
}
.joy-grid b{ color: rgba(0,0,0,.78); }
.joy-grid span{ color: rgba(0,0,0,.92); }

.joy-hr{
  margin: 12px 0;
  border-bottom: 1px solid rgba(0,0,0,.08);
}

/* ====== TABLE LOOK ====== */
[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.08);
}

/* ====== VIDEO LOOK ====== */
.joy-video-wrap{
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.10);
  box-shadow: 0 14px 30px rgba(0,0,0,.08);
  background: #fff;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# DATA LOAD
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce", dayfirst=True)
    df[COL_ID] = df[COL_ID].astype(str).str.strip()
    for c in [COL_EMPRESA, COL_DEMANDA, COL_PRODUTO, COL_AUTOR, COL_STATUS, COL_TEXTO]:
        if c in df.columns:
            df[c] = df[c].astype(str).fillna("").str.strip()
    return df

df = load_data(SHEETS_CSV_URL)

# =========================
# PARSE & FILTER
# =========================
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

    date_since = None
    msince = re.search(r"desde\s+(\d{1,2}/\d{1,2}/\d{4})", m, flags=re.I)
    if msince:
        try:
            date_since = pd.to_datetime(msince.group(1), dayfirst=True)
        except Exception:
            date_since = None

    mid = re.search(r"\b(\d{3,})\b", m)
    demanda_id = mid.group(1) if mid else None

    cleaned = re.sub(r"\bhist(ó|o)rico\b|\bhist\b", "", m, flags=re.I)
    cleaned = re.sub(r"\bsa(ú|u)de\b|\bodonto\b|\bambos\b|\bodonto\+sa(ú|u)de\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"desde\s+\d{1,2}/\d{1,2}/\d{4}", "", cleaned, flags=re.I)
    cleaned = cleaned.strip(" -|,;")

    empresa_term = None if demanda_id else cleaned.strip()
    if empresa_term == "":
        empresa_term = None

    return demanda_id, empresa_term, produto, historico, date_since

def filter_df(df: pd.DataFrame, demanda_id=None, empresa_term=None, produto=None, date_since=None):
    out = df.copy()

    if demanda_id:
        out = out[out[COL_ID] == str(demanda_id)]
    if empresa_term:
        term = empresa_term.lower()
        out = out[out[COL_EMPRESA].str.lower().str.contains(term, na=False)]
    if produto and produto != "AMBOS":
        out = out[out[COL_PRODUTO].str.lower().str.contains(produto.lower(), na=False)]
    if date_since is not None:
        out = out[out[COL_DATE] >= date_since]

    return out.sort_values(by=COL_DATE, ascending=False)

def badge_text(status: str) -> str:
    s = (status or "").upper()
    if "CONCLU" in s:
        return "Concluído"
    if "ANDAM" in s:
        return "Em andamento"
    if "PEND" in s:
        return "Pendente"
    return status.title() if status else "—"

# =========================
# HERO (2 colunas, vídeo grande e bonito)
# =========================
st.markdown("<div class='joy-hero'>", unsafe_allow_html=True)
c_vid, c_txt = st.columns([1.15, 1.85], vertical_alignment="center")

with c_vid:
    st.markdown("<div class='joy-video-wrap'>", unsafe_allow_html=True)
    st.video(VIDEO_TOP, loop=True, autoplay=True, muted=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_txt:
    st.markdown("<p class='joy-title'>J.O.Y – Assistente Placement Jr</p>", unsafe_allow_html=True)
    st.markdown(
        "<div class='joy-sub'>Status, histórico e andamento dos estudos — sem depender de mensagens no Teams.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='joy-help'><b>Digite</b> o <b>ID</b> ou a <b>empresa</b>. "
        "Pra refinar, use <b>saúde</b>/<b>odonto</b>, <b>histórico</b> e <b>desde dd/mm/aaaa</b>.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='joy-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='joy-search-label'>🔎 Onde você quer que eu olhe agora?</div>", unsafe_allow_html=True)
    cin, cbtn = st.columns([4.2, 1.2])
    with cin:
        st.session_state.query = st.text_input(
            label="",
            value=st.session_state.query,
            placeholder="Ex.: 6163 | Leadec | 6163 histórico | Leadec saúde | desde 10/01/2026",
        )
    with cbtn:
        st.markdown("<div class='joy-primary'>", unsafe_allow_html=True)
        do_search = st.button("Buscar", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # chips
    st.markdown("<div class='joy-chiprow'>", unsafe_allow_html=True)
    chip_cols = st.columns(6)
    sugs = ["6163", "6163 histórico", "Leadec", "Leadec saúde", "Leadec odonto", "desde 10/01/2026"]
    for i, s in enumerate(sugs):
        with chip_cols[i]:
            st.markdown("<div class='joy-chipbtn'>", unsafe_allow_html=True)
            if st.button(s, use_container_width=True):
                st.session_state.query = s
                do_search = True
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # fecha hero

# =========================
# FILTROS (card separado)
# =========================
st.markdown("<div class='joy-card'>", unsafe_allow_html=True)
st.markdown("<div class='joy-head'>"
            "<div>"
            "<div class='joy-card-title'>🎛️ Refine sua consulta</div>"
            "<div class='joy-muted'>Clique nos filtros e depois em <b>Buscar</b>.</div>"
            "</div>"
            "</div>", unsafe_allow_html=True)

b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    if st.button("🧽 Limpar", use_container_width=True):
        st.session_state.quick_produto = None
        st.session_state.quick_hist = False
with b2:
    if st.button("🩺 Saúde", use_container_width=True):
        st.session_state.quick_produto = "SAÚDE"
with b3:
    if st.button("🦷 Odonto", use_container_width=True):
        st.session_state.quick_produto = "ODONTO"
with b4:
    if st.button("🩺+🦷 Ambos", use_container_width=True):
        st.session_state.quick_produto = "AMBOS"
with b5:
    label = "🗂️ Histórico: OFF" if not st.session_state.quick_hist else "✅ Histórico: ON"
    if st.button(label, use_container_width=True):
        st.session_state.quick_hist = not st.session_state.quick_hist

prod_txt = st.session_state.quick_produto if st.session_state.quick_produto else "—"
modo_txt = "Histórico" if st.session_state.quick_hist else "Última atualização"
st.markdown(
    f"""
<span class="joy-pilltag">Produto: {prod_txt}</span>
<span class="joy-pilltag">Modo: {modo_txt}</span>
""",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# RESULTADO (card premium + vídeo grande só aqui)
# =========================
if do_search and st.session_state.query.strip():
    q = st.session_state.query.strip()
    demanda_id, empresa_term, produto, historico, date_since = parse_user_message(q)

    # aplica filtros rápidos se não veio no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    result = filter_df(df, demanda_id, empresa_term, produto, date_since)

    if result.empty:
        st.markdown("<div class='joy-card'>", unsafe_allow_html=True)
        st.markdown("<div class='joy-card-title'>😅 Não encontrei nada</div>", unsafe_allow_html=True)
        st.markdown("<div class='joy-muted'>Dicas: tente só o <b>ID</b> (ex: 6163) ou só a empresa (ex: Leadec).</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Layout do resultado: texto + vídeo grande no lado
        st.markdown("<div class='joy-card'>", unsafe_allow_html=True)
        r1, r2 = st.columns([2.2, 1], vertical_alignment="top")

        with r1:
            if historico:
                st.markdown("<div class='joy-card-title'>🗂️ Histórico</div>", unsafe_allow_html=True)
                st.markdown("<div class='joy-muted'>Mais recente primeiro — consulta: <b>" + q + "</b></div>", unsafe_allow_html=True)
                st.markdown("<div class='joy-hr'></div>", unsafe_allow_html=True)

                view = result[[COL_DATE, COL_STATUS, COL_PRODUTO, COL_AUTOR, COL_TEXTO]].copy()
                view[COL_DATE] = view[COL_DATE].dt.strftime("%d/%m/%Y")
                view = view.rename(columns={
                    COL_DATE: "Data",
                    COL_STATUS: "Status",
                    COL_PRODUTO: "Produto",
                    COL_AUTOR: "Autor",
                    COL_TEXTO: "Atualização",
                })
                st.dataframe(view, use_container_width=True, hide_index=True)
            else:
                r = result.iloc[0]
                d = r[COL_DATE].strftime("%d/%m/%Y") if pd.notna(r[COL_DATE]) else "—"
                badge = badge_text(r[COL_STATUS])

                st.markdown(
                    f"<div class='joy-card-title'>📌 Última atualização <span class='joy-badge'>{badge}</span></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div class='joy-muted'>Consulta: <b>" + q + "</b></div>", unsafe_allow_html=True)
                st.markdown("<div class='joy-hr'></div>", unsafe_allow_html=True)

                st.markdown(
                    f"""
<div class="joy-grid">
  <b>ID</b><span>{r[COL_ID]}</span>
  <b>Empresa</b><span>{r[COL_EMPRESA]}</span>
  <b>Demanda</b><span>{r[COL_DEMANDA]}</span>
  <b>Produto</b><span>{r[COL_PRODUTO]}</span>
  <b>Status</b><span>{r[COL_STATUS]}</span>
  <b>Data</b><span>{d}</span>
  <b>Autor</b><span>{r[COL_AUTOR]}</span>
</div>
<div class="joy-hr"></div>
<b>Resumo</b><br>
<span>{r[COL_TEXTO]}</span>
""",
                    unsafe_allow_html=True,
                )

        with r2:
            st.markdown("<div class='joy-muted' style='margin-bottom:6px;'>J.O.Y. confirmando a entrega ✅</div>", unsafe_allow_html=True)
            st.markdown("<div class='joy-video-wrap'>", unsafe_allow_html=True)
            st.video(VIDEO_RESULT, loop=True, autoplay=True, muted=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
