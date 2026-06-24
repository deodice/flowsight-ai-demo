"use client";
import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Building2, Check, Factory, UploadCloud } from "lucide-react";
import { Logo } from "@/components/logo";

const steps = ["Company", "Data", "Thresholds", "Team", "Ready"];
export default function Onboarding() {
  const [step, setStep] = useState(0);
  const [business, setBusiness] = useState("distributor");
  return (
    <main className="onboarding">
      <header><Logo /><span>Setup takes about 8 minutes</span></header>
      <div className="stepper">{steps.map((s, i) => <div key={s} className={i <= step ? "active" : ""}><i>{i < step ? <Check /> : i + 1}</i><span>{s}</span></div>)}</div>
      <section className="onboard-card">
        {step === 0 && <><span className="section-kicker">STEP 1 OF 5</span><h1>Tell us about your operation</h1><p>We’ll tailor terminology, thresholds, and starter templates.</p><label>Company name<input defaultValue="Acme Industrial Supply" /></label><div className="choice-grid"><button className={business === "distributor" ? "selected" : ""} onClick={() => setBusiness("distributor")}><Building2 /><b>Industrial distributor</b><small>Inventory, purchasing, fulfillment</small></button><button className={business === "manufacturer" ? "selected" : ""} onClick={() => setBusiness("manufacturer")}><Factory /><b>Light manufacturer</b><small>Components, suppliers, production</small></button></div><div className="two-fields"><label>Primary site<input defaultValue="Harrisburg, PA" /></label><label>Team size<select><option>50–150 employees</option><option>151–500 employees</option></select></label></div></>}
        {step === 1 && <><span className="section-kicker">STEP 2 OF 5</span><h1>Bring your first data</h1><p>Start with sample data or upload one of your own exports.</p><div className="upload-zone"><UploadCloud /><b>Drop CSV or XLSX files here</b><span>Inventory, open POs, orders, shipments, receipts, SKU or supplier master</span><button className="button ghost">Choose files</button></div><button className="sample-option">Use realistic demo data instead <ArrowRight /></button></>}
        {step === 2 && <><span className="section-kicker">STEP 3 OF 5</span><h1>Confirm your action thresholds</h1><p>These defaults can be tuned at any time.</p><div className="thresholds"><label>Stockout horizon <span><input type="number" defaultValue="14" /> days</span></label><label>Backorder aging <span><input type="number" defaultValue="7" /> days</span></label><label>Price variance <span><input type="number" defaultValue="8" /> %</span></label><label>Minimum supplier OTIF <span><input type="number" defaultValue="90" /> %</span></label></div></>}
        {step === 3 && <><span className="section-kicker">STEP 4 OF 5</span><h1>Invite your action team</h1><p>Give risks an owner from the first day.</p><div className="invite-row"><input placeholder="buyer@company.com" /><select><option>Operations manager</option><option>Analyst</option><option>Executive viewer</option></select><button>Add</button></div><div className="invite-person"><span>MC</span><div><b>Maya Chen</b><small>maya@company.com</small></div><em>Tenant admin</em></div></>}
        {step === 4 && <div className="ready-state"><div className="success-ring"><Check /></div><span className="section-kicker">YOUR CONTROL TOWER IS READY</span><h1>We found 18 actionable risks.</h1><p>Your demo workspace is loaded with one year of operating history, evidence-linked exceptions, forecasts, and scorecards.</p><div className="ready-stats"><div><b>14</b><span>stockout risks</span></div><div><b>23</b><span>late POs</span></div><div><b>$184k</b><span>revenue at risk</span></div></div><Link href="/app/overview" className="button">Open my command center <ArrowRight /></Link></div>}
        {step < 4 && <footer><button className="text-btn" disabled={step === 0} onClick={() => setStep(step - 1)}><ArrowLeft /> Back</button><button className="button" onClick={() => setStep(step + 1)}>Continue <ArrowRight /></button></footer>}
      </section>
    </main>
  );
}
