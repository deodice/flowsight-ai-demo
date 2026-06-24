export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="logo">
      <span className="logo-mark"><i /><i /><i /></span>
      {!compact && <span>FlowSight <b>AI</b></span>}
    </div>
  );
}
