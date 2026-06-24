export type ExceptionItem = {
  id: string;
  severity: "Critical" | "High" | "Medium";
  title: string;
  detail: string;
  impact: number;
  confidence: number;
  owner: string;
  due: string;
  type: string;
  status: "Open" | "In progress" | "Resolved";
  evidence: string[];
  action: string;
};

export const kpis = [
  { label: "Revenue at risk", value: "$184.2k", delta: "+12.4%", tone: "danger", note: "next 30 days" },
  { label: "Likely stockouts", value: "14", delta: "+3", tone: "danger", note: "7 need action today" },
  { label: "Late POs", value: "23", delta: "-8.0%", tone: "warning", note: "$96k open value" },
  { label: "Service level", value: "94.1%", delta: "+1.8%", tone: "good", note: "30-day rolling" }
];

export const exceptions: ExceptionItem[] = [
  {
    id: "EX-1048", severity: "Critical", title: "Stockout likely: HX-440 Hydraulic Coupler",
    detail: "3.2 days of supply remain; next confirmed receipt is 9 days away.",
    impact: 42800, confidence: 94, owner: "Maya Chen", due: "Today", type: "Inventory",
    status: "Open", evidence: ["On hand: 86 units", "Avg demand: 27/day", "PO 8841 expected Jun 30"],
    action: "Expedite 220 units on PO 8841 and rebalance 60 units from Harrisburg."
  },
  {
    id: "EX-1044", severity: "Critical", title: "PO 8836 likely 11 days late",
    detail: "Northeast Castings is trending beyond its historical lead-time band.",
    impact: 31500, confidence: 89, owner: "Unassigned", due: "Today", type: "Purchase order",
    status: "Open", evidence: ["Supplier median: 18 days", "Current elapsed: 27 days", "No ASN received"],
    action: "Request supplier commit date and qualify the alternate source."
  },
  {
    id: "EX-1039", severity: "High", title: "Backorder cluster aging above SLA",
    detail: "12 customer lines have aged beyond 7 days, concentrated in two SKUs.",
    impact: 22100, confidence: 97, owner: "Luis Ortega", due: "Tomorrow", type: "Service",
    status: "In progress", evidence: ["12 lines affected", "Oldest: 16 days", "4 key accounts impacted"],
    action: "Prioritize available stock by customer tier and notify account owners."
  },
  {
    id: "EX-1032", severity: "High", title: "Purchase price variance on BRG-220",
    detail: "Unit cost increased 14.8%, outside the tenant threshold of 8%.",
    impact: 17800, confidence: 99, owner: "Jenna Wright", due: "Jun 24", type: "Spend",
    status: "Open", evidence: ["Previous: $18.40", "Current: $21.12", "Annualized: +$17.8k"],
    action: "Validate the price break and compare the secondary supplier quote."
  },
  {
    id: "EX-1026", severity: "Medium", title: "Carrier OTIF deterioration: RoadStar",
    detail: "OTIF fell below 90% for the third consecutive week.",
    impact: 9400, confidence: 92, owner: "Maya Chen", due: "Jun 25", type: "Carrier",
    status: "Open", evidence: ["Current OTIF: 86.4%", "Baseline: 94.8%", "31 shipments"],
    action: "Open a carrier review and shift priority lanes to Keystone Freight."
  }
];

export const demandData = [
  { week: "Apr 6", actual: 720, forecast: 690, low: 620, high: 760 },
  { week: "Apr 13", actual: 680, forecast: 710, low: 640, high: 780 },
  { week: "Apr 20", actual: 760, forecast: 735, low: 660, high: 810 },
  { week: "Apr 27", actual: 810, forecast: 770, low: 690, high: 850 },
  { week: "May 4", actual: 790, forecast: 800, low: 720, high: 880 },
  { week: "May 11", actual: 870, forecast: 825, low: 740, high: 910 },
  { week: "May 18", actual: 850, forecast: 850, low: 765, high: 935 },
  { week: "May 25", actual: 930, forecast: 880, low: 790, high: 970 },
  { week: "Jun 1", actual: 910, forecast: 905, low: 815, high: 995 },
  { week: "Jun 8", actual: 980, forecast: 940, low: 845, high: 1035 },
  { week: "Jun 15", actual: 1010, forecast: 970, low: 875, high: 1070 },
  { week: "Jun 22", actual: null, forecast: 995, low: 890, high: 1100 },
  { week: "Jun 29", actual: null, forecast: 1020, low: 905, high: 1135 }
];

export const suppliers = [
  { name: "Keystone Components", otif: 97.2, lead: 12.4, late: 2.8, spend: "$418k", trend: "up" },
  { name: "Allegheny Industrial", otif: 94.1, lead: 16.8, late: 5.9, spend: "$364k", trend: "up" },
  { name: "Northeast Castings", otif: 78.6, lead: 27.2, late: 21.4, spend: "$291k", trend: "down" },
  { name: "MidAtlantic Bearings", otif: 91.5, lead: 14.1, late: 8.5, spend: "$187k", trend: "flat" }
];

export const navSections = [
  ["overview", "Command center"], ["exceptions", "Exceptions"], ["inventory", "Inventory risk"],
  ["purchase-orders", "Purchase orders"], ["forecasting", "Forecasting"], ["scorecards", "Scorecards"],
  ["tasks", "Action tracker"], ["imports", "Data imports"], ["quality", "Data quality"],
  ["ai", "AI briefings"], ["reports", "Reports"], ["feedback", "Feedback"],
  ["admin", "Admin & settings"], ["release-notes", "Release notes"]
] as const;
