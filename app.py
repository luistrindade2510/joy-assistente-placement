import re
import time
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="JOY – Assistente Placement Jr",
    page_icon="💬",
    layout="centered",
)

# =========================
# CSS (PREMIUM + ALINHADO)
# =========================
st.markdown(
    """
<style>
/* Layout geral */
.block-container { padding-top: 1.8rem; padding-bottom: 2rem; max-width: 1040px; }
section[data-testid="stSidebar"] { display:none; }

/* Card topo */
.joy-card{
  border: 1px solid rgba(15,23,42,.08);
  border-radius: 20px;
  padding: 18px 20px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 18px 40px rgba(15,23,42,.08);
}

/* Hero */
.joy-hero{
  display:flex;
  align-items:center;
  gap: 18px;
}

.joy-title{
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin: 0 0 6px 0;
}

.joy-sub{
  color: rgba(15,23,42,.65);
  font-size: 14px;
  line-height: 1.35;
  margin: 0 0 10px 0;
}

.joy-lead{
  font-size: 15px;
  line-height: 1.45;
  margin: 0;
}

.joy-pill{
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(248,250,252,.9);
  color: rgba(15,23,42,.75);
  font-size: 12px;
  margin-top: 10px;
}

/* Vídeo compacto */
.joy-video-wrap { width: 150px; max-width: 150px; }
.joy-video{
  width: 150px;
  height: auto;
  border-radius: 16px;
  display:block;
  box-shadow: 0 12px 26px rgba(15,23,42,.12);
}

/* Seções */
.joy-section{
  margin-top: 16px;
  border: 1px solid rgba(15,23,42,.08);
  border-radius: 18px;
  padding: 14px 16px;
  background: rgba(255,255,255,.86);
  box-shadow: 0 10px 24px rgba(15,23,42,.05);
}

.joy-section-title{
  display:flex;
  align-items:center;
  gap: 10px;
  font-weight: 800;
  letter-spacing: -0.2px;
  margin: 0 0 6px 0;
}

.joy-muted{
  color: rgba(15,23,42,.62);
  font-size: 13px;
  margin: 0 0 10px 0;
}

/* Busca (input + botão) */
.joy-search-row{
  display:flex;
  gap: 10px;
  align-items: center;
}

div[data-testid="stTextInput"] input{
  border-radius: 14px !important;
  padding: 14px 14px !important;
  border: 1px solid rgba(15,23,42,.14) !important;
  background: rgba(248,250,252,.95) !important;
}

div[data-testid="stButton"] > button{
  border-radius: 14px !important;
  padding: 12px 14px !important;
  border: 1px solid rgba(15,23,42,.14) !important;
  background: white !important;
  font-weight: 700 !important;
}

div[data-testid="stButton"] > button:hover{
  border-color: rgba(15,23,42,.22) !important;
  box-shadow: 0 10px 22px rgba(15,23,42,.08) !important;
}

/* Botões refine - uniformes */
.joy-btn-row div[data-testid="stButton"] > button{
  width: 100% !important;
  padding: 10px 12px !important;
  border-radius: 999px !important;
  background: rgba(248,250,252,.95) !important;
}

.joy-active div[data-testid="stButton"] > button{
  border-color: rgba(15,23,42,.30) !important;
  background: rgba(226,232,240,.65) !important;
}

/* Resultado */
.joy-result{
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 18px;
  padding: 14px 16px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 18px 40px rgba(15,23,42,.08);
  margin-top: 12px;
}

.joy-kv{
  display:grid;
  grid-template-columns: 180px 1fr;
  gap: 10px 14px;
  margin-top: 10px;
}

.joy-k{
  color: rgba(15,23,42,.65);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
}

.joy-v{
  font-weight: 650;
  color: rgba(15,23,42,.92);
}

/* Esconde o player nativo do video (deixa com cara de loop/anim) */
video::-webkit-media-controls { display:none !important; }
video::-webkit-media-controls-panel { display:none !important; }
video { outline: none; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# ARQUIVOS
# =========================
VIDEO_IDLE = "joy_idle.mp4"
VIDEO_LOADING = "joy_loading.mp4"   # (não vamos exibir agora)
VIDEO_SUCCESS = "joy_success.mp4"

# =========================
# ESTADO
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None  # SAÚDE / ODONTO / AMBOS / None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False

# =========================
# VÍDEO EM LOOP (base64)
# =========================
@st.cache_data(show_spinner=False)
def video_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def loop_video_html(path: str, width_px: int = 150, class_name: str = "joy-video"):
    try:
        url = video_to_data_url(path)
    except Exception:
        return
    st.markdown(
        f"""
<div class="joy-video-wrap">
  <video class="{class_name}" width="{width_px}" autoplay muted loop playsinline preload="auto">
    <source src="{url}" type="video/mp4">
  </video>
</div>
""",
        unsafe_allow_html=True,
    )

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
# PARSE + FILTRO
# =========================
def parse_user_message(msg: str):
    m = msg.strip()

    # histórico
    historico = bool(re.search(r"\bhist(ó|o)rico\b|\bhist\b", m, flags=re.I))

    # produto
    produto = None
    if re.search(r"\bambos\b|\bodonto\+sa(ú|u)de\b", m, flags=re.I):
        produto = "AMBOS"
    elif re.search(r"\bodonto\b", m, flags=re.I):
        produto = "ODONTO"
    elif re.search(r"\bsa(ú|u)de\b", m, flags=re.I):
        produto = "SAÚDE"

    # desde dd/mm/aaaa
    date_since = None
    msince = re.search(r"desde\s+(\d{1,2}/\d{1,2}/\d{4})", m, flags=re.I)
    if msince:
        try:
            date_since = pd.to_datetime(msince.group(1), dayfirst=True)
        except Exception:
            date_since = None

    # ID (3+ dígitos)
    mid = re.search(r"\b(\d{3,})\b", m)
    demanda_id = mid.group(1) if mid else None

    # remove tokens para sobrar empresa
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

# =========================
# UI: TOPO (CARD + VÍDEO + TEXTO)
# =========================
st.markdown('<div class="joy-card">', unsafe_allow_html=True)

left, right = st.columns([1, 3], vertical_alignment="center")

with left:
    loop_video_html(VIDEO_IDLE, width_px=150)

with right:
    st.markdown('<div class="joy-title">💬 JOY – Assistente Placement Jr</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="joy-sub">Status, histórico e andamento dos estudos — sem depender de mensagens no Teams.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="joy-lead"><b>Como pesquisar:</b> digite <b>ID</b> ou <b>empresa</b>. '
        'Para refinar: <b>saúde</b>/<b>odonto</b>, <b>histórico</b>, <b>desde dd/mm/aaaa</b>.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="joy-pill">Exemplos: <b>6163</b> · <b>Leadec</b> · <b>6163 histórico</b> · <b>Leadec saúde desde 10/01/2026</b></div>',
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# UI: BUSCA (input + botão)
# =========================
st.markdown('<div class="joy-section">', unsafe_allow_html=True)
st.markdown('<div class="joy-section-title">🔎 Pesquisa</div>', unsafe_allow_html=True)
st.markdown('<p class="joy-muted">Dica: você pode combinar texto + filtros abaixo. Ex.: <b>Leadec odonto histórico</b></p>', unsafe_allow_html=True)

scol1, scol2 = st.columns([4, 1], vertical_alignment="center")
with scol1:
    q = st.text_input(
        label="",
        placeholder="Digite aqui — ex.: 6163 | Leadec | 6163 histórico | Leadec saúde desde 10/01/2026",
        key="query_input",
    )
with scol2:
    do_search = st.button("Buscar", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# UI: REFINE (botões alinhados)
# =========================
st.markdown('<div class="joy-section">', unsafe_allow_html=True)
st.markdown('<div class="joy-section-title">🎛️ Refine</div>', unsafe_allow_html=True)
st.markdown('<p class="joy-muted">Escolha opções abaixo (opcional). Elas entram junto com o que você digitou.</p>', unsafe_allow_html=True)

r1, r2, r3, r4, r5 = st.columns(5)

# helpers para aplicar classe "ativo"
def wrap_active(is_active: bool):
    return '<div class="joy-active">' if is_active else '<div>'

with r1:
    st.markdown(wrap_active(False), unsafe_allow_html=True)
    if st.button("🧽 Limpar", use_container_width=True):
        st.session_state.quick_produto = None
        st.session_state.quick_hist = False
        st.session_state.query_input = ""
    st.markdown("</div>", unsafe_allow_html=True)

with r2:
    st.markdown(wrap_active(st.session_state.quick_produto == "SAÚDE"), unsafe_allow_html=True)
    if st.button("🩺 Saúde", use_container_width=True):
        st.session_state.quick_produto = "SAÚDE"
    st.markdown("</div>", unsafe_allow_html=True)

with r3:
    st.markdown(wrap_active(st.session_state.quick_produto == "ODONTO"), unsafe_allow_html=True)
    if st.button("🦷 Odonto", use_container_width=True):
        st.session_state.quick_produto = "ODONTO"
    st.markdown("</div>", unsafe_allow_html=True)

with r4:
    st.markdown(wrap_active(st.session_state.quick_produto == "AMBOS"), unsafe_allow_html=True)
    if st.button("🩺+🦷 Ambos", use_container_width=True):
        st.session_state.quick_produto = "AMBOS"
    st.markdown("</div>", unsafe_allow_html=True)

with r5:
    st.markdown(wrap_active(st.session_state.quick_hist is True), unsafe_allow_html=True)
    label = "🗂️ Histórico: ON" if st.session_state.quick_hist else "🗂️ Histórico: OFF"
    if st.button(label, use_container_width=True):
        st.session_state.quick_hist = not st.session_state.quick_hist
    st.markdown("</div>", unsafe_allow_html=True)

prod_txt = st.session_state.quick_produto if st.session_state.quick_produto else "—"
modo_txt = "Histórico" if st.session_state.quick_hist else "Última atualização"
st.markdown(
    f'<p class="joy-muted" style="margin-top:10px;"><b>Ativo:</b> Produto = <b>{prod_txt}</b> · Modo = <b>{modo_txt}</b></p>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# EXECUTA BUSCA
# =========================
def render_last_update(row: pd.Series):
    d = row[COL_DATE]
    d_str = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"

    st.markdown('<div class="joy-result">', unsafe_allow_html=True)

    topL, topR = st.columns([3, 1], vertical_alignment="center")
    with topL:
        st.markdown("### 📌 Última atualização")
        st.markdown(f"<span class='joy-muted'>Consulta: <b>{row[COL_ID]}</b></span>", unsafe_allow_html=True)
    with topR:
        # SÓ AQUI mostra o vídeo (sucesso), em loop e com cara de animação
        loop_video_html(VIDEO_SUCCESS, width_px=170)

    st.markdown(
        f"""
<div class="joy-kv">
  <div class="joy-k">ID</div><div class="joy-v">{row[COL_ID]}</div>
  <div class="joy-k">Empresa</div><div class="joy-v">{row[COL_EMPRESA]}</div>
  <div class="joy-k">Demanda</div><div class="joy-v">{row[COL_DEMANDA]}</div>
  <div class="joy-k">Produto</div><div class="joy-v">{row[COL_PRODUTO]}</div>
  <div class="joy-k">Status</div><div class="joy-v">{row[COL_STATUS]}</div>
  <div class="joy-k">Data</div><div class="joy-v">{d_str}</div>
  <div class="joy-k">Autor</div><div class="joy-v">{row[COL_AUTOR]}</div>
</div>
<hr style="border:none;border-top:1px solid rgba(15,23,42,.08);margin:12px 0;">
<div class="joy-k">Resumo</div>
<div class="joy-v" style="font-weight:600;">{row[COL_TEXTO]}</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

def render_history(df_hist: pd.DataFrame, consulta_label: str):
    st.markdown('<div class="joy-result">', unsafe_allow_html=True)

    topL, topR = st.columns([3, 1], vertical_alignment="center")
    with topL:
        st.markdown("### 🗂️ Histórico")
        st.markdown(f"<span class='joy-muted'>Mais recente primeiro · Consulta: <b>{consulta_label}</b></span>", unsafe_allow_html=True)
    with topR:
        loop_video_html(VIDEO_SUCCESS, width_px=170)

    # tabela clean
    view = df_hist[[COL_DATE, COL_STATUS, COL_PRODUTO, COL_AUTOR, COL_TEXTO]].copy()
    view.rename(
        columns={
            COL_DATE: "Data",
            COL_STATUS: "Status",
            COL_PRODUTO: "Produto",
            COL_AUTOR: "Autor",
            COL_TEXTO: "Atualização",
        },
        inplace=True,
    )
    view["Data"] = view["Data"].dt.strftime("%d/%m/%Y").fillna("—")

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

def run_search(query_text: str):
    if not query_text or not query_text.strip():
        st.info("Digite um ID ou uma empresa para pesquisar.")
        return

    # aplica filtros rápidos no texto (sem poluir o input visualmente)
    qtxt = query_text.strip()

    demanda_id, empresa_term, produto, historico, date_since = parse_user_message(qtxt)

    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    # loading: SEM vídeo
    with st.spinner("Buscando na base..."):
        time.sleep(0.2)

    result = filter_df(df, demanda_id, empresa_term, produto, date_since)

    if result.empty:
        st.warning(
            "Não encontrei nada com esses critérios.\n\n"
            "Tenta assim: **6163** · **Leadec** · **Leadec saúde** · **6163 histórico**"
        )
        return

    if historico:
        label = demanda_id if demanda_id else (empresa_term if empresa_term else "consulta")
        render_history(result, str(label))
    else:
        render_last_update(result.iloc[0])

# dispara por botão
if do_search:
    run_search(q)

# =========================
# (Opcional) CHAT embaixo - se quiser manter histórico
# =========================
# Se você não quiser chat nenhum, é só apagar esse bloco.
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
with st.expander("💬 Abrir histórico (opcional)", expanded=False):
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    msg = st.chat_input("Enviar uma consulta aqui também (opcional)")
    if msg:
        st.session_state.messages.append({"role": "user", "content": msg})
        with st.chat_message("user"):
            st.markdown(msg)
        # executa a mesma busca e joga resultado no chat
        with st.chat_message("assistant"):
            run_search(msg)
