import Link from "next/link";
import { ArrowRight, BarChart3, Check, Layers3, ShieldCheck, Sparkles, UploadCloud } from "lucide-react";
import { Logo } from "@/components/logo";

export default function LandingPage() {
  return (
    <main className="landing">
      <nav className="landing-nav">
        <Logo />
        <div className="nav-links"><a href="#product">Product</a><a href="#pricing">Pricing</a><a href="#security">Security</a></div>
        <div className="nav-actions"><Link href="/sign-in" className="text-btn">Sign in</Link><Link href="/onboarding" className="button small">Start a pilot <ArrowRight size={15} /></Link></div>
      </nav>

      <section className="hero">
        <div className="eyebrow"><Sparkles size={14} /> Operations intelligence, without replacing your ERP</div>
        <h1>Know what will go wrong <em>before it does.</em></h1>
        <p>Upload your orders, inventory, purchase orders, and shipment exports. FlowSight tells you what is at risk, what it will cost, and who should act now.</p>
        <div className="hero-actions"><Link href="/app/overview" className="button">Explore the live demo <ArrowRight size={17} /></Link><Link href="/onboarding" className="button ghost">Start a 30-day pilot</Link></div>
        <div className="trust-row"><span><Check /> Go live in days</span><span><Check /> No rip-and-replace</span><span><Check /> Evidence-linked AI</span></div>
      </section>

      <section className="product-preview" id="product">
        <div className="preview-glow" />
        <div className="mini-sidebar"><Logo compact /><span /><span /><span /><span /></div>
        <div className="preview-main">
          <div className="preview-head"><div><small>MONDAY, JUNE 22</small><h3>Good morning, Maya.</h3></div><span className="status-dot">Data fresh 8 min ago</span></div>
          <div className="preview-kpis"><div><small>REVENUE AT RISK</small><b>$184.2k</b><em>+12.4%</em></div><div><small>LIKELY STOCKOUTS</small><b>14</b><em>7 urgent</em></div><div><small>SERVICE LEVEL</small><b>94.1%</b><em className="good">+1.8%</em></div></div>
          <div className="preview-grid">
            <div className="preview-card brief"><small>AI DAILY BRIEF</small><h4>Seven risks need attention today.</h4><p>HX-440 will stock out before its next receipt. Expediting 220 units protects an estimated $42.8k in revenue.</p><span>Review evidence →</span></div>
            <div className="preview-card chart"><small>13-WEEK DEMAND</small><div className="fake-chart"><i /><i /><i /><i /><i /><i /><i /><i /><i /></div></div>
          </div>
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
        <div className="pilot-card"><span>PAID PILOT</span><strong>$2,500</strong><small>one time · credited on conversion</small><Link href="/onboarding" className="button">Design your pilot <ArrowRight size={16} /></Link></div>
      </section>
      <footer><Logo /><span>© 2026 FlowSight AI · Intelligence for the work that moves.</span></footer>
    </main>
  );
}
