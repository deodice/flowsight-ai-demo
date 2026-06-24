import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ControlTower } from "./control-tower";

Object.defineProperty(globalThis, "ResizeObserver", {
  value: class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
});

afterEach(cleanup);

describe("ControlTower", () => {
  it("renders the operational golden path", () => {
    render(<ControlTower section="overview" />);
    expect(screen.getByText("Good morning, Maya.")).toBeInTheDocument();
    expect(screen.getByText("Priority exceptions")).toBeInTheDocument();
    expect(screen.getByText("Demand & forecast")).toBeInTheDocument();
  });

  it("renders the import workflow", () => {
    render(<ControlTower section="imports" />);
    expect(screen.getByRole("heading", { name: "Data imports" })).toBeInTheDocument();
    expect(screen.getByText("active mapping templates")).toBeInTheDocument();
  });

  it("renders the deterministic freight quote desk", () => {
    render(<ControlTower section="freight-quotes" />);
    expect(screen.getByRole("heading", { name: "Quote desk" })).toBeInTheDocument();
    expect(screen.getByText("Calculate auditable quote")).toBeInTheDocument();
    expect(screen.getByText("INTERNAL COSTING WORKSHEET")).toBeInTheDocument();
  });

  it("renders a client-safe shipper portal", () => {
    render(<ControlTower section="freight-client" />);
    expect(screen.getByRole("heading", { name: "Apex Machine Works" })).toBeInTheDocument();
    expect(screen.getByText("Client-safe view")).toBeInTheDocument();
    expect(screen.getByText(/Carrier cost, gross margin/)).toBeInTheDocument();
  });

  it("renders the procurement execution command center", () => {
    render(<ControlTower section="freight" />);
    expect(screen.getByRole("heading", { name: "Move today’s freight with fewer blind spots." })).toBeInTheDocument();
    expect(screen.getByText("Freight opportunities")).toBeInTheDocument();
    expect(screen.getByText("Carrier gaps slowing execution")).toBeInTheDocument();
  });

  it("creates an opportunity and immediately ranks carriers", () => {
    render(<ControlTower section="freight-opportunities" />);
    fireEvent.click(screen.getByRole("button", { name: "New opportunity" }));
    expect(screen.getByRole("heading", { name: "What needs to move?" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Create and match carriers" }));
    expect(screen.getByRole("heading", { name: "Urgent depot replenishment" })).toBeInTheDocument();
    expect(screen.getByText("7 carriers ranked")).toBeInTheDocument();
    expect(screen.getByText("FIT SCORE BREAKDOWN")).toBeInTheDocument();
  });

  it("moves a seeded opportunity through RFQ generation and award", () => {
    render(<ControlTower section="freight-opportunity" />);
    fireEvent.click(screen.getByRole("button", { name: "Generate 3 RFQs" }));
    expect(screen.getByText("RFQ WORKBENCH")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Quotes & award/ }));
    expect(screen.getByText("EXPLAINABLE RECOMMENDATION")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Award freight" }));
    expect(screen.getByRole("heading", { name: "OPP-2417 awarded" })).toBeInTheDocument();
    expect(screen.getByText("Award rationale recorded")).toBeInTheDocument();
  });
});
