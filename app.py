import re
import base64
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

# Seus arquivos (no repo)
HERO_LOOP = "joy_idle.mp4"          # loop no topo (estilo gif)
RESULT_LOOP = "joy_success.mp4"     # loop só no resultado (estilo gif)
# se preferir: RESULT_LOOP = "joy_loading.mp4"

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
# CSS (alinhamento de verdade)
# =========================
st.markdown("""
<style>
/* largura */
.block-container { max-width: 980px; padding-top: 1.2rem; padding-bottom: 2.2rem; }

/* cards */
.j-card{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 22px;
  padding: 18px;
  background: rgba(255,255,255,.94);
  box-shadow: 0 16px 36px rgba(0,0,0,.06);
}
.j-gap{ height: 14px; }

/* hero layout */
.j-hero{
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 18px;
  align-items: center;
}
.j-title{
  font-size: 28px;
  font-weight: 900;
  margin: 0;
  line-height: 1.12;
}
.j-sub{
  margin-top: 6px;
  font-size: 13.5px;
  color: rgba(0,0,0,.58);
}
.j-desc{
  margin-top: 10px;
  font-size: 14px;
  color: rgba(0,0,0,.88);
  line-height: 1.55;
}

/* “gif” loop video box */
.j-loop{
  width: 160px;
  height: 160px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,.10);
  box-shadow: 0 14px 28px rgba(0,0,0,.06);
  background: white;
}
.j-loop video{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display:block;
}

/* busca alinhada */
.j-search{
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr 140px;
  gap: 12px;
  align-items: stretch;
}
.j-search input{
  width: 100%;
  height: 46px;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.12);
  padding: 0 14px;
  font-size: 14px;
  background: rgba(248,250,252,.9);
}
.j-search button{
  height: 46px;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.12);
  font-weight: 900;
  cursor: pointer;
  background: white;
}
.j-search button:hover{ background: rgba(0,0,0,.03); }

/* refine */
.j-ref-title{
  font-size: 14px;
  font-weight: 900;
  margin: 0;
}
.j-ref-sub{
  margin-top: 4px;
  font-size: 12.5px;
  color: rgba(0,0,0,.58);
}
.j-ref-grid{
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr 1fr 140px;
  gap: 12px;
  align-items: center;
}
.j-pills{
  display:flex;
  gap:10px;
  flex-wrap: wrap;
}
.j-pill{
  border: 1px solid rgba(0,0,0,.12);
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 13px;
  background: white;
  cursor: pointer;
  user-select:none;
}
.j-pill:hover{ background: rgba(0,0,0,.03); }
.j-pill.on{
  background: rgba(0,0,0,.06);
  border-color: rgba(0,0,0,.18);
  font-weight: 900;
}
.j-clear{
  height: 40px;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.12);
  background: white;
  font-weight: 900;
  cursor:pointer;
}
.j-clear:hover{ background: rgba(0,0,0,.03); }

.j-active{
  margin-top: 10px;
  font-size: 13px;
  color: rgba(0,0,0,.78);
}

/* resultado */
.j-result-head{
  display:flex;
  justify-content: space-between;
  align-items: start;
  gap: 14px;
}
.j-hr{ margin: 12px 0; border-bottom: 1px solid rgba(0,0,0,.08); }
.j-mini-loop{
  width: 150px;
  height: 150px;
  border-radius: 18px;
  overflow:hidden;
  border: 1px solid rgba(0,0,0,.10);
  box-shadow: 0 14px 28px rgba(0,0,0,.06);
  background: white;
}
.j-mini-loop video{ width:100%; height:100%; object-fit: cover; display:block; }

/* dataframe arredondado */
[data-testid="stDataFrame"]{
  border-radius: 16px;
  overflow:hidden;
  border: 1px solid rgba(0,0,0,.08);
}
</style>
""", unsafe_allow_html=True)

# =========================
# STATE
# =========================
if "q" not in st.session_state:
    st.session_state.q = ""
if "produto" not in st.session_state:
    st.session_state.produto = "Todos"  # Todos | Saúde | Odonto | Ambos
if "modo" not in st.session_state:
    st.session_state.modo = "Última atualização"  # Última atualização | Histórico

# =========================
# HELPERS
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

@st.cache_data(show_spinner=False)
def file_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def loop_video_html(path: str, size: int, cls: str):
    """Loop real (sem cara de player)."""
    try:
        b64 = file_to_b64(path)
        return f"""
        <div class="{cls}">
          <video autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{b64}" type="video/mp4">
          </video>
        </div>
        """
    except Exception:
        return ""

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

    empresa_term = None if demanda_id else (cleaned.strip() if cleaned.strip() else None)
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

def produto_from_ui(p):
    if p == "Saúde": return "SAÚDE"
    if p == "Odonto": return "ODONTO"
    if p == "Ambos": return "AMBOS"
    return None

# =========================
# UI - HERO (loop “gif” no lugar da imagem)
# =========================
df = load_data(SHEETS_CSV_URL)

hero_loop = loop_video_html(HERO_LOOP, 160, "j-loop")

st.markdown(f"""
<div class="j-card">
  <div class="j-hero">
    {hero_loop}
    <div>
      <p class="j-title">J.O.Y – Assistente Placement Jr</p>
      <div class="j-sub">Status, histórico e andamento — sem depender de mensagens no Teams.</div>
      <div class="j-desc"><b>Como pesquisar:</b> digite <b>ID</b> ou <b>empresa</b>. Para refinar: <b>saúde/odonto</b>, <b>histórico</b>, <b>desde dd/mm/aaaa</b>.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="j-gap"></div>', unsafe_allow_html=True)

# =========================
# SEARCH BAR (alinhada de verdade)
# =========================
search_html = f"""
<div class="j-card">
  <form class="j-search" method="get">
    <input name="q" placeholder="Ex.: 6163 | Leadec | 6163 histórico | Leadec saúde | desde 10/01/2026" value="{st.session_state.q}">
    <button type="submit">Buscar</button>
  </form>
</div>
"""
# Captura o valor do query param (submit do form)
params = st.query_params
if "q" in params:
    st.session_state.q = params["q"]

st.markdown(search_html, unsafe_allow_html=True)

st.markdown('<div class="j-gap"></div>', unsafe_allow_html=True)

# =========================
# REFINE (pills alinhados)
# =========================
def pill_row(label, options, key):
    current = st.session_state[key]
    cols = st.columns(len(options))
    for i, opt in enumerate(options):
        with cols[i]:
            # “pílula” simulada: botão + estado
            on = (opt == current)
            txt = f"{opt}"
            if st.button(txt, key=f"{key}_{opt}", use_container_width=True):
                st.session_state[key] = opt

st.markdown("""
<div class="j-card">
  <div class="j-ref-title">🎛️ Refine</div>
  <div class="j-ref-sub">Escolha o produto e o modo. Depois clique em <b>Buscar</b>.</div>
</div>
""", unsafe_allow_html=True)

# grid do refine com Streamlit (mais estável)
r1, r2, r3 = st.columns([2.2, 2.2, 1.1], vertical_alignment="center")

with r1:
    st.markdown("**Produto**")
    pcols = st.columns(4)
    for opt, c in zip(["Todos", "Saúde", "Odonto", "Ambos"], pcols):
        with c:
            if st.button(opt, use_container_width=True):
                st.session_state.produto = opt

with r2:
    st.markdown("**Modo**")
    mcols = st.columns(2)
    for opt, c in zip(["Última atualização", "Histórico"], mcols):
        with c:
            if st.button(opt, use_container_width=True):
                st.session_state.modo = opt

with r3:
    st.markdown(" ")
    if st.button("🧽 Limpar", use_container_width=True):
        st.session_state.produto = "Todos"
        st.session_state.modo = "Última atualização"
        st.session_state.q = ""
        st.query_params.clear()

# destaque visual do ativo via texto (limpo)
st.markdown(
    f"<div class='j-active'>Produto: <b>{st.session_state.produto}</b> &nbsp;•&nbsp; Modo: <b>{st.session_state.modo}</b></div>",
    unsafe_allow_html=True
)

# =========================
# RESULT (loop só aqui + sem vídeo no loading)
# =========================
q = (st.session_state.q or "").strip()
if q:
    demanda_id, empresa_term, produto_text, historico_text, date_since = parse_user_message(q)

    produto_final = produto_text or produto_from_ui(st.session_state.produto)
    historico_final = historico_text or (st.session_state.modo == "Histórico")

    result = filter_df(df, demanda_id, empresa_term, produto_final, date_since)

    st.markdown('<div class="j-gap"></div>', unsafe_allow_html=True)
    st.markdown("<div class='j-card'>", unsafe_allow_html=True)

    if result.empty:
        st.markdown("### 😅 Não encontrei nada")
        st.write("Tenta só **6163** ou só **Leadec** (sem mais nada) e depois refina.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        mini_loop = loop_video_html(RESULT_LOOP, 150, "j-mini-loop")

        st.markdown(f"""
<div class="j-result-head">
  <div>
    <h3 style="margin:0;">{"🗂️ Histórico" if historico_final else "📌 Última atualização"}</h3>
    <div style="color:rgba(0,0,0,.58); font-size:13px; margin-top:6px;">Consulta: <b>{q}</b></div>
  </div>
  {mini_loop}
</div>
<div class="j-hr"></div>
""", unsafe_allow_html=True)

        if historico_final:
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

        st.markdown("</div>", unsafe_allow_html=True)
