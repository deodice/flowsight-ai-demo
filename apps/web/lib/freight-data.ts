export type FreightMode = "LTL" | "TL" | "Spot Bid" | "Air Freight";

export type FreightTender = {
  id: string;
  customer: string;
  lane: string;
  mode: FreightMode;
  status: string;
  pickup: string;
  equipment: string;
  quoted: number;
  cost: number;
  margin: number;
  expires: string;
  owner: string;
};

export type FreightInvoice = {
  id: string;
  customer: string;
  shipment: string;
  mode: FreightMode;
  issued: string;
  due: string;
  quoted: number;
  billed: number;
  balance: number;
  status: string;
};

export const freightTenders: FreightTender[] = [
  { id: "TND-2084", customer: "Apex Machine Works", lane: "Harrisburg, PA → Nashville, TN", mode: "TL", status: "Awarded", pickup: "Jun 24", equipment: "53' Dry Van", quoted: 2840, cost: 2245, margin: 21.0, expires: "Jun 23 · 3:00 PM", owner: "Maya Chen" },
  { id: "TND-2081", customer: "Vantage Medical", lane: "Philadelphia, PA → Frankfurt, DE", mode: "Air Freight", status: "Countered", pickup: "Jun 25", equipment: "Priority Air", quoted: 6425, cost: 5180, margin: 19.4, expires: "Today · 4:30 PM", owner: "Eli Brooks" },
  { id: "TND-2079", customer: "Susquehanna Controls", lane: "York, PA → Charlotte, NC", mode: "LTL", status: "Issued", pickup: "Jun 26", equipment: "6 pallets · Class 70", quoted: 1185, cost: 942, margin: 20.5, expires: "Tomorrow · 12:00 PM", owner: "Nina Patel" },
  { id: "TND-2076", customer: "Keystone Components", lane: "Pittsburgh, PA → Dallas, TX", mode: "Spot Bid", status: "Accepted", pickup: "Jun 23", equipment: "48' Flatbed", quoted: 3975, cost: 3385, margin: 14.8, expires: "Accepted", owner: "Maya Chen" },
  { id: "TND-2068", customer: "Allegheny Industrial", lane: "Allentown, PA → Chicago, IL", mode: "TL", status: "In Transit", pickup: "Jun 21", equipment: "53' Dry Van", quoted: 2360, cost: 1840, margin: 22.0, expires: "Awarded Jun 19", owner: "Darius King" },
  { id: "TND-2059", customer: "Federal Supply Group", lane: "Baltimore, MD → Sacramento, CA", mode: "Air Freight", status: "Delivered", pickup: "Jun 18", equipment: "Consolidated Air", quoted: 8840, cost: 7310, margin: 17.3, expires: "Delivered Jun 21", owner: "Eli Brooks" }
];

export const freightInvoices: FreightInvoice[] = [
  { id: "INV-10482", customer: "Apex Machine Works", shipment: "SHP-8821", mode: "TL", issued: "Jun 18", due: "Jul 18", quoted: 2840, billed: 2925, balance: 2925, status: "Sent" },
  { id: "INV-10476", customer: "Vantage Medical", shipment: "SHP-8814", mode: "Air Freight", issued: "Jun 12", due: "Jul 12", quoted: 6425, billed: 6810, balance: 6810, status: "Issued" },
  { id: "INV-10461", customer: "Susquehanna Controls", shipment: "SHP-8793", mode: "LTL", issued: "May 28", due: "Jun 27", quoted: 1120, billed: 1205, balance: 1205, status: "Past Due" },
  { id: "INV-10438", customer: "Keystone Components", shipment: "SHP-8749", mode: "Spot Bid", issued: "May 11", due: "Jun 10", quoted: 3975, billed: 4225, balance: 780, status: "Partially Paid" },
  { id: "INV-10417", customer: "Allegheny Industrial", shipment: "SHP-8702", mode: "TL", issued: "Apr 29", due: "May 29", quoted: 2360, billed: 2360, balance: 0, status: "Paid" },
  { id: "INV-10398", customer: "Federal Supply Group", shipment: "SHP-8668", mode: "Air Freight", issued: "Apr 16", due: "May 16", quoted: 8840, billed: 9120, balance: 9120, status: "Disputed" }
];

export const freightTrend = [
  { month: "Jan", revenue: 148, cost: 119, margin: 19.6, loads: 74 },
  { month: "Feb", revenue: 155, cost: 122, margin: 21.3, loads: 79 },
  { month: "Mar", revenue: 171, cost: 137, margin: 19.9, loads: 86 },
  { month: "Apr", revenue: 163, cost: 128, margin: 21.5, loads: 82 },
  { month: "May", revenue: 189, cost: 148, margin: 21.7, loads: 94 },
  { month: "Jun", revenue: 204, cost: 158, margin: 22.5, loads: 101 }
];

export const modePerformance = [
  { mode: "LTL" as FreightMode, loads: 146, revenue: "$186.4k", margin: "22.8%", acceptance: "68%", otif: "94.2%" },
  { mode: "TL" as FreightMode, loads: 119, revenue: "$321.8k", margin: "20.6%", acceptance: "73%", otif: "96.1%" },
  { mode: "Spot Bid" as FreightMode, loads: 74, revenue: "$248.1k", margin: "15.4%", acceptance: "41%", otif: "91.7%" },
  { mode: "Air Freight" as FreightMode, loads: 38, revenue: "$227.9k", margin: "18.9%", acceptance: "62%", otif: "93.4%" }
];

export const quoteComparisons = [
  { carrier: "Keystone Freight Partners", service: "2-day direct", total: 2840, pickup: "Jun 24 · 10 AM", delivery: "Jun 26 · 5 PM", score: 96, note: "Best overall value", recommended: true },
  { carrier: "Blue Ridge Transport", service: "2-day direct", total: 2775, pickup: "Jun 24 · 1 PM", delivery: "Jun 26 · 7 PM", score: 89, note: "Lowest price; tighter pickup window", recommended: false },
  { carrier: "RoadStar Logistics", service: "3-day standard", total: 2610, pickup: "Jun 25 · 8 AM", delivery: "Jun 28 · 12 PM", score: 82, note: "One extra transit day", recommended: false }
];

export const invoiceTrend = [
  { month: "Jan", issued: 142, collected: 134 },
  { month: "Feb", issued: 151, collected: 145 },
  { month: "Mar", issued: 166, collected: 153 },
  { month: "Apr", issued: 159, collected: 155 },
  { month: "May", issued: 184, collected: 169 },
  { month: "Jun", issued: 198, collected: 162 }
];

export const procurementNavSections = [
  ["freight", "Procurement command"],
  ["freight-opportunities", "Opportunities"],
  ["freight-carriers", "Carrier network"],
  ["freight-rfqs", "RFQs & bids"],
  ["freight-awards", "Awards"]
] as const;

export const freightOperationsNavSections = [
  ["freight-operations", "Freight operations"],
  ["freight-tenders", "Tender board"],
  ["freight-quotes", "Quote desk"],
  ["freight-invoices", "Invoice center"],
  ["freight-client", "Shipper portal"],
  ["freight-admin", "Freight configuration"],
  ["freight-tour", "Product tour"]
] as const;
