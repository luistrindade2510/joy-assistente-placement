import re
import time
import base64
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================
# CONFIG PÁGINA
# =========================
st.set_page_config(
    page_title="JOY – Assistente Placement Jr",
    page_icon="💬",
    layout="centered",
)

# =========================
# CONSTANTES / DADOS
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

VIDEO_IDLE = "joy_idle.mp4"        # topo (sempre)
VIDEO_SUCCESS = "joy_success.mp4"  # somente no resultado

# =========================
# CSS (PREMIUM + ALINHADO)
# =========================
st.markdown(
    """
<style>
/* área geral */
.block-container { max-width: 1040px; padding-top: 1.8rem; padding-bottom: 2rem; }

/* remove espaçamentos feios de alguns containers */
div[data-testid="stVerticalBlock"] > div { gap: 0.65rem; }

/* HERO card */
.joy-hero{
  border: 1px solid rgba(0,0,0,.07);
  border-radius: 22px;
  padding: 18px 20px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 14px 38px rgba(0,0,0,.07);
}

/* title */
.joy-title{
  font-size: 34px;
  font-weight: 760;
  line-height: 1.1;
  margin: 0;
}
.joy-subtitle{
  margin-top: 8px;
  color: rgba(0,0,0,.64);
  font-size: 15px;
}
.joy-lead{
  margin-top: 10px;
  font-size: 16px;
  line-height: 1.45;
  color: rgba(0,0,0,.84);
}

/* vídeo topo: pequeno, sem “cara de player” */
.joy-video-wrap{
  width: 180px;
  max-width: 180px;
}
.joy-video{
  width: 180px;
  border-radius: 16px;
  overflow: hidden;
  display: block;
  box-shadow: 0 10px 22px rgba(0,0,0,.10);
}

/* refine card */
.joy-refine{
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 18px;
  padding: 14px 14px 10px 14px;
  background: rgba(255,255,255,.85);
}
.joy-refine-h{
  font-weight: 720;
  font-size: 16px;
  margin: 0 0 6px 0;
}
.joy-refine-tip{
  font-size: 13.5px;
  color: rgba(0,0,0,.60);
  margin: 0 0 10px 0;
}

/* botões do refine: padrão + alinhados */
.stButton > button{
  border-radius: 12px !important;
  border: 1px solid rgba(0,0,0,.12) !important;
  background: white !important;
  padding: 10px 12px !important;
  font-weight: 650 !important;
  height: 44px !important;
  box-shadow: 0 8px 18px rgba(0,0,0,.05);
}
.stButton > button:hover{
  border-color: rgba(0,0,0,.22) !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.08);
}
.joy-pill-on{
  border-color: rgba(0,0,0,.30) !important;
  box-shadow: 0 12px 24px rgba(0,0,0,.10) !important;
}

/* chips de status filtros */
.joy-badge{
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.92);
  font-size: 13px;
  margin-right: 8px;
}

/* área do resultado */
.joy-result-card{
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 18px;
  padding: 14px 14px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 12px 28px rgba(0,0,0,.06);
}

/* sucesso vídeo: do tamanho certo */
.joy-success-wrap{
  width: 220px;
}
.joy-success-video{
  width: 220px;
  border-radius: 16px;
  display:block;
  box-shadow: 0 12px 26px rgba(0,0,0,.10);
}

/* chat input: deixa mais “produto” */
section[data-testid="stChatInput"]{
  border-radius: 18px;
}
section[data-testid="stChatInput"] > div{
  border-radius: 18px !important;
  border: 1px solid rgba(0,0,0,.10) !important;
  padding: 8px 10px !important;
  background: rgba(255,255,255,.96) !important;
  box-shadow: 0 14px 30px rgba(0,0,0,.06);
}
section[data-testid="stChatInput"] textarea{
  font-size: 15px !important;
}

/* remove “linha grande feia” que às vezes aparece de container vazio */
hr { display:none; }

/* melhora alinhamento em mobile */
@media (max-width: 900px){
  .joy-video-wrap, .joy-video { width: 140px; max-width: 140px; }
  .joy-success-wrap, .joy-success-video { width: 190px; }
  .joy-title{ font-size: 28px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# HELPERS (VIDEO LOOP BASE64)
# =========================
@st.cache_data(show_spinner=False)
def video_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def render_loop_video(path: str, css_class: str, width_px: int):
    """Vídeo em loop/autoplay/muted sem UI de player (base64)."""
    try:
        url = video_to_data_url(path)
    except Exception:
        return

    st.markdown(
        f"""
<video class="{css_class}" width="{width_px}" autoplay muted loop playsinline preload="auto">
  <source src="{url}" type="video/mp4">
</video>
""",
        unsafe_allow_html=True,
    )


# =========================
# ESTADO
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None  # SAÚDE | ODONTO | AMBOS | None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False


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

    # ID
    mid = re.search(r"\b(\d{3,})\b", m)
    demanda_id = mid.group(1) if mid else None

    # limpa termos para empresa
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

def format_last_update(row: pd.Series) -> str:
    d = row[COL_DATE]
    d_str = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"

    return (
        f"**📌 Última atualização**\n\n"
        f"- **ID:** {row[COL_ID]}\n"
        f"- **Empresa:** {row[COL_EMPRESA]}\n"
        f"- **Demanda:** {row[COL_DEMANDA]}\n"
        f"- **Produto:** {row[COL_PRODUTO]}\n"
        f"- **Status:** {row[COL_STATUS]}\n"
        f"- **Data:** {d_str}\n"
        f"- **Autor:** {row[COL_AUTOR]}\n\n"
        f"**Resumo:** {row[COL_TEXTO]}"
    )

def format_history(df_hist: pd.DataFrame) -> pd.DataFrame:
    # tabela limpinha pro histórico
    tmp = df_hist.copy()
    tmp["Data"] = tmp[COL_DATE].dt.strftime("%d/%m/%Y").fillna("—")
    tmp = tmp.rename(columns={
        COL_STATUS: "Status",
        COL_PRODUTO: "Produto",
        COL_AUTOR: "Autor",
        COL_TEXTO: "Atualização",
    })
    return tmp[["Data", "Status", "Produto", "Autor", "Atualização"]]


# =========================
# HERO (TOPO) — VÍDEO IDLE EM LOOP
# =========================
st.markdown('<div class="joy-hero">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 3], vertical_alignment="center")

with c1:
    st.markdown('<div class="joy-video-wrap">', unsafe_allow_html=True)
    render_loop_video(VIDEO_IDLE, "joy-video", 180)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="joy-title">💬 JOY – Assistente Placement Jr</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="joy-subtitle">Status, histórico e andamento dos estudos — sem depender de mensagens no Teams.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="joy-lead"><b>Pesquise por ID ou empresa.</b> Para refinar, adicione <b>saúde</b>/<b>odonto</b>, '
        '<b>histórico</b> e/ou <b>desde dd/mm/aaaa</b>.</div>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# REFINE (BONITO + PADRÃO)
# =========================
st.markdown('<div class="joy-refine">', unsafe_allow_html=True)
st.markdown('<div class="joy-refine-h">🎛️ Refine sua consulta</div>', unsafe_allow_html=True)
st.markdown('<div class="joy-refine-tip">Clique para aplicar. Você pode combinar com o que digitar na busca.</div>', unsafe_allow_html=True)

b1, b2, b3, b4, b5 = st.columns([1.05, 1, 1, 1.2, 1.25], vertical_alignment="center")

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
<div style="margin-top:10px;">
  <span class="joy-badge"><b>Produto:</b> {prod_txt}</span>
  <span class="joy-badge"><b>Modo:</b> {modo_txt}</span>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)


# =========================
# HISTÓRICO CHAT (mantém conversa)
# =========================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


# =========================
# INPUT (BARRA DE PESQUISA)
# =========================
hint = "Ex.: 6163 | Leadec | 6163 histórico | Leadec saúde | desde 10/01/2026"
if st.session_state.quick_produto and not st.session_state.quick_hist:
    hint = f"Ex.: 6163 | Leadec | desde 10/01/2026  •  (filtro ativo: {st.session_state.quick_produto})"
elif st.session_state.quick_hist and not st.session_state.quick_produto:
    hint = "Ex.: 6163 histórico | Leadec histórico | Leadec desde 10/01/2026"
elif st.session_state.quick_hist and st.session_state.quick_produto:
    hint = f"Ex.: 6163 histórico | Leadec histórico desde 10/01/2026  •  (filtros: {st.session_state.quick_produto} + histórico)"

user_msg = st.chat_input(f"Pesquisar (ID ou empresa) — {hint}")


# =========================
# EXECUÇÃO DA BUSCA
# =========================
if user_msg:
    # salva msg do usuário
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # resposta do bot (SEM vídeo no loading)
    with st.chat_message("assistant"):
        st.markdown("Só um segundo… tô puxando os dados aqui 🔎")
    time.sleep(0.4)

    demanda_id, empresa_term, produto, historico, date_since = parse_user_message(user_msg)

    # aplica filtros do refine se não vieram no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    result = filter_df(df, demanda_id, empresa_term, produto, date_since)

    with st.chat_message("assistant"):
        if result.empty:
            st.markdown(
                "Não encontrei nada com esses critérios 😅\n\n"
                "Tenta assim:\n"
                "- só o **ID** (ex: **6163**)\n"
                "- ou só parte da empresa (ex: **Leadec**)\n"
                "- ou adicione **saúde / odonto**\n"
                "- ou **desde dd/mm/aaaa**"
            )
        else:
            # ✅ vídeo success em loop (somente no resultado)
            st.markdown('<div class="joy-success-wrap">', unsafe_allow_html=True)
            render_loop_video(VIDEO_SUCCESS, "joy-success-video", 220)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="joy-result-card">', unsafe_allow_html=True)

            if historico:
                st.markdown("**🗂️ Histórico (mais recente primeiro)**")
                st.dataframe(
                    format_history(result),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.markdown(format_last_update(result.iloc[0]))

            st.markdown("</div>", unsafe_allow_html=True)
