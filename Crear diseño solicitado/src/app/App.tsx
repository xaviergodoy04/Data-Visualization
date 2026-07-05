import { useState } from "react";
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
  BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Treemap, ResponsiveContainer, Legend,
} from "recharts";
import {
  Home, Map, GraduationCap, Users, BarChart2, Activity,
  Briefcase, Info, AlertTriangle,
} from "lucide-react";

// ── Design tokens ─────────────────────────────────────────────────────────────

const C_Q1 = "#F2635B";
const C_Q5 = "#2DD4BF";
const DIM   = "#a0aec0";
const GRID_C = "rgba(255,255,255,0.08)";

const GRAD = {
  info:    "linear-gradient(310deg,#2152FF,#21D4FD)",
  success: "linear-gradient(310deg,#17AD37,#98EC2D)",
  warning: "linear-gradient(310deg,#F53939,#FBCF33)",
  primary: "linear-gradient(310deg,#7928CA,#FF0080)",
};

const glass = {
  background:           "linear-gradient(127deg,rgba(6,11,40,0.74),rgba(10,14,35,0.49))",
  backdropFilter:       "blur(20px)",
  WebkitBackdropFilter: "blur(20px)",
  border:               "1px solid rgba(255,255,255,0.10)",
  boxShadow:            "0 8px 24px rgba(0,0,0,0.35)",
  borderRadius:         "20px",
};

const tooltipStyle = {
  contentStyle: {
    backgroundColor: "#0f1535",
    border: "1px solid rgba(255,255,255,0.15)",
    borderRadius: "12px",
    color: "#fff",
    fontSize: 12,
    padding: "8px 14px",
  },
  labelStyle: { color: DIM, marginBottom: 4, fontWeight: 600 },
  itemStyle:  { color: "#fff" },
};

const axisStyle = {
  tick:     { fill: DIM, fontSize: 11 },
  axisLine: { stroke: GRID_C },
  tickLine: false as const,
};

// ── Mock data ─────────────────────────────────────────────────────────────────

function rnd(min: number, max: number) { return min + Math.random() * (max - min); }

const scatter1 = Array.from({ length: 130 }, () => ({
  income: Math.round(rnd(110, 460)),
  burden: +rnd(22, 74).toFixed(1),
}));
const scatter5 = Array.from({ length: 130 }, () => ({
  income: Math.round(rnd(900, 3600)),
  burden: +rnd(4, 26).toFixed(1),
}));

const educData = [
  { nivel: "Básica",        q1: 5.1, q5: 6.3 },
  { nivel: "Media",         q1: 10.4, q5: 11.9 },
  { nivel: "Técnica",       q1: 13.2, q5: 14.6 },
  { nivel: "Universitaria", q1: 15.8, q5: 17.3 },
  { nivel: "Posgrado",      q1: 17.1, q5: 19.6 },
];

const edadData = [
  { tramo: "0–14",  q1: 28.2, q5: 16.1 },
  { tramo: "15–29", q1: 22.4, q5: 18.8 },
  { tramo: "30–44", q1: 18.7, q5: 23.1 },
  { tramo: "45–59", q1: 16.5, q5: 24.4 },
  { tramo: "60–74", q1: 10.6, q5: 14.2 },
  { tramo: "75+",   q1: 3.6,  q5: 3.4  },
];

const pobrezaData = [
  { dim: "Ingreso",   q1: -68.2, q5: 2.1  },
  { dim: "Empleo",    q1: -61.4, q5: 9.4  },
  { dim: "Vivienda",  q1: -52.3, q5: 5.8  },
  { dim: "Educación", q1: -45.7, q5: 4.3  },
  { dim: "Salud",     q1: -38.9, q5: 7.2  },
  { dim: "Seguridad", q1: -29.8, q5: 11.6 },
];

const radarData = [
  { subject: "Salud",     q1: 42, q5: 81 },
  { subject: "Educación", q1: 51, q5: 88 },
  { subject: "Vivienda",  q1: 38, q5: 86 },
  { subject: "Empleo",    q1: 35, q5: 84 },
  { subject: "Seguridad", q1: 47, q5: 72 },
  { subject: "Movilidad", q1: 53, q5: 79 },
];

const empleoData = [
  { name: "Comercio",     size: 2840, quintil: "q1" },
  { name: "Agricultura",  size: 2210, quintil: "q1" },
  { name: "Construcción", size: 1960, quintil: "q1" },
  { name: "Manufactura",  size: 1580, quintil: "q1" },
  { name: "Doméstico",    size: 1340, quintil: "q1" },
  { name: "Serv. Prof.",  size: 3120, quintil: "q5" },
  { name: "Finanzas",     size: 2650, quintil: "q5" },
  { name: "Educación",    size: 2180, quintil: "q5" },
  { name: "Salud",        size: 1940, quintil: "q5" },
  { name: "TI / Tech",    size: 1720, quintil: "q5" },
];

const LISA_REGIONS = [
  { name: "Arica y Parinacota", short: "XV",   cat: "LL", q1: 178, q5: 1680 },
  { name: "Tarapacá",           short: "I",    cat: "LL", q1: 192, q5: 1820 },
  { name: "Antofagasta",        short: "II",   cat: "HL", q1: 285, q5: 2640 },
  { name: "Atacama",            short: "III",  cat: "NS", q1: 241, q5: 2120 },
  { name: "Coquimbo",           short: "IV",   cat: "LH", q1: 198, q5: 2180 },
  { name: "Valparaíso",         short: "V",    cat: "HH", q1: 312, q5: 3240 },
  { name: "Metropolitana",      short: "RM",   cat: "HH", q1: 368, q5: 4120 },
  { name: "O'Higgins",          short: "VI",   cat: "LH", q1: 218, q5: 2280 },
  { name: "Maule",              short: "VII",  cat: "LL", q1: 182, q5: 1780 },
  { name: "Ñuble",              short: "XVI",  cat: "LL", q1: 169, q5: 1620 },
  { name: "Biobío",             short: "VIII", cat: "LH", q1: 224, q5: 2350 },
  { name: "La Araucanía",       short: "IX",   cat: "LL", q1: 158, q5: 1520 },
  { name: "Los Ríos",           short: "XIV",  cat: "NS", q1: 187, q5: 1860 },
  { name: "Los Lagos",          short: "X",    cat: "LL", q1: 195, q5: 1920 },
  { name: "Aysén",              short: "XI",   cat: "NS", q1: 264, q5: 2380 },
  { name: "Magallanes",         short: "XII",  cat: "NS", q1: 312, q5: 2860 },
];

const LISA_COLORS: Record<string, string> = {
  HH: "#F2635B", LL: "#2DD4BF", HL: "#FBCF33", LH: "#9F7AEA", NS: "#4a5568",
};
const LISA_LABELS: Record<string, string> = {
  HH: "Alto–Alto", LL: "Bajo–Bajo", HL: "Alto–Bajo", LH: "Bajo–Alto", NS: "No significativo",
};

const TABS = ["Vivienda", "Mapa LISA", "Educación", "Edad y Género", "Pobreza", "Calidad de Vida", "Empleo"];
const TAB_ICONS = [Home, Map, GraduationCap, Users, BarChart2, Activity, Briefcase];
const TAB_DESC = [
  "Carga de vivienda (% ingreso) vs ingreso mensual. La línea punteada marca el umbral crítico del 30%.",
  "Autocorrelación espacial por región — índice de Moran I = 0.34 (p < 0.01). Identifica clústeres geográficos de desigualdad.",
  "Años de escolaridad promedio por nivel educativo alcanzado. La brecha se amplía en niveles superiores.",
  "Distribución etaria de la población por quintil. Q1 concentra más menores; Q5 tiene mayor proporción de adultos en edad productiva.",
  "Pobreza multidimensional: proporción de la población con carencia en cada dimensión. Q1 a la izquierda, Q5 a la derecha del eje.",
  "Índice compuesto de calidad de vida (0–100) en seis dimensiones. La brecha promedio entre quintiles es de 37 puntos.",
  "Distribución de ocupación por sector económico y quintil predominante. Q1 en rojo, Q5 en teal.",
];

// ── Treemap content ───────────────────────────────────────────────────────────

function TreeCell(props: any) {
  const { x, y, width, height, name, quintil } = props;
  if (!width || !height || width < 2 || height < 2) return null;
  const fill = quintil === "q1" ? C_Q1 : C_Q5;
  const fontSize = Math.min(12, width / 7);
  return (
    <g>
      <rect x={x} y={y} width={width} height={height}
        fill={fill} stroke="#060b26" strokeWidth={2} rx={4} />
      {width > 52 && height > 26 && (
        <>
          <text x={x + width / 2} y={y + height / 2 - 6}
            textAnchor="middle" fill="rgba(255,255,255,0.95)"
            fontSize={fontSize} fontWeight={700} fontFamily="Plus Jakarta Sans, sans-serif">
            {name}
          </text>
          <text x={x + width / 2} y={y + height / 2 + 10}
            textAnchor="middle" fill="rgba(255,255,255,0.45)"
            fontSize={9} fontFamily="Plus Jakarta Sans, sans-serif">
            {quintil === "q1" ? "Q1" : "Q5"}
          </text>
        </>
      )}
    </g>
  );
}

// ── KPI card ──────────────────────────────────────────────────────────────────

function KpiCard({ label, value, delta, icon, gradient, deltaGood = true }: {
  label: string; value: string; delta?: string;
  icon: string; gradient: string; deltaGood?: boolean;
}) {
  const isPos = delta?.startsWith("+");
  const deltaColor = deltaGood
    ? (isPos ? "#17AD37" : "#F53939")
    : (isPos ? "#F53939" : "#17AD37");
  return (
    <div style={glass as any} className="p-5 flex gap-4 items-center">
      <div className="w-12 h-12 rounded-xl flex-shrink-0 flex items-center justify-center text-xl"
        style={{ background: gradient }}>
        {icon}
      </div>
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] mb-0.5" style={{ color: DIM }}>
          {label}
        </p>
        <p className="text-[26px] font-bold text-white leading-none">{value}</p>
        {delta && (
          <p className="text-[11px] font-bold mt-1" style={{ color: deltaColor }}>{delta}</p>
        )}
      </div>
    </div>
  );
}

// ── Charts ────────────────────────────────────────────────────────────────────

function ViviendaChart({ showQ1, showQ5 }: { showQ1: boolean; showQ5: boolean }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart margin={{ top: 10, right: 24, bottom: 28, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_C} />
        <XAxis dataKey="income" type="number" name="Ingreso" unit="k"
          {...axisStyle}
          label={{ value: "Ingreso mensual (miles CLP)", position: "insideBottom", offset: -12, fill: DIM, fontSize: 11 }} />
        <YAxis dataKey="burden" type="number" name="Carga" unit="%" {...axisStyle} />
        <Tooltip
          {...tooltipStyle}
          cursor={{ stroke: "rgba(255,255,255,0.1)", strokeWidth: 1 }}
          content={({ active, payload }) => {
            if (!active || !payload?.[0]) return null;
            const d = payload[0].payload;
            const fill = payload[0].fill as string;
            return (
              <div style={tooltipStyle.contentStyle}>
                <p style={{ color: fill, fontWeight: 700, marginBottom: 4 }}>
                  {fill === C_Q1 ? "Quintil 1" : "Quintil 5"}
                </p>
                <p style={{ color: DIM }}>Ingreso: <span style={{ color: "#fff" }}>${d.income}k CLP</span></p>
                <p style={{ color: DIM }}>Carga vivienda: <span style={{ color: "#fff" }}>{d.burden}%</span></p>
              </div>
            );
          }}
        />
        <ReferenceLine y={30} stroke="#a0aec0" strokeDasharray="6 3"
          label={{ value: "Umbral 30%", fill: DIM, fontSize: 10, position: "insideTopRight" }} />
        {showQ1 && <Scatter name="Quintil 1" data={scatter1} fill={C_Q1} fillOpacity={0.5} />}
        {showQ5 && <Scatter name="Quintil 5" data={scatter5} fill={C_Q5} fillOpacity={0.5} />}
      </ScatterChart>
    </ResponsiveContainer>
  );
}

function LisaChart() {
  return (
    <div className="flex gap-5 h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto flex flex-col gap-1.5 pr-1">
        {LISA_REGIONS.map((r) => (
          <div key={r.short}
            className="flex items-center gap-3 px-3 py-2.5 rounded-2xl transition-all duration-200 hover:scale-[1.015] cursor-default"
            style={{
              background: `linear-gradient(90deg,${LISA_COLORS[r.cat]}20,transparent)`,
              border: `1px solid ${LISA_COLORS[r.cat]}38`,
            }}>
            <div className="w-10 h-8 rounded-lg flex items-center justify-center text-[11px] font-black text-white flex-shrink-0"
              style={{ background: LISA_COLORS[r.cat] }}>
              {r.short}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-semibold truncate">{r.name}</p>
              <p className="text-[11px] font-medium" style={{ color: LISA_COLORS[r.cat] }}>
                {LISA_LABELS[r.cat]}
              </p>
            </div>
            <div className="text-right flex-shrink-0 space-y-0.5">
              <p className="text-[11px] font-bold" style={{ color: C_Q1 }}>Q1 ${r.q1}k</p>
              <p className="text-[11px] font-bold" style={{ color: C_Q5 }}>Q5 ${r.q5}k</p>
            </div>
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-2 justify-start pt-1 w-52 flex-shrink-0">
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] mb-1" style={{ color: DIM }}>
          Categorías LISA
        </p>
        {Object.entries(LISA_LABELS).map(([cat, label]) => (
          <div key={cat} className="flex items-center gap-2.5">
            <div className="w-3.5 h-3.5 rounded flex-shrink-0" style={{ background: LISA_COLORS[cat] }} />
            <span className="text-xs text-white font-medium">{cat} — {label}</span>
          </div>
        ))}
        <div className="mt-4 p-3 rounded-xl text-xs space-y-1"
          style={{ background: "rgba(33,82,255,0.14)", border: "1px solid rgba(33,82,255,0.28)" }}>
          <p className="font-bold text-white">Autocorrelación espacial</p>
          <p style={{ color: DIM }}>Índice de Moran I: <span className="text-white font-semibold">0.34</span></p>
          <p style={{ color: DIM }}>p-valor: <span className="text-white font-semibold">&lt; 0.01</span></p>
          <p style={{ color: DIM }} className="mt-1 leading-relaxed">
            La desigualdad de ingresos tiene un patrón geográfico estadísticamente significativo.
          </p>
        </div>
      </div>
    </div>
  );
}

function EducacionChart({ showQ1, showQ5 }: { showQ1: boolean; showQ5: boolean }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={educData} margin={{ top: 10, right: 20, bottom: 20, left: 0 }} barGap={4} barCategoryGap="30%">
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_C} vertical={false} />
        <XAxis dataKey="nivel" {...axisStyle} />
        <YAxis {...axisStyle} unit=" años" domain={[0, 22]} />
        <Tooltip {...tooltipStyle} formatter={(v: any) => [`${v} años`]} />
        <Legend formatter={(v) => <span style={{ color: DIM, fontSize: 12, fontWeight: 600 }}>{v}</span>} />
        {showQ1 && <Bar dataKey="q1" name="Quintil 1" fill={C_Q1} radius={[6, 6, 0, 0]} maxBarSize={40} />}
        {showQ5 && <Bar dataKey="q5" name="Quintil 5" fill={C_Q5} radius={[6, 6, 0, 0]} maxBarSize={40} />}
      </BarChart>
    </ResponsiveContainer>
  );
}

function EdadChart({ showQ1, showQ5 }: { showQ1: boolean; showQ5: boolean }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={edadData} margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_C} />
        <XAxis dataKey="tramo" {...axisStyle} />
        <YAxis {...axisStyle} unit="%" />
        <Tooltip {...tooltipStyle} formatter={(v: any) => [`${v}%`]} />
        <Legend formatter={(v) => <span style={{ color: DIM, fontSize: 12, fontWeight: 600 }}>{v}</span>} />
        {showQ1 && (
          <Line dataKey="q1" name="Quintil 1" stroke={C_Q1} strokeWidth={3}
            dot={{ fill: C_Q1, r: 4, strokeWidth: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} />
        )}
        {showQ5 && (
          <Line dataKey="q5" name="Quintil 5" stroke={C_Q5} strokeWidth={3}
            dot={{ fill: C_Q5, r: 4, strokeWidth: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}

function PobrezaChart({ showQ1, showQ5 }: { showQ1: boolean; showQ5: boolean }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={pobrezaData} layout="vertical" margin={{ top: 10, right: 30, bottom: 10, left: 62 }} barGap={4}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_C} horizontal={false} />
        <XAxis type="number" {...axisStyle} unit="%" tickFormatter={(v) => `${Math.abs(v)}%`} domain={[-80, 20]} />
        <YAxis type="category" dataKey="dim" {...axisStyle} width={62} />
        <Tooltip {...tooltipStyle}
          content={({ active, payload }) => {
            if (!active || !payload?.[0]) return null;
            return (
              <div style={tooltipStyle.contentStyle}>
                <p style={{ color: DIM, fontWeight: 600, marginBottom: 4 }}>{payload[0].payload.dim}</p>
                {payload.map((p: any) => (
                  <p key={p.dataKey} style={{ color: p.dataKey === "q1" ? C_Q1 : C_Q5 }}>
                    {p.dataKey === "q1" ? "Quintil 1" : "Quintil 5"}: {Math.abs(p.value)}%
                  </p>
                ))}
              </div>
            );
          }}
        />
        <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" />
        {showQ1 && <Bar dataKey="q1" name="Quintil 1" fill={C_Q1} radius={[0, 4, 4, 0]} maxBarSize={28} />}
        {showQ5 && <Bar dataKey="q5" name="Quintil 5" fill={C_Q5} radius={[4, 0, 0, 4]} maxBarSize={28} />}
      </BarChart>
    </ResponsiveContainer>
  );
}

function CalidadChart({ showQ1, showQ5 }: { showQ1: boolean; showQ5: boolean }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid gridType="circle" stroke={GRID_C} />
        <PolarAngleAxis dataKey="subject" tick={{ fill: "#fff", fontSize: 12, fontWeight: 600 }} />
        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: DIM, fontSize: 9 }} />
        <Tooltip {...tooltipStyle} />
        {showQ1 && (
          <Radar name="Quintil 1" dataKey="q1" stroke={C_Q1} fill={C_Q1} fillOpacity={0.22} strokeWidth={2} />
        )}
        {showQ5 && (
          <Radar name="Quintil 5" dataKey="q5" stroke={C_Q5} fill={C_Q5} fillOpacity={0.22} strokeWidth={2} />
        )}
        <Legend formatter={(v) => <span style={{ color: DIM, fontSize: 12, fontWeight: 600 }}>{v}</span>} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

function EmpleoChart() {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <Treemap data={empleoData} dataKey="size" aspectRatio={4 / 3} content={<TreeCell />}>
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.[0]) return null;
            const d = payload[0].payload;
            return (
              <div style={tooltipStyle.contentStyle}>
                <p style={{ color: d.quintil === "q1" ? C_Q1 : C_Q5, fontWeight: 700, marginBottom: 4 }}>
                  {d.name}
                </p>
                <p style={{ color: DIM }}>
                  Quintil: <span style={{ color: "#fff" }}>{d.quintil === "q1" ? "Q1" : "Q5"}</span>
                </p>
                <p style={{ color: DIM }}>
                  Trabajadores: <span style={{ color: "#fff" }}>{d.size.toLocaleString("es-CL")}</span>
                </p>
              </div>
            );
          }}
        />
      </Treemap>
    </ResponsiveContainer>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState(0);
  const [showQ1, setShowQ1] = useState(true);
  const [showQ5, setShowQ5] = useState(true);

  const chartProps = { showQ1, showQ5 };

  const charts = [
    <ViviendaChart {...chartProps} />,
    <LisaChart />,
    <EducacionChart {...chartProps} />,
    <EdadChart {...chartProps} />,
    <PobrezaChart {...chartProps} />,
    <CalidadChart {...chartProps} />,
    <EmpleoChart />,
  ];

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{
        fontFamily: "'Plus Jakarta Sans', Inter, sans-serif",
        background: "#060b26",
        backgroundImage: [
          "radial-gradient(ellipse 65% 55% at 85% 0%,rgba(33,82,255,0.20) 0%,transparent 55%)",
          "radial-gradient(ellipse 55% 45% at 8%  0%,rgba(121,40,202,0.16) 0%,transparent 52%)",
        ].join(","),
      }}
    >
      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <aside
        className="flex flex-col w-60 flex-shrink-0 p-5 gap-6 overflow-y-auto"
        style={{ ...(glass as any), borderRadius: "0 20px 20px 0", margin: "12px 0 12px 12px" }}
      >
        {/* Logo */}
        <div>
          <div className="w-10 h-10 rounded-xl mb-3 flex items-center justify-center text-sm font-black text-white"
            style={{ background: GRAD.info }}>
            C24
          </div>
          <h1 className="text-white font-bold text-[15px] leading-tight">CASEN 2024</h1>
          <p className="text-[11px] mt-0.5 font-medium" style={{ color: DIM }}>
            Quintil 1 vs Quintil 5
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1">
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] mb-1 px-3" style={{ color: DIM }}>
            Secciones
          </p>
          {TABS.map((t, i) => {
            const Icon = TAB_ICONS[i];
            const active = tab === i;
            return (
              <button key={t} onClick={() => setTab(i)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] font-semibold transition-all duration-200 text-left"
                style={{
                  background: active ? GRAD.info : "transparent",
                  color: active ? "#fff" : DIM,
                }}>
                <Icon size={14} strokeWidth={2} />
                {t}
              </button>
            );
          })}
        </nav>

        {/* Q1/Q5 toggles */}
        <div>
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] mb-2 px-1" style={{ color: DIM }}>
            Mostrar series
          </p>
          {[
            { label: "Quintil 1", color: C_Q1, val: showQ1, set: setShowQ1 },
            { label: "Quintil 5", color: C_Q5, val: showQ5, set: setShowQ5 },
          ].map(({ label, color, val, set }) => (
            <div key={label}
              className="flex items-center justify-between px-3 py-2.5 mb-2 rounded-xl"
              style={{ border: `1px solid ${color}30`, background: `${color}10` }}>
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: color }} />
                <span className="text-[13px] font-semibold text-white">{label}</span>
              </div>
              <button
                onClick={() => set((v: boolean) => !v)}
                className="w-9 h-5 rounded-full relative transition-all duration-300 flex-shrink-0"
                style={{ background: val ? color : "rgba(255,255,255,0.10)" }}
                aria-label={`Toggle ${label}`}
              >
                <div
                  className="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-300"
                  style={{ left: val ? "18px" : "2px" }}
                />
              </button>
            </div>
          ))}
        </div>

        {/* Alert section */}
        <div className="mt-auto space-y-2">
          <div className="p-3 rounded-xl text-[11px] leading-relaxed"
            style={{ background: "rgba(33,82,255,0.14)", border: "1px solid rgba(33,82,255,0.28)" }}>
            <div className="flex items-center gap-1.5 mb-1">
              <Info size={11} color="#21D4FD" />
              <span className="font-bold text-white">Fuente</span>
            </div>
            <p style={{ color: DIM }}>
              Encuesta CASEN 2024 · Ministerio de Desarrollo Social, Chile.
              <br />n = 216.439 hogares.
            </p>
          </div>
          <div className="p-3 rounded-xl text-[11px] leading-relaxed"
            style={{ background: "rgba(245,57,57,0.10)", border: "1px solid rgba(245,57,57,0.22)" }}>
            <div className="flex items-center gap-1.5 mb-1">
              <AlertTriangle size={11} color="#F53939" />
              <span className="font-bold text-white">Nota</span>
            </div>
            <p style={{ color: DIM }}>Datos simulados con distribuciones representativas de la encuesta real.</p>
          </div>
        </div>
      </aside>

      {/* ── Main ─────────────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col overflow-hidden p-4 pl-5 gap-4 min-w-0">

        {/* Header */}
        <div className="flex items-center justify-between pt-1 flex-shrink-0">
          <div>
            <h2 className="text-white text-xl font-bold leading-tight">
              Dashboard de Desigualdad
            </h2>
            <p className="text-sm mt-0.5 font-medium" style={{ color: DIM }}>
              Análisis comparativo · ingresos, vivienda, empleo y bienestar · Chile 2024
            </p>
          </div>
          <div className="text-[11px] font-bold px-3.5 py-1.5 rounded-full"
            style={{ background: GRAD.info, color: "#fff" }}>
            Actualizado jul 2025
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-4 gap-4 flex-shrink-0">
          <KpiCard label="Carga vivienda · Q1"  value="42%"   delta="+24 pp vs Q5" icon="🏠" gradient={GRAD.warning} deltaGood={false} />
          <KpiCard label="Brecha ingreso Q5÷Q1"  value="10.1×"                      icon="⚖️" gradient={GRAD.info} />
          <KpiCard label="Informalidad laboral · Q1" value="63%" delta="+51 pp vs Q5" icon="🧩" gradient={GRAD.warning} deltaGood={false} />
          <KpiCard label="Casa propia · Q1"      value="56%"   delta="−22 pp vs Q5" icon="🔑" gradient={GRAD.success} deltaGood={false} />
        </div>

        {/* Chart panel */}
        <div style={{ ...(glass as any) }} className="flex-1 flex flex-col overflow-hidden p-6 gap-4 min-h-0">

          {/* Tab pills */}
          <div className="flex gap-1.5 flex-wrap flex-shrink-0">
            {TABS.map((t, i) => (
              <button key={t} onClick={() => setTab(i)}
                className="px-4 py-1.5 rounded-full text-[12px] font-bold transition-all duration-200"
                style={{
                  background: tab === i ? GRAD.info : "rgba(255,255,255,0.05)",
                  color: tab === i ? "#fff" : DIM,
                  border: tab === i ? "none" : "1px solid rgba(255,255,255,0.07)",
                }}>
                {t}
              </button>
            ))}
          </div>

          {/* Chart title */}
          <div className="flex-shrink-0">
            <div className="flex items-center gap-2 mb-1">
              {(() => { const Icon = TAB_ICONS[tab]; return <Icon size={16} color="#21D4FD" strokeWidth={2} />; })()}
              <h3 className="text-white font-bold text-[15px]">{TABS[tab]}</h3>
            </div>
            <p className="text-[12px] leading-relaxed" style={{ color: DIM }}>{TAB_DESC[tab]}</p>
          </div>

          {/* Chart */}
          <div className="flex-1 min-h-0">
            {charts[tab]}
          </div>
        </div>
      </main>
    </div>
  );
}
