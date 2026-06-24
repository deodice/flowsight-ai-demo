# Freight Ops operating model

FlowSight Freight Ops extends the existing control tower with a shared source-to-cash workspace for shippers, brokers, carriers, owner-operators, freight forwarders, government contractors, and logistics analysts.

## Supported lifecycle

Freight need → opportunity → carrier match → shortlist → RFQ → carrier bids → award → tender → shipment execution → delivery → invoice → dispute or credit → payment.

One tenant-scoped canonical record connects the parties, lane, shipment, tender revisions, quote versions, line items, documents, events, invoice, credits, and disputes. The client portal is a permission-safe view of that graph rather than a separate database copy.

## Freight opportunity workflow

The opportunity is the shipper-side sourcing record. It captures the lane, dates, mode, commodity, handling units, special capabilities, government relevance, required compliance tags, required documents, priority, and quote deadline.

Carrier matching produces a visible score breakdown. Users shortlist candidates, generate copy-ready RFQ text, mark outreach sent, record response and no-bid states, enter quote details, compare eligible bids, and store a human award rationale. The procurement summary preserves all carriers considered—not only the winner.

## Modes

- LTL: weight, class, pallets, minimums, fuel, and accessorials.
- TL: equipment, distance, lane overrides, per-mile or flat rates, fuel, and accessorials.
- Spot Bid: market and lane signals, capacity adjustments, validity windows, and approval floors.
- Air Freight: origin and destination airports, service level, pieces, actual and dimensional weight, chargeable weight, minimums, handling, security, and AWB references.

## Deterministic quote policy

The pricing service calculates the same result for the same inputs and rule version. Every quote stores:

- normalized request inputs;
- applied rate-card and rule identifiers;
- base cost, minima, fuel, accessorials, and line-haul adjustments;
- client total, internal cost, margin amount, and margin percentage;
- approval-floor result;
- a readable calculation trace.

This is an original clean-room workflow. It uses standard freight concepts and does not reproduce a competitor’s protected interface, copy, source code, or proprietary pricing method.

## Permission views

Internal users may see buy cost, margin, pricing trace, approvals, and internal notes. Client and partner roles receive only approved service, quote, tender, document, shipment, and invoice fields. New internal fields are excluded from external serializers until deliberately approved.

## Integration seams

Accounting, TMS, carrier-rate, market-index, OCR, and payment services connect through adapters. The demo accounting adapter is intentionally provider-neutral so QuickBooks, Xero, NetSuite, or another platform can be added without changing freight domain records.
