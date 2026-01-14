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
# CSS (CARD COMPACTO + PREMIUM)
# =========================
st.markdown(
    """
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 980px; }

/* Card topo */
.joy-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 18px 18px;
  background: rgba(255,255,255,.90);
  box-shadow: 0 10px 25px rgba(0,0,0,.06);
}

/* Texto */
.joy-muted{ color: rgba(0,0,0,.60); font-size: 14px; margin-top: 4px; }
.joy-lead{ font-size: 16px; margin-top: 8px; line-height: 1.35; }

/* Chips */
.joy-chip{
  display:inline-block;
  padding: 6px 10px;
  margin: 6px 8px 0 0;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.95);
  font-size: 13px;
}

/* Vídeo compacto (no lugar da imagem) */
.joy-video-wrap{
  width: 150px;
  max-width: 150px;
}
.joy-video{
  width: 150px;
  height: auto;
  border-radius: 14px;
  display:block;
}

/* Seção filtros */
.joy-section-title{
  font-weight: 650;
  margin-top: 18px;
  margin-bottom: 6px;
}

/* Chat input mais “colado” */
.stChatInput{ margin-top: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# ARQUIVOS
# =========================
VIDEO_IDLE = "joy_idle.mp4"
VIDEO_LOADING = "joy_loading.mp4"
VIDEO_SUCCESS = "joy_success.mp4"

# =========================
# ESTADO
# =========================
if "state" not in st.session_state:
    st.session_state.state = "idle"  # idle | loading | success

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# VÍDEO EM LOOP (base64 → funciona no Streamlit Cloud)
# =========================
@st.cache_data(show_spinner=False)
def video_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def loop_video_html(path: str, width_px: int = 150):
    """
    Mostra vídeo pequeno em loop/autoplay/muted.
    Usa base64 para funcionar no Streamlit Cloud.
    """
    try:
        url = video_to_data_url(path)
    except Exception:
        return  # se não achar o arquivo, só não mostra

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

# =========================
# TOPO (CARD + VÍDEO PEQUENO + TEXTO)
# =========================
st.markdown('<div class="joy-card">', unsafe_allow_html=True)

c1, c2 = st.columns([1, 3], vertical_alignment="center")

with c1:
    # vídeo pequeno, no tamanho da imagem antiga
    loop_video_html(VIDEO_IDLE, width_px=150)

with c2:
    st.markdown("## 💬 JOY – Assistente Placement Jr")
    st.markdown(
        '<div class="joy-muted">Status, histórico e andamento dos estudos — sem depender de mensagens no Teams.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="joy-lead"><b>Consulte estudos de Placement com clareza e rapidez.</b><br>'
        'Digite o código da demanda ou o nome da empresa para começar.</div>',
        unsafe_allow_html=True,
    )

 )

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FILTROS RÁPIDOS
# =========================
st.markdown('<div class="joy-section-title">🎛️ Refine sua consulta</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="joy-muted">Dica: você pode combinar (empresa/ID + saúde/odonto + histórico + desde data).</div>',
    unsafe_allow_html=True,
)

if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False

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
<b>Consulta atual:</b> Produto = <b>{prod_txt}</b> • Modo = <b>{modo_txt}</b>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")  # espaçamento

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
# PARSE (ID/EMPRESA/PRODUTO/HIST/DATAS)
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

    date_exact = None
    mexact = re.search(r"\bem\s+(\d{1,2}/\d{1,2}/\d{4})", m, flags=re.I)
    if mexact:
        try:
            date_exact = pd.to_datetime(mexact.group(1), dayfirst=True)
        except Exception:
            date_exact = None

    mid = re.search(r"\b(\d{3,})\b", m)
    demanda_id = mid.group(1) if mid else None

    cleaned = re.sub(r"\bhist(ó|o)rico\b|\bhist\b", "", m, flags=re.I)
    cleaned = re.sub(r"\bsa(ú|u)de\b|\bodonto\b|\bambos\b|\bodonto\+sa(ú|u)de\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"desde\s+\d{1,2}/\d{1,2}/\d{4}", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\bem\s+\d{1,2}/\d{1,2}/\d{4}", "", cleaned, flags=re.I)
    cleaned = cleaned.strip(" -|,;")

    empresa_term = None if demanda_id else cleaned.strip()
    if empresa_term == "":
        empresa_term = None

    return demanda_id, empresa_term, produto, historico, date_exact, date_since

def filter_df(df: pd.DataFrame, demanda_id=None, empresa_term=None, produto=None, date_exact=None, date_since=None):
    out = df.copy()

    if demanda_id:
        out = out[out[COL_ID] == str(demanda_id)]

    if empresa_term:
        term = empresa_term.lower()
        out = out[out[COL_EMPRESA].str.lower().str.contains(term, na=False)]

    if produto and produto != "AMBOS":
        out = out[out[COL_PRODUTO].str.lower().str.contains(produto.lower(), na=False)]

    if date_exact is not None:
        out = out[out[COL_DATE].dt.date == date_exact.date()]

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
        f"- **Data:** {d_str}\n"
        f"- **Status:** {row[COL_STATUS]}\n"
        f"- **Autor:** {row[COL_AUTOR]}\n\n"
        f"**Resumo:** {row[COL_TEXTO]}"
    )

def format_history(df_hist: pd.DataFrame) -> str:
    lines = ["**🗂️ Histórico (mais recente primeiro):**\n"]
    for _, r in df_hist.iterrows():
        d = r[COL_DATE]
        d_str = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        lines.append(
            f"- **{d_str}** | **{r[COL_STATUS]}** | {r[COL_TEXTO]} _(por {r[COL_AUTOR]})_"
        )
    return "\n".join(lines)

# =========================
# CHAT
# =========================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

hint_parts = []
if st.session_state.quick_produto:
    hint_parts.append(st.session_state.quick_produto.lower())
if st.session_state.quick_hist:
    hint_parts.append("histórico")
hint_txt = " • ".join(hint_parts) if hint_parts else "ex.: 6163 | Leadec | Leadec desde 10/01/2026"

user_msg = st.chat_input(f"Pesquisar (ID ou empresa) — {hint_txt}")

if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # vídeo/loading dentro da resposta
    with st.chat_message("assistant"):
        st.markdown("Só um segundo… tô puxando os dados aqui 🔎")
        loop_video_html(VIDEO_LOADING, width_px=180)

    time.sleep(0.6)

    demanda_id, empresa_term, produto, historico, date_exact, date_since = parse_user_message(user_msg)

    # aplica filtros rápidos se não veio no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    result = filter_df(df, demanda_id, empresa_term, produto, date_exact, date_since)

    with st.chat_message("assistant"):
        if result.empty:
            st.markdown(
                "Não encontrei nada com esses critérios 😅\n\n"
                "Tenta assim:\n"
                "- só o **ID** (ex: **6163**)\n"
                "- ou só parte da empresa (ex: **Leadec**)\n"
                "- ou adiciona **saúde / odonto** pra refinar"
            )
        else:
            # vídeo de sucesso pequeno
            loop_video_html(VIDEO_SUCCESS, width_px=180)

            if historico:
                st.markdown(format_history(result))
            else:
                st.markdown(format_last_update(result.iloc[0]))
