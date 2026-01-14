import re
import base64
import random
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
ASSISTANT_NAME = "LARA"
APP_TITLE = f"{ASSISTANT_NAME} – Estagiária Placement"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💬",
    layout="centered",
)

ASSETS_DIR = Path("assets") / "lara"

VIDEO_IDLE = ASSETS_DIR / "Lara_idle.mp4"          # topo FIXO
VIDEO_LOADING = ASSETS_DIR / "Lara_loading.mp4"    # (se quiser usar no futuro)
VIDEO_SUCCESS = ASSETS_DIR / "Lara_success.mp4"

# vídeos "extras" pra randomizar no resultado
RESULT_VIDEOS = [
    ASSETS_DIR / "Lara_success.mp4",
    ASSETS_DIR / "Lara_01.mp4",
    ASSETS_DIR / "Lara_02.mp4",
]

SHEETS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7eJXK_IARZPmt6GdsQLDPX4sSI-aCWZK286Y4DtwhVXr3NOH22eTIPwkFSbF14rfdYReQndgU51st/pub?gid=0&single=true&output=csv"

COL_ID = "COD_ACRISURE"
COL_DATE = "DATA_ATUALIZACAO"
COL_EMPRESA = "EMPRESA"
COL_DEMANDA = "DEMANDA"
COL_PRODUTO = "PRODUTO"
COL_AUTOR = "AUTOR"
COL_STATUS = "STATUS"
COL_TEXTO = "TEXTO"

# =========================================================
# FRASES HUMANIZADAS (10 variações)
# =========================================================
SEARCHING_PHRASES = [
    "Opa! Só um segundinho… deixa eu puxar isso aqui pra você 🔎",
    "Já peguei! Só vou consultar aqui rapidinho e te trago 😉",
    "Beleza — tô indo buscar nos registros agora. Um instante 🔍",
    "Entendi! Deixa comigo… conferindo aqui agora 🧾",
    "Certo! Só vou abrir a planilha e checar isso pra você 📄",
    "Opa, bora lá! Tô consultando e já volto com a resposta 🏃‍♀️",
    "Show! Deixa eu localizar isso aqui… já te trago 🙌",
    "Ok! Só um tiquinho… carregando as infos certinhas 📌",
    "Anotado! Deixa eu buscar direitinho pra não te passar errado ✅",
    "Fechado! Tô indo lá conferir e já te atualizo 💬",
]

NOT_FOUND_PHRASES = [
    "Opa, desculpa! Não encontrei nada com esses critérios 😅",
    "Puts… não achei nada com esse filtro 😬",
    "Hmm… procurei aqui e não apareceu resultado 🥲",
    "Ih, dessa vez não veio nada — mas a gente resolve já já 😄",
]

NOT_FOUND_TIP = "Tenta só **ID** (ex.: **6163**) ou só **empresa** (ex.: **Leadec**)."

# =========================================================
# CSS (premium + remove “quadro/linhas” do vídeo)
# =========================================================
st.markdown(
    """
<style>
:root{
  --lara-bg: #ffffff;
}

.block-container{
  padding-top: 1.2rem;
  padding-bottom: 1.2rem;
  max-width: 1040px;
}

/* Card topo */
.joy-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 18px 18px 14px 18px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 14px 35px rgba(0,0,0,.06);
}

.joy-title{
  font-size: 30px;
  line-height: 1.05;
  margin: 0 0 6px 0;
  font-weight: 900;
  letter-spacing: -0.3px;
}
.joy-sub{
  color: rgba(0,0,0,.62);
  font-size: 14px;
  margin: 0 0 10px 0;
}
.joy-lead{
  font-size: 15.5px;
  line-height: 1.35;
  margin: 0 0 10px 0;
}
.joy-lead b{ font-weight: 900; }

/* ===== Vídeo SEM player/SEM quadro/SEM linhas =====
   - wrapper com overflow hidden
   - leve zoom + clip pra esconder borda/linhas do mp4
   - fundo branco igual ao app
*/
.lara-video-wrap{
  width: 165px;
  max-width: 165px;
  background: var(--lara-bg) !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;

  overflow: hidden !important;      /* corta qualquer “linha” */
  border-radius: 14px !important;   /* arredonda o recorte (não o vídeo) */
}
.lara-video{
  width: 165px;
  height: auto;
  display:block;

  background: var(--lara-bg) !important;
  outline: none !important;
  box-shadow: none !important;
  border: 0 !important;

  transform: scale(1.03);           /* “zoom” leve pra matar linhas na borda */
  transform-origin: center center;

  clip-path: inset(1px);            /* micro-corte extra */
}

/* Search box */
.joy-search-wrap{
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,.08);
  background: rgba(0,0,0,.02);
}

div[data-baseweb="input"] > div{
  border-radius: 14px !important;
}
div[data-baseweb="input"] input{
  font-size: 15px !important;
  padding-top: 14px !important;
  padding-bottom: 14px !important;
}

.stButton button{
  border-radius: 14px !important;
  height: 48px !important;
  font-weight: 900 !important;
  border: 1px solid rgba(0,0,0,.14) !important;
}
.stButton button:hover{
  border-color: rgba(0,0,0,.25) !important;
  transform: translateY(-1px);
}

/* Refine */
.joy-refine{
  margin-top: 14px;
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 14px 14px 10px 14px;
  background: rgba(255,255,255,.88);
  box-shadow: 0 10px 25px rgba(0,0,0,.05);
}
.joy-refine-title{
  font-weight: 950;
  margin: 0 0 6px 0;
  font-size: 16px;
}
.joy-refine-sub{
  color: rgba(0,0,0,.58);
  font-size: 13px;
  margin: 0 0 10px 0;
}
.joy-badge{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.95);
  font-size: 12.5px;
  color: rgba(0,0,0,.70);
  margin-right: 6px;
}

/* Result header + toolbar */
.joy-result-card{
  margin-top: 14px;
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 14px 14px 12px 14px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 14px 35px rgba(0,0,0,.06);
}

.joy-result-title{
  font-size: 28px;
  font-weight: 950;
  margin: 0;
  letter-spacing: -0.35px;
}
.joy-result-sub{
  color: rgba(0,0,0,.55);
  font-size: 13.5px;
  margin-top: 6px;
}

/* Toolbar (ícones) */
.joy-toolbar{
  display:flex;
  justify-content:flex-end;
  align-items:center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.92);
  border-radius: 12px;
  width: fit-content;
  margin-left: auto;
}
.joy-icon{
  display:inline-flex;
  width: 34px;
  height: 30px;
  align-items:center;
  justify-content:center;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(0,0,0,.02);
  text-decoration:none;
  color: rgba(0,0,0,.70);
  font-size: 15px;
  line-height: 1;
}
.joy-icon:hover{
  background: rgba(0,0,0,.05);
  border-color: rgba(0,0,0,.18);
  color: rgba(0,0,0,.88);
}

/* tabela */
div[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.08);
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# STATE
# =========================================================
if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""
if "last_run_id" not in st.session_state:
    st.session_state.last_run_id = 0
if "result_video_path" not in st.session_state:
    st.session_state.result_video_path = None

# =========================================================
# VIDEO LOOP (base64)
# =========================================================
@st.cache_data(show_spinner=False)
def video_to_data_url(path_str: str) -> str:
    path = Path(path_str)
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def loop_video_html(path: Path, width_px: int = 165):
    """Vídeo em loop/autoplay/muted, sem controles e sem “quadro”."""
    try:
        url = video_to_data_url(str(path))
    except Exception:
        return
    st.markdown(
        f"""
<div class="lara-video-wrap" style="width:{width_px}px;max-width:{width_px}px;">
  <video class="lara-video" width="{width_px}" autoplay muted loop playsinline preload="auto">
    <source src="{url}" type="video/mp4">
  </video>
</div>
""",
        unsafe_allow_html=True,
    )

def pick_result_video() -> Path:
    # escolhe 1 por “execução” e mantém fixo até a próxima busca
    if not RESULT_VIDEOS:
        return VIDEO_SUCCESS
    return random.choice(RESULT_VIDEOS)

# =========================================================
# DATA
# =========================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce", dayfirst=True)
    df[COL_ID] = df[COL_ID].astype(str).str.strip()

    for c in [COL_EMPRESA, COL_DEMANDA, COL_PRODUTO, COL_AUTOR, COL_STATUS, COL_TEXTO]:
        if c in df.columns:
            df[c] = df[c].astype(str).fillna("").str.strip()

    # normaliza PRODUTO pra ajudar comparações
    df["_PRODUTO_N"] = (
        df[COL_PRODUTO]
        .astype(str)
        .str.upper()
        .str.replace("Ç", "C")
        .str.replace("Ú", "U")
        .str.replace("Â", "A")
        .str.replace("Á", "A")
        .str.replace("É", "E")
        .str.replace("Í", "I")
        .str.replace("Ó", "O")
        .str.replace("Õ", "O")
        .str.replace("Ô", "O")
        .str.replace("Ã", "A")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df

df = load_data(SHEETS_CSV_URL)

# =========================================================
# PARSE/FILTER
# =========================================================
def parse_user_message(msg: str):
    m = (msg or "").strip()

    historico = bool(re.search(r"\bhist(ó|o)rico\b|\bhist\b", m, flags=re.I))

    produto = None
    if re.search(r"\bambos\b|\bodonto\+sa(ú|u)de\b|\bsa(ú|u)de\+odonto\b", m, flags=re.I):
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
    cleaned = re.sub(
        r"\bsa(ú|u)de\b|\bodonto\b|\bambos\b|\bodonto\+sa(ú|u)de\b|\bsa(ú|u)de\+odonto\b",
        "",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"desde\s+\d{1,2}/\d{1,2}/\d{4}", "", cleaned, flags=re.I)
    cleaned = cleaned.strip(" -|,;")

    empresa_term = None if demanda_id else cleaned.strip()
    if empresa_term == "":
        empresa_term = None

    return demanda_id, empresa_term, produto, historico, date_since

def match_produto_series(prod_n: pd.Series, produto: str) -> pd.Series:
    """
    Regras:
    - SAÚDE: só linhas com SAUDE e sem ODONTO
    - ODONTO: só linhas com ODONTO e sem SAUDE
    - AMBOS: precisa ter SAUDE e ODONTO na mesma linha
    """
    s = (
        prod_n.astype(str)
        .str.replace("&", " E ", regex=False)
        .str.replace("/", " ", regex=False)
        .str.replace("+", " ", regex=False)
        .str.replace("-", " ", regex=False)
    )

    has_saude = s.str.contains(r"\bSAUDE\b", na=False)
    has_odonto = s.str.contains(r"\bODONTO\b", na=False)

    if produto == "SAÚDE":
        return has_saude & (~has_odonto)
    if produto == "ODONTO":
        return has_odonto & (~has_saude)
    if produto == "AMBOS":
        return has_saude & has_odonto

    return pd.Series([True] * len(prod_n), index=prod_n.index)

def filter_df(df_in: pd.DataFrame, demanda_id=None, empresa_term=None, produto=None, date_since=None):
    out = df_in.copy()

    if demanda_id:
        out = out[out[COL_ID] == str(demanda_id)]

    if empresa_term:
        term = empresa_term.lower()
        out = out[out[COL_EMPRESA].str.lower().str.contains(term, na=False)]

    if produto:
        out = out[match_produto_series(out["_PRODUTO_N"], produto)]

    if date_since is not None:
        out = out[out[COL_DATE] >= date_since]

    return out.sort_values(by=COL_DATE, ascending=False)

def to_csv_bytes(df_export: pd.DataFrame) -> bytes:
    return df_export.to_csv(index=False).encode("utf-8")

def download_icon_link(data_bytes: bytes, filename: str, icon: str, tooltip: str):
    b64 = base64.b64encode(data_bytes).decode("utf-8")
    href = f"data:text/csv;base64,{b64}"
    return f'<a class="joy-icon" href="{href}" download="{filename}" title="{tooltip}">{icon}</a>'

# =========================================================
# HERO
# =========================================================
st.markdown('<div class="joy-card">', unsafe_allow_html=True)

c1, c2 = st.columns([1, 3], vertical_alignment="center")

with c1:
    loop_video_html(VIDEO_IDLE, width_px=165)

with c2:
    st.markdown(f'<div class="joy-title">💬 {ASSISTANT_NAME} – Estagiária Placement</div>', unsafe_allow_html=True)
    st.markdown(
    '<div class="joy-sub">Status, histórico e atualizações dos estudos — sem depender de mensagens no Teams.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="joy-lead"><b>Deixa comigo 😉</b><br>'
    'Eu te ajudo a acompanhar status, histórico e atualizações dos estudos — '
    'sem dor de cabeça e sem Teams.</div>',
    unsafe_allow_html=True,
)

    st.markdown('<div class="joy-search-wrap">', unsafe_allow_html=True)
    with st.form("search_form", clear_on_submit=False):
        s1, s2 = st.columns([6, 2], vertical_alignment="center")
        with s1:
            st.session_state.pending_query = st.text_input(
                "Pesquisar",
                value=st.session_state.pending_query,
                label_visibility="collapsed",
                placeholder="Ex.: 6163 | Leadec | 6163 histórico | Leadec saúde",
            )
        with s2:
            submitted = st.form_submit_button("Buscar", use_container_width=True)

        st.caption("💡 Dica: clique nos filtros abaixo e depois em Buscar — não precisa redigitar.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# REFINE (sem botão de histórico)
# =========================================================
st.markdown('<div class="joy-refine">', unsafe_allow_html=True)
st.markdown('<div class="joy-refine-title">🎛️ Refine sua consulta</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="joy-refine-sub">Esses botões filtram o produto. Histórico fica no texto (ex.: “6163 histórico”).</div>',
    unsafe_allow_html=True,
)

p1, p2, p3, p4 = st.columns([1.2, 1.2, 1.2, 1.2], vertical_alignment="center")
with p1:
    if st.button("🧽 Limpar", use_container_width=True):
        st.session_state.quick_produto = None
with p2:
    if st.button("🩺 Saúde", use_container_width=True):
        st.session_state.quick_produto = "SAÚDE"
with p3:
    if st.button("🦷 Odonto", use_container_width=True):
        st.session_state.quick_produto = "ODONTO"
with p4:
    if st.button("🩺+🦷 Ambos", use_container_width=True):
        st.session_state.quick_produto = "AMBOS"

prod_txt = st.session_state.quick_produto if st.session_state.quick_produto else "—"
st.markdown(
    f"""
<div style="margin-top:10px;">
  <span class="joy-badge"><b>Produto:</b> {prod_txt}</span>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# RESULT RENDER
# =========================================================
def render_result_header(title: str, consulta_label: str, csv_bytes: bytes, filename: str):
    st.markdown('<div class="joy-result-card">', unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1.0, 4.4, 1.2], vertical_alignment="top")

    with col_left:
        # vídeo aleatório no resultado (persistente por execução)
        if not st.session_state.result_video_path:
            st.session_state.result_video_path = pick_result_video()
        loop_video_html(st.session_state.result_video_path, width_px=150)

    with col_mid:
        st.markdown(f'<div class="joy-result-title">💬 {title}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="joy-result-sub">Mais recente primeiro • Consulta: <b>{consulta_label}</b></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        download_link = download_icon_link(csv_bytes, filename, "⬇️", "Exportar CSV")
        st.markdown(f'<div class="joy-toolbar">{download_link}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def show_history(result: pd.DataFrame, consulta_label: str):
    table = result[[COL_DATE, COL_STATUS, COL_PRODUTO, COL_AUTOR, COL_TEXTO]].copy()
    table.rename(
        columns={
            COL_DATE: "Data",
            COL_STATUS: "Status",
            COL_PRODUTO: "Produto",
            COL_AUTOR: "Autor",
            COL_TEXTO: "Atualização",
        },
        inplace=True,
    )
    table["Data"] = pd.to_datetime(table["Data"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("—")
    csv_bytes = to_csv_bytes(table)

    render_result_header("Histórico", consulta_label, csv_bytes, f"historico_{consulta_label}.csv")
    st.dataframe(table, use_container_width=True, hide_index=True)

def show_last_update(result: pd.DataFrame, consulta_label: str):
    r = result.iloc[0]
    d = r[COL_DATE].strftime("%d/%m/%Y") if pd.notna(r[COL_DATE]) else "—"

    export_df = pd.DataFrame([{
        "ID": r[COL_ID],
        "Empresa": r[COL_EMPRESA],
        "Demanda": r[COL_DEMANDA],
        "Produto": r[COL_PRODUTO],
        "Status": r[COL_STATUS],
        "Data": d,
        "Autor": r[COL_AUTOR],
        "Atualização": r[COL_TEXTO],
    }])

    csv_bytes = to_csv_bytes(export_df)

    render_result_header("Última atualização", consulta_label, csv_bytes, f"ultima_atualizacao_{consulta_label}.csv")

    st.markdown(
        f"""
- **ID:** {r[COL_ID]}
- **Empresa:** {r[COL_EMPRESA]}
- **Demanda:** {r[COL_DEMANDA]}
- **Produto:** {r[COL_PRODUTO]}
- **Status:** {r[COL_STATUS]}
- **Data:** {d}
- **Autor:** {r[COL_AUTOR]}

**Resumo:** {r[COL_TEXTO]}
"""
    )

def run_query(q: str):
    q = (q or "").strip()
    if not q:
        st.warning("Digite um ID ou uma empresa para pesquisar.")
        return

    # Mensagem humana (random)
    st.info(random.choice(SEARCHING_PHRASES))

    demanda_id, empresa_term, produto, historico, date_since = parse_user_message(q)

    # aplica refine se não veio no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto

    result = filter_df(df, demanda_id, empresa_term, produto, date_since)

    if result.empty:
        st.error(f"{random.choice(NOT_FOUND_PHRASES)}\n\n{NOT_FOUND_TIP}")
        return

    consulta_label = demanda_id or (empresa_term if empresa_term else "consulta")

    if historico:
        show_history(result, consulta_label)
    else:
        show_last_update(result, consulta_label)

# =========================================================
# RUN (recarrega o resultado de forma “limpa”)
# =========================================================
if "submitted" in locals() and submitted:
    st.session_state.last_run_id += 1
    st.session_state.result_video_path = None  # força novo vídeo aleatório por busca

with st.container(key=f"result_container_{st.session_state.last_run_id}"):
    if "submitted" in locals() and submitted:
        run_query(st.session_state.pending_query)
