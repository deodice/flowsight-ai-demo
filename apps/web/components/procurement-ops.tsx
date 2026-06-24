"use client";

import React, { useMemo, useState } from "react";
import {
  AlertTriangle, ArrowLeft, ArrowRight, Award, Building2, Calendar, Check, CheckCircle2,
  ChevronDown, ChevronRight, Clipboard, Clock3, Download, FileCheck2, FileText,
  Filter, Flag, Gauge, Handshake, Info, Mail, MapPin, PackageCheck, Plus, Route,
  Search, Send, ShieldAlert, ShieldCheck, Sparkles, Target, Truck, UserRoundCheck,
  Users, X, Zap
} from "lucide-react";
import {
  initialCandidates, procurementCarriers, procurementOpportunities, type CandidateState,
  type ProcurementCarrier, type ProcurementMode, type ProcurementOpportunity
} from "../lib/procurement-data";

export type ProcurementSection =
  | "freight" | "freight-opportunities" | "freight-opportunity"
  | "freight-carriers" | "freight-rfqs" | "freight-awards";

const money = (value: number) => value.toLocaleString("en-US", {
  style: "currency", currency: "USD", maximumFractionDigits: 0
});

function Head({ eyebrow, title, text, actions }: {
  eyebrow: string; title: string; text: string; actions?: React.ReactNode;
}) {
  return <div className="page-head freight-head"><div><span>{eyebrow}</span><h1>{title}</h1><p>{text}</p></div>{actions}</div>;
}

function statusClass(value: string) {
  return value.toLowerCase().replaceAll(" ", "-");
}

function scoreOpportunity(opportunity: ProcurementOpportunity): CandidateState[] {
  if (opportunity.id === "OPP-2417") return initialCandidates;
  return procurementCarriers.map(carrier => {
    const mode = carrier.modes.includes(opportunity.mode) ? 25 : -25;
    const government = opportunity.government
      ? (carrier.government || carrier.sddc || carrier.gfm ? 15 : -15)
      : (carrier.government ? 5 : 0);
    const region = carrier.regions.includes("Nationwide")
      || carrier.regions.some(regionName => opportunity.origin.includes(regionName))
      ? 15 : carrier.headquarters.endsWith(opportunity.origin.split(", ")[1]?.slice(0, 2) || "") ? 15 : 5;
    const special = (!opportunity.hazmat || carrier.hazmat) && (!opportunity.refrigerated || carrier.refrigerated) ? 10 : -20;
    const relationship = carrier.relationship === "Preferred" ? 10 : carrier.relationship === "Active" ? 7 : carrier.relationship === "Prospect" ? 2 : carrier.relationship === "Do not use" ? -50 : 0;
    const compliance = carrier.compliance === "Complete" ? 15 : carrier.compliance === "Review due" ? 7 : carrier.compliance === "Expired" ? -30 : -8;
    const contact = carrier.email ? 5 : -5;
    const awards = Math.min(10, carrier.priorAwards * 2);
    const points = mode + government + region + special + relationship + compliance + contact + awards;
    return {
      carrierId: carrier.id, score: Math.max(0, Math.min(100, points)),
      eligible: mode > 0 && special > 0 && compliance > -20 && carrier.relationship !== "Do not use",
      shortlisted: false, status: "Not contacted" as const,
      breakdown: [
        { label: "Mode match", points: mode, reason: carrier.modes.includes(opportunity.mode) ? `${opportunity.mode} is covered` : `${opportunity.mode} is not covered` },
        { label: "Government readiness", points: government, reason: carrier.government ? "Government indicator present" : "No government indicator" },
        { label: "Region fit", points: region, reason: carrier.regions.join(", ") },
        { label: "Special capability", points: special, reason: special > 0 ? "Shipment requirements supported" : "Required capability is missing" },
        { label: "Relationship", points: relationship, reason: carrier.relationship },
        { label: "Compliance", points: compliance, reason: carrier.compliance },
        { label: "Prior awards", points: awards, reason: `${carrier.priorAwards} prior awards` },
        { label: "Contact completeness", points: contact, reason: carrier.email ? "RFQ email available" : "POC email missing" }
      ]
    };
  }).sort((a, b) => b.score - a.score);
}

function recommendationFor(candidates: CandidateState[]) {
  const quoted = candidates.filter(item => item.eligible && item.rate && item.transitDays);
  if (!quoted.length) return null;
  const lowest = Math.min(...quoted.map(item => item.rate || Infinity));
  const fastest = Math.min(...quoted.map(item => item.transitDays || Infinity));
  return quoted.map(item => ({
    item,
    total: item.score * .55 + (lowest / (item.rate || lowest)) * 35 + (fastest / (item.transitDays || fastest)) * 10
  })).sort((a, b) => b.total - a.total)[0];
}

function rfqText(opportunity: ProcurementOpportunity, carrier: ProcurementCarrier) {
  const requirements = [
    opportunity.hazmat && "Hazmat capable",
    opportunity.refrigerated && "Temperature controlled",
    opportunity.sddc && "SDDC readiness",
    opportunity.gfm && "GFM relevance",
    ...opportunity.complianceTags
  ].filter(Boolean).join(", ");
  return {
    subject: `RFQ: ${opportunity.mode} | ${opportunity.origin} to ${opportunity.destination}`,
    body: `Hello ${carrier.contact === "POC missing" ? "Carrier Partner" : carrier.contact},

Please provide a rate and capacity confirmation for the following freight opportunity:

Opportunity: ${opportunity.name}
Program / contract: ${opportunity.program} / ${opportunity.contract}
Origin: ${opportunity.origin}
Destination: ${opportunity.destination}
Pickup: ${opportunity.pickup}
Delivery required: ${opportunity.delivery}
Mode: ${opportunity.mode}
Commodity: ${opportunity.commodity}
Weight: ${opportunity.weight.toLocaleString()} lb
Dimensions: ${opportunity.dimensions}
Special requirements: ${requirements || "None noted"}
Quote deadline: ${opportunity.deadline}

Please include total rate, fuel, accessorials, transit time, rate expiration, and any exceptions.

Thank you,
[Your name / contact information]`
  };
}

export function ProcurementOps({ section, notify }: {
  section: ProcurementSection; notify: (message: string) => void;
}) {
  const [opportunities, setOpportunities] = useState(procurementOpportunities);
  const [activeId, setActiveId] = useState("OPP-2417");
  const [candidateSets, setCandidateSets] = useState<Record<string, CandidateState[]>>({
    "OPP-2417": initialCandidates
  });
  const [workspaceFromList, setWorkspaceFromList] = useState(false);

  const active = opportunities.find(item => item.id === activeId) || opportunities[0];
  const candidates = candidateSets[active.id] || scoreOpportunity(active);
  const setCandidates = (next: CandidateState[]) => setCandidateSets(current => ({ ...current, [active.id]: next }));
  const updateOpportunity = (next: ProcurementOpportunity) => {
    setOpportunities(items => items.map(item => item.id === next.id ? next : item));
  };
  const openOpportunity = (opportunity: ProcurementOpportunity) => {
    setActiveId(opportunity.id);
    if (!candidateSets[opportunity.id]) {
      setCandidateSets(current => ({ ...current, [opportunity.id]: scoreOpportunity(opportunity) }));
    }
    setWorkspaceFromList(true);
  };
  const createOpportunity = (opportunity: ProcurementOpportunity) => {
    setOpportunities(items => [opportunity, ...items]);
    setActiveId(opportunity.id);
    setCandidateSets(current => ({ ...current, [opportunity.id]: scoreOpportunity(opportunity) }));
    setWorkspaceFromList(true);
    notify(`${opportunity.id} created and carrier matching completed`);
  };

  if (section === "freight") {
    return <ProcurementCommand opportunities={opportunities} onOpen={openOpportunity} />;
  }
  if (section === "freight-carriers") return <CarrierNetwork notify={notify} />;
  if (section === "freight-rfqs") return <RFQCenter opportunities={opportunities} />;
  if (section === "freight-awards") return <AwardRegister opportunities={opportunities} />;
  if (section === "freight-opportunities" && !workspaceFromList) {
    return <OpportunityList opportunities={opportunities} onOpen={openOpportunity} onCreate={createOpportunity} />;
  }
  return <OpportunityWorkspace
    opportunity={active} candidates={candidates}
    setCandidates={setCandidates} updateOpportunity={updateOpportunity}
    notify={notify} onBack={section === "freight-opportunities" ? () => setWorkspaceFromList(false) : undefined}
  />;
}

function ProcurementCommand({ opportunities, onOpen }: {
  opportunities: ProcurementOpportunity[]; onOpen: (opportunity: ProcurementOpportunity) => void;
}) {
  const active = opportunities.filter(item => item.status !== "Awarded");
  return <main className="page freight-page procurement-page">
    <Head eyebrow="FREIGHT PROCUREMENT · DAILY EXECUTION" title="Move today’s freight with fewer blind spots."
      text="Find qualified capacity, run competitive RFQs, compare compliant bids, and preserve the award decision in one workspace."
      actions={<div className="freight-actions"><a className="button ghost" href="/app/freight-carriers"><Users /> Carrier network</a><a className="button" href="/app/freight-opportunities"><Plus /> New opportunity</a></div>} />
    <section className="procurement-hero">
      <div><span><Target /> SOURCING PRIORITY</span><h2>Four movements need carrier action before today’s quote deadlines.</h2><p>The Ramstein air uplift has no RFQs out, one spot movement has no matched carriers, and the DLA replenishment is ready for award. Closing those gaps protects the operating schedule and creates a defensible procurement record.</p><a href="/app/freight-opportunities">Open opportunity queue <ArrowRight /></a></div>
      <aside><strong>47 min</strong><small>saved per sourced load</small><hr/><b>3.2×</b><small>more compliant quotes captured</small></aside>
    </section>
    <section className="procurement-kpis">
      {[["Open opportunities",active.length.toString(),"2 urgent"],["RFQs sent","14","5 today"],["Quotes received","9","64% response"],["Average TL quote","$2,864","-4.1% vs May"],["Awards this month","22","91% documented"]].map(item => <div key={item[0]}><span>{item[0]}</span><b>{item[1]}</b><small>{item[2]}</small></div>)}
    </section>
    <section className="procurement-grid">
      <div className="panel opportunity-queue"><header><div><span>WORK QUEUE</span><h3>Freight opportunities</h3></div><a href="/app/freight-opportunities">View all <ArrowRight /></a></header>
        {active.slice(0, 4).map(item => <button key={item.id} onClick={() => onOpen(item)}><span className={`priority-dot ${item.priority.toLowerCase()}`} /><div><b>{item.name}</b><small>{item.id} · {item.origin} → {item.destination}</small></div><span className={`mode-pill ${statusClass(item.mode)}`}>{item.mode}</span><div className="queue-progress"><b>{item.quotes}/{item.shortlisted || "—"}</b><small>quotes / shortlisted</small></div><span className={`freight-status ${statusClass(item.status)}`}>{item.status}</span><ChevronRight /></button>)}
      </div>
      <aside className="panel sourcing-alerts"><header><span>DATA READINESS</span><h3>Carrier gaps slowing execution</h3></header>
        <div><ShieldAlert /><span><b>2 carrier files need review</b><small>Insurance expires inside 60 days</small></span><a href="/app/freight-carriers">Review</a></div>
        <div><UserRoundCheck /><span><b>1 high-fit carrier has no POC</b><small>Titan National Parcel cannot receive an RFQ</small></span><a href="/app/freight-carriers">Complete</a></div>
        <div><Clock3 /><span><b>3 RFQs need follow-up</b><small>No response after four hours</small></span><a href="/app/freight-rfqs">Open</a></div>
      </aside>
    </section>
    <section className="panel procurement-pipeline"><header><div><span>PROCUREMENT PIPELINE</span><h3>Work by stage</h3></div><small>Updated from opportunity activity</small></header><div>{[["Draft",1,"$4.0k"],["Sourcing",1,"$8.8k"],["RFQ open",1,"$1.2k"],["Evaluating",1,"$2.8k"],["Awarded",22,"$86.4k"]].map((item,index)=><article key={item[0]}><i className={index < 4 ? "active" : "done"} /><span>{item[0]}</span><b>{item[1]}</b><small>{item[2]} expected spend</small></article>)}</div></section>
  </main>;
}

function OpportunityList({ opportunities, onOpen, onCreate }: {
  opportunities: ProcurementOpportunity[];
  onOpen: (opportunity: ProcurementOpportunity) => void;
  onCreate: (opportunity: ProcurementOpportunity) => void;
}) {
  const [showCreate, setShowCreate] = useState(false);
  if (showCreate) return <NewOpportunityForm onCancel={() => setShowCreate(false)} onCreate={onCreate} />;
  return <main className="page freight-page procurement-page">
    <Head eyebrow="FREIGHT PROCUREMENT · OPPORTUNITY QUEUE" title="Freight opportunities"
      text="Every sourcing event, carrier response, bid, and award decision in one operating queue."
      actions={<button className="button" onClick={() => setShowCreate(true)}><Plus /> New opportunity</button>} />
    <section className="tender-summary procurement-summary">{[["Open","4","$16.8k expected"],["RFQ deadline today","3","Air, TL, spot"],["Quotes received","9","64% response"],["Ready to award","1","OPP-2417"]].map(item => <div key={item[0]}><span>{item[0]}</span><b>{item[1]}</b><small>{item[2]}</small></div>)}</section>
    <div className="freight-filterbar"><div><button className="active">Open</button><button>Draft</button><button>Awarded</button><button>All</button></div><button><Filter /> Mode: all</button><button><Calendar /> Pickup: next 14 days</button><button><Search /> Search</button></div>
    <section className="panel opportunity-table-wrap"><table className="freight-table opportunity-table"><thead><tr><th>Opportunity</th><th>Lane</th><th>Mode</th><th>Pickup / deadline</th><th>Carrier activity</th><th>Owner</th><th>Status</th><th /></tr></thead><tbody>{opportunities.map(item => <tr key={item.id} onClick={() => onOpen(item)}><td><div><b>{item.id} · {item.name}</b><small>{item.program}</small></div></td><td><div><b>{item.origin}</b><small>→ {item.destination}</small></div></td><td><span className={`mode-pill ${statusClass(item.mode)}`}>{item.mode}</span></td><td><div><b>{item.pickup}</b><small>Quotes: {item.deadline}</small></div></td><td><div className="activity-counts"><span>{item.matched}<small>matched</small></span><span>{item.rfqs}<small>RFQs</small></span><span>{item.quotes}<small>quotes</small></span></div></td><td>{item.owner}</td><td><span className={`freight-status ${statusClass(item.status)}`}>{item.status}</span></td><td><ChevronRight /></td></tr>)}</tbody></table></section>
  </main>;
}

function NewOpportunityForm({ onCancel, onCreate }: {
  onCancel: () => void; onCreate: (opportunity: ProcurementOpportunity) => void;
}) {
  const [government, setGovernment] = useState(true);
  const [hazmat, setHazmat] = useState(false);
  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const id = `OPP-${Math.floor(2420 + Math.random() * 400)}`;
    onCreate({
      id, name: String(data.get("name")), program: String(data.get("program")),
      contract: String(data.get("contract") || "Not specified"),
      origin: String(data.get("origin")), destination: String(data.get("destination")),
      pickup: String(data.get("pickup")), delivery: String(data.get("delivery")),
      deadline: String(data.get("deadline")), mode: String(data.get("mode")) as ProcurementMode,
      weight: Number(data.get("weight")), dimensions: String(data.get("dimensions")),
      commodity: String(data.get("commodity")), hazmat, refrigerated: data.get("refrigerated") === "on",
      government, sddc: data.get("sddc") === "on", gfm: data.get("gfm") === "on",
      complianceTags: government ? ["Active authority", "Cargo insurance", "Government readiness"] : ["Active authority", "Cargo insurance"],
      documents: ["Operating authority", "Cargo insurance", "W-9"],
      priority: String(data.get("priority")) as ProcurementOpportunity["priority"],
      status: "Sourcing", owner: "Maya Chen", matched: 7, shortlisted: 0, rfqs: 0, quotes: 0
    });
  };
  return <main className="page freight-page procurement-page">
    <button className="back-link" onClick={onCancel}><ArrowLeft /> Back to opportunities</button>
    <Head eyebrow="NEW FREIGHT OPPORTUNITY" title="What needs to move?"
      text="Capture the shipment once. FlowSight will use it to find, vet, contact, and compare the right carriers." />
    <form className="panel opportunity-form" onSubmit={submit}>
      <section><header><span>1</span><div><h2>Opportunity context</h2><p>Name the work so the procurement record survives beyond the inbox.</p></div></header><div className="opportunity-fields three"><label>Opportunity name<input required name="name" defaultValue="Urgent depot replenishment" /></label><label>Customer / program<input required name="program" defaultValue="DLA depot support" /></label><label>Contract / reference<input name="contract" defaultValue="DEMO-SP4701-26-D-0220" /></label></div></section>
      <section><header><span>2</span><div><h2>Shipment requirements</h2><p>These fields drive mode, capability, region, and compliance matching.</p></div></header>
        <div className="opportunity-fields two"><label>Origin city, state, ZIP<input required name="origin" defaultValue="Harrisburg, PA 17101" /></label><label>Destination city, state, ZIP<input required name="destination" defaultValue="Nashville, TN 37201" /></label></div>
        <div className="opportunity-fields four"><label>Pickup<input required name="pickup" defaultValue="Jun 28 · 8:00 AM" /></label><label>Delivery<input required name="delivery" defaultValue="Jun 30 · 5:00 PM" /></label><label>Quote deadline<input required name="deadline" defaultValue="Jun 24 · 4:00 PM" /></label><label>Priority<select name="priority" defaultValue="Urgent"><option>Normal</option><option>Urgent</option><option>Critical</option></select></label></div>
        <div className="opportunity-fields four"><label>Mode<select name="mode" defaultValue="TL">{(["Small Parcel","LTL","TL","Air Freight","Spot Bid","Other"] as ProcurementMode[]).map(mode => <option key={mode}>{mode}</option>)}</select></label><label>Weight (lb)<input required type="number" name="weight" defaultValue="38200" /></label><label>Dimensions / handling units<input name="dimensions" defaultValue="24 pallets · 48 × 40 × 52 in" /></label><label>Commodity<input required name="commodity" defaultValue="Hydraulic assemblies" /></label></div>
      </section>
      <section><header><span>3</span><div><h2>Capability and compliance</h2><p>Make disqualifiers explicit before an RFQ goes out.</p></div></header>
        <div className="requirement-checks"><label><input type="checkbox" checked={hazmat} onChange={event => setHazmat(event.target.checked)} /><span><AlertTriangle /> Hazmat</span></label><label><input type="checkbox" name="refrigerated" /><span><PackageCheck /> Refrigerated</span></label><label><input type="checkbox" checked={government} onChange={event => setGovernment(event.target.checked)} /><span><Flag /> Government relevance</span></label><label><input type="checkbox" name="sddc" defaultChecked /><span><ShieldCheck /> SDDC</span></label><label><input type="checkbox" name="gfm" defaultChecked /><span><FileCheck2 /> GFM</span></label></div>
      </section>
      <footer><button type="button" className="button ghost" onClick={onCancel}>Cancel</button><button className="button"><Sparkles /> Create and match carriers</button></footer>
    </form>
  </main>;
}

function OpportunityWorkspace({ opportunity, candidates, setCandidates, updateOpportunity, notify, onBack }: {
  opportunity: ProcurementOpportunity; candidates: CandidateState[];
  setCandidates: (items: CandidateState[]) => void;
  updateOpportunity: (opportunity: ProcurementOpportunity) => void;
  notify: (message: string) => void; onBack?: () => void;
}) {
  const [tab, setTab] = useState("Carrier matching");
  const [rfqCarrierId, setRfqCarrierId] = useState<string | null>(null);
  const recommended = recommendationFor(candidates);
  const shortlisted = candidates.filter(item => item.shortlisted);
  const toggleShortlist = (carrierId: string) => setCandidates(candidates.map(item => item.carrierId === carrierId ? {
    ...item, shortlisted: !item.shortlisted,
    status: !item.shortlisted ? "Shortlisted" : "Not contacted"
  } : item));
  const generateRfqs = () => {
    setCandidates(candidates.map(item => item.shortlisted && !["Quoted","RFQ sent"].includes(item.status) ? { ...item, status: "RFQ ready" } : item));
    setTab("RFQ desk");
    notify(`${shortlisted.length} copy-ready RFQs generated`);
  };
  const markSent = (carrierId: string) => {
    setCandidates(candidates.map(item => item.carrierId === carrierId ? { ...item, status: "RFQ sent" } : item));
    setRfqCarrierId(null); notify("RFQ marked sent and response timer started");
  };
  const saveQuote = (carrierId: string, values: { rate: number; transitDays: number; fuel: number; accessorials: string; notes: string }) => {
    setCandidates(candidates.map(item => item.carrierId === carrierId ? { ...item, ...values, status: "Quoted" } : item));
    notify("Carrier quote saved to the opportunity");
  };
  const awardCarrier = () => {
    if (!recommended) return;
    const carrier = procurementCarriers.find(item => item.id === recommended.item.carrierId)!;
    const rationale = `Recommended and awarded to ${carrier.name}: ${money(recommended.item.rate || 0)} total, ${recommended.item.transitDays}-day transit, ${recommended.item.score}/100 carrier fit, complete compliance, and the strongest combined price/service/readiness score.`;
    setCandidates(candidates.map(item => ({ ...item, status: item.carrierId === carrier.id ? "Awarded" : item.shortlisted ? "Rejected" : item.status })));
    updateOpportunity({ ...opportunity, status: "Awarded", awardedCarrier: carrier.name, rationale });
    setTab("Decision record"); notify(`${opportunity.id} awarded to ${carrier.name}`);
  };
  const exportSummary = () => {
    const rows = candidates.filter(item => item.rate).map(item => {
      const carrier = procurementCarriers.find(row => row.id === item.carrierId)!;
      return `| ${carrier.name} | ${money(item.rate || 0)} | ${item.transitDays} days | ${item.score}/100 | ${carrier.compliance} |`;
    }).join("\n");
    const summary = `# Procurement Summary — ${opportunity.id}

**Opportunity:** ${opportunity.name}
**Program / contract:** ${opportunity.program} / ${opportunity.contract}
**Lane:** ${opportunity.origin} → ${opportunity.destination}
**Mode:** ${opportunity.mode}
**Pickup:** ${opportunity.pickup}

## Bid comparison
| Carrier | Rate | Transit | Fit score | Compliance |
|---|---:|---:|---:|---|
${rows}

## Award decision
**Awarded carrier:** ${opportunity.awardedCarrier || "Pending"}
**Decision rationale:** ${opportunity.rationale || "Pending"}
`;
    const blob = new Blob([summary], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = `${opportunity.id.toLowerCase()}-procurement-summary.md`; anchor.click();
    URL.revokeObjectURL(url); notify("Procurement summary exported");
  };
  const selectedRfqCarrier = procurementCarriers.find(item => item.id === rfqCarrierId);

  return <main className="page freight-page procurement-page">
    {onBack && <button className="back-link" onClick={onBack}><ArrowLeft /> Back to opportunity queue</button>}
    <Head eyebrow={`FREIGHT OPPORTUNITY · ${opportunity.id}`} title={opportunity.name}
      text={`${opportunity.program} · ${opportunity.origin} → ${opportunity.destination}`}
      actions={<div className="freight-actions"><button className="button ghost" onClick={exportSummary}><Download /> Export summary</button>{opportunity.status !== "Awarded" && <button className="button" onClick={() => setTab("Carrier matching")}><Target /> Continue sourcing</button>}</div>} />
    <section className="opportunity-statusbar">
      <div><span className={`priority-badge ${opportunity.priority.toLowerCase()}`}>{opportunity.priority}</span><span className={`freight-status ${statusClass(opportunity.status)}`}>{opportunity.status}</span></div>
      <dl><div><dt>Mode</dt><dd>{opportunity.mode}</dd></div><div><dt>Pickup</dt><dd>{opportunity.pickup}</dd></div><div><dt>Quote deadline</dt><dd>{opportunity.deadline}</dd></div><div><dt>Weight</dt><dd>{opportunity.weight.toLocaleString()} lb</dd></div><div><dt>Owner</dt><dd>{opportunity.owner}</dd></div></dl>
    </section>
    <section className="procurement-stepper">
      {["Shipment details","Carrier matching","RFQ desk","Quotes & award","Decision record"].map((item,index) => {
        const activeIndex = ["Shipment details","Carrier matching","RFQ desk","Quotes & award","Decision record"].indexOf(tab);
        return <button key={item} className={tab === item ? "active" : index < activeIndex ? "complete" : ""} onClick={() => setTab(item)}><i>{index < activeIndex || opportunity.status === "Awarded" ? <Check /> : index + 1}</i><span>{item}</span></button>;
      })}
    </section>
    {tab === "Shipment details" && <ShipmentDetails opportunity={opportunity} />}
    {tab === "Carrier matching" && <CarrierMatching candidates={candidates} toggleShortlist={toggleShortlist} generateRfqs={generateRfqs} />}
    {tab === "RFQ desk" && <OpportunityRFQs opportunity={opportunity} candidates={candidates} onPreview={setRfqCarrierId} generateRfqs={generateRfqs} />}
    {tab === "Quotes & award" && <QuotesAndAward candidates={candidates} saveQuote={saveQuote} awardCarrier={awardCarrier} />}
    {tab === "Decision record" && <DecisionRecord opportunity={opportunity} candidates={candidates} onExport={exportSummary} />}
    {selectedRfqCarrier && <RFQModal opportunity={opportunity} carrier={selectedRfqCarrier} close={() => setRfqCarrierId(null)} markSent={() => markSent(selectedRfqCarrier.id)} notify={notify} />}
  </main>;
}

function ShipmentDetails({ opportunity }: { opportunity: ProcurementOpportunity }) {
  return <section className="workspace-grid">
    <div className="panel shipment-detail-card"><header><span>SHIPMENT REQUIREMENTS</span><h2>What carriers are bidding on</h2></header><dl><div><dt>Origin</dt><dd><MapPin />{opportunity.origin}</dd></div><div><dt>Destination</dt><dd><MapPin />{opportunity.destination}</dd></div><div><dt>Pickup</dt><dd><Calendar />{opportunity.pickup}</dd></div><div><dt>Delivery</dt><dd><Calendar />{opportunity.delivery}</dd></div><div><dt>Commodity</dt><dd>{opportunity.commodity}</dd></div><div><dt>Handling units</dt><dd>{opportunity.dimensions}</dd></div></dl></div>
    <aside className="panel requirement-card"><header><span>QUALIFICATION GATES</span><h3>Required before award</h3></header>{opportunity.complianceTags.map(item => <div key={item}><ShieldCheck /><span><b>{item}</b><small>Required compliance tag</small></span></div>)}{opportunity.documents.map(item => <div key={item}><FileCheck2 /><span><b>{item}</b><small>Document must be current</small></span></div>)}</aside>
  </section>;
}

function CarrierMatching({ candidates, toggleShortlist, generateRfqs }: {
  candidates: CandidateState[]; toggleShortlist: (id: string) => void; generateRfqs: () => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(candidates[0]?.carrierId || null);
  const shortlisted = candidates.filter(item => item.shortlisted).length;
  return <section className="matching-layout">
    <div className="matching-main"><div className="matching-toolbar"><div><b>{candidates.length} carriers ranked</b><small>Transparent fit scoring from mode, region, capability, compliance, relationship, and award history.</small></div><button><Filter /> Adjust matching rules</button></div>
      {candidates.map(candidate => {
        const carrier = procurementCarriers.find(item => item.id === candidate.carrierId)!;
        return <article className={`panel carrier-match-card ${!candidate.eligible ? "ineligible" : ""}`} key={carrier.id}>
          <button className="match-summary" onClick={() => setExpanded(expanded === carrier.id ? null : carrier.id)}>
            <span className={`fit-score ${candidate.score >= 80 ? "high" : candidate.score >= 55 ? "medium" : "low"}`}><b>{candidate.score}</b><small>/100</small></span>
            <span className="carrier-logo">{carrier.code}</span><span className="match-carrier"><b>{carrier.name}</b><small>{carrier.classification} · {carrier.headquarters} · {carrier.relationship}</small><span>{carrier.modes.map(mode => <em key={mode}>{mode}</em>)}</span></span>
            <span className="readiness-badges">{carrier.government && <em><Flag /> Government</em>}{carrier.sddc && <em><ShieldCheck /> SDDC</em>}<em className={carrier.compliance === "Complete" ? "complete" : "warning"}>{carrier.compliance}</em></span>
            {!candidate.eligible && <span className="not-eligible"><AlertTriangle /> Not award eligible</span>}<ChevronDown />
          </button>
          {expanded === carrier.id && <div className="score-breakdown"><header><span>FIT SCORE BREAKDOWN</span><b>{candidate.score}/100</b></header><div>{candidate.breakdown.map(item => <span key={item.label}><i className={item.points >= 0 ? "positive" : "negative"}>{item.points > 0 ? "+" : ""}{item.points}</i><b>{item.label}</b><small>{item.reason}</small></span>)}</div></div>}
          <footer><span>{carrier.email ? <><Mail /> {carrier.email}</> : <><AlertTriangle /> Missing RFQ email</>}</span><button disabled={!candidate.eligible} className={candidate.shortlisted ? "button shortlisted" : "button ghost"} onClick={() => toggleShortlist(carrier.id)}>{candidate.shortlisted ? <Check /> : <Plus />}{candidate.shortlisted ? "Shortlisted" : "Shortlist"}</button></footer>
        </article>;
      })}
    </div>
    <aside className="panel shortlist-rail"><header><span>SHORTLIST</span><b>{shortlisted} carriers</b></header>{candidates.filter(item => item.shortlisted).map(item => { const carrier = procurementCarriers.find(row => row.id === item.carrierId)!; return <div key={carrier.id}><span className="carrier-logo">{carrier.code}</span><span><b>{carrier.name}</b><small>{item.score}/100 fit · {carrier.compliance}</small></span><CheckCircle2 /></div>})}<button className="button" disabled={!shortlisted} onClick={generateRfqs}><Mail /> Generate {shortlisted || ""} RFQs</button><small>RFQs are generated as copy-ready drafts. Nothing is sent automatically.</small></aside>
  </section>;
}

function OpportunityRFQs({ opportunity, candidates, onPreview, generateRfqs }: {
  opportunity: ProcurementOpportunity; candidates: CandidateState[];
  onPreview: (id: string) => void; generateRfqs: () => void;
}) {
  const rows = candidates.filter(item => item.shortlisted);
  if (!rows.length) return <section className="panel procurement-empty"><Mail /><h2>No carriers shortlisted yet</h2><p>Return to carrier matching and shortlist qualified carriers before generating RFQs.</p><button className="button" onClick={generateRfqs}>Return to matching</button></section>;
  return <section className="panel rfq-workbench"><header><div><span>RFQ WORKBENCH</span><h2>{opportunity.id} · {rows.length} selected carriers</h2><p>Generate consistent shipment details, then track each carrier response independently.</p></div><button className="button" onClick={generateRfqs}><Sparkles /> Regenerate all</button></header><table className="freight-table"><thead><tr><th>Carrier</th><th>Contact</th><th>Fit</th><th>RFQ status</th><th>Response clock</th><th /></tr></thead><tbody>{rows.map(item => { const carrier = procurementCarriers.find(row => row.id === item.carrierId)!; return <tr key={carrier.id}><td><div><b>{carrier.name}</b><small>{carrier.classification} · {carrier.relationship}</small></div></td><td><div><b>{carrier.contact}</b><small>{carrier.email || "Email missing"}</small></div></td><td><b>{item.score}/100</b></td><td><span className={`freight-status ${statusClass(item.status)}`}>{item.status}</span></td><td>{item.status === "RFQ sent" ? "2h 14m elapsed" : item.status === "Quoted" ? "Responded" : "Not started"}</td><td><button className="link-button" onClick={() => onPreview(carrier.id)}><FileText /> Preview RFQ</button></td></tr>})}</tbody></table></section>;
}

function RFQModal({ opportunity, carrier, close, markSent, notify }: {
  opportunity: ProcurementOpportunity; carrier: ProcurementCarrier; close: () => void;
  markSent: () => void; notify: (message: string) => void;
}) {
  const rfq = rfqText(opportunity, carrier);
  const copy = async () => {
    await navigator.clipboard?.writeText(`Subject: ${rfq.subject}\n\n${rfq.body}`);
    notify("RFQ copied to clipboard");
  };
  return <div className="drawer-backdrop" onMouseDown={close}><aside className="drawer rfq-drawer" onMouseDown={event => event.stopPropagation()}><header><div><span>COPY-READY RFQ</span><h2>{carrier.name}</h2></div><button onClick={close}><X /></button></header><div className="drawer-body"><label>Subject<input value={rfq.subject} readOnly /></label><label>Email body<textarea value={rfq.body} readOnly /></label><div className="rfq-guardrail"><Info /><span><b>No email is sent from FlowSight.</b><small>Copy this draft into your approved email system, then mark it sent to start response tracking.</small></span></div></div><footer><button className="button ghost" onClick={copy}><Clipboard /> Copy RFQ</button><button className="button" onClick={markSent}><Send /> Mark RFQ sent</button></footer></aside></div>;
}

function QuotesAndAward({ candidates, saveQuote, awardCarrier }: {
  candidates: CandidateState[];
  saveQuote: (id: string, values: { rate: number; transitDays: number; fuel: number; accessorials: string; notes: string }) => void;
  awardCarrier: () => void;
}) {
  const quoted = candidates.filter(item => item.shortlisted);
  const recommendation = recommendationFor(candidates);
  const recommendedCarrier = recommendation ? procurementCarriers.find(item => item.id === recommendation.item.carrierId) : null;
  return <section className="quote-award-layout">
    <div className="quote-entry-list"><header><div><span>QUOTE TRACKER</span><h2>Carrier responses</h2></div><small>{candidates.filter(item => item.rate).length} of {quoted.length} quotes received</small></header>{quoted.map(item => <QuoteEntry key={item.carrierId} candidate={item} save={saveQuote} />)}</div>
    <aside className="panel award-recommendation"><header><Sparkles /><span><b>EXPLAINABLE RECOMMENDATION</b><small>Price, carrier fit, transit, and compliance</small></span></header>{recommendedCarrier && recommendation ? <><span className="carrier-logo">{recommendedCarrier.code}</span><h2>{recommendedCarrier.name}</h2><strong>{money(recommendation.item.rate || 0)}</strong><p>Recommended because it combines a <b>{recommendation.item.score}/100 carrier-fit score</b>, {recommendation.item.transitDays}-day transit, {recommendedCarrier.compliance.toLowerCase()} compliance, and the strongest weighted procurement score.</p><dl><div><dt>Carrier fit</dt><dd>{recommendation.item.score}/100</dd></div><div><dt>Total rate</dt><dd>{money(recommendation.item.rate || 0)}</dd></div><div><dt>Transit</dt><dd>{recommendation.item.transitDays} days</dd></div><div><dt>Government ready</dt><dd>{recommendedCarrier.government ? "Yes" : "No"}</dd></div></dl><button className="button" onClick={awardCarrier}><Award /> Award freight</button><small>Other shortlisted carriers will be marked rejected. The rationale and score snapshot will be stored.</small></> : <div className="recommendation-waiting"><Clock3 /><h3>Waiting for quote data</h3><p>Enter at least one eligible carrier quote to produce an award recommendation.</p></div>}</aside>
    <div className="panel bid-comparison"><header><div><span>BID COMPARISON</span><h3>Side-by-side procurement view</h3></div></header><table className="freight-table"><thead><tr><th>Carrier</th><th>Rate</th><th>Transit</th><th>Fit</th><th>Compliance</th><th>Government</th><th>Notes</th><th>Recommendation</th></tr></thead><tbody>{candidates.filter(item => item.rate).map(item => { const carrier = procurementCarriers.find(row => row.id === item.carrierId)!; const recommended = recommendation?.item.carrierId === item.carrierId; return <tr key={carrier.id}><td><b>{carrier.name}</b></td><td><b>{money(item.rate || 0)}</b></td><td>{item.transitDays} days</td><td>{item.score}/100</td><td><span className={`compliance-label ${carrier.compliance === "Complete" ? "complete" : "warning"}`}>{carrier.compliance}</span></td><td>{carrier.government ? <Check /> : "—"}</td><td>{item.notes}</td><td>{recommended ? <span className="recommended-label"><Sparkles /> Recommended</span> : "Not selected"}</td></tr>})}</tbody></table></div>
  </section>;
}

function QuoteEntry({ candidate, save }: {
  candidate: CandidateState;
  save: (id: string, values: { rate: number; transitDays: number; fuel: number; accessorials: string; notes: string }) => void;
}) {
  const carrier = procurementCarriers.find(item => item.id === candidate.carrierId)!;
  const [rate, setRate] = useState(candidate.rate || 0);
  const [transit, setTransit] = useState(candidate.transitDays || 2);
  const [fuel, setFuel] = useState(candidate.fuel || 0);
  const [accessorials, setAccessorials] = useState(candidate.accessorials || "");
  const [notes, setNotes] = useState(candidate.notes || "");
  return <article className="panel quote-entry"><header><span className="carrier-logo">{carrier.code}</span><span><b>{carrier.name}</b><small>{carrier.contact} · {candidate.score}/100 fit</small></span><span className={`freight-status ${statusClass(candidate.status)}`}>{candidate.status}</span></header><div><label>Total rate<input aria-label={`${carrier.name} rate`} type="number" value={rate || ""} onChange={event => setRate(+event.target.value)} /></label><label>Transit days<input aria-label={`${carrier.name} transit days`} type="number" value={transit} onChange={event => setTransit(+event.target.value)} /></label><label>Fuel<input aria-label={`${carrier.name} fuel`} type="number" value={fuel} onChange={event => setFuel(+event.target.value)} /></label><label>Accessorials<input aria-label={`${carrier.name} accessorials`} value={accessorials} onChange={event => setAccessorials(event.target.value)} /></label></div><label className="quote-notes">Quote notes<input aria-label={`${carrier.name} quote notes`} value={notes} onChange={event => setNotes(event.target.value)} /></label><footer><small>Currency USD · quote expiration required before award</small><button className="button ghost" disabled={!rate} onClick={() => save(carrier.id, { rate, transitDays: transit, fuel, accessorials, notes })}><Check /> Save quote</button></footer></article>;
}

function DecisionRecord({ opportunity, candidates, onExport }: {
  opportunity: ProcurementOpportunity; candidates: CandidateState[]; onExport: () => void;
}) {
  const awarded = candidates.find(item => item.status === "Awarded");
  const carrier = awarded ? procurementCarriers.find(item => item.id === awarded.carrierId) : undefined;
  return <section className="decision-layout">
    <article className="panel decision-card"><header><span className={opportunity.status === "Awarded" ? "decision-icon awarded" : "decision-icon"}>{opportunity.status === "Awarded" ? <Award /> : <Clock3 />}</span><div><span>PROCUREMENT DECISION</span><h2>{opportunity.status === "Awarded" ? `${opportunity.id} awarded` : "Award decision pending"}</h2><p>{opportunity.status === "Awarded" ? `${carrier?.name || opportunity.awardedCarrier} · ${money(awarded?.rate || 0)} · ${awarded?.transitDays} days` : "Complete quote comparison to create the award record."}</p></div></header>{opportunity.rationale && <blockquote>{opportunity.rationale}</blockquote>}<div className="decision-checks">{["Shipment requirements captured","Carrier fit scores preserved","RFQ activity timestamped","All received bids compared","Award rationale recorded"].map(item => <span key={item}><CheckCircle2 />{item}</span>)}</div><button className="button" onClick={onExport}><Download /> Export procurement summary</button></article>
    <aside className="panel decision-timeline"><header><span>AUDIT TIMELINE</span><h3>Decision history</h3></header>{[["Opportunity created","Maya Chen","Jun 23 · 8:12 AM"],["5 carriers matched","System","Jun 23 · 8:13 AM"],["3 carriers shortlisted","Maya Chen","Jun 23 · 8:19 AM"],["3 RFQs marked sent","Maya Chen","Jun 23 · 8:24 AM"],["3 quotes recorded","Quote desk","Jun 23 · 10:31 AM"],[opportunity.status === "Awarded" ? "Award recorded" : "Award pending", opportunity.status === "Awarded" ? "Maya Chen" : "—", opportunity.status === "Awarded" ? "Jun 23 · 10:42 AM" : "Awaiting decision"]].map((item,index)=><div key={item[0]}><i className={index < 5 || opportunity.status === "Awarded" ? "complete" : ""}/><span><b>{item[0]}</b><small>{item[1]} · {item[2]}</small></span></div>)}</aside>
  </section>;
}

function CarrierNetwork({ notify }: { notify: (message: string) => void }) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("All");
  const [governmentOnly, setGovernmentOnly] = useState(false);
  const [selected, setSelected] = useState<ProcurementCarrier | null>(null);
  const filtered = procurementCarriers.filter(carrier =>
    (!query || `${carrier.name} ${carrier.code} ${carrier.headquarters}`.toLowerCase().includes(query.toLowerCase()))
    && (mode === "All" || carrier.modes.includes(mode as ProcurementMode))
    && (!governmentOnly || carrier.government)
  );
  return <main className="page freight-page procurement-page">
    <Head eyebrow="FREIGHT PROCUREMENT · CARRIER MANAGEMENT" title="Carrier network"
      text="Search, qualify, and maintain the carrier relationships your team depends on."
      actions={<button className="button" onClick={() => notify("New carrier profile draft created")}><Plus /> Add carrier</button>} />
    <section className="procurement-kpis carrier-kpis">{[["Active carriers","127","18 preferred"],["Government ready","34","19 SDDC"],["Compliance complete","91%","11 need review"],["Missing POC","8","3 high-fit"],["Insurance < 60 days","6","Follow-up due"]].map(item => <div key={item[0]}><span>{item[0]}</span><b>{item[1]}</b><small>{item[2]}</small></div>)}</section>
    <div className="carrier-toolbar"><label><Search /><input aria-label="Search carriers" placeholder="Search carrier, code, location…" value={query} onChange={event => setQuery(event.target.value)} /></label><select aria-label="Filter carrier mode" value={mode} onChange={event => setMode(event.target.value)}><option>All</option>{(["Small Parcel","LTL","TL","Air Freight","Spot Bid"] as ProcurementMode[]).map(item => <option key={item}>{item}</option>)}</select><button className={governmentOnly ? "active" : ""} onClick={() => setGovernmentOnly(!governmentOnly)}><Flag /> Government ready</button><button><ShieldCheck /> Compliance: all</button></div>
    <section className="panel carrier-table-wrap"><table className="freight-table carrier-table"><thead><tr><th>Carrier</th><th>Classification</th><th>Modes</th><th>Coverage</th><th>Government</th><th>Compliance</th><th>Relationship</th><th>Performance</th><th /></tr></thead><tbody>{filtered.map(carrier => <tr key={carrier.id} onClick={() => setSelected(carrier)}><td><div className="carrier-name-cell"><span className="carrier-logo">{carrier.code}</span><span><b>{carrier.name}</b><small>{carrier.headquarters} · {carrier.contact}</small></span></div></td><td>{carrier.classification}</td><td><div className="mode-tags">{carrier.modes.map(item => <span key={item}>{item}</span>)}</div></td><td>{carrier.regions.join(", ")}</td><td><div className="government-icons">{carrier.government && <Flag />}{carrier.sddc && <span>SDDC</span>}{carrier.gfm && <span>GFM</span>}</div></td><td><span className={`compliance-label ${carrier.compliance === "Complete" ? "complete" : carrier.compliance === "Review due" ? "warning" : "bad"}`}>{carrier.compliance}</span></td><td>{carrier.relationship}</td><td><b>{carrier.performance}</b>/100</td><td><ChevronRight /></td></tr>)}</tbody></table></section>
    {selected && <CarrierDrawer carrier={selected} close={() => setSelected(null)} />}
  </main>;
}

function CarrierDrawer({ carrier, close }: { carrier: ProcurementCarrier; close: () => void }) {
  return <div className="drawer-backdrop" onMouseDown={close}><aside className="drawer carrier-drawer" onMouseDown={event => event.stopPropagation()}><header><div><span className="carrier-logo">{carrier.code}</span><span><b>{carrier.name}</b><small>{carrier.classification} · {carrier.relationship}</small></span></div><button onClick={close}><X /></button></header><div className="drawer-body"><section className="carrier-score-row"><div><small>PERFORMANCE</small><b>{carrier.performance}/100</b></div><div><small>PRIOR AWARDS</small><b>{carrier.priorAwards}</b></div><div><small>COMPLIANCE</small><b>{carrier.compliance}</b></div></section><section><h3><Route /> Operating profile</h3><dl className="carrier-profile"><div><dt>Headquarters</dt><dd>{carrier.headquarters}</dd></div><div><dt>Regions</dt><dd>{carrier.regions.join(", ")}</dd></div><div><dt>Modes</dt><dd>{carrier.modes.join(", ")}</dd></div><div><dt>Authority</dt><dd>{carrier.authority}</dd></div><div><dt>Insurance expiry</dt><dd>{carrier.insurance}</dd></div></dl></section><section><h3><Flag /> Government readiness</h3><div className="readiness-list"><span className={carrier.government ? "ready" : ""}><Check /> Government business</span><span className={carrier.sddc ? "ready" : ""}><Check /> SDDC registered</span><span className={carrier.gfm ? "ready" : ""}><Check /> GFM approved</span><span className={carrier.dod ? "ready" : ""}><Check /> DoD relevant</span></div></section><section><h3><UserRoundCheck /> Best known contact</h3><div className="contact-card"><b>{carrier.contact}</b><span>{carrier.email || "Email missing"}</span><span>{carrier.phone || "Phone missing"}</span></div></section></div><footer><button className="button ghost"><FileText /> View activity</button><button className="button"><Mail /> Start RFQ</button></footer></aside></div>;
}

function RFQCenter({ opportunities }: { opportunities: ProcurementOpportunity[] }) {
  const rows = [
    ["OPP-2417","Keystone Freight Partners","TL","Quoted","2h 07m","$2,840"],
    ["OPP-2417","Sentinel Government Logistics","TL","Quoted","2h 24m","$2,975"],
    ["OPP-2417","Blue Ridge Transport","TL","Quoted","3h 11m","$2,775"],
    ["OPP-2409","Keystone Freight Partners","LTL","RFQ sent","9h 06m","—"],
    ["OPP-2409","Blue Ridge Transport","LTL","RFQ sent","9h 06m","—"],
    ["OPP-2409","Titan National Parcel","LTL","RFQ sent","9h 06m","—"],
  ];
  return <main className="page freight-page procurement-page"><Head eyebrow="FREIGHT PROCUREMENT · RFQ CONTROL" title="RFQs and carrier responses" text="Follow every request from shortlist to quote without rebuilding the status tracker in email." actions={<a className="button" href="/app/freight-opportunities"><Plus /> New opportunity</a>} /><section className="tender-summary procurement-summary">{[["RFQs sent","14","5 today"],["Awaiting response","5","3 overdue"],["Quotes received","9","64% response"],["No bids","2","14% of responses"]].map(item => <div key={item[0]}><span>{item[0]}</span><b>{item[1]}</b><small>{item[2]}</small></div>)}</section><div className="freight-filterbar"><div><button className="active">Active</button><button>Awaiting</button><button>Quoted</button><button>No bid</button><button>All</button></div><button><Clock3 /> Response age</button><button><Filter /> Mode</button></div><section className="panel rfq-center"><table className="freight-table"><thead><tr><th>Opportunity</th><th>Carrier</th><th>Mode</th><th>Status</th><th>Response clock</th><th>Quoted rate</th><th>Next action</th></tr></thead><tbody>{rows.map(row => <tr key={`${row[0]}-${row[1]}`}><td><div><b>{row[0]}</b><small>{opportunities.find(item => item.id === row[0])?.name}</small></div></td><td><b>{row[1]}</b></td><td><span className={`mode-pill ${statusClass(row[2])}`}>{row[2]}</span></td><td><span className={`freight-status ${statusClass(row[3])}`}>{row[3]}</span></td><td className={row[3] === "RFQ sent" ? "bad-text" : ""}>{row[4]}</td><td><b>{row[5]}</b></td><td><button className="link-button">{row[3] === "Quoted" ? "Compare bid" : "Prepare follow-up"} <ArrowRight /></button></td></tr>)}</tbody></table></section></main>;
}

function AwardRegister({ opportunities }: { opportunities: ProcurementOpportunity[] }) {
  const awards = [
    ["AWD-883","OPP-2387","Titan National Parcel","Small Parcel","$486","Darius King","Jun 22"],
    ["AWD-881","OPP-2379","Keystone Freight Partners","TL","$2,645","Maya Chen","Jun 21"],
    ["AWD-876","OPP-2368","Liberty Air Cargo","Air Freight","$8,240","Eli Brooks","Jun 19"],
    ["AWD-871","OPP-2355","Blue Ridge Transport","LTL","$1,168","Nina Patel","Jun 18"],
  ];
  return <main className="page freight-page procurement-page"><Head eyebrow="FREIGHT PROCUREMENT · DECISION HISTORY" title="Awards and procurement record" text="A defensible record of who was considered, what was quoted, and why each carrier won." actions={<button className="button ghost"><Download /> Export register</button>} /><section className="procurement-kpis">{[["Awards this month","22","+4 vs May"],["Awarded spend","$86.4k","4 modes"],["Avg savings vs high bid","8.7%","$8.2k captured"],["Documented rationale","91%","2 need completion"],["Preferred-carrier awards","68%","+6 pts"]].map(item => <div key={item[0]}><span>{item[0]}</span><b>{item[1]}</b><small>{item[2]}</small></div>)}</section><section className="panel award-register"><table className="freight-table"><thead><tr><th>Award</th><th>Opportunity</th><th>Carrier</th><th>Mode</th><th>Rate</th><th>Awarded by</th><th>Date</th><th>Decision record</th></tr></thead><tbody>{awards.map(row => <tr key={row[0]}><td><b>{row[0]}</b></td><td><div><b>{row[1]}</b><small>{opportunities.find(item => item.id === row[1])?.name || "Completed freight opportunity"}</small></div></td><td><b>{row[2]}</b></td><td><span className={`mode-pill ${statusClass(row[3])}`}>{row[3]}</span></td><td><b>{row[4]}</b></td><td>{row[5]}</td><td>{row[6]}</td><td><button className="link-button"><FileCheck2 /> Complete</button></td></tr>)}</tbody></table></section></main>;
}
