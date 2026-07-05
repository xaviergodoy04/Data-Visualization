# Plan de implementación — Estética *Vision UI Dashboard* en Streamlit

**Proyecto:** `Data-Visualization` (dashboard CASEN 2024 · Quintil 1 vs Quintil 5)
**Objetivo:** replicar el lenguaje visual de *Vision UI Dashboard React* (glassmorphism dark navy + degradados azul→cian) sobre el dashboard actual, **manteniéndolo 100% en Streamlit** para deploy en `streamlit.io`.
**Herramienta de trabajo:** Claude Code (no Figma — ver §9).

---

## 1. Decisión de arquitectura (resumen)

| Opción | ¿Viable? | Por qué |
|---|---|---|
| Importar el template React/MUI | ❌ | Streamlit no monta React salvo *custom components* (bundle JS); rompe la simplicidad del deploy. |
| Claude × Figma | ⚠️ Solo referencia | El MCP de Figma genera React/HTML, no Streamlit. Rodeo innecesario. |
| **CSS inyectado + tema Plotly** | ✅ **Elegida** | Reproduce el look sin dependencias nuevas; ya lo haces parcialmente. |

**Regla de oro:** se restiliza el *chrome* (fondo, cards, tabs, sidebar, KPIs). Los colores de **datos** (`C_Q1 = #F2635B`, `C_Q5 = #2DD4BF`) **no se tocan** porque son semánticos.

---

## 2. Design system Vision UI (tokens)

### 2.1 Superficies y fondo
- **Fondo app:** navy `#060b26` con 2 *radial-gradients* de acento (azul arriba-derecha, morado arriba-izquierda).
- **Card (glass):** `linear-gradient(127deg, rgba(6,11,40,0.74), rgba(10,14,35,0.49))` + `backdrop-filter: blur(20px)`.
- **Borde card:** `rgba(255,255,255,0.10)` (1px).
- **Sombra:** `0 8px 24px rgba(0,0,0,0.35)`.
- **Radio:** `20px` (cards / gráficos), `14–16px` (tabs, toggles, alerts).

### 2.2 Degradados de marca (para chrome, no datos)
| Nombre | Valor | Uso |
|---|---|---|
| `info` | `linear-gradient(310deg,#2152FF,#21D4FD)` | Acento principal, tab activo, badges KPI |
| `primary` | `linear-gradient(310deg,#7928CA,#FF0080)` | Badge secundario |
| `success` | `linear-gradient(310deg,#17AD37,#98EC2D)` | KPI "bueno" |
| `warning` | `linear-gradient(310deg,#F53939,#FBCF33)` | KPI de alerta (informalidad) |

### 2.3 Tipografía
- **Fuente:** `Plus Jakarta Sans` (Google Fonts, importada por CSS). Fallback `Inter, sans-serif`.
- **Pesos:** 700 títulos/valores, 600 labels, 400 cuerpo.
- **Texto:** principal `#ffffff`, atenuado `#a0aec0`.

### 2.4 Ejes de gráficos
- Grid: `rgba(255,255,255,0.08)` · Plot/paper bg: transparente · Hover: fondo `#0f1535`.

> Todos estos tokens ya están codificados en **`vision_ui_theme.py`** (entregado aparte). Este plan explica **cómo aplicarlos**.

---

## 3. Estructura de archivos

```
Data-Visualization/
├── dashboard.py            # editar (ver §4)
├── vision_ui_theme.py      # NUEVO — copiar a la raíz
├── requirements.txt        # sin cambios (no hay deps nuevas)
└── data/
    ├── casen_2024.parquet
    └── lisa_clusters.geojson
```

---

## 4. Guía de integración paso a paso (`dashboard.py`)

**Paso 1 — Import (arriba del archivo):**
```python
from vision_ui_theme import inject_theme, plotly_layout, kpi_card, GRAD, C_Q1, C_Q5
```

**Paso 2 — Reemplazar el bloque de estilo.** Borra por completo tu actual `st.markdown("""<style>...""", unsafe_allow_html=True)` y déjalo en:
```python
st.set_page_config(page_title="Quintil 1 vs Quintil 5 · CASEN 2024",
                   page_icon="📊", layout="wide")
inject_theme()
```
> Puedes borrar también las constantes `C_Q1`, `C_Q5`, `GRID`, `PLOT_BG`, `FONT` locales: ahora vienen del módulo (mantén `ACCENT` si lo usas en algún gráfico).

**Paso 3 — Sustituir `_layout()`.** Elimina tu función `def _layout(...)` y cambia cada llamada `_layout(fig, titulo, alto)` por `plotly_layout(fig, titulo, alto)` (firma idéntica).

**Paso 4 — KPIs.** Reemplaza los cuatro `st.metric(...)` por `kpi_card(...)`. Guía en §5.2.

**Paso 5 — Commit y deploy** (§8).

---

## 5. Guías detalladas por componente

### 5.1 Fondo global
Lo aplica `inject_theme()`. Nada que hacer manual. Verifica que **no** quede tu antiguo gradiente `radial-gradient(... #1b2350 ...)` duplicado.

### 5.2 KPI cards (las 4 tarjetas superiores)
La `kpi_card()` añade lo que `st.metric` no puede: **badge de ícono con degradado**. Firma:
```python
kpi_card(col, label, value, delta=None, icon="📊",
         gradient=GRAD["info"], delta_good=True)
```
- `delta_good=False` → invierte el color del delta (cuando *más* es peor).

Mapeo recomendado para tus 4 KPIs:
```python
k1, k2, k3, k4 = st.columns(4)
kpi_card(k1, "% ingreso a vivienda · Q1", f"{carga_q1:.0f}%",
         f"{carga_q1-carga_q5:+.0f} pp vs Q5", icon="🏠",
         gradient=GRAD["warning"], delta_good=False)
kpi_card(k2, "Brecha de ingreso · Q5 ÷ Q1", f"{ratio:.1f}×",
         icon="⚖️", gradient=GRAD["info"])
kpi_card(k3, "Informalidad laboral · Q1", f"{inf_q1:.0f}%",
         f"{inf_q1-inf_q5:+.0f} pp vs Q5", icon="🧩",
         gradient=GRAD["warning"], delta_good=False)
kpi_card(k4, "Casa propia · Q1", f"{casa_q1:.0f}%",
         f"{casa_q1-casa_q5:+.0f} pp vs Q5", icon="🔑",
         gradient=GRAD["success"], delta_good=True)
```

### 5.3 Gráficos Plotly (card glass)
El contenedor `[data-testid="stPlotlyChart"]` ya recibe el look glass vía CSS. Solo asegúrate de pasar cada figura por `plotly_layout()`. Recomendado: `st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})` para ocultar la barra de Plotly y ganar limpieza.

### 5.4 Tabs
Se convierten en *pills*; el tab activo usa el degradado `info`. Sin cambios en tu código de tabs — solo el CSS.

### 5.5 Sidebar / Toggles / Alerts
Restilizados por CSS. Los `st.toggle` de Q1/Q5 quedan como card glass. Los `st.info(...)` quedan como alert translúcido azul.

---

## 6. Ajustes finos por gráfico (tus 7 tabs)

Detalles opcionales para que cada visual "se sienta" Vision UI. Aplícalos **después** de que el look base funcione.

1. **Vivienda (scatter):** puntos `marker=dict(size=6, line=dict(width=0))`, `opacity≈0.55`. La línea del umbral 30% en `#a0aec0` (ya la tienes en gris).
2. **Mapa LISA (choropleth):** usa `mapbox_style="carto-darkmatter"` para que el mapa combine con el navy; `marker_line_color="rgba(255,255,255,0.15)"`.
3. **Educación (barras de crecimiento):** relleno con degradado vertical Vision UI:
   ```python
   fig.update_traces(marker=dict(
       color=cr.values.flatten(),
       colorscale=[[0, "#2152FF"], [1, "#21D4FD"]],
       line=dict(width=0)))
   ```
4. **Edad y género (líneas):** `line=dict(width=3, shape="spline")` + relleno tenue `fill='tozeroy'` con `rgba` del color de serie al 10%.
5. **Pobreza (tornado):** barras Q1 en `C_Q1`, Q5 en `C_Q5`, `marker_line_width=0`, esquinas suaves no aplican en Plotly → deja gap `bargap=0.35`.
6. **Calidad de vida (radar):** `fill='toself'` con opacidad 0.25; borde de serie al color pleno; `radialaxis` gridcolor `rgba(255,255,255,0.10)`.
7. **Empleo (treemap):** `marker=dict(line=dict(color="#060b26", width=2))` para separar bloques sobre el navy; texto en blanco.

---

## 7. Checklist de QA visual

- [ ] Fondo navy con acentos; sin restos del gradiente morado antiguo.
- [ ] 4 KPI cards con badge de ícono en degradado y delta coloreado correcto (informalidad y vivienda en rojo cuando suben).
- [ ] Cada gráfico dentro de card glass con blur y borde translúcido.
- [ ] Tab activo con degradado azul→cian.
- [ ] Toggles Q1/Q5 legibles (texto blanco) y como card.
- [ ] Series Q1 rojo / Q5 teal intactas en los 7 gráficos.
- [ ] Legibilidad de captions (`#a0aec0`) sobre navy.
- [ ] Mapa LISA en base oscura (no blanca).

---

## 8. Deploy (streamlit.io)

1. `vision_ui_theme.py` en la raíz del repo.
2. `requirements.txt` **sin cambios** (no hay dependencias nuevas).
3. `git add . && git commit -m "feat: tema Vision UI" && git push`.
4. Streamlit Cloud redeploya automático; si no, *Reboot app* desde el panel.
5. Verifica que `Plus Jakarta Sans` cargue (requiere que Streamlit Cloud tenga salida a `fonts.googleapis.com`, que sí tiene).

---

## 9. Figma (opcional, no requerido)

No es necesario para construir esto. Si quisieras una maqueta previa:
1. Diseñas el frame en Figma con los tokens de §2.
2. Usas el MCP de Figma (ya conectado) para *leer* el frame.
3. Claude Code traduce el diseño a este mismo CSS de Streamlit.

Es un rodeo: el resultado es idéntico al que ya produce `vision_ui_theme.py`, y Vision UI ya define la estética. **Recomendación: ir directo a Claude Code.**

---

## 10. Orden de ejecución sugerido

1. Copiar `vision_ui_theme.py` (§3).
2. Integrar §4 (import, `inject_theme`, `plotly_layout`, KPIs).
3. Probar local: `streamlit run dashboard.py`.
4. QA base (§7, primeros 6 ítems).
5. Aplicar ajustes finos §6 gráfico por gráfico.
6. Deploy §8.
