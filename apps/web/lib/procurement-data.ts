export type ProcurementMode = "Small Parcel" | "LTL" | "TL" | "Air Freight" | "Spot Bid" | "Other";

export type ProcurementCarrier = {
  id: string;
  code: string;
  name: string;
  tier: string;
  classification: "Carrier" | "Broker" | "Owner-operator";
  modes: ProcurementMode[];
  headquarters: string;
  regions: string[];
  government: boolean;
  sddc: boolean;
  gfm: boolean;
  dod: boolean;
  contact: string;
  email: string;
  phone: string;
  authority: "Active" | "Pending" | "Inactive";
  insurance: string;
  hazmat: boolean;
  refrigerated: boolean;
  relationship: "Unknown" | "Prospect" | "Active" | "Preferred" | "Do not use";
  compliance: "Complete" | "Review due" | "Incomplete" | "Expired";
  performance: number;
  priorAwards: number;
};

export type ProcurementOpportunity = {
  id: string;
  name: string;
  program: string;
  contract: string;
  origin: string;
  destination: string;
  pickup: string;
  delivery: string;
  deadline: string;
  mode: ProcurementMode;
  weight: number;
  dimensions: string;
  commodity: string;
  hazmat: boolean;
  refrigerated: boolean;
  government: boolean;
  sddc: boolean;
  gfm: boolean;
  complianceTags: string[];
  documents: string[];
  priority: "Normal" | "Urgent" | "Critical";
  status: "Draft" | "Sourcing" | "RFQ open" | "Evaluating" | "Awarded";
  owner: string;
  matched: number;
  shortlisted: number;
  rfqs: number;
  quotes: number;
  awardedCarrier?: string;
  rationale?: string;
};

export type CandidateState = {
  carrierId: string;
  score: number;
  eligible: boolean;
  shortlisted: boolean;
  status: "Not contacted" | "Shortlisted" | "RFQ ready" | "RFQ sent" | "No bid" | "Quoted" | "Awarded" | "Rejected";
  breakdown: { label: string; points: number; reason: string }[];
  rate?: number;
  transitDays?: number;
  fuel?: number;
  accessorials?: string;
  notes?: string;
};

export const procurementCarriers: ProcurementCarrier[] = [
  {
    id: "car-kfp", code: "KFP", name: "Keystone Freight Partners", tier: "Strategic",
    classification: "Carrier", modes: ["LTL", "TL", "Spot Bid"], headquarters: "Harrisburg, PA",
    regions: ["Northeast", "Southeast", "Midwest"], government: true, sddc: true, gfm: true,
    dod: true, contact: "Jordan Ellis", email: "jordan.ellis@keystone.demo", phone: "717-555-0142",
    authority: "Active", insurance: "Jan 23, 2027", hazmat: true, refrigerated: false,
    relationship: "Preferred", compliance: "Complete", performance: 96, priorAwards: 8
  },
  {
    id: "car-sgl", code: "SGL", name: "Sentinel Government Logistics", tier: "Strategic",
    classification: "Broker", modes: ["Small Parcel", "LTL", "TL", "Air Freight", "Spot Bid"],
    headquarters: "Alexandria, VA", regions: ["Nationwide"], government: true, sddc: true, gfm: true,
    dod: true, contact: "Morgan Hayes", email: "morgan.hayes@sentinel.demo", phone: "703-555-0181",
    authority: "Active", insurance: "Apr 6, 2027", hazmat: true, refrigerated: true,
    relationship: "Active", compliance: "Complete", performance: 94, priorAwards: 6
  },
  {
    id: "car-brx", code: "BRX", name: "Blue Ridge Transport", tier: "Preferred",
    classification: "Carrier", modes: ["LTL", "TL", "Spot Bid"], headquarters: "Roanoke, VA",
    regions: ["Northeast", "Southeast"], government: false, sddc: false, gfm: false,
    dod: false, contact: "Taylor Morgan", email: "taylor.morgan@blueridge.demo", phone: "540-555-0127",
    authority: "Active", insurance: "Oct 22, 2026", hazmat: true, refrigerated: true,
    relationship: "Active", compliance: "Complete", performance: 89, priorAwards: 4
  },
  {
    id: "car-lac", code: "LAC", name: "Liberty Air Cargo", tier: "Preferred",
    classification: "Carrier", modes: ["Air Freight"], headquarters: "Philadelphia, PA",
    regions: ["Northeast", "Nationwide"], government: true, sddc: false, gfm: true,
    dod: true, contact: "Avery Brooks", email: "avery.brooks@libertyair.demo", phone: "215-555-0168",
    authority: "Active", insurance: "Dec 18, 2026", hazmat: true, refrigerated: false,
    relationship: "Active", compliance: "Complete", performance: 92, priorAwards: 5
  },
  {
    id: "car-cfl", code: "CFL", name: "Confluence Freight Brokerage", tier: "Standard",
    classification: "Broker", modes: ["LTL", "TL", "Spot Bid"], headquarters: "Pittsburgh, PA",
    regions: ["Northeast", "Midwest"], government: false, sddc: false, gfm: false,
    dod: false, contact: "Casey Reed", email: "casey.reed@confluence.demo", phone: "412-555-0193",
    authority: "Active", insurance: "Aug 25, 2026", hazmat: false, refrigerated: false,
    relationship: "Prospect", compliance: "Review due", performance: 84, priorAwards: 1
  },
  {
    id: "car-aio", code: "AIO", name: "Allegheny Independent Transport", tier: "Community",
    classification: "Owner-operator", modes: ["TL", "Spot Bid"], headquarters: "Johnstown, PA",
    regions: ["PA", "OH", "WV", "MD"], government: false, sddc: false, gfm: false,
    dod: false, contact: "Jamie Cole", email: "jamie.cole@allegheny.demo", phone: "814-555-0119",
    authority: "Active", insurance: "Aug 3, 2026", hazmat: false, refrigerated: false,
    relationship: "Prospect", compliance: "Incomplete", performance: 87, priorAwards: 0
  },
  {
    id: "car-tnp", code: "TNP", name: "Titan National Parcel", tier: "Standard",
    classification: "Carrier", modes: ["Small Parcel", "LTL"], headquarters: "Columbus, OH",
    regions: ["Nationwide"], government: true, sddc: false, gfm: false,
    dod: true, contact: "POC missing", email: "", phone: "", authority: "Active",
    insurance: "May 28, 2027", hazmat: false, refrigerated: false,
    relationship: "Unknown", compliance: "Complete", performance: 86, priorAwards: 2
  }
];

export const procurementOpportunities: ProcurementOpportunity[] = [
  {
    id: "OPP-2417", name: "DLA depot replenishment movement",
    program: "Federal Supply Group / DLA support", contract: "DEMO-SP4701-26-D-0142",
    origin: "Harrisburg, PA 17101", destination: "Nashville, TN 37201",
    pickup: "Jun 25 · 8:00 AM", delivery: "Jun 27 · 5:00 PM", deadline: "Today · 4:00 PM",
    mode: "TL", weight: 38200, dimensions: "24 pallets · 48 × 40 × 52 in",
    commodity: "Machined hydraulic assemblies", hazmat: false, refrigerated: false,
    government: true, sddc: true, gfm: true,
    complianceTags: ["Active authority", "Cargo insurance", "SDDC/GFM readiness"],
    documents: ["Operating authority", "Cargo insurance", "W-9"],
    priority: "Urgent", status: "Evaluating", owner: "Maya Chen",
    matched: 5, shortlisted: 3, rfqs: 3, quotes: 3
  },
  {
    id: "OPP-2412", name: "Urgent avionics uplift to Ramstein",
    program: "Aviation readiness program", contract: "DEMO-FA8604-26-P-0088",
    origin: "Philadelphia, PA 19153", destination: "Frankfurt, DE 60549",
    pickup: "Jun 24 · 2:00 PM", delivery: "Jun 26 · 8:00 PM", deadline: "Today · 12:30 PM",
    mode: "Air Freight", weight: 4062, dimensions: "4 pieces · 48 × 40 × 52 in",
    commodity: "Non-sensitive avionics components", hazmat: false, refrigerated: false,
    government: true, sddc: false, gfm: true,
    complianceTags: ["Air cargo security", "GFM readiness"], documents: ["Cargo insurance", "W-9"],
    priority: "Critical", status: "Sourcing", owner: "Eli Brooks", matched: 2, shortlisted: 2, rfqs: 0, quotes: 0
  },
  {
    id: "OPP-2409", name: "York plant LTL replenishment",
    program: "Susquehanna Controls", contract: "Annual routing guide",
    origin: "York, PA 17401", destination: "Charlotte, NC 28202",
    pickup: "Jun 28 · 10:00 AM", delivery: "Jul 1 · 4:00 PM", deadline: "Jun 25 · 2:00 PM",
    mode: "LTL", weight: 4200, dimensions: "6 pallets · Class 70",
    commodity: "Industrial control valves", hazmat: false, refrigerated: false,
    government: false, sddc: false, gfm: false,
    complianceTags: ["Active authority", "Cargo insurance"], documents: ["Cargo insurance"],
    priority: "Normal", status: "RFQ open", owner: "Nina Patel", matched: 4, shortlisted: 3, rfqs: 3, quotes: 1
  },
  {
    id: "OPP-2398", name: "Pittsburgh–Dallas flatbed surge",
    program: "Keystone Components", contract: "Spot capacity",
    origin: "Pittsburgh, PA 15222", destination: "Dallas, TX 75201",
    pickup: "Jun 26 · 6:00 AM", delivery: "Jun 29 · 3:00 PM", deadline: "Today · 6:00 PM",
    mode: "Spot Bid", weight: 44000, dimensions: "48 ft flatbed",
    commodity: "Fabricated steel skids", hazmat: false, refrigerated: false,
    government: false, sddc: false, gfm: false,
    complianceTags: ["Active authority", "Cargo insurance"], documents: ["Cargo insurance"],
    priority: "Urgent", status: "Draft", owner: "Maya Chen", matched: 0, shortlisted: 0, rfqs: 0, quotes: 0
  },
  {
    id: "OPP-2387", name: "Federal lab small-parcel replenishment",
    program: "Federal Supply Group", contract: "DEMO-47QSHA-26-A-0190",
    origin: "Allentown, PA 18101", destination: "Aberdeen, MD 21001",
    pickup: "Jun 24", delivery: "Jun 25", deadline: "Closed",
    mode: "Small Parcel", weight: 186, dimensions: "14 cartons",
    commodity: "Calibration components", hazmat: false, refrigerated: false,
    government: true, sddc: false, gfm: false,
    complianceTags: ["Active authority"], documents: ["W-9"],
    priority: "Normal", status: "Awarded", owner: "Darius King",
    matched: 3, shortlisted: 2, rfqs: 2, quotes: 2,
    awardedCarrier: "Titan National Parcel",
    rationale: "Lowest compliant parcel rate with next-day service and an established government-business indicator."
  }
];

export const initialCandidates: CandidateState[] = [
  {
    carrierId: "car-kfp", score: 100, eligible: true, shortlisted: true, status: "Quoted",
    rate: 2840, transitDays: 2, fuel: 0, accessorials: "All-in",
    notes: "Capacity confirmed; direct service.",
    breakdown: [
      { label: "Mode match", points: 25, reason: "TL is a covered mode" },
      { label: "Government readiness", points: 15, reason: "SDDC and GFM indicators complete" },
      { label: "Region fit", points: 15, reason: "Northeast–Southeast coverage" },
      { label: "Compliance", points: 15, reason: "Authority, insurance, and W-9 verified" },
      { label: "Preferred relationship", points: 10, reason: "Preferred carrier" },
      { label: "Prior awards", points: 10, reason: "8 prior awards" },
      { label: "Contact completeness", points: 5, reason: "Capacity POC available" }
    ]
  },
  {
    carrierId: "car-sgl", score: 96, eligible: true, shortlisted: true, status: "Quoted",
    rate: 2975, transitDays: 2, fuel: 0, accessorials: "All-in",
    notes: "Government-program desk confirmed.",
    breakdown: [
      { label: "Mode match", points: 25, reason: "TL is a covered mode" },
      { label: "Government readiness", points: 15, reason: "SDDC, GFM, and DoD indicators" },
      { label: "Region fit", points: 15, reason: "Nationwide coverage" },
      { label: "Compliance", points: 15, reason: "Compliance file complete" },
      { label: "Active relationship", points: 7, reason: "Active relationship" },
      { label: "Prior awards", points: 10, reason: "6 prior awards" },
      { label: "Contact completeness", points: 5, reason: "Government desk available" }
    ]
  },
  {
    carrierId: "car-brx", score: 81, eligible: true, shortlisted: true, status: "Quoted",
    rate: 2775, transitDays: 2, fuel: 0, accessorials: "Appointment included",
    notes: "Lowest quote; no government registration.",
    breakdown: [
      { label: "Mode match", points: 25, reason: "TL is a covered mode" },
      { label: "Government readiness", points: -15, reason: "No SDDC/GFM indicator" },
      { label: "Region fit", points: 15, reason: "Northeast–Southeast coverage" },
      { label: "Compliance", points: 15, reason: "Compliance file complete" },
      { label: "Active relationship", points: 7, reason: "Active relationship" },
      { label: "Prior awards", points: 8, reason: "4 prior awards" },
      { label: "Contact completeness", points: 5, reason: "Capacity POC available" }
    ]
  },
  {
    carrierId: "car-cfl", score: 46, eligible: true, shortlisted: false, status: "Not contacted",
    breakdown: [
      { label: "Mode match", points: 25, reason: "TL is a covered mode" },
      { label: "Government readiness", points: -15, reason: "No government indicators" },
      { label: "Region fit", points: 15, reason: "Origin-region coverage" },
      { label: "Compliance", points: 7, reason: "Insurance review due" },
      { label: "Prospect relationship", points: 2, reason: "No prior operating history" },
      { label: "Contact completeness", points: 5, reason: "POC available" }
    ]
  },
  {
    carrierId: "car-aio", score: 24, eligible: false, shortlisted: false, status: "Not contacted",
    breakdown: [
      { label: "Mode match", points: 25, reason: "TL is a covered mode" },
      { label: "Government readiness", points: -15, reason: "No government indicators" },
      { label: "Region fit", points: -5, reason: "Destination outside normal service area" },
      { label: "Compliance", points: -8, reason: "Compliance file incomplete" },
      { label: "Prospect relationship", points: 2, reason: "No prior awards" },
      { label: "Contact completeness", points: 5, reason: "POC available" }
    ]
  }
];
