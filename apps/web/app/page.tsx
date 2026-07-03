import Link from "next/link";
import type { CSSProperties } from "react";
import {
  ArrowRight, BarChart3, Check, FileText, Layers3, ReceiptText, ShieldCheck,
  Shuffle, Sparkles, Truck, UploadCloud
} from "lucide-react";
import { CurrentDateLabel } from "@/components/current-date-label";
import { Logo } from "@/components/logo";

const walkthroughCards = [
  {
    icon: <BarChart3 />,
    title: "Analytics by load type",
    caption: "Mode mix, margin, service, and attention queues across LTL, TL, Spot Bid, and Air Freight.",
    className: "analytics"
  },
  {
    icon: <FileText />,
    title: "Quote Desk",
    caption: "Calculate auditable freight quotes, save history, and keep the pricing trace visible.",
    className: "quote"
  },
  {
    icon: <ReceiptText />,
    title: "Invoice Center",
    caption: "Track AR, aging, disputes, quote-to-bill variance, and PDF-style invoice previews.",
    className: "invoice"
  },
  {
    icon: <Shuffle />,
    title: "RFQs and role switching",
    caption: "Move from broker command center to shipper, carrier, or compliance views in one click.",
    className: "rfq"
  }
];

export default function LandingPage() {
  return (
    <main className="landing">
      <nav className="landing-nav">
        <Logo />
        <div className="nav-links"><a href="#product">Product</a><a href="#pricing">Pricing</a><a href="#security">Security</a></div>
        <div className="nav-actions"><Link href="/sign-in" className="text-btn">Sign in</Link><Link href="/app/freight" className="button small">Try Live Demo <ArrowRight size={15} /></Link></div>
      </nav>

      <section className="hero">
        <div className="eyebrow"><Sparkles size={14} /> Operations intelligence, without replacing your ERP</div>
        <h1>Know what will go wrong <em>before it does.</em></h1>
        <p>Upload your orders, inventory, purchase orders, and shipment exports. FlowSight tells you what is at risk, what it will cost, and who should act now.</p>
        <div className="hero-actions demo-hero-actions">
          <div className="demo-cta-wrap">
            <Link href="/app/freight" className="button demo-cta" aria-describedby="demo-access-card">Try Live Demo <ArrowRight size={17} /></Link>
            <div className="demo-access-card" id="demo-access-card" role="note">
              <b>Demo access</b>
              <span>Username: <code>flowsight</code></span>
              <span>Password: <code>&lt;private password from invite&gt;</code></span>
              <small>App login if prompted: maya@demo.flowsight.ai / FlowSightDemo!</small>
            </div>
          </div>
          <Link href="/onboarding" className="button ghost">Start a 30-day pilot</Link>
        </div>
        <div className="trust-row"><span><Check /> Go live in days</span><span><Check /> No rip-and-replace</span><span><Check /> Evidence-linked AI</span></div>
      </section>

      <section className="product-preview" id="product">
        <div className="preview-glow" />
        <div className="mini-sidebar"><Logo compact /><span /><span /><span /><span /></div>
        <div className="preview-main">
          <div className="preview-head"><div><small><CurrentDateLabel /></small><h3>Good morning, Maya.</h3></div><span className="status-dot">Data fresh 8 min ago</span></div>
          <div className="preview-kpis"><div><small>REVENUE AT RISK</small><b>$184.2k</b><em>+12.4%</em></div><div><small>LIKELY STOCKOUTS</small><b>14</b><em>7 urgent</em></div><div><small>SERVICE LEVEL</small><b>94.1%</b><em className="good">+1.8%</em></div></div>
          <div className="preview-grid">
            <div className="preview-card brief"><small>AI DAILY BRIEF</small><h4>Seven risks need attention today.</h4><p>HX-440 will stock out before its next receipt. Expediting 220 units protects an estimated $42.8k in revenue.</p><span>Review evidence →</span></div>
            <div className="preview-card chart"><small>13-WEEK DEMAND</small><div className="fake-chart"><i /><i /><i /><i /><i /><i /><i /><i /><i /></div></div>
          </div>
        </div>
      </section>

      <section className="demo-walkthrough" aria-label="FlowSight freight walkthrough">
        <div className="walkthrough-head">
          <span className="section-kicker">VISUAL WALKTHROUGH</span>
          <h2>Four fast looks at the freight demo.</h2>
          <p>Lightweight animated panels preview the paths prospects should try first: analytics, quotes, invoices, RFQs, and role switching.</p>
        </div>
        <div className="walkthrough-grid">
          {walkthroughCards.map((card, index) => (
            <article className={`walkthrough-card ${card.className}`} key={card.title} style={{"--delay": `${index * 0.35}s`} as CSSProperties}>
              <header><span>{card.icon}</span><b>{card.title}</b></header>
              <div className="walkthrough-shot" aria-hidden="true">
                <div className="shot-top"><i /><i /><i /></div>
                <div className="shot-body">
                  <span className="shot-rail"><Truck /><i /><i /><i /></span>
                  <div className="shot-main">
                    <strong />
                    <div className="shot-kpis"><i /><i /><i /></div>
                    <div className="shot-lines"><i /><i /><i /><i /></div>
                  </div>
                </div>
              </div>
              <p>{card.caption}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="value-strip">
        <div><UploadCloud /><h3>Start with exports</h3><p>Map messy CSV and Excel files once, then reuse the template.</p></div>
        <div><Layers3 /><h3>See the whole operation</h3><p>Inventory, POs, suppliers, service, and spend in one daily brief.</p></div>
        <div><BarChart3 /><h3>Act on what matters</h3><p>Every risk includes impact, evidence, owner, and recommended action.</p></div>
        <div id="security"><ShieldCheck /><h3>Built for trust</h3><p>Tenant isolation, role controls, audit trails, and grounded AI.</p></div>
      </section>

      <section className="pricing-section" id="pricing">
        <div><span className="section-kicker">A practical first step</span><h2>Prove the value in 30 days.</h2><p>One site, four feeds, a working exception inbox, and an executive ROI closeout. Your pilot fee is fully credited when you convert.</p></div>
        <div className="pilot-card"><span>PAID PILOT</span><strong>$2,500</strong><small>one time - credited on conversion</small><Link href="/onboarding" className="button">Design your pilot <ArrowRight size={16} /></Link></div>
      </section>
      <footer><Logo /><span>© 2026 FlowSight AI - Intelligence for the work that moves.</span></footer>
      <style>{`
        .demo-hero-actions{align-items:flex-start}.demo-cta-wrap{position:relative;display:flex;flex-direction:column;align-items:center;gap:10px}.demo-cta{font-size:16px!important;padding:15px 24px!important;box-shadow:0 14px 34px rgba(26,126,115,.24),0 0 0 4px rgba(36,163,147,.11);transform:translateY(-1px)}.demo-cta:hover{transform:translateY(-3px);box-shadow:0 18px 42px rgba(26,126,115,.28),0 0 0 5px rgba(36,163,147,.13)}.demo-access-card{width:min(410px,88vw);background:#fff;border:1px solid #cfe4e0;border-radius:12px;box-shadow:0 14px 36px rgba(16,45,43,.12);padding:12px 14px;display:grid;gap:5px;text-align:left;color:var(--ink);font-size:11px}.demo-access-card b{font-size:10px;letter-spacing:.08em;color:var(--teal);text-transform:uppercase}.demo-access-card code{background:#eef7f5;border:1px solid #d8e9e6;border-radius:5px;padding:2px 5px;color:#0f3b37}.demo-access-card small{font-size:10px;color:#607370;line-height:1.45}.demo-walkthrough{max-width:1120px;margin:0 auto 95px;padding:0 24px}.walkthrough-head{text-align:center;max-width:720px;margin:0 auto 24px}.walkthrough-head h2{font-size:32px;letter-spacing:-.04em;margin:8px 0}.walkthrough-head p{color:#62736f;line-height:1.65}.walkthrough-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.walkthrough-card{background:#fff;border:1px solid #d9e4e2;border-radius:16px;padding:15px;box-shadow:0 14px 34px rgba(24,63,58,.08);overflow:hidden}.walkthrough-card header{display:flex;align-items:center;gap:9px;margin-bottom:12px}.walkthrough-card header span{width:32px;height:32px;border-radius:9px;background:var(--teal-soft);color:var(--teal);display:grid;place-items:center}.walkthrough-card header svg{width:17px}.walkthrough-card header b{font-size:13px}.walkthrough-card p{font-size:11px;color:#657773;line-height:1.55;margin:12px 0 0}.walkthrough-shot{height:168px;border:1px solid #e0e9e7;border-radius:13px;background:linear-gradient(180deg,#f7fbfa,#fff);overflow:hidden}.shot-top{height:26px;border-bottom:1px solid #e4ecea;display:flex;align-items:center;gap:5px;padding:0 9px}.shot-top i{width:6px;height:6px;border-radius:50%;background:#a8bbb7}.shot-body{height:142px;display:grid;grid-template-columns:35px 1fr}.shot-rail{background:#102e2d;color:#73cabe;display:flex;flex-direction:column;align-items:center;gap:13px;padding:10px 0}.shot-rail svg{width:15px}.shot-rail i{width:16px;height:16px;border-radius:5px;background:#214642}.shot-main{padding:12px}.shot-main strong{display:block;width:52%;height:12px;border-radius:5px;background:#153331;margin-bottom:12px}.shot-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-bottom:11px}.shot-kpis i{height:38px;border-radius:8px;background:#eaf4f2;position:relative;overflow:hidden}.shot-kpis i:after{content:"";position:absolute;left:8px;right:18px;bottom:9px;height:8px;border-radius:8px;background:#208f80;animation:walkPulse 2.8s ease-in-out infinite;animation-delay:var(--delay)}.shot-lines{display:grid;gap:6px}.shot-lines i{height:9px;border-radius:5px;background:#dfe9e6;position:relative;overflow:hidden}.shot-lines i:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(32,143,128,.45),transparent);transform:translateX(-100%);animation:walkSweep 3.6s ease-in-out infinite;animation-delay:var(--delay)}.walkthrough-card.quote .shot-main strong,.walkthrough-card.quote .shot-kpis i:after{background:#b57417}.walkthrough-card.invoice .shot-main strong,.walkthrough-card.invoice .shot-kpis i:after{background:#536c91}.walkthrough-card.rfq .shot-main strong,.walkthrough-card.rfq .shot-kpis i:after{background:#7164aa}@keyframes walkPulse{0%,100%{width:38%;opacity:.75}50%{width:72%;opacity:1}}@keyframes walkSweep{0%{transform:translateX(-100%)}48%,100%{transform:translateX(100%)}}@media(max-width:900px){.walkthrough-grid{grid-template-columns:1fr 1fr}.demo-walkthrough{margin-bottom:70px}}@media(max-width:640px){.demo-access-card{width:100%}.walkthrough-grid{grid-template-columns:1fr}.walkthrough-card{padding:14px}.walkthrough-shot{height:154px}.demo-walkthrough{padding:0 15px}.walkthrough-head h2{font-size:25px}.demo-hero-actions{width:100%}.demo-cta-wrap{width:100%}.demo-cta{width:100%;justify-content:center}}
      `}</style>
    </main>
  );
}
