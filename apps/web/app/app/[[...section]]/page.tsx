import { ControlTower } from "@/components/control-tower";
import { FreightRoleOverlay } from "@/components/freight-role-overlay";

export default async function AppPage({ params }: { params: Promise<{ section?: string[] }> }) {
  const { section } = await params;
  const activeSection = section?.[0] || "freight";

  return <>
    <FreightRoleOverlay section={activeSection} />
    <ControlTower section={activeSection} />
  </>;
}
