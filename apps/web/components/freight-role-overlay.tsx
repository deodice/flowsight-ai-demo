"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Check } from "lucide-react";

const roles = [
  { label: "Broker", href: "/app/freight", short: "BR" },
  { label: "Shipper", href: "/app/freight-client", short: "SH" },
  { label: "Carrier", href: "/app/freight-operations", short: "CA" },
  { label: "Government/Compliance", href: "/app/freight-carriers", short: "GC" }
];

function roleForSection(section: string) {
  if (section === "freight-client") return "Shipper";
  if (["freight-operations", "freight-tenders", "freight-quotes", "freight-invoices"].includes(section)) return "Carrier";
  if (["freight-carriers", "freight-admin"].includes(section)) return "Government/Compliance";
  return "Broker";
}

export function FreightRoleOverlay({ section }: { section: string }) {
  const [active, setActive] = useState(roleForSection(section));
  const [toast, setToast] = useState("");

  useEffect(() => {
    setActive(roleForSection(section));
  }, [section]);

  if (!section.startsWith("freight")) return null;

  const switchRole = (label: string) => {
    setActive(label);
    setToast(`Switched to ${label} view`);
    window.setTimeout(() => setToast(""), 2200);
  };

  return <>
    <section className="prospect-role-switch" aria-label="Logged in role switcher">
      <div><span><Check /> Logged in as Maya</span><b>Switch role:</b></div>
      <nav>{roles.map(role => <Link key={role.label} href={role.href} className={active === role.label ? "active" : ""} onClick={() => switchRole(role.label)}>{role.label}</Link>)}</nav>
    </section>
    <aside className="prospect-role-rail" aria-label="Quick role shortcuts">
      <span>Roles</span>
      {roles.map(role => <Link key={role.short} href={role.href} title={role.label} className={active === role.label ? "active" : ""} onClick={() => switchRole(role.label)}>{role.short}</Link>)}
    </aside>
    {toast && <div className="prospect-role-toast"><Check /> {toast}</div>}
    <style>{`
      .prospect-role-switch{position:fixed;left:126px;right:24px;top:78px;z-index:80;background:linear-gradient(115deg,#102e2d,#1b514a);color:#fff;border-radius:13px;padding:13px 16px;display:flex;align-items:center;justify-content:space-between;gap:16px;box-shadow:0 12px 28px rgba(10,45,41,.18)}
      .prospect-role-switch>div{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.prospect-role-switch span{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#bce0db}.prospect-role-switch span svg{width:14px}.prospect-role-switch b{font-size:12px}.prospect-role-switch nav{display:flex;gap:7px;flex-wrap:wrap}.prospect-role-switch a{border:1px solid #3d6963;background:#1e5d55;color:#e8fffb;border-radius:999px;padding:8px 11px;font-size:10px;font-weight:800;text-decoration:none}.prospect-role-switch a:hover,.prospect-role-switch a.active{background:#fff;color:#12312f;border-color:#fff}
      .prospect-role-rail{position:fixed;left:12px;bottom:110px;z-index:82;width:78px;background:#102e2d;border:1px solid #214642;border-radius:13px;padding:8px 7px;box-shadow:0 14px 34px rgba(10,45,41,.2);display:grid;grid-template-columns:1fr 1fr;gap:4px}.prospect-role-rail>span{grid-column:1/3;text-align:center;font-size:7px;letter-spacing:.11em;text-transform:uppercase;color:#88aaa4;font-weight:900;margin-bottom:3px}.prospect-role-rail a{height:25px;border-radius:7px;background:#173432;color:#a9bfbb;display:grid;place-items:center;font-size:7px;font-weight:900;text-decoration:none}.prospect-role-rail a.active,.prospect-role-rail a:hover{background:#dff2ed;color:#113431}
      .prospect-role-toast{position:fixed;right:22px;bottom:22px;z-index:120;background:#102e2d;color:#fff;border-radius:999px;padding:11px 14px;display:flex;gap:8px;align-items:center;box-shadow:0 18px 42px rgba(0,0,0,.2);font-size:12px}.prospect-role-toast svg{width:15px;color:#79d5c9}
      @media(max-width:900px){.prospect-role-switch{left:100px;right:12px;top:70px;align-items:flex-start;flex-direction:column}.prospect-role-switch nav{width:100%}.prospect-role-switch a{flex:1;text-align:center}.prospect-role-rail{display:none}}
      @media(max-width:640px){.prospect-role-switch{left:90px;right:10px;top:68px;padding:12px}.prospect-role-switch nav{display:grid;grid-template-columns:1fr 1fr}.prospect-role-switch a{padding:9px 7px}}
    `}</style>
  </>;
}
