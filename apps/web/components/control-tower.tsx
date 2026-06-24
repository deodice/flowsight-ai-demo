"use client";
import React from "react";
import Link from "next/link";
import { useMemo, useState } from "react";
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowLeft, ArrowRight, ArrowUpRight, Award, Bell, Bot, Boxes, Building2,
  Calendar, Check, ChevronDown, ChevronRight, ClipboardCheck, Clock3, Download, FileBarChart,
  FileCheck2, FileSpreadsheet, Flag, Gauge, HelpCircle, Inbox, LayoutDashboard, ListChecks, Menu,
  Handshake, Mail, MessageSquareMore, PackageSearch, PanelLeftClose, Plus, Search, Send, Settings, ShieldCheck,
  Sparkles, Target, ThumbsDown, ThumbsUp, Truck, UploadCloud, Users, WandSparkles, X, Zap
} from "lucide-react";
import { Area, AreaChart, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Logo } from "./logo";
import { FreightOps } from "./freight-ops";
import { demandData, exceptions as seedExceptions, kpis, navSections, suppliers, type ExceptionItem } from "../lib/demo-data";
import { freightOperationsNavSections, procurementNavSections } from "../lib/freight-data";

const icons: Record<string, React.ReactNode> = {
  overview: <LayoutDashboard />, exceptions: <Inbox />, inventory: <Boxes />, "purchase-orders": <Truck />,
  forecasting: <Activity />, scorecards: <Gauge />, tasks: <ListChecks />, imports: <UploadCloud />,
  quality: <FileCheck2 />, ai: <Bot />, reports: <FileBarChart />, feedback: <MessageSquareMore />,
  admin: <Settings />, "release-notes": <Flag />
  ,freight: <Target />, "freight-opportunities": <ClipboardCheck />, "freight-carriers": <Users />,
  "freight-rfqs": <Mail />, "freight-awards": <Award />, "freight-operations": <Truck />,
  "freight-tenders": <Handshake />, "freight-quotes": <Zap />,
  "freight-invoices": <FileBarChart />, "freight-client": <Users />,
  "freight-admin": <Settings />, "freight-tour": <Sparkles />
};

export function ControlTower({ section }: { section: string }) {
  const [collapsed, setCollapsed] = useState(false);
  const [tenant, setTenant] = useState("Industrial Distributor Demo");
  const [exceptions, setExceptions] = useState(seedExceptions);
  const [selected, setSelected] = useState<ExceptionItem | null>(null);
  const [toast, setToast] = useState("");

  const notify = (message: string) => { setToast(message); setTimeout(() => setToast(""), 2400); };
  const updateException = (id: string, status: ExceptionItem["status"]) => {
    setExceptions(items => items.map(item => item.id === id ? { ...item, status, owner: item.owner === "Unassigned" ? "Maya Chen" : item.owner } : item));
    setSelected(null); notify(status === "In progress" ? "Task created and assigned to Maya Chen" : "Exception updated");
  };

  return (
    <div className="app-shell">
      <aside className={collapsed ? "sidebar collapsed" : "sidebar"}>
        <div className="side-logo"><Logo compact={collapsed} /><button onClick={() => setCollapsed(!collapsed)}><PanelLeftClose /></button></div>
        <nav>{navSections.map(([key, label]) => <Link key={key} className={section === key ? "active" : ""} href={`/app/${key}`}>{icons[key]}<span>{label}</span>{key === "exceptions" && <em>18</em>}</Link>)}<div className="nav-group-label"><span>FREIGHT PROCUREMENT</span></div>{procurementNavSections.map(([key,label]) => <Link key={key} className={section === key ? "active" : ""} href={`/app/${key}`}>{icons[key]}<span>{label}</span>{key === "freight-opportunities" && <em>4</em>}</Link>)}<div className="nav-group-label"><span>FREIGHT OPERATIONS</span></div>{freightOperationsNavSections.map(([key,label]) => <Link key={key} className={section === key ? "active" : ""} href={`/app/${key}`}>{icons[key]}<span>{label}</span>{key === "freight-tenders" && <em>18</em>}</Link>)}</nav>
        <div className="side-bottom"><button><HelpCircle /><span>Help & guides</span></button><div className="profile"><span>MC</span><div><b>Maya Chen</b><small>Tenant admin</small></div><ChevronRight /></div></div>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <button className="mobile-menu"><Menu /></button>
          <button className="tenant-switcher" onClick={() => setTenant(tenant.includes("Industrial") ? "Light Manufacturer Demo" : "Industrial Distributor Demo")}><span className="tenant-icon"><Building2 /></span><span><small>WORKSPACE</small><b>{tenant}</b></span><ChevronDown /></button>
          <div className="top-actions"><div className="search"><Search /><input placeholder="Search SKUs, POs, customers…" /><kbd>⌘ K</kbd></div><button className="icon-btn"><Bell /><i /></button><button className="avatar">MC</button></div>
        </header>
        {section === "overview" && <Overview exceptions={exceptions} onSelect={setSelected} notify={notify} tenant={tenant} />}
        {section === "exceptions" && <ExceptionsPage exceptions={exceptions} onSelect={setSelected} />}
        {section === "forecasting" && <Forecasting />}
        {section === "scorecards" && <Scorecards />}
        {section === "tasks" && <Tasks exceptions={exceptions} notify={notify} />}
        {section === "imports" && <Imports notify={notify} />}
        {section === "ai" && <AISummaries />}
        {section === "reports" && <Reports notify={notify} />}
        {section === "feedback" && <Feedback notify={notify} />}
        {section === "admin" && <Admin />}
        {section === "quality" && <Quality />}
        {section === "inventory" && <RiskCenter title="Inventory risk center" type="Inventory" exceptions={exceptions} onSelect={setSelected} />}
        {section === "purchase-orders" && <RiskCenter title="Purchase order risk center" type="Purchase order" exceptions={exceptions} onSelect={setSelected} />}
        {section === "release-notes" && <ReleaseNotes />}
        {section.startsWith("freight") && <FreightOps section={section as Parameters<typeof FreightOps>[0]["section"]} notify={notify} />}
        {!navSections.some(n => n[0] === section) && !section.startsWith("freight") && <Overview exceptions={exceptions} onSelect={setSelected} notify={notify} tenant={tenant} />}
      </div>
      {selected && <ExceptionDrawer item={selected} close={() => setSelected(null)} act={() => updateException(selected.id, "In progress")} resolve={() => updateException(selected.id, "Resolved")} />}
      {toast && <div className="toast"><Check /> {toast}</div>}
    </div>
  );
}

function PageHead({ eyebrow, title, text, action }: { eyebrow?: string; title: string; text: string; action?: React.ReactNode }) {
  return <div className="page-head"><div>{eyebrow && <span>{eyebrow}</span>}<h1>{title}</h1><p>{text}</p></div>{action}</div>;
}

function Overview({ exceptions, onSelect, notify, tenant }: { exceptions: ExceptionItem[]; onSelect: (x: ExceptionItem) => void; notify: (x: string) => void; tenant: string }) {
  return <main className="page">
    <PageHead eyebrow="MONDAY, JUNE 22 · 8:42 AM" title="Good morning, Maya." text={`Here’s what needs attention across ${tenant}.`} action={<div className="fresh"><i /> All sources current <span>8 min ago</span></div>} />
    <section className="ai-brief">
      <div className="ai-symbol"><Sparkles /></div>
      <div><span>FLOWSIGHT DAILY BRIEF</span><h2>Seven risks need action today. Two could affect key accounts.</h2><p><b>HX-440</b> is projected to stock out in 3.2 days, before its next receipt. Expediting PO 8841 and rebalancing Harrisburg inventory could protect <b>$42.8k</b> in revenue. <b>Northeast Castings</b> also has a high-confidence late PO risk.</p><button onClick={() => onSelect(exceptions[0])}>Review the top risk <ArrowRight /></button></div>
      <div className="brief-meta"><span>7</span><small>urgent actions</small><i /></div>
    </section>
    <section className="kpi-grid">{kpis.map((k, i) => <div className="kpi-card" key={k.label}><div><span>{k.label}</span><HelpCircle /></div><strong>{k.value}</strong><p className={k.tone}><em>{i === 2 || i === 3 ? <ArrowUpRight /> : <ArrowDownRight />}{k.delta}</em> {k.note}</p><div className={`spark s${i}`}><i /><i /><i /><i /><i /><i /><i /></div></div>)}</section>
    <section className="dashboard-grid">
      <div className="panel action-panel"><div className="panel-head"><div><span>WHAT NEEDS ACTION</span><h3>Priority exceptions</h3></div><Link href="/app/exceptions">View all 18 <ArrowRight /></Link></div>
        <div className="exception-list">{exceptions.slice(0, 4).map(item => <button key={item.id} onClick={() => onSelect(item)}><span className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</span><div><b>{item.title}</b><p>{item.detail}</p><small><Clock3 /> {item.due} · {item.owner}</small></div><div className="impact"><small>EST. IMPACT</small><b>${(item.impact / 1000).toFixed(1)}k</b><ChevronRight /></div></button>)}</div>
      </div>
      <div className="panel chart-panel"><div className="panel-head"><div><span>13-WEEK OUTLOOK</span><h3>Demand & forecast</h3></div><button>All sites <ChevronDown /></button></div>
        <ResponsiveContainer width="100%" height={240}><ComposedChart data={demandData}><defs><linearGradient id="forecast" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#1c9a8b" stopOpacity={0.25}/><stop offset="95%" stopColor="#1c9a8b" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e7eceb"/><XAxis dataKey="week" axisLine={false} tickLine={false} tick={{fontSize: 11, fill: "#7d8987"}}/><YAxis hide domain={[500, 1200]}/><Tooltip contentStyle={{borderRadius: 12, border: "1px solid #dfe7e5"}}/><Area type="monotone" dataKey="forecast" stroke="#1c9a8b" strokeWidth={2.5} fill="url(#forecast)"/><Line type="monotone" dataKey="actual" stroke="#132a2a" strokeWidth={2.2} dot={false}/></ComposedChart></ResponsiveContainer>
        <div className="chart-foot"><span><i className="actual" /> Actual</span><span><i className="forecast" /> Forecast</span><b>Forecast accuracy <em>91.8%</em></b></div>
      </div>
    </section>
    <section className="lower-grid"><div className="panel horizon"><div className="panel-head"><div><span>RISK HORIZON</span><h3>What may go wrong next</h3></div></div><div className="horizon-cols"><div><b>7 days</b><strong>9</strong><span>risks · $76k impact</span></div><div><b>14 days</b><strong>18</strong><span>risks · $184k impact</span></div><div><b>30 days</b><strong>31</strong><span>risks · $302k impact</span></div></div></div>
      <div className="panel leakage"><div className="panel-head"><div><span>SERVICE & MARGIN LEAKAGE</span><h3>Top drivers</h3></div></div><div><span>Stockouts</span><b>$83.4k</b><i style={{width:"78%"}} /></div><div><span>Expedite freight</span><b>$41.2k</b><i style={{width:"49%"}} /></div><div><span>Price variance</span><b>$28.7k</b><i style={{width:"34%"}} /></div></div>
      <div className="panel quick-actions"><div className="panel-head"><div><span>QUICK ACTIONS</span><h3>Keep work moving</h3></div></div><button onClick={() => notify("Executive report queued for download")}><Download /> Export executive brief</button><button onClick={() => notify("Import workspace opened")}><UploadCloud /> Upload fresh data</button><button onClick={() => notify("A new task draft is ready")}><Plus /> Create a task</button></div>
    </section>
  </main>;
}

function ExceptionsPage({ exceptions, onSelect }: { exceptions: ExceptionItem[]; onSelect: (x: ExceptionItem) => void }) {
  const [filter, setFilter] = useState("All");
  const shown = filter === "All" ? exceptions : exceptions.filter(x => x.severity === filter || x.status === filter);
  return <main className="page"><PageHead title="Exceptions inbox" text="Prioritized, explainable risks across inventory, purchasing, service, carriers, and spend." action={<button className="button"><Plus /> Create rule</button>} />
    <div className="filterbar"><div>{["All", "Critical", "High", "Open", "In progress"].map(x => <button key={x} className={filter === x ? "active" : ""} onClick={() => setFilter(x)}>{x}{x === "All" && <em>18</em>}</button>)}</div><button><Calendar /> Last 30 days</button><button><Settings /> Filters</button></div>
    <div className="table-card"><table><thead><tr><th>Exception</th><th>Type</th><th>Confidence</th><th>Impact</th><th>Owner</th><th>Status</th><th /></tr></thead><tbody>{shown.map(item => <tr key={item.id} onClick={() => onSelect(item)}><td><span className={`dot ${item.severity.toLowerCase()}`} /><div><b>{item.title}</b><small>{item.id} · Due {item.due}</small></div></td><td>{item.type}</td><td><span className="confidence"><i style={{width:`${item.confidence}%`}} />{item.confidence}%</span></td><td><b>${item.impact.toLocaleString()}</b></td><td>{item.owner}</td><td><span className={`status ${item.status.replace(" ","-").toLowerCase()}`}>{item.status}</span></td><td><ChevronRight /></td></tr>)}</tbody></table></div>
  </main>;
}

function ExceptionDrawer({ item, close, act, resolve }: { item: ExceptionItem; close: () => void; act: () => void; resolve: () => void }) {
  return <div className="drawer-backdrop" onMouseDown={close}><aside className="drawer" onMouseDown={e => e.stopPropagation()}>
    <header><div><span>{item.id}</span><b className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</b></div><button onClick={close}><X /></button></header>
    <div className="drawer-body"><span className="section-kicker">{item.type.toUpperCase()} EXCEPTION</span><h2>{item.title}</h2><p className="lead">{item.detail}</p>
      <div className="impact-box"><div><small>ESTIMATED BUSINESS IMPACT</small><b>${item.impact.toLocaleString()}</b></div><div><small>CONFIDENCE</small><b>{item.confidence}%</b></div></div>
      <section><h3><FileCheck2 /> Evidence</h3>{item.evidence.map(e => <div className="evidence" key={e}><Check />{e}</div>)}</section>
      <section><h3><WandSparkles /> Recommended action</h3><div className="recommendation">{item.action}<small>Recommendation generated from tenant thresholds and linked operating records.</small></div></section>
      <section><h3><PackageSearch /> Related records</h3><div className="related"><button>SKU HX-440 <ArrowRight /></button><button>PO 8841 <ArrowRight /></button><button>Harrisburg DC <ArrowRight /></button></div></section>
      <section className="useful"><span>Was this exception useful?</span><button><ThumbsUp /></button><button><ThumbsDown /></button></section>
    </div><footer><button className="button ghost" onClick={resolve}><Check /> Mark resolved</button><button className="button" onClick={act}><ClipboardCheck /> Create & assign task</button></footer>
  </aside></div>;
}

function Forecasting() {
  const [sku, setSku] = useState("HX-440 · Hydraulic Coupler");
  return <main className="page"><PageHead title="Forecasting workspace" text="Transparent SKU-level forecasts with backtesting, confidence bands, and reorder guidance." action={<button className="button"><Zap /> Run forecast</button>} />
    <div className="forecast-toolbar"><label>SKU<Search /><input value={sku} onChange={e => setSku(e.target.value)} /></label><label>Site<select><option>All sites</option><option>Harrisburg DC</option></select></label><label>Horizon<select><option>13 weeks</option><option>26 weeks</option></select></label></div>
    <section className="forecast-grid"><div className="panel forecast-chart"><div className="panel-head"><div><span>DEMAND FORECAST</span><h3>{sku}</h3></div><span className="model-badge">Holt-Winters · best fit</span></div><ResponsiveContainer width="100%" height={360}><ComposedChart data={demandData}><defs><linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#58b8aa" stopOpacity=".28"/><stop offset="1" stopColor="#58b8aa" stopOpacity=".03"/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5ecea"/><XAxis dataKey="week" axisLine={false} tickLine={false}/><YAxis axisLine={false} tickLine={false}/><Tooltip/><Area type="monotone" dataKey="high" stroke="transparent" fill="url(#band)"/><Area type="monotone" dataKey="low" stroke="transparent" fill="#fff"/><Line type="monotone" dataKey="actual" stroke="#142d2b" strokeWidth={3} dot={false}/><Line type="monotone" dataKey="forecast" stroke="#1d9a8a" strokeWidth={3} strokeDasharray="6 4" dot={false}/></ComposedChart></ResponsiveContainer><div className="chart-foot"><span><i className="actual"/>Actual demand</span><span><i className="forecast"/>Selected forecast</span><span><i className="band"/>80% confidence band</span></div></div>
      <aside className="forecast-side"><div className="panel recommendation-card"><span>REPLENISHMENT GUIDANCE</span><div><small>Recommended reorder point</small><b>468 units</b><em>+42 vs current</em></div><div><small>Safety stock</small><b>188 units</b><em>96% service target</em></div><div><small>Next order date</small><b>Jun 24</b><em>in 2 days</em></div><button className="button">Create replenishment task</button></div><div className="panel model-card"><span>MODEL SELECTION</span>{[["Holt-Winters","8.2%","Selected"],["Moving average","11.6%",""],["Croston","14.1%",""]].map(x => <div key={x[0]}><b>{x[0]}</b><span>WAPE {x[1]}</span>{x[2] && <em><Check />{x[2]}</em>}</div>)}<small>Selected by rolling-window backtest. Lower WAPE is better.</small></div></aside>
    </section>
  </main>;
}

function Scorecards() {
  return <main className="page"><PageHead title="Supplier scorecards" text="A shared, evidence-based view of reliability, lead time, service, and spend." action={<button className="button ghost"><Download /> Export scorecard</button>} />
    <section className="score-hero"><div><span>NETWORK SUPPLIER OTIF</span><b>91.2%</b><em><ArrowUpRight /> 1.4 pts vs last month</em></div><div><span>AVG LEAD TIME</span><b>17.6 days</b><em className="bad"><ArrowUpRight /> 1.8 days slower</em></div><div><span>OPEN SUPPLIER RISK</span><b>$127.3k</b><em>across 11 POs</em></div><div><span>PRICE VARIANCE</span><b>+3.2%</b><em className="bad">above 2% target</em></div></section>
    <div className="table-card supplier-table"><table><thead><tr><th>Supplier</th><th>OTIF</th><th>Avg lead time</th><th>Late PO rate</th><th>12-mo spend</th><th>Trend</th><th /></tr></thead><tbody>{suppliers.map(s => <tr key={s.name}><td><span className="supplier-logo">{s.name.slice(0,2).toUpperCase()}</span><b>{s.name}</b></td><td><strong className={s.otif < 85 ? "bad-text":""}>{s.otif}%</strong></td><td>{s.lead} days</td><td>{s.late}%</td><td>{s.spend}</td><td>{s.trend === "up" ? <span className="good-text"><ArrowUpRight/>Improving</span> : s.trend === "down" ? <span className="bad-text"><ArrowDownRight/>Declining</span> : "Stable"}</td><td><ChevronRight /></td></tr>)}</tbody></table></div>
  </main>;
}

function Tasks({ exceptions, notify }: { exceptions: ExceptionItem[]; notify: (x: string) => void }) {
  const tasks = exceptions.filter(x => x.status !== "Resolved");
  return <main className="page"><PageHead title="Action tracker" text="Keep every operational exception owned, visible, and moving toward resolution." action={<button className="button" onClick={() => notify("New task draft created")}><Plus /> New task</button>} />
    <div className="task-tabs"><button className="active">Board</button><button>List</button><span /> <button>My tasks</button><button>This week</button></div>
    <section className="kanban">{["Open","In progress","Resolved"].map(status => <div className="kanban-col" key={status}><header><b>{status}</b><span>{status === "Resolved" ? 2 : tasks.filter(t => t.status === status).length}</span><button><Plus /></button></header>{(status === "Resolved" ? [{...exceptions[4],title:"Carrier review completed",owner:"Maya Chen"}] : tasks.filter(t => t.status === status)).map(t => <article key={t.id + status}><span className={`priority ${t.severity.toLowerCase()}`}>{t.severity}</span><h3>{t.title}</h3><p>{t.action}</p><div><span className="mini-avatar">{t.owner.slice(0,2)}</span><small><Calendar /> {t.due}</small></div></article>)}</div>)}</section>
  </main>;
}

function Imports({ notify }: { notify: (x: string) => void }) {
  const [mapping, setMapping] = useState(false);
  return <main className="page"><PageHead title="Data imports" text="Bring messy operating exports into a reusable, validated data pipeline." action={<button className="button" onClick={() => setMapping(true)}><UploadCloud /> New import</button>} />
    {!mapping ? <><section className="import-summary"><div><FileSpreadsheet /><span><b>7</b><small>active mapping templates</small></span></div><div><FileCheck2 /><span><b>99.3%</b><small>rows accepted this month</small></span></div><div><Clock3 /><span><b>8 min</b><small>since last refresh</small></span></div></section>
    <div className="table-card"><table><thead><tr><th>Import</th><th>Entity</th><th>Rows</th><th>Quality</th><th>Imported</th><th>Status</th><th /></tr></thead><tbody>{[["inventory_0622.xlsx","Inventory snapshot","12,481","99.8%","8 min ago"],["open_po_0622.csv","Purchase orders","2,814","98.9%","10 min ago"],["sales_orders.csv","Sales orders","8,206","99.5%","Yesterday"],["receipts_week24.xlsx","Receipts","1,122","97.2%","Jun 20"]].map((r,i)=><tr key={r[0]}><td><FileSpreadsheet/><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td><span className="status resolved">Completed</span></td><td><button>•••</button></td></tr>)}</tbody></table></div></> :
    <section className="mapping-flow"><div className="map-head"><button onClick={() => setMapping(false)}><ArrowLeft /></button><div><span>NEW IMPORT · INVENTORY SNAPSHOT</span><h2>Map your columns</h2><p>We matched 5 of 6 required fields automatically.</p></div></div><div className="mapping-grid"><div><h3>Source column</h3><span>SKU_NUMBER</span><span>WAREHOUSE</span><span>QTY_ON_HAND</span><span>QTY_ALLOCATED</span><span>SNAPSHOT_DT</span><span className="warning-map">ITEM_COST</span></div><div className="mapping-arrows">{[1,2,3,4,5,6].map(i=><ArrowRight key={i}/>)}</div><div><h3>FlowSight field</h3><select><option>SKU code</option></select><select><option>Site code</option></select><select><option>Quantity on hand</option></select><select><option>Quantity allocated</option></select><select><option>Snapshot date</option></select><select className="warning-map"><option>Select a field…</option><option>Unit cost</option></select></div></div><div className="validation-note"><AlertTriangle/><span><b>1 mapping needs attention</b><small>Unit cost is recommended for margin-impact calculations.</small></span></div><footer><button className="button ghost">Save as template</button><button className="button" onClick={() => {setMapping(false);notify("12,481 rows imported; 24 rejected rows are ready to review")}}>Validate & import <ArrowRight /></button></footer></section>}
  </main>;
}

function AISummaries() {
  const [liked, setLiked] = useState(0);
  return <main className="page"><PageHead title="AI briefing center" text="Grounded summaries for operations leaders, with every claim linked to source records." action={<button className="button"><Sparkles /> Generate briefing</button>} />
    <div className="ai-layout"><aside className="brief-list"><span>BRIEFINGS</span>{["Daily operations brief","Weekly executive summary","What changed this week","Buyer action brief"].map((x,i)=><button className={i===0?"active":""} key={x}><i>{i===0?<Sparkles/>:<FileBarChart/>}</i><span><b>{x}</b><small>{i===0?"Today · 8:40 AM":i===1?"Friday · 4:00 PM":"Jun 20"}</small></span><ChevronRight/></button>)}</aside><article className="ai-document"><header><div><span>DAILY OPERATIONS BRIEF</span><h1>Seven risks need action today</h1><p>Industrial Distributor Demo · June 22, 2026 · 8:40 AM</p></div><button><Download /></button></header><section><h2>Executive readout</h2><p>Near-term operating risk increased since yesterday, led by one projected stockout and two supplier delays. The current risk set represents <a>$184,200 in estimated impact</a>, with $76,400 concentrated inside the next seven days.</p></section><section><h2>Act now</h2><ol><li><b>Protect HX-440 availability.</b> On-hand inventory covers 3.2 days while PO 8841 is due in 9 days. Expedite 220 units and rebalance 60 units from Harrisburg. <a>EX-1048 · SKU HX-440 · PO 8841</a></li><li><b>Escalate Northeast Castings.</b> PO 8836 has passed the supplier’s normal lead-time band by 9 days with no ASN. <a>EX-1044 · PO 8836</a></li><li><b>Triage aged backorders.</b> Twelve lines are older than the 7-day SLA and four key accounts are affected. <a>EX-1039 · 12 order lines</a></li></ol></section><section><h2>What improved</h2><p>Service level rose 1.8 points to 94.1%, driven by better availability in the bearings category. Late purchase orders declined 8% week over week.</p></section><footer><span>Was this briefing useful?</span><button className={liked===1?"liked":""} onClick={()=>setLiked(1)}><ThumbsUp/></button><button className={liked===-1?"liked":""} onClick={()=>setLiked(-1)}><ThumbsDown/></button><small><ShieldCheck/> Generated from 214 linked records · No external data used</small></footer></article></div>
  </main>;
}

function Reports({ notify }: { notify: (x: string) => void }) {
  return <main className="page"><PageHead title="Reports & exports" text="Branded, role-ready reporting for leadership, operating teams, and customer reviews." action={<button className="button"><Plus /> New report</button>} />
    <section className="report-grid">{[["Executive operating brief","PDF","Weekly snapshot of risk, service, inventory, and actions."],["Supplier performance pack","PDF","OTIF, lead-time, late PO, and price variance trends."],["Exception register","CSV","Full evidence-linked exception history and resolution data."],["Inventory health review","PDF","Stockout risk, excess, aging, and working-capital exposure."]].map((r,i)=><article key={r[0]}><div className={`report-icon r${i}`}><FileBarChart/></div><span>{r[1]}</span><h3>{r[0]}</h3><p>{r[2]}</p><div><button onClick={()=>notify(`${r[0]} is ready to download`)}><Download/> Export</button><button>•••</button></div></article>)}</section>
    <section className="schedule-panel"><div><Calendar/><span><b>Scheduled executive summary</b><small>Every Monday at 7:30 AM · 6 recipients · Branded PDF + email brief</small></span></div><span className="status resolved">Active</span><button>Edit schedule</button></section>
  </main>;
}

function Feedback({ notify }: { notify: (x: string) => void }) {
  const [type,setType]=useState("Feature request");
  return <main className="page"><PageHead title="Feedback center" text="Help shape FlowSight. Every submission is reviewed and tied to the product roadmap." />
    <div className="feedback-layout"><form onSubmit={e=>{e.preventDefault();notify("Thanks — your feedback was submitted")}}><span className="section-kicker">SHARE FEEDBACK</span><h2>What would make FlowSight more useful?</h2><div className="feedback-types">{["Feature request","Report a bug","Bad recommendation"].map(x=><button type="button" className={type===x?"active":""} key={x} onClick={()=>setType(x)}>{x==="Feature request"?<Sparkles/>:x==="Report a bug"?<AlertTriangle/>:<ThumbsDown/>}{x}</button>)}</div><label>Tell us what happened<textarea placeholder="The more context you share, the faster we can improve it…" /></label><label>Area<select><option>Dashboard & exceptions</option><option>Forecasting</option><option>Imports</option><option>Reports</option></select></label><button className="button"><Send/> Submit feedback</button></form><aside><span className="section-kicker">RECENTLY SHIPPED</span><h2>Your feedback, in the product</h2>{[["Jun 18","Confidence bands on every forecast"],["Jun 12","Saved import mapping templates"],["Jun 4","False-positive reason capture"]].map(x=><div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><p>Requested by customers · Now available</p></div>)}<Link href="/app/release-notes">View all release notes <ArrowRight/></Link></aside></div>
  </main>;
}

function Admin() {
  return <main className="page"><PageHead title="Admin & tenant settings" text="Manage workspace configuration, users, branding, entitlements, and audit activity." />
    <div className="admin-tabs"><button className="active">Workspace</button><button>Users & roles</button><button>Branding</button><button>Plan & billing</button><button>Feature flags</button><button>Audit log</button></div>
    <section className="admin-grid"><div className="panel settings-card"><span className="section-kicker">WORKSPACE PROFILE</span><label>Workspace name<input defaultValue="Industrial Distributor Demo"/></label><label>Business type<select><option>Industrial distributor</option></select></label><label>Primary time zone<select><option>America/New_York</option></select></label><button className="button">Save changes</button></div><div className="panel plan-card"><span className="plan-pill">GROWTH PLAN</span><h2>$1,250 <small>/ month</small></h2><p>Renews July 22, 2026</p>{["3 of 3 sites","8 active users · unlimited viewers","Hourly data refresh","Forecasting & AI enabled","Vendor and carrier scorecards"].map(x=><div key={x}><Check/>{x}</div>)}<button className="button ghost">Manage subscription</button></div><div className="panel flag-card"><span className="section-kicker">FEATURE FLAGS</span>{([["AI briefings",true],["Advanced forecasting",true],["White-label reports",false],["REST API access",false]] as [string, boolean][]).map(([label, enabled])=><label key={label}><span>{label}</span><input type="checkbox" defaultChecked={enabled}/><i/></label>)}</div></section>
  </main>;
}

function Quality() {
  return <main className="page"><PageHead title="Data quality center" text="Catch completeness, freshness, validity, and relationship issues before they distort decisions." />
    <section className="quality-score"><div><span>OVERALL DATA HEALTH</span><b>96.8</b><em>Excellent</em></div>{[["Completeness","98.4%"],["Validity","99.1%"],["Freshness","94.2%"],["Relationships","95.6%"]].map(x=><div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><i><em style={{width:x[1]}}/></i></div>)}</section>
    <div className="table-card"><table><thead><tr><th>Issue</th><th>Source</th><th>Rows</th><th>Severity</th><th>First seen</th><th>Status</th></tr></thead><tbody>{[["Missing promised date","open_po_0622.csv","18","High","Today"],["Unknown site code: PITT-2","inventory_0622.xlsx","6","Medium","Today"],["Duplicate sales order lines","sales_orders.csv","11","Medium","Yesterday"]].map(x=><tr key={x[0]}><td><AlertTriangle/><b>{x[0]}</b></td><td>{x[1]}</td><td>{x[2]}</td><td><span className={`severity ${x[3].toLowerCase()}`}>{x[3]}</span></td><td>{x[4]}</td><td><button className="link-btn">Review rows</button></td></tr>)}</tbody></table></div>
  </main>;
}

function RiskCenter({ title, type, exceptions, onSelect }: { title: string; type: string; exceptions: ExceptionItem[]; onSelect: (x: ExceptionItem)=>void }) {
  const rows = exceptions.filter(x=>x.type===type);
  return <main className="page"><PageHead title={title} text={type==="Inventory"?"See where availability, aging, and working capital need action.":"See late-order probability, supplier behavior, and downstream impact."} action={<button className="button ghost"><Download/> Export</button>}/>
    <section className="risk-summary">{(type==="Inventory"?[["SKUs at risk","14"],["Revenue exposed","$83.4k"],["Excess inventory","$241k"],["Inventory turns","7.4x"]]:[["Late / at risk POs","23"],["Open value","$96.2k"],["Avg days late","8.4"],["Supplier OTIF","91.2%"]]).map(x=><div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b></div>)}</section>
    <div className="panel"><div className="panel-head"><div><span>PRIORITIZED</span><h3>{type} exceptions</h3></div></div><div className="exception-list">{rows.length?rows.map(x=><button key={x.id} onClick={()=>onSelect(x)}><span className={`severity ${x.severity.toLowerCase()}`}>{x.severity}</span><div><b>{x.title}</b><p>{x.detail}</p></div><div className="impact"><small>EST. IMPACT</small><b>${x.impact.toLocaleString()}</b><ChevronRight/></div></button>):<div className="empty-state"><Check/><b>No unreviewed exceptions</b><p>Your current filters have no additional items.</p></div>}</div></div>
  </main>;
}

function ReleaseNotes() {
  return <main className="page"><PageHead title="Release notes" text="A transparent record of what’s new, improved, and fixed in FlowSight." /><div className="release-list">{[["June 23, 2026","Freight procurement becomes executable","The new opportunity workspace turns carrier intelligence into RFQs, quote comparison, awards, and a defensible procurement record.",["Transparent carrier matching","Copy-ready RFQ generation","Response and no-bid tracking","Explainable award recommendation","Procurement summary export"]],["June 22, 2026","Freight Ops, from quote to collected cash","A new shared workspace gives brokers, carriers, and shippers mode-aware analytics and an auditable commercial workflow.",["LTL, TL, Spot Bid, and Air Freight","Deterministic quote desk","Invoice aging and disputes","Client-safe shipper portal"]],["June 18, 2026","Forecast confidence, made clearer","Forecast workspaces now show 80% confidence bands, backtest scores, and the reason each model was selected.",["Confidence bands","Transparent WAPE scoring","Improved SKU search"]],["June 12, 2026","Faster repeat imports","Save tenant-specific mappings and reuse them whenever a familiar ERP export arrives.",["Mapping templates","Partial-import rejection reports","Import history"]],["June 4, 2026","Better feedback on exceptions","Tell us when a recommendation missed the mark, including a structured false-positive reason.",["Usefulness voting","False-positive reasons","Admin feedback analytics"]]].map(x=><article key={x[0] as string}><time>{x[0]}</time><div><span>PRODUCT UPDATE</span><h2>{x[1]}</h2><p>{x[2]}</p><ul>{(x[3] as string[]).map(i=><li key={i}><Check/>{i}</li>)}</ul></div></article>)}</div></main>
}
