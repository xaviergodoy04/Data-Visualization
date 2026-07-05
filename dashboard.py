# -*- coding: utf-8 -*-
"""
Dashboard interactivo — Brechas entre el Quintil 1 y el Quintil 5 (CASEN 2024)
Autores: Benjamín Alvear Aravena, Xavier Godoy Cerda y Eduardo Ruiz Quezada

Layout inspirado en el mockup de Figma "Crear diseño solicitado" (sidebar + panel glass),
implementado 100% en Streamlit y alimentado con los datos reales de CASEN 2024.

Ejecutar con:   streamlit run dashboard.py
Requisitos:     pip install streamlit plotly pandas numpy pyarrow
"""
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# Design tokens (calcados del mockup Figma: navy glass + degradados)
# ----------------------------------------------------------------------
C_Q1 = "#F2635B"   # Quintil 1 (más pobre) — no tocar, color semántico
C_Q5 = "#2DD4BF"   # Quintil 5 (más rico) — no tocar, color semántico
DIM = "#a0aec0"
GRID = "rgba(255,255,255,0.08)"
PLOT_BG = "rgba(0,0,0,0)"
FONT = dict(family="'Plus Jakarta Sans', Inter, sans-serif", color="#ffffff")

GRAD = {
    "info":    "linear-gradient(310deg,#2152FF,#21D4FD)",
    "success": "linear-gradient(310deg,#17AD37,#98EC2D)",
    "warning": "linear-gradient(310deg,#F53939,#FBCF33)",
    "primary": "linear-gradient(310deg,#7928CA,#FF0080)",
}
GLASS_CSS = (
    "background:linear-gradient(127deg,rgba(6,11,40,0.74) 0%,rgba(10,14,35,0.49) 100%);"
    "border:1px solid rgba(255,255,255,0.10);border-radius:20px;"
    "backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);"
    "box-shadow:0 8px 24px rgba(0,0,0,0.35);"
)

# Escala tipográfica y de espaciado — un solo lugar para mantener consistencia visual
TYPE = {
    "eyebrow": ".65rem",    # labels en mayúscula (SECCIONES, MOSTRAR SERIES, KPI label)
    "caption": ".72rem",    # texto secundario (badges, pills, delta KPI, tarjeta fuente)
    "body_sm": ".82rem",    # descripciones (subtítulo header, descripción de sección)
    "body":    ".875rem",   # texto de controles (nav, radio, multiselect)
    "title_sm": "1rem",     # títulos pequeños (logo sidebar, nombre de sección)
    "metric":  "1.5rem",    # valor numérico de los KPI
    "title":   "1.375rem",  # título principal del header
}
SPACE = {"xs": "4px", "sm": "8px", "md": "12px", "lg": "16px", "xl": "24px"}


def _rgba(hex_color, alpha):
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _layout(fig, titulo, alto=420):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=17, color="#ffffff")),
        template="plotly_dark", height=alto, font=FONT,
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        margin=dict(l=60, r=30, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff")),
        hoverlabel=dict(bgcolor="#0f1535", bordercolor="rgba(255,255,255,0.15)",
                        font=dict(color="#ffffff", family="Plus Jakarta Sans")),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    return fig


def kpi_card(col, label, value, delta=None, icon="📊", gradient=GRAD["info"], delta_good=True):
    """Tarjeta KPI glass con badge de ícono en degradado (mockup App.tsx líneas 184-209)."""
    if delta is None:
        delta_html = ""
    else:
        up = delta.strip().startswith("+")
        positivo = up if delta_good else (not up)
        color = "#17AD37" if positivo else "#F53939"
        arrow = "▲" if up else "▼"
        delta_html = (f"<div style='font-size:{TYPE['caption']};font-weight:700;color:{color};"
                      f"margin-top:3px'>{arrow} {delta}</div>")
    col.markdown(f"""
<div style="{GLASS_CSS} padding:18px 20px;display:flex;justify-content:space-between;
     align-items:center;gap:{SPACE['md']};">
  <div style="min-width:0">
    <div style="color:{DIM};font-size:{TYPE['eyebrow']};font-weight:700;text-transform:uppercase;
         letter-spacing:.1em">{label}</div>
    <div style="color:#fff;font-size:{TYPE['metric']};font-weight:800;line-height:1.25;margin-top:2px">{value}</div>
    {delta_html}
  </div>
  <div style="flex:none;width:46px;height:46px;border-radius:12px;background:{gradient};
       display:flex;align-items:center;justify-content:center;font-size:1.2rem">{icon}</div>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Configuración general + CSS del shell (sidebar + glass + tipografía)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Quintil 1 vs Quintil 5 · CASEN 2024",
                   page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{ font-family:'Plus Jakarta Sans', Inter, sans-serif; }}
.stApp {{
    background:#060b26;
    background-image:
        radial-gradient(1200px 700px at 88% -8%, rgba(33,82,255,0.22) 0%, transparent 55%),
        radial-gradient(900px 600px at 5% -5%, rgba(121,40,202,0.16) 0%, transparent 52%);
}}
h1, h2, h3, h4 {{ color:#ffffff !important; font-weight:700 !important; letter-spacing:-.01em; }}
.stMarkdown p, .stMarkdown span, .stMarkdown li {{ color:#e2e8f0 !important; }}
.stCaption, [data-testid="stCaptionContainer"] p {{ color:{DIM} !important; }}
#MainMenu, footer {{ visibility:hidden; }}
header[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stToolbar"] {{ background:transparent; }}

/* Fuente Plus Jakarta Sans forzada en TODOS los widgets (BaseWeb fija su propia fuente
   con mayor especificidad que html/body, por eso necesitan su propio !important) */
.stApp button, .stApp input, .stApp label,
[data-baseweb], [data-baseweb] *,
.stButton button, .stButton button p,
[data-testid="stCheckbox"] *, [data-testid="stWidgetLabel"] *,
.stRadio *, .stMultiSelect *, .stAlert *, [data-testid="stCaptionContainer"] * {{
    font-family:'Plus Jakarta Sans', Inter, sans-serif !important;
}}

/* ---- Sidebar shell ---- */
section[data-testid="stSidebar"] {{
    background:linear-gradient(127deg,rgba(6,11,40,0.90) 0%,rgba(10,14,35,0.80) 100%);
    border-right:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(20px);
}}
section[data-testid="stSidebar"] .block-container {{ padding-top:1.4rem; }}

/* Nav buttons (secciones) */
section[data-testid="stSidebar"] .stButton > button {{
    width:100%; display:flex; justify-content:flex-start;
    background:transparent; border:1px solid transparent; color:{DIM} !important;
    font-weight:600; font-size:{TYPE['body']}; border-radius:12px; padding:.55rem .8rem;
    transition:background .15s ease, color .15s ease;
}}
section[data-testid="stSidebar"] .stButton > button p {{ text-align:left; color:inherit !important; }}
section[data-testid="stSidebar"] .stButton > button:hover {{ background:rgba(255,255,255,0.07); color:#fff !important; }}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background:{GRAD['info']} !important; color:#fff !important; border:none !important;
    box-shadow:0 4px 14px rgba(33,82,255,0.40);
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p {{ color:#fff !important; }}
/* Ícono de los botones de navegación en columna fija (los 7 emoji tienen ancho visual
   distinto; sin esto el texto de cada fila no alinea) */
section[data-testid="stSidebar"] [data-testid="stIconEmoji"] {{
    display:inline-block; width:1.4rem; text-align:center; margin-right:{SPACE['xs']};
}}

/* Toggles Q1/Q5 (contenedores con key="tog_q1"/"tog_q5") — tarjeta con tinte propio
   por quintil y color del switch coherente con el dato que representa */
.st-key-tog_q1, .st-key-tog_q5 {{
    border-radius:14px; padding:10px 14px; margin-bottom:{SPACE['sm']}; border:1px solid;
}}
.st-key-tog_q1 {{ background:{_rgba(C_Q1, 0.10)}; border-color:{_rgba(C_Q1, 0.30)}; }}
.st-key-tog_q5 {{ background:{_rgba(C_Q5, 0.10)}; border-color:{_rgba(C_Q5, 0.30)}; }}
[data-testid="stCheckbox"] * {{ color:#ffffff !important; font-weight:600; }}
label[data-baseweb="checkbox"] span {{ color:#ffffff !important; }}
/* :has() pinta el track (hermano ANTERIOR al <input> en el DOM de st.toggle) cuando
   está activo — un combinador de hermanos posteriores no lo alcanzaría */
.st-key-tog_q1 label[data-baseweb="checkbox"]:has(input:checked) > div:first-of-type {{
    background-color:{C_Q1} !important;
}}
.st-key-tog_q5 label[data-baseweb="checkbox"]:has(input:checked) > div:first-of-type {{
    background-color:{C_Q5} !important;
}}

/* Glass panel del gráfico (contenedor con key="chart_panel") */
.st-key-chart_panel {{
    {GLASS_CSS}
    padding:22px 24px !important;
}}

/* Alerts */
.stAlert {{ background:rgba(33,82,255,0.10); border:1px solid rgba(33,212,253,0.30);
    border-radius:16px; backdrop-filter:blur(12px); }}
.stAlert p {{ color:#e2e8f0 !important; }}

/* Multiselect / radio dentro del panel */
.stMultiSelect label p, .stRadio label p {{ color:#ffffff !important; }}
[data-baseweb="tag"] {{ background:{GRAD['info']} !important; }}
</style>
""", unsafe_allow_html=True)

PARQUET = "data/casen_2024.parquet"

# Only load the columns actually used — full 877-col DataFrame exceeds Streamlit Cloud's 1 GB limit
NEEDED_COLS = [
    'qaut', 'expr',
    'yautcorh', 'v13', 'v13_propia', 'v17', 'v18',
    'ytrabajocor', 'educc',
    'ytotcor', 'edad', 'sexo',
    'hh_d_esc', 'hh_d_acc', 'hh_d_ali', 'hh_d_contprev', 'hh_d_dpf',
    'hh_d_actsub', 'hh_d_inf', 'hh_d_jub', 'hh_d_cui', 'hh_d_defcuali',
    'hh_d_defcuanti', 'hh_d_medio', 'hh_d_conec', 'hh_d_seg',
    'ind_estado', 'v12', 'v35a', 'v35c',
    'rama1',
]


# ----------------------------------------------------------------------
# Carga de datos (cacheada)
# ----------------------------------------------------------------------
@st.cache_data(show_spinner="Cargando CASEN 2024…")
def load_data():
    return pd.read_parquet(PARQUET, columns=NEEDED_COLS)


@st.cache_data
def prep_scatter(_df):
    cols = ['qaut', 'yautcorh', 'v13', 'v13_propia', 'v17', 'v18']
    d = _df[cols].copy()
    d = d[d['qaut'].isin([1.0, 5.0]) & (d['yautcorh'] > 0)].copy()
    d = d[~((d['v13'] == 1.0) & (d['v13_propia'].isin([1.0, 3.0])))].copy()
    d = d[~d['v13'].isin([3.0, 9, 10.0, 11.0])].copy()
    d['gasto'] = d['v17'].clip(lower=0).fillna(0) + d['v18'].clip(lower=0).fillna(0)
    d['prop'] = (d['gasto'] / d['yautcorh']) * 100
    d = d[(d['yautcorh'] <= 7_000_000) & (d['prop'] <= 120)].copy()
    d['Quintil'] = d['qaut'].map({1.0: "Quintil 1", 5.0: "Quintil 5"})
    return d[['qaut', 'yautcorh', 'prop', 'Quintil']]


@st.cache_data
def prep_growth(_df):
    dg = _df[['qaut', 'ytrabajocor', 'educc']].copy()
    dg = dg[dg['qaut'].isin([1, 5]) & (dg['ytrabajocor'] > 0)
            & (dg['educc'] >= 0) & (dg['educc'] <= 6)]
    ie = (dg.groupby(['qaut', 'educc'])['ytrabajocor'].mean()
          .reset_index().pivot(index='educc', columns='qaut', values='ytrabajocor'))
    cr = (ie.pct_change() * 100).dropna()
    et = ['Sin Educ. → Básica Inc.', 'Básica Inc. → Básica Comp.', 'Básica Comp. → Media Inc.',
          'Media Inc. → Media Comp.', 'Media Comp. → Superior Inc.', 'Superior Inc. → Sup. Completa']
    cr.index = et
    return cr


@st.cache_data
def prep_lines(_df):
    dc = _df[['qaut', 'ytotcor', 'edad', 'sexo']].dropna().copy()
    dc['qaut'] = dc['qaut'].astype(int)
    dc['Sexo'] = dc['sexo'].map({1: 'Hombre', 2: 'Mujer'})
    dc['Quintil'] = dc['qaut'].map({1: 'Quintil 1', 5: 'Quintil 5'})
    dc = dc[dc['qaut'].isin([1, 5])].copy()
    dc['ge'] = pd.cut(dc['edad'], bins=range(18, 85, 5))
    agg = dc.groupby(['ge', 'Quintil', 'Sexo'], observed=False)['ytotcor'].mean().reset_index()
    agg['Rango'] = agg['ge'].astype(str).str.replace(r'[\(\]]', '', regex=True).str.replace(', ', '–')
    return agg


@st.cache_data
def prep_tornado(_df):
    vp = 'expr'
    dims = [('hh_d_esc', "Escolaridad"), ('hh_d_acc', "Atención de salud"),
            ('hh_d_ali', "Acceso a alimentos"), ('hh_d_contprev', "Control preventivo"),
            ('hh_d_dpf', "Dependencia funcional"), ('hh_d_actsub', "Ocupación y subempleo"),
            ('hh_d_inf', "Informalidad laboral"), ('hh_d_jub', "Jubilaciones"),
            ('hh_d_cui', "Cuidados"), ('hh_d_defcuali', "Déficit cualitativo"),
            ('hh_d_defcuanti', "Déficit cuantitativo"), ('hh_d_medio', "Medioambiente"),
            ('hh_d_conec', "Conectividad digital"), ('hh_d_seg', "Seguridad")]
    cols = [c for c, _ in dims if c in _df.columns]
    dd = pd.DataFrame({c: pd.to_numeric(_df[c], errors='coerce') for c in cols + ['qaut', vp]})
    dd = dd[dd['qaut'].isin([1, 5])]

    def carencia(sub, var):
        if var not in sub.columns:
            return 0.0
        v = sub.dropna(subset=[var, vp])
        return 0.0 if len(v) == 0 else np.average((v[var] == 1).astype(int), weights=v[vp]) * 100

    dq1, dq5 = dd[dd['qaut'] == 1], dd[dd['qaut'] == 5]
    res = [{'Dimensión': lab, 'Q1': carencia(dq1, c), 'Q5': carencia(dq5, c)}
           for c, lab in dims if c in _df.columns]
    return pd.DataFrame(res).sort_values('Q1').reset_index(drop=True)


@st.cache_data
def prep_radar(_df):
    vp = 'expr'
    vn = ['qaut', vp, 'ind_estado', 'v12', 'v13', 'v35a', 'v35c']
    dc = pd.DataFrame({v: pd.to_numeric(_df[v], errors='coerce') for v in vn if v in _df.columns})
    m = dc['ind_estado'] > 0;  dc.loc[m, 'cal'] = (dc.loc[m, 'ind_estado'] == 1).astype(int)
    m = dc['v12'] != -88;      dc.loc[m, 'sup'] = (dc.loc[m, 'v12'] >= 4).astype(int)
    m = dc['v13'] != -88;      dc.loc[m, 'prop'] = dc.loc[m, 'v13'].isin([1, 2]).astype(int)
    m = dc['v35a'] != -88;     dc.loc[m, 'tra'] = (dc.loc[m, 'v35a'] == 1).astype(int)
    m = dc['v35c'] != -88;     dc.loc[m, 'sal'] = (dc.loc[m, 'v35c'] == 1).astype(int)

    def mp(sub, col):
        t = sub.dropna(subset=[col, vp])
        return 0.0 if len(t) == 0 else np.average(t[col], weights=t[vp]) * 100

    ejes = [('prop', 'Casa propia'), ('sup', 'Tamaño vivienda'), ('cal', 'Buen estado'),
            ('tra', 'Transporte cercano'), ('sal', 'Salud cercana')]
    dq1, dq5 = dc[dc['qaut'] == 1], dc[dc['qaut'] == 5]
    return pd.DataFrame({'Eje': [e[1] for e in ejes],
                         'Q1': [mp(dq1, e[0]) for e in ejes],
                         'Q5': [mp(dq5, e[0]) for e in ejes]})


@st.cache_data
def prep_treemap(_df):
    vp, vo = 'expr', 'rama1'
    dt = pd.DataFrame({c: pd.to_numeric(_df[c], errors='coerce') for c in ['qaut', vo, vp]})
    dt = dt[dt['qaut'].isin([1, 5]) & (dt[vo] > 0)].copy()

    def macro(c):
        if c in [1, 2, 3]: return "1. Primario"
        if c in [4, 5, 6]: return "2. Industria/Construcción"
        if c in [7, 8, 9]: return "3. Comercio/Servicios"
        if c in [10, 11, 12, 13, 14]: return "4. Serv. Profesionales"
        return "5. Estado/Educación/Salud"

    subs = {1: "Agricultura y Pesca", 2: "Minería", 3: "Industria Manufacturera", 4: "Electricidad y Gas",
            5: "Agua y Desechos", 6: "Construcción", 7: "Comercio", 8: "Transporte/Almacenamiento",
            9: "Alojamiento y Comidas", 10: "Información y Comunicaciones", 11: "Finanzas y Seguros",
            12: "Inmobiliarias", 13: "Profesionales y Científicas", 14: "Servicios Administrativos",
            15: "Administración Pública", 16: "Enseñanza", 17: "Salud y Asistencia", 18: "Artes y Entretenimiento",
            19: "Otros Servicios", 20: "Servicio Doméstico", 21: "Org. Extraterritoriales"}
    dt['Macro'] = dt[vo].apply(macro)
    dt['Sub'] = dt[vo].map(subs).fillna("Desconocido")
    dt['Quintil'] = dt['qaut'].map({1: "Quintil 1", 5: "Quintil 5"})
    g = dt.groupby(['Quintil', 'Macro', 'Sub'])[vp].sum().reset_index()
    tot = g.groupby('Quintil')[vp].transform('sum')
    g['Pct'] = g[vp] / tot * 100
    return g


@st.cache_data
def prep_lisa():
    with open("data/lisa_clusters.geojson", encoding="utf-8") as f:
        raw = json.load(f)
    features, rows = [], []
    for i, feat in enumerate(raw["features"]):
        features.append({**feat, "id": str(i)})
        rows.append({"_idx": i, **feat.get("properties", {})})
    dlisa = pd.DataFrame(rows).set_index("_idx")
    dlisa['ingreso_fmt'] = (dlisa['ingreso_autonomo'] / 1e3).round(0).astype(int).astype(str) + "K"
    return dlisa, features


# ----------------------------------------------------------------------
# Carga de datos real
# ----------------------------------------------------------------------
try:
    df = load_data()
except Exception as e:
    st.error(f"No pude cargar **{PARQUET}**. Colócalo junto a este archivo.\n\n{e}")
    st.stop()

ing_max, n_pts = 7_000_000, 800

# ----------------------------------------------------------------------
# Secciones de navegación (icono, nombre, descripción)
# ----------------------------------------------------------------------
SECTIONS = [
    dict(icon="🏠", name="Vivienda",
         desc="Carga de vivienda (% del ingreso del hogar) vs ingreso autónomo. "
              "La línea punteada marca el umbral crítico del 30%."),
    dict(icon="🗺️", name="Mapa LISA",
         desc="Autocorrelación espacial del ingreso autónomo por comuna (335 comunas) — "
              "clústers de Moran Local. Identifica patrones geográficos de desigualdad."),
    dict(icon="📈", name="Educación",
         desc="Variación porcentual del ingreso del trabajo al completar cada nivel "
              "educativo, por quintil."),
    dict(icon="👥", name="Edad y Género",
         desc="Ingreso total promedio a lo largo de la vida por tramo etario, quintil y "
              "género (línea sólida = hombres, punteada = mujeres)."),
    dict(icon="🌪️", name="Pobreza",
         desc="Pobreza multidimensional: % de hogares con carencia en cada dimensión. "
              "Quintil 1 a la izquierda, Quintil 5 a la derecha del eje."),
    dict(icon="🧭", name="Calidad de Vida",
         desc="% de hogares que cumple cada atributo de vivienda y acceso urbano, por quintil."),
    dict(icon="🧩", name="Empleo",
         desc="Distribución de ocupados por sector económico dentro del quintil seleccionado."),
]

if "section" not in st.session_state:
    st.session_state.section = 0

# ----------------------------------------------------------------------
# Sidebar — logo, navegación, toggles Q1/Q5, tarjeta de fuente
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
<div style="margin-bottom:1.4rem">
  <h1 style="color:#fff;font-weight:800;font-size:{TYPE['title_sm']};line-height:1.2;margin:0">CASEN 2024</h1>
  <p style="color:{DIM};font-size:{TYPE['caption']};font-weight:600;margin:2px 0 0 0">Quintil 1 vs Quintil 5</p>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"<p style='color:{DIM};font-size:{TYPE['eyebrow']};font-weight:700;"
                f"text-transform:uppercase;letter-spacing:.12em;margin:0 0 4px 4px'>Secciones</p>",
                unsafe_allow_html=True)
    for i, sec in enumerate(SECTIONS):
        active = st.session_state.section == i
        if st.button(sec['name'], key=f"nav_{i}", icon=sec['icon'],
                     type="primary" if active else "secondary", use_container_width=True):
            st.session_state.section = i
            st.rerun()

    st.markdown(f"<div style='height:{SPACE['lg']}'></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{DIM};font-size:{TYPE['eyebrow']};font-weight:700;"
                f"text-transform:uppercase;letter-spacing:.12em;margin:0 0 6px 4px'>Mostrar series</p>",
                unsafe_allow_html=True)
    with st.container(key="tog_q1"):
        ver_q1 = st.toggle("Quintil 1 (más pobre)", value=True)
    with st.container(key="tog_q5"):
        ver_q5 = st.toggle("Quintil 5 (más rico)", value=True)
    quintiles = ([("Quintil 1", C_Q1)] if ver_q1 else []) + ([("Quintil 5", C_Q5)] if ver_q5 else [])

    st.markdown(f"""
<div style="margin-top:{SPACE['lg']};padding:{SPACE['md']} 14px;border-radius:14px;
     font-size:{TYPE['caption']};line-height:1.55;
     background:rgba(33,82,255,0.14);border:1px solid rgba(33,82,255,0.28)">
  <div style="font-weight:700;color:#fff;margin-bottom:{SPACE['xs']}">ℹ️ Fuente</div>
  <div style="color:{DIM}">Encuesta CASEN 2024 · Ministerio de Desarrollo Social y Familia.<br>
  n = {len(df):,} hogares.</div>
</div>
""", unsafe_allow_html=True)

tab = st.session_state.section

# ----------------------------------------------------------------------
# KPIs (calculados sobre los datos reales)
# ----------------------------------------------------------------------
_s = prep_scatter(df)
carga_q1 = _s.loc[_s['Quintil'] == "Quintil 1", 'prop'].mean()
carga_q5 = _s.loc[_s['Quintil'] == "Quintil 5", 'prop'].mean()
_inc = df.loc[df['qaut'].isin([1, 5]), ['qaut', 'yautcorh']]
med_q1 = _inc.loc[_inc['qaut'] == 1, 'yautcorh'].median()
med_q5 = _inc.loc[_inc['qaut'] == 5, 'yautcorh'].median()
ratio = (med_q5 / med_q1) if med_q1 else float('nan')
_t = prep_tornado(df).set_index('Dimensión')
inf_q1, inf_q5 = _t.loc['Informalidad laboral', 'Q1'], _t.loc['Informalidad laboral', 'Q5']
_r = prep_radar(df).set_index('Eje')
casa_q1, casa_q5 = _r.loc['Casa propia', 'Q1'], _r.loc['Casa propia', 'Q5']

# ----------------------------------------------------------------------
# Header principal
# ----------------------------------------------------------------------
st.markdown(f"<h2 style='color:#fff;font-weight:800;font-size:{TYPE['title']};margin:0'>"
            "Brechas entre el Quintil 1 y el Quintil 5 · Encuesta CASEN 2024</h2>",
            unsafe_allow_html=True)
st.markdown(f"<p style='color:{DIM};font-size:{TYPE['body_sm']};line-height:1.3;margin:3px 0 0 0'>"
            "Autores: Benjamín Alvear Aravena, Xavier Godoy Cerda y Eduardo Ruiz Quezada</p>",
            unsafe_allow_html=True)

st.markdown(f"<div style='height:{SPACE['xl']}'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Fila de KPIs
# ----------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
kpi_card(k1, "% ingreso a vivienda · Q1", f"{carga_q1:.0f}%",
         f"{carga_q1 - carga_q5:+.0f} pp vs Q5", icon="🏠",
         gradient=GRAD["warning"], delta_good=False)
kpi_card(k2, "Brecha de ingreso · Q5 ÷ Q1", f"{ratio:.1f}×",
         icon="⚖️", gradient=GRAD["info"])
kpi_card(k3, "Informalidad laboral · Q1", f"{inf_q1:.0f}%",
         f"{inf_q1 - inf_q5:+.0f} pp vs Q5", icon="🧩",
         gradient=GRAD["warning"], delta_good=False)
kpi_card(k4, "Casa propia · Q1", f"{casa_q1:.0f}%",
         f"{casa_q1 - casa_q5:+.0f} pp vs Q5", icon="🔑",
         gradient=GRAD["success"], delta_good=True)

# ----------------------------------------------------------------------
# Panel glass — pills (echo de la sección activa) + título + descripción + gráfico
# ----------------------------------------------------------------------
with st.container(key="chart_panel"):
    sec = SECTIONS[tab]
    st.markdown(f"<div style='display:flex;align-items:center;gap:{SPACE['sm']};margin-bottom:2px'>"
                f"<span style='font-size:1.1rem'>{sec['icon']}</span>"
                f"<span style='color:#fff;font-weight:800;font-size:{TYPE['title_sm']}'>{sec['name']}</span></div>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color:{DIM};font-size:{TYPE['body_sm']};line-height:1.55;margin:0 0 {SPACE['lg']} 0'>"
                f"{sec['desc']}</p>", unsafe_allow_html=True)

    # ---- 0. Scatter: carga de la vivienda ----
    if tab == 0:
        d = prep_scatter(df)
        d = d[d['yautcorh'] <= ing_max]
        frames = []
        for q, _ in quintiles:
            sub = d[d['Quintil'] == q]
            frames.append(sub.sample(min(len(sub), n_pts), random_state=42))
        dd = pd.concat(frames) if frames else d.iloc[:0]
        fig = px.scatter(dd, x='yautcorh', y='prop', color='Quintil',
                         color_discrete_map={"Quintil 1": C_Q1, "Quintil 5": C_Q5},
                         opacity=0.55, labels={'yautcorh': 'Ingreso autónomo del hogar (CLP)',
                                               'prop': '% del ingreso a vivienda'})
        fig.add_hline(y=30, line_dash="dash", line_color="#a0aec0",
                      annotation_text="Umbral de carga crítica (30%)", annotation_position="top right")
        fig.update_traces(marker=dict(size=6, line=dict(width=0)))
        _layout(fig, "Porcentaje del ingreso del hogar destinado a dividendo o arriendo")
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
        st.info("El Quintil 1 destina una proporción mucho mayor de su ingreso a la vivienda; "
                "gran parte supera el umbral crítico del 30%.")

    # ---- 1. Mapa LISA: autocorrelación espacial ----
    elif tab == 1:
        LISA_COLORS = {"High-High": C_Q5, "Low-Low": C_Q1, "Low-High": "#d8a23a",
                       "High-Low": "#d8a23a", "No Significativo": "#3a3f5c"}
        LISA_LABELS = {"High-High": "Alto ingreso (clúster)", "Low-Low": "Bajo ingreso (clúster)",
                       "Low-High": "Caso atípico", "High-Low": "Caso atípico",
                       "No Significativo": "Sin patrón claro"}
        try:
            df_lisa, features_lisa = prep_lisa()
            fig = go.Figure()
            for cluster_type in ["High-High", "Low-Low", "Low-High", "High-Low", "No Significativo"]:
                sub_idx = df_lisa[df_lisa['cluster'] == cluster_type].index.tolist()
                if not sub_idx:
                    continue
                sub = df_lisa.loc[sub_idx]
                sub_geoj = {"type": "FeatureCollection",
                            "features": [features_lisa[i] for i in sub_idx]}
                fig.add_trace(go.Choroplethmapbox(
                    geojson=sub_geoj,
                    locations=[str(i) for i in sub_idx],
                    featureidkey="id",
                    z=[1] * len(sub_idx),
                    showscale=False,
                    marker=dict(opacity=0.75, line=dict(width=0.3, color="rgba(255,255,255,0.15)")),
                    colorscale=[[0, LISA_COLORS[cluster_type]], [1, LISA_COLORS[cluster_type]]],
                    name=LISA_LABELS[cluster_type],
                    text=sub['Comuna'] + "<br>Ingreso: $" + sub['ingreso_fmt'],
                    hovertemplate="%{text}<br>" + LISA_LABELS[cluster_type] + "<extra></extra>",
                ))
            fig.update_layout(
                mapbox=dict(style="carto-darkmatter", center=dict(lat=-35.5, lon=-71.5), zoom=3.8),
                height=580, margin=dict(l=0, r=0, t=10, b=0),
                font=FONT, paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5,
                            bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff")),
            )
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
            st.info("Las comunas verdes (High-High) forman clústers de alto ingreso; las rojas "
                    "(Low-Low) concentran comunas de bajo ingreso rodeadas de vecinas también "
                    "pobres. Los casos atípicos (amarillo) son comunas que rompen el patrón de "
                    "su entorno.")
        except FileNotFoundError:
            st.warning("El archivo `data/lisa_clusters.geojson` no está disponible. "
                       "Agrégalo a la carpeta `data/` para visualizar el mapa LISA.")

    # ---- 2. Crecimiento por educación ----
    elif tab == 2:
        cr = prep_growth(df)
        fig = go.Figure()
        if ver_q1:
            fig.add_bar(y=cr.index, x=cr[1], orientation='h', name='Quintil 1', marker_color=C_Q1,
                        text=[f"{v:+.0f}%" for v in cr[1]], textposition="outside")
        if ver_q5:
            fig.add_bar(y=cr.index, x=cr[5], orientation='h', name='Quintil 5', marker_color=C_Q5,
                        text=[f"{v:+.0f}%" for v in cr[5]], textposition="outside")
        fig.update_layout(barmode='group')
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(title="Crecimiento del ingreso del trabajo (%)")
        _layout(fig, "Cuánto varía el ingreso del trabajo al completar cada nivel educativo")
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ---- 3. Trayectoria por edad y género ----
    elif tab == 3:
        agg = prep_lines(df)
        sexos = st.multiselect("Género", ["Hombre", "Mujer"], default=["Hombre", "Mujer"])
        fig = go.Figure()
        for q, color in quintiles:
            for sx in sexos:
                sub = agg[(agg['Quintil'] == q) & (agg['Sexo'] == sx)].sort_values('ge')
                fig.add_trace(go.Scatter(x=sub['Rango'], y=sub['ytotcor'], mode='lines+markers',
                                         name=f"{q} · {sx}",
                                         line=dict(color=color, width=3, shape="spline",
                                                   dash='solid' if sx == 'Hombre' else 'dash'),
                                         fill='tozeroy', fillcolor=_rgba(color, 0.10)))
        fig.update_yaxes(title="Ingreso total promedio (CLP)", tickformat="$,.0f")
        fig.update_xaxes(title="Rango de edad")
        _layout(fig, "Ingreso total promedio a lo largo de la vida")
        # Más aire entre el título y la leyenda de 4 series (Quintil x Género) — solo este
        # gráfico tiene tantas entradas de leyenda, por eso no se ajusta _layout() globalmente
        fig.update_layout(margin_t=75, legend_y=1.08)
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ---- 4. Tornado: pobreza multidimensional ----
    elif tab == 4:
        dp = prep_tornado(df)
        fig = go.Figure()
        if ver_q1:
            fig.add_bar(y=dp['Dimensión'], x=-dp['Q1'], orientation='h', name='Quintil 1',
                        marker_color=C_Q1, marker_line_width=0, customdata=dp['Q1'],
                        hovertemplate="%{y}<br>Q1: %{customdata:.1f}%<extra></extra>")
        if ver_q5:
            fig.add_bar(y=dp['Dimensión'], x=dp['Q5'], orientation='h', name='Quintil 5',
                        marker_color=C_Q5, marker_line_width=0,
                        hovertemplate="%{y}<br>Q5: %{x:.1f}%<extra></extra>")
        fig.update_layout(barmode='relative', bargap=0.35)
        mx = max(dp['Q1'].max(), dp['Q5'].max()) * 1.25
        fig.update_xaxes(title="% de hogares carentes  (Q1 ←   |   → Q5)",
                         range=[-mx, mx], tickvals=np.arange(-40, 41, 10),
                         ticktext=[f"{abs(v)}%" for v in np.arange(-40, 41, 10)])
        _layout(fig, "Hogares carentes en cada dimensión de la pobreza multidimensional", alto=560)
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ---- 5. Radar: calidad de vida ----
    elif tab == 5:
        dr = prep_radar(df)
        fig = go.Figure()
        if ver_q5:
            fig.add_trace(go.Scatterpolar(r=list(dr['Q5']) + [dr['Q5'].iloc[0]],
                          theta=list(dr['Eje']) + [dr['Eje'].iloc[0]], fill='toself',
                          fillcolor=_rgba(C_Q5, 0.25), name='Quintil 5', line_color=C_Q5))
        if ver_q1:
            fig.add_trace(go.Scatterpolar(r=list(dr['Q1']) + [dr['Q1'].iloc[0]],
                          theta=list(dr['Eje']) + [dr['Eje'].iloc[0]], fill='toself',
                          fillcolor=_rgba(C_Q1, 0.25), name='Quintil 1', line_color=C_Q1))
        fig.update_polars(bgcolor="rgba(0,0,0,0)",
                          radialaxis=dict(range=[0, 100], ticksuffix="%", gridcolor=GRID),
                          angularaxis=dict(gridcolor=GRID))
        _layout(fig, "% de hogares que cumple cada atributo de vivienda y acceso urbano", alto=500)
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ---- 6. Treemap: composición ocupacional ----
    elif tab == 6:
        g = prep_treemap(df)
        qsel = st.radio("Quintil", ["Quintil 1", "Quintil 5"], horizontal=True,
                        index=0 if ver_q1 else 1)
        gg = g[g['Quintil'] == qsel].copy()
        fig = px.treemap(gg, path=[px.Constant(qsel), 'Macro', 'Sub'], values='Pct',
                         color='Macro', color_discrete_sequence=px.colors.qualitative.Bold,
                         custom_data=['Pct'])
        fig.update_traces(texttemplate="%{label}<br>%{customdata[0]:.1f}%",
                          marker=dict(line=dict(color="#060b26", width=2)),
                          hovertemplate="%{label}<br>%{customdata[0]:.1f}% de los ocupados<extra></extra>")
        fig.update_layout(height=540, margin=dict(l=10, r=10, t=10, b=10), font=FONT,
                          paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG)
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

# ----------------------------------------------------------------------
# Conclusión
# ----------------------------------------------------------------------
st.markdown(f"<div style='height:{SPACE['sm']}'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "**Conclusión.** El análisis evidencia una profunda brecha estructural de oportunidades. "
    "Mientras el Quintil 5 goza de estabilidad financiera, empleos calificados y baja vulnerabilidad, "
    "el Quintil 1 enfrenta un ciclo de precariedad: sufren mayores carencias multidimensionales, habitan "
    "viviendas de peor calidad que consumen más del 30% de sus ingresos, y carecen de redes de apoyo, lo "
    "que castiga severamente sus ingresos si desertan de la educación superior. Estas desventajas estancan "
    "al sector de menores ingresos en empleos de baja calificación y amplían drásticamente la brecha "
    "económica en la vida adulta, una realidad que además está cruzada por una persistente desigualdad "
    "salarial de género en ambos grupos.")
st.caption("Fuente: Encuesta CASEN 2024, Ministerio de Desarrollo Social y Familia.")
