# -*- coding: utf-8 -*-
"""
Dashboard interactivo — Brechas entre el Quintil 1 y el Quintil 5 (CASEN 2024)
Autores: Benjamín Alvear Aravena, Xavier Godoy Cerda y Eduardo Ruiz Quezada

Ejecutar con:   streamlit run dashboard.py
Requisitos:     pip install streamlit plotly pandas numpy pyarrow
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# Configuración general y paleta (alineada con el informe)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Quintil 1 vs Quintil 5 · CASEN 2024",
                   page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp { background: radial-gradient(1200px 600px at 80% -10%, #1b2350 0%, #0b0f24 55%); }
[data-testid="stMetric"] { background:#141a36; border:1px solid #242c52;
    border-radius:16px; padding:14px 18px 10px 18px; }
[data-testid="stMetricLabel"] p { color:#ffffff; font-size:0.80rem; }
[data-testid="stMetricValue"] { color:#f1f3ff; }
[data-testid="stPlotlyChart"] { background:#10152f; border:1px solid #222a4d;
    border-radius:16px; padding:8px 10px; }
section[data-testid="stSidebar"] { background:#0e1330; border-right:1px solid #1d244a; }
h1, h2, h3, h4 { color:#eef1ff !important; }
.stTabs [data-baseweb="tab-list"] { gap:6px; }
.stTabs [data-baseweb="tab"] { background:#141a36; border-radius:10px 10px 0 0; padding:6px 14px; }
.stTabs [aria-selected="true"] { background:#241c52; color:#cbbcff; }
/* --- Toggles del filtro de quintil (más grandes) --- */
[data-testid="stToggle"] { background:#141a36; border:1px solid #242c52;
    border-radius:16px; padding:16px 22px; }
[data-testid="stToggle"] label { transform: scale(1.45); transform-origin:left center; }
[data-testid="stToggle"] label p { font-weight:600; color:#ffffff !important; }
[data-testid="stToggle"] * { color:#ffffff !important; }
[data-testid="stCheckbox"] * { color:#ffffff !important; }
.stToggle * { color:#ffffff !important; }
label[data-baseweb="checkbox"] span { color:#ffffff !important; }
/* --- Textos generales legibles --- */
.stCaption, [data-testid="stCaptionContainer"] p { color:#d0d5e8 !important; }
.stMarkdown p, .stMarkdown span { color:#e0e4f0 !important; }
.stAlert p { color:#e0e4f0 !important; }
.stTabs [data-baseweb="tab"] { color:#c0c6dc !important; }
</style>
""", unsafe_allow_html=True)

C_Q1 = "#F2635B"   # Quintil 1 (más pobre)
C_Q5 = "#2DD4BF"   # Quintil 5 (más rico)
ACCENT = "#7C5CFC" # acento de interfaz (morado)
GRID = "#232a4d"
PLOT_BG = "rgba(0,0,0,0)"
FONT = dict(family="Inter, Segoe UI, sans-serif", color="#ffffff")

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


def _layout(fig, titulo, alto=420):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=17, color="#eef1ff")),
        template="plotly_dark", height=alto, font=FONT,
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        margin=dict(l=60, r=30, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff")),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig


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


# ----------------------------------------------------------------------
# Cabecera
# ----------------------------------------------------------------------
st.title("Brechas entre el Quintil 1 y el Quintil 5 en Chile")
st.caption("Seis miradas a la desigualdad de ingresos, vivienda, trabajo y calidad de vida · "
           "Encuesta CASEN 2024 · Autores: Benjamín Alvear Aravena, Xavier Godoy Cerda y Eduardo Ruiz Quezada")

# ----------------------------------------------------------------------
# Filtro de quintil (centrado, al inicio de la página)
# ----------------------------------------------------------------------
st.markdown("<p style='text-align:center; color:#ffffff; margin:4px 0 2px 0; "
            "font-size:0.85rem; letter-spacing:.03em'>MOSTRAR / OCULTAR QUINTILES</p>",
            unsafe_allow_html=True)
_c = st.columns([0.7, 1.6, 1.6, 0.7])
with _c[1]:
    ver_q1 = st.toggle("🔴  Quintil 1 (más pobre)", value=True)
with _c[2]:
    ver_q5 = st.toggle("🟢  Quintil 5 (más rico)", value=True)
quintiles = ([("Quintil 1", C_Q1)] if ver_q1 else []) + ([("Quintil 5", C_Q5)] if ver_q5 else [])
ing_max, n_pts = 7_000_000, 800   # valores fijos (antes estaban en la barra lateral)

try:
    df = load_data()
except Exception as e:
    st.error(f"No pude cargar **{PARQUET}**. Colócalo junto a este archivo.\n\n{e}")
    st.stop()

# ----------------------------------------------------------------------
# KPIs (tarjetas resumen, estilo dashboard)
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

k1, k2, k3, k4 = st.columns(4)
k1.metric("% del ingreso a vivienda · Q1", f"{carga_q1:.0f}%",
          f"{carga_q1 - carga_q5:+.0f} pp vs Q5", delta_color="inverse")
k2.metric("Brecha de ingreso  ·  Q5 ÷ Q1", f"{ratio:.1f}×")
k3.metric("Informalidad laboral · Q1", f"{inf_q1:.0f}%",
          f"{inf_q1 - inf_q5:+.0f} pp vs Q5", delta_color="inverse")
k4.metric("Casa propia · Q1", f"{casa_q1:.0f}%",
          f"{casa_q1 - casa_q5:+.0f} pp vs Q5")
st.markdown("")

tabs = st.tabs(["🏠 Vivienda", "🗺 Mapa LISA", "📈 Educación", "👥 Edad y género",
                "🌪 Pobreza", "🧭 Calidad de vida", "🧩 Empleo"])

# ---- 1. Scatter: carga de la vivienda ----
with tabs[0]:
    st.subheader("I. La carga de la vivienda")
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
    fig.add_hline(y=30, line_dash="dash", line_color="#7b8794",
                  annotation_text="Umbral de carga crítica (30%)", annotation_position="top right")
    fig.update_traces(marker=dict(size=6))
    _layout(fig, "Porcentaje del ingreso del hogar destinado a dividendo o arriendo")
    st.plotly_chart(fig, width='stretch')
    st.info("El Quintil 1 destina una proporción mucho mayor de su ingreso a la vivienda; "
            "gran parte supera el umbral crítico del 30%.")

# ---- 2. Mapa LISA: autocorrelación espacial ----
with tabs[1]:
    st.subheader("II. Autocorrelación espacial del ingreso (LISA)")
    import json as _json

    @st.cache_data
    def prep_lisa():
        with open("data/lisa_clusters.geojson", encoding="utf-8") as f:
            raw = _json.load(f)
        features, rows = [], []
        for i, feat in enumerate(raw["features"]):
            features.append({**feat, "id": str(i)})
            rows.append({"_idx": i, **feat.get("properties", {})})
        df = pd.DataFrame(rows).set_index("_idx")
        df['ingreso_fmt'] = (df['ingreso_autonomo'] / 1e3).round(0).astype(int).astype(str) + "K"
        return df, features

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
                z=[1]*len(sub_idx),
                showscale=False,
                marker=dict(opacity=0.75, line=dict(width=0.3, color="#222")),
                colorscale=[[0, LISA_COLORS[cluster_type]], [1, LISA_COLORS[cluster_type]]],
                name=LISA_LABELS[cluster_type],
                text=sub['Comuna'] + "<br>Ingreso: $" + sub['ingreso_fmt'],
                hovertemplate="%{text}<br>" + LISA_LABELS[cluster_type] + "<extra></extra>",
            ))
        fig.update_layout(
            mapbox=dict(style="carto-darkmatter", center=dict(lat=-35.5, lon=-71.5), zoom=3.8),
            height=620, margin=dict(l=0, r=0, t=50, b=0),
            font=FONT, paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            title=dict(text="Clústers de Moran Local — Ingreso autónomo por comuna",
                       font=dict(size=17, color="#eef1ff")),
            legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5,
                        bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff")),
        )
        st.plotly_chart(fig, width='stretch')
        st.info("Las comunas verdes (High-High) forman clústers de alto ingreso; las rojas (Low-Low) "
                "concentran comunas de bajo ingreso rodeadas de vecinas también pobres. "
                "Los casos atípicos (amarillo) son comunas que rompen el patrón de su entorno.")
    except FileNotFoundError:
        st.warning("El archivo `data/lisa_clusters.geojson` no está disponible. "
                   "Agrégalo a la carpeta `data/` para visualizar el mapa LISA.")

# ---- 3. Crecimiento por educación ----
with tabs[2]:
    st.subheader("III. Retorno educativo del ingreso")
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
    st.plotly_chart(fig, width='stretch')

# ---- 4. Trayectoria por edad y género ----
with tabs[3]:
    st.subheader("IV. Trayectoria de ingresos por edad y género")
    agg = prep_lines(df)
    sexos = st.multiselect("Género", ["Hombre", "Mujer"], default=["Hombre", "Mujer"])
    orden = [str(c) for c in pd.cut(pd.Series([20]), bins=range(18, 85, 5)).cat.categories]
    fig = go.Figure()
    for q, color in quintiles:
        for sx in sexos:
            sub = agg[(agg['Quintil'] == q) & (agg['Sexo'] == sx)].sort_values('ge')
            fig.add_trace(go.Scatter(x=sub['Rango'], y=sub['ytotcor'], mode='lines+markers',
                                     name=f"{q} · {sx}", line=dict(color=color,
                                     dash='solid' if sx == 'Hombre' else 'dash')))
    fig.update_yaxes(title="Ingreso total promedio (CLP)", tickformat="$,.0f")
    fig.update_xaxes(title="Rango de edad")
    _layout(fig, "Ingreso total promedio a lo largo de la vida (línea sólida = hombres, punteada = mujeres)")
    st.plotly_chart(fig, width='stretch')

# ---- 5. Tornado: pobreza multidimensional ----
with tabs[4]:
    st.subheader("V. Tornado de la desigualdad")
    dp = prep_tornado(df)
    fig = go.Figure()
    if ver_q1:
        fig.add_bar(y=dp['Dimensión'], x=-dp['Q1'], orientation='h', name='Quintil 1',
                    marker_color=C_Q1, customdata=dp['Q1'],
                    hovertemplate="%{y}<br>Q1: %{customdata:.1f}%<extra></extra>")
    if ver_q5:
        fig.add_bar(y=dp['Dimensión'], x=dp['Q5'], orientation='h', name='Quintil 5',
                    marker_color=C_Q5, hovertemplate="%{y}<br>Q5: %{x:.1f}%<extra></extra>")
    fig.update_layout(barmode='relative')
    mx = max(dp['Q1'].max(), dp['Q5'].max()) * 1.25
    fig.update_xaxes(title="% de hogares carentes  (Q1 ←   |   → Q5)",
                     range=[-mx, mx], tickvals=np.arange(-40, 41, 10),
                     ticktext=[f"{abs(v)}%" for v in np.arange(-40, 41, 10)])
    _layout(fig, "Hogares carentes en cada dimensión de la pobreza multidimensional", alto=560)
    st.plotly_chart(fig, width='stretch')

# ---- 6. Radar: calidad de vida ----
with tabs[5]:
    st.subheader("VI. Calidad de vida e integración urbana")
    dr = prep_radar(df)
    fig = go.Figure()
    if ver_q5:
        fig.add_trace(go.Scatterpolar(r=list(dr['Q5']) + [dr['Q5'].iloc[0]],
                      theta=list(dr['Eje']) + [dr['Eje'].iloc[0]], fill='toself',
                      name='Quintil 5', line_color=C_Q5))
    if ver_q1:
        fig.add_trace(go.Scatterpolar(r=list(dr['Q1']) + [dr['Q1'].iloc[0]],
                      theta=list(dr['Eje']) + [dr['Eje'].iloc[0]], fill='toself',
                      name='Quintil 1', line_color=C_Q1))
    fig.update_polars(bgcolor="rgba(0,0,0,0)",
                      radialaxis=dict(range=[0, 100], ticksuffix="%", gridcolor=GRID),
                      angularaxis=dict(gridcolor=GRID))
    _layout(fig, "% de hogares que cumple cada atributo de vivienda y acceso urbano", alto=520)
    st.plotly_chart(fig, width='stretch')

# ---- 7. Treemap: composición ocupacional ----
with tabs[6]:
    st.subheader("VII. Composición ocupacional de la población ocupada")
    g = prep_treemap(df)
    qsel = st.radio("Quintil", ["Quintil 1", "Quintil 5"], horizontal=True,
                    index=0 if ver_q1 else 1)
    gg = g[g['Quintil'] == qsel].copy()
    fig = px.treemap(gg, path=[px.Constant(qsel), 'Macro', 'Sub'], values='Pct',
                     color='Macro', color_discrete_sequence=px.colors.qualitative.Bold,
                     custom_data=['Pct'])
    fig.update_traces(texttemplate="%{label}<br>%{customdata[0]:.1f}%",
                      marker=dict(line=dict(color="#10152f", width=1)),
                      hovertemplate="%{label}<br>%{customdata[0]:.1f}% de los ocupados<extra></extra>")
    fig.update_layout(height=560, margin=dict(l=10, r=10, t=50, b=10), font=FONT,
                      paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                      title=dict(text=f"Distribución de ocupados por sector · {qsel}",
                                 font=dict(color="#eef1ff")))
    st.plotly_chart(fig, width='stretch')

# ----------------------------------------------------------------------
# Conclusión
# ----------------------------------------------------------------------
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
