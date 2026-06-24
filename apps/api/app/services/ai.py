from datetime import date


class GroundedSummaryProvider:
    name = "deterministic-evidence-v1"

    def daily_brief(self, exceptions: list[dict], kpis: dict) -> dict:
        ranked = sorted(exceptions, key=lambda x: (x["severity_score"], x["estimated_impact"]), reverse=True)
        top = ranked[:3]
        total = sum(float(x["estimated_impact"]) for x in exceptions)
        lines = [
            f"{len([x for x in exceptions if x['status'] == 'open'])} open risks represent ${total:,.0f} in estimated impact."
        ]
        citations = []
        for item in top:
            lines.append(f"{item['title']}: {item['recommended_action']}")
            citations.append({"entity": "exception", "id": item["id"], "value": float(item["estimated_impact"])})
        return {
            "title": f"Daily operations brief - {date.today().isoformat()}",
            "summary": " ".join(lines),
            "citations": citations,
            "provider": self.name,
            "guardrail": "Generated only from supplied tenant-scoped records."
        }
