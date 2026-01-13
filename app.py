import re
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="J.O.Y – Assistente Placement Jr",
    layout="centered",
)

# =========================
# ARQUIVOS
# =========================
VIDEO_TOP = "joy_idle.mp4"         # vídeo do topo (fica)
VIDEO_RESULT = "joy_success.mp4"   # vídeo do resultado (fica)

# =========================
# CSS (PREMIUM / PRODUTO)
# =========================
st.markdown(
    """
<style>
.block-container { max-width: 980px; padding-top: 1.4rem; padding-bottom: 2.2rem; }

/* Hero card */
.joy-hero{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 18px;
  padding: 18px 18px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 10px 25px rgba(0,0,0,.06);
}

.joy-title{
  font-size: 28px;
  font-weight: 760;
  line-height: 1.15;
  margin: 0;
}
.joy-sub{
  margin-top: 6px;
  color: rgba(0,0,0,.62);
  font-size: 14px;
}
.joy-lead{
  margin-top: 10px;
  font-size: 15px;
  color: rgba(0,0,0,.90);
  line-height: 1.45;
}

.joy-section-title{
  font-weight: 700;
  margin-top: 14px;
  margin-bottom: 8px;
  font-size: 15px;
}
.joy-muted{
  color: rgba(0,0,0,.58);
  font-size: 13px;
}

/* Sugestões */
.joy-suggest{
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Filtros */
.joy-filters{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 16px;
  padding: 12px 12px;
  background: rgba(255,255,255,.70);
}
.joy-chip{
  display:inline-block;
  padding: 6px 10px;
  margin: 6px 8px 0 0;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.10);
  background: rgba(255,255,255,.95);
  font-size: 12.5px;
}

/* Chat input */
.stChatInput{ margin-top: 1rem; }
.stChatInput textarea{ border-radius: 14px !important; }

/* Resultado */
.joy-result-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 16px;
  padding: 14px 14px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 10px 22px rgba(0,0,0,.05);
}
.joy-kv{
  display:grid;
  grid-template-columns: 140px 1fr;
  gap: 6px 10px;
  margin-top: 10px;
  font-size: 14px;
}
.joy-kv b{ color: rgba(0,0,0,.80); }
.joy-kv span{ color: rgba(0,0,0,.88); }
.joy-hr{
  margin: 14px 0;
  border-bottom: 1px solid rgba(0,0,0,.08);
}

/* Vídeo pequeno */
.joy-video-wrap{ width: 120px; max-width: 120px; }
.joy-video{
  width: 120px;
  height: auto;
  border-radius: 14px;
  display:block;
}

/* Linha topo com vídeo + texto */
.joy-row{
  display:flex;
  gap: 14px;
  align-items:flex-start;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# UTIL: VÍDEO EM LOOP (base64)
# =========================
@st.cache_data(show_spinner=False)
def video_to_data_url(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:video/mp4;base64,{b64}"

def loop_video_html(path: str, width_px: int = 120):
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

# =========================
# ESTADO
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_produto" not in st.session_state:
    st.session_state.quick_produto = None
if "quick_hist" not in st.session_state:
    st.session_state.quick_hist = False

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
# PARSE / FILTRO
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

# =========================
# HERO (com vídeo no topo)
# =========================
st.markdown('<div class="joy-hero">', unsafe_allow_html=True)
st.markdown('<div class="joy-row">', unsafe_allow_html=True)

# ✅ vídeo do topo (fica)
loop_video_html(VIDEO_TOP, width_px=120)

st.markdown(
    """
<div>
  <div class="joy-title">J.O.Y – Assistente Placement Jr</div>
  <div class="joy-sub">Status, histórico e andamento dos estudos — sem depender de mensagens no Teams.</div>
  <div class="joy-lead">
    <b>Como pesquisar:</b> digite <b>ID</b> ou <b>empresa</b>.
    Para refinar, use <b>saúde</b>/<b>odonto</b>, <b>histórico</b> e <b>desde dd/mm/aaaa</b>.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FILTROS
# =========================
st.markdown('<div class="joy-section-title">🎛️ Refine sua consulta</div>', unsafe_allow_html=True)
st.markdown('<div class="joy-muted">Dica: dá pra combinar (empresa/ID + saúde/odonto + histórico + desde data).</div>', unsafe_allow_html=True)

st.markdown('<div class="joy-filters">', unsafe_allow_html=True)

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
<b>Consulta atual:</b>
<span class="joy-chip">Produto: {prod_txt}</span>
<span class="joy-chip">Modo: {modo_txt}</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
st.write("")

# =========================
# CHAT (histórico)
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

    demanda_id, empresa_term, produto, historico, date_exact, date_since = parse_user_message(user_msg)

    # aplica filtros rápidos se não veio no texto
    if not produto and st.session_state.quick_produto:
        produto = st.session_state.quick_produto
    if not historico and st.session_state.quick_hist:
        historico = True

    result = filter_df(df, demanda_id, empresa_term, produto, date_exact, date_since)

    with st.chat_message("assistant"):
        # ❌ SEM vídeo no loading (APENAS texto)
        st.markdown("Só um segundo… tô puxando os dados aqui 🔎")

    # (sem video aqui!)
    # (sem st.spinner também, pq você não quer a tela “poluída”)
    # Se quiser deixar mais rápido ou mais lento, mexe aqui:
    # time.sleep(0.2)

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
            # ✅ vídeo SÓ no resultado
            loop_video_html(VIDEO_RESULT, width_px=120)

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
                st.markdown('<div class="joy-result-card">', unsafe_allow_html=True)
                st.markdown("**🗂️ Histórico (mais recente primeiro)**")
                st.markdown('<div class="joy-hr"></div>', unsafe_allow_html=True)
                st.dataframe(view, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                r = result.iloc[0]
                d = r[COL_DATE].strftime("%d/%m/%Y") if pd.notna(r[COL_DATE]) else "—"

                st.markdown('<div class="joy-result-card">', unsafe_allow_html=True)
                st.markdown("**📌 Última atualização**")

                st.markdown(
                    f"""
<div class="joy-kv">
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
