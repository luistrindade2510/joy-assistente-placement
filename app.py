import re
import base64
from pathlib import Path

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
# CSS PREMIUM (DE VERDADE)
# =========================
st.markdown(
    """
<style>
.block-container{max-width:980px;padding-top:1.1rem;padding-bottom:2.2rem}

/* HERO */
.joy-hero{
  border:1px solid rgba(0,0,0,.07);
  border-radius:20px;
  padding:16px 16px;
  background:linear-gradient(180deg, rgba(255,255,255,.96), rgba(255,255,255,.88));
  box-shadow:0 12px 30px rgba(0,0,0,.06);
}
.joy-hero-row{display:flex;gap:14px;align-items:center}
.joy-avatar{
  width:64px;height:64px;border-radius:18px;
  overflow:hidden;
  border:1px solid rgba(0,0,0,.08);
  box-shadow:0 10px 18px rgba(0,0,0,.06);
  background:#fff;
  flex:0 0 auto;
}
.joy-avatar video{width:64px;height:64px;object-fit:cover;display:block}

/* TITULOS */
.joy-title{margin:0;font-size:24px;font-weight:780;line-height:1.12}
.joy-tagline{margin-top:4px;color:rgba(0,0,0,.62);font-size:13px}
.joy-help{margin-top:10px;color:rgba(0,0,0,.86);font-size:14px;line-height:1.45}
.joy-help b{font-weight:740}

/* SEARCH BAR PREMIUM */
.joy-search-wrap{margin-top:14px}
.joy-search-label{font-size:13px;color:rgba(0,0,0,.62);margin-bottom:6px}
div[data-testid="stTextInput"] input{
  border-radius:14px !important;
  border:1px solid rgba(0,0,0,.10) !important;
  padding:12px 14px !important;
}
div[data-testid="stTextInput"] input:focus{
  border:1px solid rgba(0,0,0,.20) !important;
  box-shadow:0 0 0 4px rgba(0,0,0,.06) !important;
}

/* BOTAO BUSCAR */
.joy-btn > button{
  border-radius:14px !important;
  padding:10px 14px !important;
  border:1px solid rgba(0,0,0,.10) !important;
}

/* SUGESTOES */
.joy-suggestions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.joy-pill > button{
  border-radius:999px !important;
  padding:6px 10px !important;
  border:1px solid rgba(0,0,0,.10) !important;
  font-size:12.5px !important;
}

/* FILTROS */
.joy-section-title{font-weight:760;margin-top:14px;margin-bottom:8px;font-size:14px}
.joy-muted{color:rgba(0,0,0,.58);font-size:12.8px}
.joy-filters{
  border:1px solid rgba(0,0,0,.07);
  border-radius:18px;
  padding:12px 12px;
  background:rgba(255,255,255,.70);
}
.joy-chip{
  display:inline-block;
  padding:6px 10px;
  margin:6px 8px 0 0;
  border-radius:999px;
  border:1px solid rgba(0,0,0,.10);
  background:rgba(255,255,255,.95);
  font-size:12px;
}

/* RESULTADO CARD */
.joy-card{
  border:1px solid rgba(0,0,0,.07);
  border-radius:18px;
  padding:14px 14px;
  background:rgba(255,255,255,.92);
  box-shadow:0 10px 22px rgba(0,0,0,.05);
}
.joy-card-title{font-weight:780;font-size:14px;margin:0}
.joy-hr{margin:12px 0;border-bottom:1px solid rgba(0,0,0,.07)}
.joy-grid{
  display:grid;
  grid-template-columns:120px 1fr;
  gap:6px 10px;
  font-size:13.8px;
}
.joy-grid b{color:rgba(0,0,0,.78)}
.joy-grid span{color:rgba(0,0,0,.90)}
.joy-badge{
  display:inline-block;
  padding:5px 10px;
  border-radius:999px;
  border:1px solid rgba(0,0,0,.10);
  background:rgba(0,0,0,.03);
  font-size:12px;
  margin-left:8px;
}

/* VIDEO RESULT PEQUENO */
.joy-result-video{width:110px;border-radius:16px;overflow:hidden;border:1px solid rgba(0,0,0,.08);box-shadow:0 10px 18px rgba(0,0,0,.06)}
.joy-result-video video{width:110px;height:110px;object-fit:cover;display:block}

/* CHAT (deixa mais limpo) */
[data-testid="stChatMessage"]{margin-top:10px}
.stChatInput{margin-top:12px}
.stChatInput textarea{border-radius:14px !important}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# VIDEO LOOP (base64)
# =========================
@st.cache_data(show_spinner=False)
def video_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def video_loop_square(path: str, size_px: int = 64):
    """Avatar do topo (quadradinho arredondado)."""
    try:
        url = video_to_data_url(path)
    except Exception:
        st.markdown(f"<div class='joy-avatar'></div>", unsafe_allow_html=True)
        return
    st.markdown(
        f"""
<div class="joy-avatar">
  <video autoplay muted loop playsinline preload="auto">
    <source src="{url}" type="video/mp4">
  </video>
</div>
""",
        unsafe_allow_html=True,
    )

def video_loop_result(path: str, size_px: int = 110):
    """Video do resultado (aparece só quando tem resposta)."""
    try:
        url = video_to_data_url(path)
    except Exception:
        return
    st.markdown(
        f"""
<div class="joy-result-video">
  <video autoplay muted loop playsinline preload="auto">
    <source src="{url}" type="video/mp4">
  </video>
</div>
""",
        unsafe_allow_html=True,
    )

# =========================
# STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False
if "query" not in st.session_state:
    st.session_state.query = ""

# =========================
# LOAD DATA
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

    out = out.sort_values(by=COL_DATE, ascending=False)
    return out

def status_badge(status: str) -> str:
    s = (status or "").upper()
    if "CONCLU" in s:
        return "Concluído"
    if "ANDAM" in s:
        return "Em andamento"
    if "PEND" in s:
        return "Pendente"
    return status.title() if status else "—"

# =========================
# HERO (compacto + premium)
# =========================
st.markdown("<div class='joy-hero'>", unsafe_allow_html=True)
st.markdown("<div class='joy-hero-row'>", unsafe_allow_html=True)
video_loop_square(VIDEO_TOP)

st.markdown(
    """
<div>
  <div class="joy-title">J.O.Y – Assistente Placement Jr</div>
  <div class="joy-tagline">Acompanhe demandas com status, histórico e última atualização — sem depender de mensagens no Teams.</div>
  <div class="joy-help">
    <b>Pesquise</b> por <b>ID</b> ou <b>empresa</b>.  
    Para refinar, use <b>saúde</b>/<b>odonto</b>, <b>histórico</b> e <b>desde dd/mm/aaaa</b>.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# SEARCH BAR PREMIUM (principal)
# =========================
st.markdown("<div class='joy-search-wrap'>", unsafe_allow_html=True)
st.markdown("<div class='joy-search-label'>🔎 Onde você quer que eu olhe agora?</div>", unsafe_allow_html=True)

c_in, c_btn = st.columns([5, 1.25])
with c_in:
    st.session_state.query = st.text_input(
        label="",
        value=st.session_state.query,
        placeholder="Digite o ID ou empresa… Ex.: 6163 | Leadec | Leadec saúde | desde 10/01/2026",
    )
with c_btn:
    st.markdown("<div class='joy-btn'>", unsafe_allow_html=True)
    do_search = st.button("Buscar", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Sugestões (clicáveis)
st.markdown("<div class='joy-suggestions'>", unsafe_allow_html=True)
sug_cols = st.columns(6)
sugs = ["6163", "6163 histórico", "Leadec", "Leadec saúde", "Leadec odonto", "Leadec desde 10/01/2026"]
for i, s in enumerate(sugs):
    with sug_cols[i]:
        st.markdown("<div class='joy-pill'>", unsafe_allow_html=True)
        if st.button(s, use_container_width=True):
            st.session_state.query = s
            do_search = True
        st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # fecha hero

# =========================
# FILTROS (mais clean)
# =========================
st.markdown("<div class='joy-section-title'>🎛️ Refine sua consulta</div>", unsafe_allow_html=True)
st.markdown("<div class='joy-muted'>Aplique filtros e depois clique em <b>Buscar</b>.</div>", unsafe_allow_html=True)

st.markdown("<div class='joy-filters'>", unsafe_allow_html=True)
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
<div class="joy-muted" style="margin-top:8px;">
<b>Ativo:</b>
<span class="joy-chip">Produto: {prod_txt}</span>
<span class="joy-chip">Modo: {modo_txt}</span>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# CHAT HISTORY (se quiser manter)
# =========================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# =========================
# EXECUTA BUSCA (sem vídeo no loading!)
# =========================
if do_search and st.session_state.query.strip():
    q = st.session_state.query.strip()

    # registra no chat
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    demanda_id, empresa_term, produto, historico, date_since = parse_user_message(q)

    # aplica filtros rápidos se não veio no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    # loading só com texto (sem vídeo)
    with st.chat_message("assistant"):
        st.markdown("Beleza — tô puxando os dados aqui rapidinho 🔎")

    result = filter_df(df, demanda_id, empresa_term, produto, date_since)

    with st.chat_message("assistant"):
        if result.empty:
            st.markdown(
                "Não achei nada com esses critérios 😅\n\n"
                "Tenta assim:\n"
                "- só o **ID** (ex: **6163**)\n"
                "- ou só a empresa (ex: **Leadec**)\n"
                "- ou adiciona **saúde/odonto**"
            )
        else:
            # ✅ vídeo só no resultado
            video_loop_result(VIDEO_RESULT)

            if historico:
                view = result[[COL_DATE, COL_STATUS, COL_PRODUTO, COL_AUTOR, COL_TEXTO]].copy()
                view[COL_DATE] = view[COL_DATE].dt.strftime("%d/%m/%Y")
                view = view.rename(
                    columns={
                        COL_DATE: "Data",
                        COL_STATUS: "Status",
                        COL_PRODUTO: "Produto",
                        COL_AUTOR: "Autor",
                        COL_TEXTO: "Atualização",
                    }
                )
                st.markdown("<div class='joy-card'>", unsafe_allow_html=True)
                st.markdown("<div class='joy-card-title'>🗂️ Histórico (mais recente primeiro)</div>", unsafe_allow_html=True)
                st.markdown("<div class='joy-hr'></div>", unsafe_allow_html=True)
                st.dataframe(view, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                r = result.iloc[0]
                d = r[COL_DATE].strftime("%d/%m/%Y") if pd.notna(r[COL_DATE]) else "—"
                badge = status_badge(r[COL_STATUS])

                st.markdown("<div class='joy-card'>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='joy-card-title'>📌 Última atualização <span class='joy-badge'>{badge}</span></div>",
                    unsafe_allow_html=True,
                )
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
                st.markdown("</div>", unsafe_allow_html=True)

    # guarda resposta no histórico (opcional)
    st.session_state.messages.append({"role": "assistant", "content": "✅ Consulta executada."})

# =========================
# BACKUP: chat_input (se quiser manter também)
# =========================
st.caption("Opcional: você também pode usar o campo abaixo (modo chat).")
chat_msg = st.chat_input("Modo chat — ex.: 6163 | Leadec | Leadec saúde | desde 10/01/2026")
if chat_msg:
    st.session_state.query = chat_msg
    st.rerun()
