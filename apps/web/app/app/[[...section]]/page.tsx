import { ControlTower } from "@/components/control-tower";

export default async function AppPage({ params }: { params: Promise<{ section?: string[] }> }) {
  const { section } = await params;
  return <ControlTower section={section?.[0] || "overview"} />;
}
