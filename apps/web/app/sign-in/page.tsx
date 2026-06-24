"use client";
import Link from "next/link";
import { useState } from "react";
import { ArrowRight, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { Logo } from "@/components/logo";

export default function SignIn() {
  const [show, setShow] = useState(false);
  return (
    <main className="auth-page">
      <section className="auth-art">
        <Logo />
        <div className="auth-quote"><span>“</span><h2>We went from chasing spreadsheets to knowing our top five risks before the morning meeting.</h2><p>Operations Director · Industrial Distribution</p></div>
        <div className="auth-proof"><ShieldCheck /><span><b>Tenant-safe by design</b><small>Encrypted, auditable, role-aware access</small></span></div>
      </section>
      <section className="auth-form-wrap">
        <form className="auth-form" action="/app/overview">
          <span className="eyebrow">WELCOME BACK</span><h1>Sign in to FlowSight</h1><p>Use the demo credentials to explore the control tower.</p>
          <label>Work email<input type="email" defaultValue="maya@demo.flowsight.ai" /></label>
          <label>Password<div className="password"><input type={show ? "text" : "password"} defaultValue="FlowSightDemo!" /><button type="button" onClick={() => setShow(!show)}>{show ? <EyeOff /> : <Eye />}</button></div></label>
          <div className="form-row"><label className="check"><input type="checkbox" defaultChecked /> Remember me</label><a href="#">Forgot password?</a></div>
          <button className="button auth-submit">Sign in <ArrowRight size={16} /></button>
          <div className="divider"><span>or</span></div>
          <Link className="demo-login" href="/app/overview"><i /> Enter Industrial Distributor Demo <ArrowRight size={16} /></Link>
          <small className="legal">By continuing, you agree to the Terms and Privacy Policy.</small>
        </form>
      </section>
    </main>
  );
}
