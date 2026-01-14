import re
import base64
from pathlib import Path
import pandas as pd
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="JOY – Assistente Placement Jr",
    page_icon="💬",
    layout="centered",
)

VIDEO_IDLE = "joy_idle.mp4"
VIDEO_SUCCESS = "joy_success.mp4"  # aparece só no resultado (pequeno)

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
# CSS (layout anterior atualizado + resultado estilo print)
# =========================================================
st.markdown(
    """
<style>
.block-container{
  padding-top: 1.4rem;
  padding-bottom: 1.2rem;
  max-width: 1040px;
}

/* HERO card */
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
  font-weight: 800;
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
.joy-lead b{ font-weight: 800; }

/* vídeo loop sem cara de player */
.joy-video-wrap{ width: 160px; max-width: 160px; }
.joy-video{
  width: 160px;
  height: auto;
  border-radius: 14px;
  display:block;
  box-shadow: 0 10px 24px rgba(0,0,0,.10);
}

/* Search wrapper */
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
  font-weight: 800 !important;
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
  font-weight: 900;
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

/* Result header (estilo print) */
.joy-result-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 18px;
  margin: 10px 0 8px 0;
}
.joy-result-title{
  font-size: 34px;
  font-weight: 900;
  margin: 0;
  letter-spacing: -0.4px;
}
.joy-result-sub{
  color: rgba(0,0,0,.55);
  font-size: 13.5px;
  margin-top: 6px;
}

/* tabela */
div[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.08);
}

/* expander */
div[data-testid="stExpander"]{
  border-radius: 14px !important;
  border: 1px solid rgba(0,0,0,.08) !important;
}

/* Chat input */
.stChatInput { margin-top: .8rem; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# STATE
# =========================================================
if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None  # SAÚDE | ODONTO | AMBOS | None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

# =========================================================
# VIDEO LOOP (base64)
# =========================================================
@st.cache_data(show_spinner=False)
def video_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def loop_video_html(path: str, width_px: int = 160):
    try:
        url = video_to_data_url(path)
    except Exception:
        return
    st.markdown(
        f"""
<div class="joy-video-wrap">
  <video class="joy-video" width="{width_px}" autoplay muted loop playsinline preload="auto">
    <source src="{url}" type="video/mp4">
  </video>
</div>
""",
        unsafe_allow_html=True,
    )

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

    return df

df = load_data(SHEETS_CSV_URL)

# =========================================================
# PARSE/FILTER
# =========================================================
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

# =========================================================
# HERO (layout anterior)
# =========================================================
st.markdown('<div class="joy-card">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 3], vertical_alignment="center")

with c1:
    loop_video_html(VIDEO_IDLE, width_px=160)

with c2:
    st.markdown('<div class="joy-title">💬 JOY – Assistente Placement Jr</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="joy-sub">Status, histórico e andamento dos estudos — sem depender de mensagens no Teams.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="joy-lead"><b>Consulte estudos de Placement com clareza e rapidez.</b><br>'
        'Pesquise por <b>ID</b> ou <b>empresa</b>. Depois refine com <b>saúde/odonto</b>, <b>histórico</b> e <b>desde dd/mm/aaaa</b>.</div>',
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
                placeholder="Ex.: 6163 | Leadec | Leadec saúde | 6163 histórico | desde 10/01/2026",
            )
        with s2:
            submitted = st.form_submit_button("Buscar", use_container_width=True)

        st.caption("💡 Você pode combinar tudo na mesma frase. Ex.: “Leadec saúde histórico desde 10/01/2026”.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# REFINE (card limpo e alinhado)
# =========================================================
st.markdown('<div class="joy-refine">', unsafe_allow_html=True)
st.markdown('<div class="joy-refine-title">🎛️ Refine sua consulta</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="joy-refine-sub">Esses filtros entram junto com o texto da busca. (Você não precisa digitar “saúde/odonto/histórico” se clicar aqui.)</div>',
    unsafe_allow_html=True,
)

p1, p2, p3, p4, p5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.6], vertical_alignment="center")

with p1:
    if st.button("🧽 Limpar", use_container_width=True):
        st.session_state.quick_produto = None
        st.session_state.quick_hist = False

with p2:
    if st.button("🩺 Saúde", use_container_width=True):
        st.session_state.quick_produto = "SAÚDE"

with p3:
    if st.button("🦷 Odonto", use_container_width=True):
        st.session_state.quick_produto = "ODONTO"

with p4:
    if st.button("🩺+🦷 Ambos", use_container_width=True):
        st.session_state.quick_produto = "AMBOS"

with p5:
    label = "🗂️ Histórico: OFF" if not st.session_state.quick_hist else "✅ Histórico: ON"
    if st.button(label, use_container_width=True):
        st.session_state.quick_hist = not st.session_state.quick_hist

prod_txt = st.session_state.quick_produto if st.session_state.quick_produto else "—"
modo_txt = "Histórico" if st.session_state.quick_hist else "Última atualização"

st.markdown_toggle = st.markdown(
    f"""
<div style="margin-top:10px;">
  <span class="joy-badge"><b>Produto:</b> {prod_txt}</span>
  <span class="joy-badge"><b>Modo:</b> {modo_txt}</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# =========================================================
# RESULT (estilo print + export)
# =========================================================
def render_result_header(title: str, demanda_id: str | None, show_success_video: bool = True):
    # Header + vídeo pequeno (premium) do lado direito
    left, right = st.columns([5, 1.4], vertical_alignment="top")
    with left:
        st.markdown(
            f"""
<div class="joy-result-head">
  <div>
    <div class="joy-result-title">🗂️ {title}</div>
    <div class="joy-result-sub">Mais recente primeiro • Consulta: <b>{demanda_id or "—"}</b></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        if show_success_video:
            loop_video_html(VIDEO_SUCCESS, width_px=170)

def build_export_csv(df_export: pd.DataFrame) -> bytes:
    return df_export.to_csv(index=False).encode("utf-8")

def show_history_table(result: pd.DataFrame, demanda_id: str | None):
    render_result_header("Histórico", demanda_id, show_success_video=True)

    table = result[[COL_DATE, COL_STATUS, COL_PRODUTO, COL_AUTOR, COL_TEXTO]].copy()
    table.rename(columns={
        COL_DATE: "Data",
        COL_STATUS: "Status",
        COL_PRODUTO: "Produto",
        COL_AUTOR: "Autor",
        COL_TEXTO: "Atualização",
    }, inplace=True)

    # formata data
    table["Data"] = table["Data"].dt.strftime("%d/%m/%Y").fillna("—")

    st.dataframe(table, use_container_width=True, hide_index=True)

    # Export
    st.download_button(
        "⬇️ Exportar histórico (CSV)",
        data=build_export_csv(table),
        file_name=f"historico_{demanda_id or 'consulta'}.csv",
        mime="text/csv",
        use_container_width=False,
    )

    # Expander opcional (mais detalhado)
    with st.expander("💬 Abrir histórico (opcional)", expanded=False):
        st.markdown("Aqui você pode ver o texto completo em lista, caso precise copiar/colar:")
        for _, r in result.iterrows():
            d = r[COL_DATE].strftime("%d/%m/%Y") if pd.notna(r[COL_DATE]) else "—"
            st.markdown(f"- **{d}** | **{r[COL_STATUS]}** | {r[COL_TEXTO]} _(por {r[COL_AUTOR]})_")

def show_last_update(result: pd.DataFrame, demanda_id: str | None):
    render_result_header("Última atualização", demanda_id, show_success_video=True)

    r = result.iloc[0]
    d = r[COL_DATE].strftime("%d/%m/%Y") if pd.notna(r[COL_DATE]) else "—"

    left, right = st.columns([3.2, 2], vertical_alignment="top")
    with left:
        st.markdown(
            f"""
**📌 Resumo do estudo**

- **ID:** {r[COL_ID]}
- **Empresa:** {r[COL_EMPRESA]}
- **Demanda:** {r[COL_DEMANDA]}
- **Produto:** {r[COL_PRODUTO]}
- **Status:** {r[COL_STATUS]}
- **Data:** {d}
- **Autor:** {r[COL_AUTOR]}

**Atualização:** {r[COL_TEXTO]}
"""
        )
    with right:
        # Export da “ficha” (1 linha)
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
        st.download_button(
            "⬇️ Exportar última atualização (CSV)",
            data=build_export_csv(export_df),
            file_name=f"ultima_atualizacao_{r[COL_ID]}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Use o export pra mandar no e-mail / anexar na demanda / salvar histórico.")

# =========================================================
# EXECUTE SEARCH
# =========================================================
def run_query(q: str):
    q = (q or "").strip()
    if not q:
        st.warning("Digite um ID ou uma empresa para pesquisar.")
        return

    demanda_id, empresa_term, produto, historico, date_since = parse_user_message(q)

    # aplica refine se não veio no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    # filtra
    result = filter_df(df, demanda_id, empresa_term, produto, date_since)

    if result.empty:
        st.error("Não encontrei nada com esses critérios. Tenta só o ID (ex: 6163) ou só a empresa (ex: Leadec).")
        return

    # se usuário pesquisou empresa (sem ID), mostra “consulta” como termo
    consulta_label = demanda_id or (empresa_term if empresa_term else "—")

    # renderiza conforme modo
    if historico:
        show_history_table(result, consulta_label)
    else:
        show_last_update(result, consulta_label)

# =========================================================
# RUN
# =========================================================
if "submitted" in locals() and submitted:
    run_query(st.session_state.pending_query)
