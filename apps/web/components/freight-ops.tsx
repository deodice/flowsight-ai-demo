"use client";
import React, { useMemo, useState } from "react";
import {
  AlertTriangle, ArrowRight, ArrowUpRight, BadgeDollarSign, BarChart3, Building2, Calendar,
  Check, ChevronDown, ChevronRight, CircleDollarSign, Clock3, Download, FileCheck2,
  FileText, Fuel, Gauge, Handshake, Info, Landmark, Mail, MapPin, MessageSquareMore,
  PackageCheck, Plane, Plus, ReceiptText, Route, Scale, Send, Settings2, ShieldCheck,
  Sparkles, Truck, UploadCloud, Users, X, Zap
} from "lucide-react";
import {
  Area, Bar, BarChart, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip,
  XAxis, YAxis
} from "recharts";
import {
  freightInvoices, freightTenders, freightTrend, invoiceTrend, modePerformance,
  quoteComparisons, type FreightMode, type FreightTender
} from "../lib/freight-data";
import { ProcurementOps, type ProcurementSection } from "./procurement-ops";

type FreightSection =
  | ProcurementSection | "freight-operations" | "freight-tenders" | "freight-quotes" | "freight-invoices"
  | "freight-client" | "freight-admin" | "freight-tour";

const money = (value: number) => value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export function FreightOps({ section, notify }: { section: FreightSection; notify: (message: string) => void }) {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [selectedTender, setSelectedTender] = useState<FreightTender | null>(null);

  return <>
    {(["freight","freight-opportunities","freight-opportunity","freight-carriers","freight-rfqs","freight-awards"] as string[]).includes(section) && <ProcurementOps section={section as ProcurementSection} notify={notify} />}
    {section === "freight-operations" && <FreightDashboard notify={notify} onTender={setSelectedTender} />}
    {section === "freight-tenders" && <TenderBoard onTender={setSelectedTender} notify={notify} />}
    {section === "freight-quotes" && <QuoteDesk notify={notify} />}
    {section === "freight-invoices" && <InvoiceCenter notify={notify} />}
    {section === "freight-client" && <ShipperPortal notify={notify} />}
    {section === "freight-admin" && <FreightAdmin notify={notify} />}
    {section === "freight-tour" && <FreightTour />}
    <button className="freight-feedback-button" onClick={() => setFeedbackOpen(true)}><MessageSquareMore /> Feedback</button>
    {feedbackOpen && <FreightFeedback close={() => setFeedbackOpen(false)} notify={notify} />}
    {selectedTender && <TenderDrawer tender={selectedTender} close={() => setSelectedTender(null)} notify={notify} />}
  </>;
}

function FreightHead({ label, title, text, actions }: { label: string; title: string; text: string; actions?: React.ReactNode }) {
  return <div className="page-head freight-head"><div><span>{label}</span><h1>{title}</h1><p>{text}</p></div>{actions}</div>;
}

function ModeIcon({ mode }: { mode: FreightMode }) {
  return <span className={`mode-icon ${mode.toLowerCase().replace(" ", "-")}`}>{mode === "Air Freight" ? <Plane /> : mode === "LTL" ? <PackageCheck /> : mode === "Spot Bid" ? <Zap /> : <Truck />}</span>;
}

function FreightDashboard({ notify, onTender }: { notify: (message: string) => void; onTender: (tender: FreightTender) => void }) {
  const attention = [
    ["Quote approval", "TND-2076 is below the 15% spot-bid margin floor.", "$590 margin exposure", "critical"],
    ["Tender expiring", "Vantage Medical air tender expires at 4:30 PM.", "$6,425 opportunity", "high"],
    ["Unbilled load", "SHP-8809 delivered 4 days ago with POD attached.", "$3,180 ready to bill", "medium"],
    ["Past-due invoice", "INV-10398 is 37 days past due and disputed.", "$9,120 outstanding", "high"]
  ];
  return <main className="page freight-page">
    <FreightHead label="FREIGHT OPS · BROKER & CARRIER" title="Freight command center" text="Quote speed, tender execution, service, margin, and cash flow in one operating view." actions={<div className="freight-actions"><button className="button ghost"><UploadCloud /> Import freight data</button><a className="button" href="/app/freight-quotes"><Plus /> Build a quote</a></div>} />
    <section className="freight-brief">
      <span className="freight-brief-icon"><Sparkles /></span><div><b>FREIGHT DAILY READOUT</b><h2>Margin improved, but two loads need commercial action before noon.</h2><p>TL margin is up 1.8 points this month. A spot bid on the Pittsburgh-Dallas lane is below the configured floor, and one air tender expires in under five hours. Resolving both protects an estimated <strong>$8.7k</strong> in revenue.</p></div><button onClick={() => notify("Four freight exceptions added to your action queue")}>Open action queue <ArrowRight /></button>
    </section>
    <section className="freight-kpis">
      {[["Loads this month","377","+11.2%","good"],["Gross revenue","$984.2k","+$74.8k","good"],["Gross margin","20.9%","+1.3 pts","good"],["Open AR","$82.4k","$14.1k past due","warning"],["Quote turnaround","18 min","-7 min","good"]].map(k => <div key={k[0]}><span>{k[0]}</span><strong>{k[1]}</strong><em className={k[3]}><ArrowUpRight />{k[2]}</em></div>)}
    </section>
    <section className="mode-performance">
      {modePerformance.map(mode => <article key={mode.mode}><header><ModeIcon mode={mode.mode} /><div><b>{mode.mode}</b><small>{mode.loads} loads this quarter</small></div><ChevronRight /></header><div><span>Revenue<b>{mode.revenue}</b></span><span>Margin<b>{mode.margin}</b></span><span>Acceptance<b>{mode.acceptance}</b></span><span>OTD<b>{mode.otif}</b></span></div></article>)}
    </section>
    <section className="freight-dashboard-grid">
      <div className="panel freight-trend"><div className="panel-head"><div><span>6-MONTH PERFORMANCE</span><h3>Revenue, cost & margin</h3></div><button>All modes <ChevronDown /></button></div>
        <ResponsiveContainer width="100%" height={290}><ComposedChart data={freightTrend}><defs><linearGradient id="freightRevenue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#1c9a8b" stopOpacity=".25"/><stop offset="1" stopColor="#1c9a8b" stopOpacity=".02"/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5ecea"/><XAxis dataKey="month" axisLine={false} tickLine={false}/><YAxis axisLine={false} tickLine={false} tickFormatter={v => `$${v}k`}/><Tooltip/><Area type="monotone" dataKey="revenue" stroke="#168779" strokeWidth={2.5} fill="url(#freightRevenue)"/><Line type="monotone" dataKey="cost" stroke="#7b8b88" strokeWidth={2} strokeDasharray="5 4" dot={false}/></ComposedChart></ResponsiveContainer>
        <footer><span><i className="revenue-line" /> Revenue</span><span><i className="cost-line" /> Carrier cost</span><b>June margin <em>22.5%</em></b></footer>
      </div>
      <div className="panel freight-attention"><div className="panel-head"><div><span>COMMERCIAL EXCEPTIONS</span><h3>Needs attention</h3></div><b>4 open</b></div>{attention.map(item => <button key={item[0]}><span className={`attention-dot ${item[3]}`} /><div><b>{item[0]}</b><p>{item[1]}</p><small>{item[2]}</small></div><ChevronRight /></button>)}</div>
    </section>
    <section className="panel recent-tenders"><div className="panel-head"><div><span>LIVE WORK</span><h3>Recent tenders</h3></div><a href="/app/freight-tenders">Open tender board <ArrowRight /></a></div><FreightTenderTable tenders={freightTenders.slice(0, 5)} onTender={onTender} internal /></section>
  </main>;
}

function FreightTenderTable({ tenders, onTender, internal }: { tenders: FreightTender[]; onTender: (tender: FreightTender) => void; internal: boolean }) {
  return <div className="freight-table-scroll"><table className="freight-table"><thead><tr><th>Tender</th><th>Mode</th><th>Lane</th><th>Pickup</th><th>Quote</th>{internal && <><th>Margin</th><th>Owner</th></>}<th>Status</th><th /></tr></thead><tbody>{tenders.map(t => <tr key={t.id} onClick={() => onTender(t)}><td><div><b>{t.id}</b><small>{t.customer}</small></div></td><td><span className={`mode-pill ${t.mode.toLowerCase().replace(" ", "-")}`}>{t.mode}</span></td><td><div><b>{t.lane}</b><small>{t.equipment}</small></div></td><td>{t.pickup}</td><td><b>{money(t.quoted)}</b></td>{internal && <><td><span className={t.margin < 15 ? "bad-text" : "good-text"}>{t.margin.toFixed(1)}%</span></td><td>{t.owner}</td></>}<td><span className={`freight-status ${t.status.toLowerCase().replaceAll(" ", "-")}`}>{t.status}</span></td><td><ChevronRight /></td></tr>)}</tbody></table></div>;
}

function TenderBoard({ onTender, notify }: { onTender: (tender: FreightTender) => void; notify: (message: string) => void }) {
  const [mode, setMode] = useState("All");
  const [status, setStatus] = useState("Active");
  const shown = freightTenders.filter(t => (mode === "All" || t.mode === mode) && (status === "All" || status === "Active" && !["Delivered","Paid","Closed"].includes(t.status) || t.status === status));
  return <main className="page freight-page">
    <FreightHead label="FREIGHT OPS · SHARED RECORDS" title="Tender board" text="One canonical tender history with revisions, award logic, documents, and role-safe visibility." actions={<button className="button" onClick={() => notify("New tender draft created")}><Plus /> New tender</button>} />
    <div className="freight-filterbar"><div>{["Active","Awarded","In Transit","Delivered","All"].map(x => <button className={status === x ? "active" : ""} onClick={() => setStatus(x)} key={x}>{x}</button>)}</div><select value={mode} onChange={e => setMode(e.target.value)}><option>All</option><option>LTL</option><option>TL</option><option>Spot Bid</option><option>Air Freight</option></select><button><Calendar /> Pickup: next 30 days</button><button><Settings2 /> Saved views</button></div>
    <section className="tender-summary">{[["Active tenders","18","$74.6k quoted"],["Awaiting response","7","3 expire today"],["Award rate","64.8%","+4.1 pts"],["Avg response","22 min","8 min faster"]].map(x => <div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><small>{x[2]}</small></div>)}</section>
    <section className="panel"><FreightTenderTable tenders={shown} onTender={onTender} internal /></section>
  </main>;
}

type QuoteInput = {
  mode: FreightMode; origin: string; destination: string; miles: number; weight: number;
  pallets: number; targetMargin: number; fuelPct: number; liftgate: boolean; appointment: boolean;
  hazmat: boolean; pieces: number; length: number; width: number; height: number;
};

function calculateQuote(input: QuoteInput) {
  const chargeableKg = Math.max(input.weight * .453592, input.pieces * input.length * input.width * input.height * 16.387 / 6000);
  let linehaul = input.mode === "TL" ? input.miles * 2.08
    : input.mode === "Spot Bid" ? input.miles * 2.34
    : input.mode === "Air Freight" ? 225 + chargeableKg * 2.82
    : 165 + input.miles * .48 + (input.weight / 100) * 8.9;
  const minimum = input.mode === "Air Freight" ? 650 : input.mode === "TL" || input.mode === "Spot Bid" ? 950 : 285;
  linehaul = Math.max(minimum, linehaul);
  const fuel = linehaul * (input.fuelPct / 100);
  const accessorials = (input.liftgate ? 95 : 0) + (input.appointment ? 65 : 0) + (input.hazmat ? 175 : 0);
  const internalCost = linehaul + fuel + accessorials;
  const sell = internalCost / (1 - input.targetMargin / 100);
  const requiresApproval = input.targetMargin < (input.mode === "Spot Bid" ? 15 : 17);
  const lines: [string, number][] = [
    ["Base transportation", linehaul],
    [`Fuel surcharge (${input.fuelPct.toFixed(1)}%)`, fuel],
    ["Accessorials", accessorials]
  ];
  return {
    linehaul, fuel, accessorials, internalCost, sell, chargeableKg,
    marginDollars: sell - internalCost, requiresApproval,
    lines,
    trace: [
      `${input.mode} rate basis selected for ${input.miles.toLocaleString()} miles`,
      `Minimum charge checked: ${money(minimum)}`,
      input.mode === "Air Freight" ? `Chargeable weight: ${chargeableKg.toFixed(1)} kg (greater of actual and dimensional)` : `Billable weight: ${input.weight.toLocaleString()} lb`,
      `Target gross margin applied: ${input.targetMargin.toFixed(1)}%`,
      requiresApproval ? "Manual approval required: margin is below the configured floor" : "Quote is inside tenant approval thresholds"
    ]
  };
}

function QuoteDesk({ notify }: { notify: (message: string) => void }) {
  const [input, setInput] = useState<QuoteInput>({ mode: "TL", origin: "Harrisburg, PA 17101", destination: "Nashville, TN 37201", miles: 718, weight: 38200, pallets: 24, targetMargin: 20, fuelPct: 18.5, liftgate: false, appointment: true, hazmat: false, pieces: 1, length: 48, width: 40, height: 52 });
  const [calculated, setCalculated] = useState(false);
  const quote = useMemo(() => calculateQuote(input), [input]);
  const set = <K extends keyof QuoteInput>(key: K, value: QuoteInput[K]) => { setInput(prev => ({...prev, [key]: value})); setCalculated(false); };
  return <main className="page freight-page">
    <FreightHead label="FREIGHT OPS · DETERMINISTIC PRICING" title="Quote desk" text="Build explainable, rate-card-driven freight quotes with an internal calculation trace." actions={<button className="button ghost"><FileText /> Quote history</button>} />
    <div className="quote-layout">
      <section className="quote-form panel"><header><span>RATE REQUEST</span><h2>Shipment and service details</h2><p>Pricing is calculated from tenant rules and rate tables - never from an LLM.</p></header>
        <div className="mode-selector">{(["LTL","TL","Spot Bid","Air Freight"] as FreightMode[]).map(mode => <button key={mode} className={input.mode === mode ? "active" : ""} onClick={() => set("mode", mode)}><ModeIcon mode={mode} />{mode}</button>)}</div>
        <div className="quote-fields two"><label>Origin<div><MapPin /><input value={input.origin} onChange={e => set("origin", e.target.value)} /></div></label><label>Destination<div><MapPin /><input value={input.destination} onChange={e => set("destination", e.target.value)} /></div></label></div>
        <div className="quote-fields four"><label>Distance<input type="number" value={input.miles} onChange={e => set("miles", +e.target.value)} /><small>miles</small></label><label>Weight<input type="number" value={input.weight} onChange={e => set("weight", +e.target.value)} /><small>lb</small></label><label>Pallets<input type="number" value={input.pallets} onChange={e => set("pallets", +e.target.value)} /></label><label>Equipment<select><option>{input.mode === "Air Freight" ? "Priority Air" : input.mode === "LTL" ? "LTL Standard" : "53' Dry Van"}</option></select></label></div>
        {input.mode === "Air Freight" && <div className="air-fields"><span><Plane /> Air cargo details</span><div className="quote-fields four"><label>Pieces<input type="number" value={input.pieces} onChange={e => set("pieces", +e.target.value)} /></label><label>Length<input type="number" value={input.length} onChange={e => set("length", +e.target.value)} /><small>in</small></label><label>Width<input type="number" value={input.width} onChange={e => set("width", +e.target.value)} /><small>in</small></label><label>Height<input type="number" value={input.height} onChange={e => set("height", +e.target.value)} /><small>in</small></label></div><div className="quote-fields two"><label>Airport pair<select><option>PHL → FRA</option><option>JFK → LHR</option></select></label><label>AWB references<input placeholder="MAWB / HAWB assigned after booking" /></label></div></div>}
        <div className="quote-subsection"><h3>Accessorials and special handling</h3><div className="check-grid"><label><input type="checkbox" checked={input.liftgate} onChange={e => set("liftgate", e.target.checked)} /><span><PackageCheck /> Liftgate</span></label><label><input type="checkbox" checked={input.appointment} onChange={e => set("appointment", e.target.checked)} /><span><Clock3 /> Appointment</span></label><label><input type="checkbox" checked={input.hazmat} onChange={e => set("hazmat", e.target.checked)} /><span><AlertTriangle /> Hazmat</span></label></div></div>
        <div className="quote-fields two"><label>Target margin<input type="number" value={input.targetMargin} onChange={e => set("targetMargin", +e.target.value)} /><small>%</small></label><label>Fuel surcharge<input type="number" value={input.fuelPct} onChange={e => set("fuelPct", +e.target.value)} /><small>%</small></label></div>
        <button className="button calculate-button" onClick={() => setCalculated(true)}><BadgeDollarSign /> Calculate auditable quote</button>
      </section>
      <aside className={calculated ? "quote-result calculated" : "quote-result"}>
        <section className="panel quote-client-card"><header><span>CLIENT-FACING QUOTE</span><em className={quote.requiresApproval ? "approval-required" : "within-policy"}>{quote.requiresApproval ? <AlertTriangle /> : <Check />}{quote.requiresApproval ? "Approval required" : "Within policy"}</em></header><div className="quote-number"><small>ESTIMATED TOTAL</small><strong>{money(quote.sell)}</strong><span>{input.mode} · valid for 48 hours</span></div>{quote.lines.map(line => <div className="quote-line" key={line[0]}><span>{line[0]}</span><b>{money(line[1])}</b></div>)}<div className="quote-total"><span>Quoted total</span><b>{money(quote.sell)}</b></div><button className="button" disabled={!calculated} onClick={() => notify(`Quote Q-${Date.now().toString().slice(-5)} issued to Apex Machine Works`)}><Send /> Issue quote</button></section>
        <section className="panel internal-worksheet"><header><span>INTERNAL COSTING WORKSHEET</span><ShieldCheck /></header><div><small>Carrier / operating cost</small><b>{money(quote.internalCost)}</b></div><div><small>Gross margin</small><b>{input.targetMargin.toFixed(1)}% · {money(quote.marginDollars)}</b></div>{input.mode === "Air Freight" && <div><small>Chargeable weight</small><b>{quote.chargeableKg.toFixed(1)} kg</b></div>}<ol>{quote.trace.map(item => <li key={item}><Check />{item}</li>)}</ol><footer><Sparkles /><span><b>Explanation assistant</b><small>This quote uses the active {input.mode} rate basis, fuel index, selected accessorials, and the {input.targetMargin}% target margin. The calculation trace above is the pricing source of truth.</small></span></footer></section>
      </aside>
    </div>
  </main>;
}

function InvoiceCenter({ notify }: { notify: (message: string) => void }) {
  const [tab, setTab] = useState("Invoices");
  return <main className="page freight-page">
    <FreightHead label="FREIGHT OPS · QUOTE TO CASH" title="Invoice center" text="Reconcile quoted, delivered, billed, disputed, and collected values without losing the freight story." actions={<button className="button" onClick={() => notify("Invoice draft created from delivered shipment SHP-8809")}><Plus /> Create invoice</button>} />
    <div className="freight-tabs">{["Invoices","Summary analytics","Disputes & credits"].map(x => <button className={tab === x ? "active" : ""} onClick={() => setTab(x)} key={x}>{x}</button>)}</div>
    {tab === "Invoices" && <><section className="invoice-kpis">{[["Open receivables","$82.4k","31 invoices"],["Past due","$14.1k","6 invoices"],["Average days to pay","32.4","-2.1 days"],["Quoted vs billed","+3.8%","$9.4k variance"],["Disputed","$9.1k","1 invoice"]].map(x => <div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><small>{x[2]}</small></div>)}</section><section className="panel"><div className="freight-filterbar invoice-filters"><div><button className="active">Open</button><button>Past due</button><button>Paid</button><button>All</button></div><button><Download /> Export CSV</button><button><Settings2 /> Columns</button></div><div className="freight-table-scroll"><table className="freight-table invoice-table"><thead><tr><th>Invoice</th><th>Customer</th><th>Shipment</th><th>Mode</th><th>Issued / due</th><th>Quoted</th><th>Billed</th><th>Balance</th><th>Status</th></tr></thead><tbody>{freightInvoices.map(inv => <tr key={inv.id}><td><b>{inv.id}</b></td><td>{inv.customer}</td><td>{inv.shipment}</td><td><span className={`mode-pill ${inv.mode.toLowerCase().replace(" ","-")}`}>{inv.mode}</span></td><td><div><b>{inv.issued}</b><small>Due {inv.due}</small></div></td><td>{money(inv.quoted)}</td><td><b>{money(inv.billed)}</b><small className={inv.billed > inv.quoted ? "bad-text" : ""}>{((inv.billed / inv.quoted - 1) * 100).toFixed(1)}%</small></td><td><b>{money(inv.balance)}</b></td><td><span className={`freight-status ${inv.status.toLowerCase().replaceAll(" ","-")}`}>{inv.status}</span></td></tr>)}</tbody></table></div></section></>}
    {tab === "Summary analytics" && <InvoiceAnalytics />}
    {tab === "Disputes & credits" && <section className="dispute-layout"><div className="panel dispute-card"><header><span className="severity high">Open dispute</span><b>INV-10398 · Federal Supply Group</b><small>Opened Jun 18 · $9,120 on hold</small></header><h3>Air chargeable-weight variance</h3><p>Customer disputes 84.3 kg of dimensional weight and requests the original warehouse dimensions and reweigh certificate.</p><div><span><FileText /> Commercial invoice.pdf</span><span><Plane /> MAWB 074-38192044</span></div><button className="button ghost" onClick={() => notify("Dispute response draft prepared")}>Prepare response</button></div><div className="panel credit-summary"><span>CREDITS · 90 DAYS</span><b>$4,860</b><p>7 credit notes · 0.52% of billed revenue</p><hr/><small>Top reason</small><strong>Duplicate accessorial · $2,140</strong></div></section>}
  </main>;
}

function InvoiceAnalytics() {
  return <section className="invoice-analytics">
    <div className="panel ar-chart"><div className="panel-head"><div><span>6-MONTH CASH TREND</span><h3>Issued vs collected</h3></div></div><ResponsiveContainer width="100%" height={280}><BarChart data={invoiceTrend}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5ecea"/><XAxis dataKey="month" axisLine={false} tickLine={false}/><YAxis axisLine={false} tickLine={false} tickFormatter={v => `$${v}k`}/><Tooltip/><Bar dataKey="issued" fill="#b9dcd7" radius={[4,4,0,0]}/><Bar dataKey="collected" fill="#198b7c" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div>
    <div className="panel aging-card"><div className="panel-head"><div><span>AR AGING</span><h3>Outstanding by bucket</h3></div></div>{[["Current",54.6,66],["1-30 days",13.7,17],["31-60 days",8.2,10],["61-90 days",3.1,4],[">90 days",2.8,3]].map(x => <div key={x[0]}><span>{x[0]}</span><b>${x[1]}k</b><i><em style={{width:`${x[2]}%`}}/></i></div>)}</div>
    <div className="panel variance-card"><div className="panel-head"><div><span>LEAKAGE ANALYSIS</span><h3>Quoted vs billed variance</h3></div></div>{[["Accessorials","+$5.2k","55%"],["Weight / class","+$2.7k","29%"],["Fuel index","+$1.1k","12%"],["Other","+$0.4k","4%"]].map(x => <div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><small>{x[2]} of variance</small></div>)}</div>
  </section>;
}

function ShipperPortal({ notify }: { notify: (message: string) => void }) {
  const [view, setView] = useState("Overview");
  return <main className="page freight-page client-portal">
    <FreightHead label="FREIGHT OPS · CLIENT-SAFE PORTAL" title="Apex Machine Works" text="Freight spend, tenders, service, quotes, and invoices - with internal carrier costs excluded by design." actions={<button className="button" onClick={() => notify("New rate request opened")}><Plus /> Request a rate</button>} />
    <div className="client-safety"><ShieldCheck /><span><b>Client-safe view</b><small>Carrier cost, gross margin, internal notes, and approval thresholds are not available in this workspace.</small></span></div>
    <div className="freight-tabs">{["Overview","Tenders","Compare quotes","Invoices"].map(x => <button className={view === x ? "active" : ""} onClick={() => setView(x)} key={x}>{x}</button>)}</div>
    {view === "Overview" && <><section className="client-kpis">{[["Freight spend · YTD","$412.8k","+8.2% volume"],["Active shipments","14","2 need attention"],["On-time delivery","95.4%","+1.6 pts"],["Avg cost / shipment","$2,184","-3.8%"],["Open invoices","$31.7k","5 invoices"]].map(x => <div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><small>{x[2]}</small></div>)}</section><section className="client-grid"><div className="panel client-spend"><div className="panel-head"><div><span>MODE MIX</span><h3>Freight spend by load type</h3></div></div>{[["TL",184.2,44.6],["Air Freight",96.8,23.4],["LTL",78.4,19],["Spot Bid",53.4,13]].map(x => <div key={x[0]}><span>{x[0]}</span><b>${x[1]}k</b><i><em style={{width:`${x[2]}%`}}/></i><small>{x[2]}%</small></div>)}</div><div className="panel carrier-performance"><div className="panel-head"><div><span>CARRIER PERFORMANCE</span><h3>Service scorecard</h3></div></div>{[["Keystone Freight Partners","96","95.8%","$184k"],["Blue Ridge Transport","89","92.1%","$121k"],["RoadStar Logistics","82","87.4%","$68k"]].map(x => <div key={x[0]}><span className="supplier-logo">{x[0].slice(0,2)}</span><b>{x[0]}</b><em>{x[1]}</em><small>OTD {x[2]} · Spend {x[3]}</small></div>)}</div></section></>}
    {view === "Tenders" && <section className="panel"><FreightTenderTable tenders={freightTenders.filter(t => t.customer === "Apex Machine Works" || t.customer === "Vantage Medical")} onTender={() => notify("Tender document history opened")} internal={false} /></section>}
    {view === "Compare quotes" && <QuoteComparison notify={notify} />}
    {view === "Invoices" && <section className="panel"><div className="freight-table-scroll"><table className="freight-table"><thead><tr><th>Invoice</th><th>Shipment</th><th>Mode</th><th>Quoted</th><th>Billed</th><th>Due</th><th>Status</th><th /></tr></thead><tbody>{freightInvoices.slice(0,4).map(inv => <tr key={inv.id}><td><b>{inv.id}</b></td><td>{inv.shipment}</td><td><span className={`mode-pill ${inv.mode.toLowerCase().replace(" ","-")}`}>{inv.mode}</span></td><td>{money(inv.quoted)}</td><td><b>{money(inv.billed)}</b></td><td>{inv.due}</td><td><span className={`freight-status ${inv.status.toLowerCase().replaceAll(" ","-")}`}>{inv.status}</span></td><td><ChevronRight /></td></tr>)}</tbody></table></div></section>}
  </main>;
}

function QuoteComparison({ notify }: { notify: (message: string) => void }) {
  return <section className="quote-comparison"><header><div><span>RATE REQUEST RR-2841</span><h2>Harrisburg, PA → Nashville, TN</h2><p>53' dry van · 38,200 lb · Pickup Jun 24</p></div><span>3 complete quotes</span></header><div className="comparison-grid">{quoteComparisons.map(q => <article className={q.recommended ? "recommended" : ""} key={q.carrier}>{q.recommended && <em><Sparkles /> Recommended</em>}<span className="supplier-logo">{q.carrier.slice(0,2)}</span><h3>{q.carrier}</h3><strong>{money(q.total)}</strong><small>{q.service}</small><dl><div><dt>Pickup</dt><dd>{q.pickup}</dd></div><div><dt>Delivery</dt><dd>{q.delivery}</dd></div><div><dt>Service score</dt><dd>{q.score}/100</dd></div></dl><p><Info />{q.note}</p><button className={q.recommended ? "button" : "button ghost"} onClick={() => notify(`${q.carrier} selected; award confirmation prepared`)}>Select quote</button></article>)}</div></section>;
}

function FreightAdmin({ notify }: { notify: (message: string) => void }) {
  const [tab, setTab] = useState("Rate cards");
  return <main className="page freight-page">
    <FreightHead label="FREIGHT OPS · SHARED ADMIN" title="Freight configuration" text="Change commercial rules safely with tenant-scoped versions, approvals, and audit history." actions={<button className="button ghost"><Download /> Export configuration</button>} />
    <div className="freight-tabs">{["Rate cards","Pricing rules","Accessorials","Workflows","Portal & flags"].map(x => <button className={tab === x ? "active" : ""} onClick={() => setTab(x)} key={x}>{x}</button>)}</div>
    {tab === "Rate cards" && <section className="admin-rate-layout"><div className="panel rate-list"><header><span>ACTIVE RATE CARDS</span><button onClick={() => notify("New rate card draft created")}><Plus /> Add</button></header>{[["Apex Machine Works · TL","Customer sell","TL","v4 · Jun 1"],["Keystone Network · LTL","Carrier buy","LTL","v7 · May 18"],["Priority Air · Northeast-Europe","Carrier buy","Air Freight","v2 · Jun 10"],["Spot market baseline","Internal benchmark","Spot Bid","Daily index"]].map((x,i) => <button className={i===0?"active":""} key={x[0]}><ModeIcon mode={x[2] as FreightMode}/><span><b>{x[0]}</b><small>{x[1]} · {x[3]}</small></span><ChevronRight /></button>)}</div><div className="panel rate-editor"><span className="section-kicker">CUSTOMER RATE CARD · VERSION 4</span><h2>Apex Machine Works · TL</h2><p>Effective June 1, 2026 · Applies before lane overrides</p><div className="rule-grid"><label>Rate basis<select><option>Per loaded mile</option></select></label><label>Base rate<input defaultValue="$2.08" /></label><label>Minimum charge<input defaultValue="$950.00" /></label><label>Fuel index<select><option>DOE weekly · 18.5%</option></select></label><label>Margin floor<input defaultValue="17.0%" /></label><label>Approval threshold<input defaultValue="15.0%" /></label></div><div className="config-callout"><ShieldCheck /><span><b>Versioned and auditable</b><small>Publishing creates a new immutable version and records the user, timestamp, and changed fields.</small></span></div><footer><button className="button ghost">View audit history</button><button className="button" onClick={() => notify("Rate card version 5 published")}>Publish new version</button></footer></div></section>}
    {tab === "Pricing rules" && <RuleTable rows={[["PA → Southeast TL override","Lane override","$2.14 / mile","Priority 10","Active"],["Air dimensional divisor","Air Freight","6,000 cm³/kg","Priority 20","Active"],["Spot margin guardrail","Spot Bid","15% minimum","Priority 30","Active"],["Customer fuel cap · Apex","Customer","22% maximum","Priority 40","Active"]]} />}
    {tab === "Accessorials" && <RuleTable rows={[["Liftgate service","LTL","$95 fixed","Origin or destination","Active"],["Appointment delivery","LTL / TL","$65 fixed","Per stop","Active"],["Hazmat handling","All surface","$175 fixed","Per shipment","Active"],["Air security screening","Air Freight","$0.18 / kg","Chargeable weight","Active"]]} />}
    {tab === "Workflows" && <section className="workflow-cards">{[["Under-floor quote approval","Sales manager","Margin below mode floor","Quote cannot be issued until approved"],["Tender expiry escalation","Quote desk","2 hours before expiry","Email and in-app alert"],["Delivered, not billed","Billing","48 hours after POD","Create invoice task"],["Invoice past due","Finance","1 day after due date","Collections follow-up"]].map(x => <article key={x[0]}><span><Zap /></span><h3>{x[0]}</h3><p>{x[2]}</p><div><small>Owner</small><b>{x[1]}</b></div><div><small>Action</small><b>{x[3]}</b></div><label><input type="checkbox" defaultChecked/><i/></label></article>)}</section>}
    {tab === "Portal & flags" && <section className="panel portal-flags"><h2>Workspace capabilities</h2>{([["Broker and carrier workspace",true],["Client and shipper portal",true],["Air freight fields",true],["Client quote comparison",true],["Accounting sync beta",false],["Document OCR beta",false]] as [string, boolean][]).map(([label, enabled]) => <label key={label}><span><b>{label}</b><small>Tenant-scoped rollout</small></span><input type="checkbox" defaultChecked={enabled}/><i/></label>)}</section>}
  </main>;
}

function RuleTable({ rows }: { rows: string[][] }) {
  return <section className="panel"><div className="freight-filterbar"><div><button className="active">Active</button><button>Draft</button><button>Archived</button></div><button><Plus /> New rule</button></div><div className="freight-table-scroll"><table className="freight-table"><thead><tr><th>Rule</th><th>Scope</th><th>Value</th><th>Application</th><th>Status</th><th /></tr></thead><tbody>{rows.map(x => <tr key={x[0]}><td><b>{x[0]}</b></td><td>{x[1]}</td><td><b>{x[2]}</b></td><td>{x[3]}</td><td><span className="freight-status accepted">{x[4]}</span></td><td><ChevronRight /></td></tr>)}</tbody></table></div></section>;
}

function FreightTour() {
  const steps = [
    ["1","Create the freight opportunity","Capture the lane, dates, mode, commodity, government relevance, compliance gates, and quote deadline once."],
    ["2","Find qualified capacity","Rank carriers transparently by mode, region, capability, compliance, relationship, and prior awards."],
    ["3","Run the RFQ and award","Shortlist carriers, generate RFQ text, track responses, compare bids, and preserve the decision rationale."],
    ["4","Build an auditable sell quote","Use Quote Desk to apply rate cards, fuel, accessorials, chargeable weight, and margin guardrails."],
    ["5","Move the tender to execution","Issue, counter, award, and track one canonical tender with revision and document history."],
    ["6","Reconcile and share safely","Invoice delivered freight, resolve variances, and give clients visibility without revealing internal cost or margin."]
  ];
  return <main className="page freight-page freight-tour">
    <FreightHead label="FREIGHT OPS · GUIDED WALKTHROUGH" title="From freight need to collected cash" text="A ten-minute product tour for shippers, brokers, carriers, government contractors, and logistics teams." />
    <section className="tour-hero"><div><span>THE EXECUTION WEDGE</span><h2>Professional freight procurement and operations without a heavyweight TMS implementation.</h2><p>Start with a movement that needs capacity. FlowSight turns carrier intelligence into a shared source-to-cash workflow with transparent matching, RFQ control, explainable pricing, role-safe collaboration, and decision-grade analytics.</p><a className="button" href="/app/freight">Start the guided tour <ArrowRight /></a></div><aside><div><b>47 min</b><small>saved per sourced load</small></div><div><b>64%</b><small>quote response visibility</small></div><div><b>91%</b><small>awards with rationale</small></div></aside></section>
    <section className="tour-steps">{steps.map(step => <article key={step[0]}><span>{step[0]}</span><div><h3>{step[1]}</h3><p>{step[2]}</p></div><Check /></article>)}</section>
    <section className="tour-pricing"><div><span>STARTER</span><b>$249<small>/month</small></b><p>Owner-operators, micro-brokers, and small regional carriers.</p></div><div className="featured"><span>GROWTH</span><b>$599<small>/month</small></b><p>Both workspaces, tender management, advanced analytics, and branded portal.</p></div><div><span>PRO</span><b>$1,250<small>/month</small></b><p>Full quote-to-cash, advanced permissions, API, and accounting integration.</p></div></section>
  </main>;
}

function TenderDrawer({ tender, close, notify }: { tender: FreightTender; close: () => void; notify: (message: string) => void }) {
  return <div className="drawer-backdrop" onMouseDown={close}><aside className="drawer freight-drawer" onMouseDown={e => e.stopPropagation()}><header><div><span>{tender.id}</span><b className={`freight-status ${tender.status.toLowerCase().replaceAll(" ","-")}`}>{tender.status}</b></div><button onClick={close}><X /></button></header><div className="drawer-body"><span className="section-kicker">{tender.mode.toUpperCase()} TENDER</span><h2>{tender.lane}</h2><p className="lead">{tender.customer} · Pickup {tender.pickup} · {tender.equipment}</p><div className="tender-value-grid"><div><small>CLIENT QUOTE</small><b>{money(tender.quoted)}</b></div><div><small>INTERNAL COST</small><b>{money(tender.cost)}</b></div><div><small>GROSS MARGIN</small><b className={tender.margin < 15 ? "bad-text" : "good-text"}>{tender.margin.toFixed(1)}%</b></div></div><section><h3><Clock3 /> Tender timeline</h3>{[["Issued","Jun 22 · 9:14 AM","Quote Q-3128 attached"],[tender.status,"Jun 22 · 10:06 AM",tender.status === "Countered" ? "Customer requested earlier uplift" : "Commercial terms confirmed"],["Pickup",`${tender.pickup} · 10:00 AM`,"Appointment requested"]].map((x,i) => <div className="timeline-event" key={x[0]}><i className={i < 2 ? "done" : ""}/><span><b>{x[0]}</b><small>{x[1]} · {x[2]}</small></span></div>)}</section>{tender.mode === "Air Freight" && <section><h3><Plane /> Air freight references</h3><div className="air-reference"><span><small>MAWB</small><b>074-38192044</b></span><span><small>HAWB</small><b>KFP-882941</b></span><span><small>Chargeable weight</small><b>1,842.6 kg</b></span></div></section>}<section><h3><FileCheck2 /> Documents</h3><div className="related"><button>Rate confirmation.pdf</button><button>Customer tender.xlsx</button>{tender.mode === "Air Freight" && <button>Draft AWB.pdf</button>}</div></section></div><footer><button className="button ghost" onClick={() => notify("Tender revision created")}>Create revision</button><button className="button" onClick={() => {notify(`${tender.id} advanced to the next workflow state`);close()}}><Handshake /> Advance tender</button></footer></aside></div>;
}

function FreightFeedback({ close, notify }: { close: () => void; notify: (message: string) => void }) {
  return <div className="freight-feedback-modal"><header><div><span>FREIGHT OPS FEEDBACK</span><h3>Help us smooth the rough edges.</h3></div><button onClick={close}><X /></button></header><div><label>Feedback type<select><option>Workflow pain point</option><option>Feature request</option><option>Report an issue</option><option>Bad recommendation</option></select></label><label>What happened?<textarea placeholder="Tell us what slowed you down or what would make this page more useful…" /></label><div className="feedback-context"><Info /><span>We’ll include this page, your workspace role, tenant, and browser context. No quote costs or customer documents are attached automatically.</span></div><button className="button" onClick={() => {notify("Freight Ops feedback submitted with page context");close()}}><Send /> Submit feedback</button></div></div>;
}
