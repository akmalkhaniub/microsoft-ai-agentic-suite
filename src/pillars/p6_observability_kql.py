"""Pillar 6: Live OpenTelemetry GenAI Telemetry & Azure Log Analytics KQL Studio (`REQ-OBS-01`).

Architectural Invariant `INV-09`:
Every graph execution, node transition, and tool call must emit structured OpenTelemetry
GenAI (gen_ai.*) spans with department cost-center attribution, queryable via Azure
Log Analytics Kusto Query Language (KQL) without data loss.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from src.core.schemas import (
    DepartmentCostAttribution,
    KqlQueryRequest,
    KqlQueryResponse,
    KqlQueryType,
    LiveSpanStreamEvent,
    OTelGenAISpan,
    utc_now_iso,
)


class AzureLogAnalyticsKqlStudio:
    """Simulates an enterprise Azure Monitor Log Analytics workspace with KQL execution engine."""

    def __init__(self) -> None:
        self._span_buffer: deque[LiveSpanStreamEvent] = deque(maxlen=200)
        self._seed_telemetry()

    def _seed_telemetry(self) -> None:
        """Seeds realistic historical spans across Contoso enterprise departments."""
        sample_departments = [
            ("Procurement", "gpt-4o", 1850, 420, 0.0152, "Pillar 1: Copilot/Foundry Router", 120),
            ("Procurement", "gpt-4o-mini", 950, 180, 0.0018, "Pillar 1: Dataverse Audit Logger", 240),
            ("Supply Chain & Logistics", "gpt-4o", 2200, 580, 0.0210, "Pillar 3: ERP Supervisor Agent", 95),
            ("Supply Chain & Logistics", "gpt-4o-mini", 800, 120, 0.0012, "Pillar 3: Warehouse Inventory Worker", 180),
            ("Legal & Compliance", "text-embedding-3-large", 450, 0, 0.0001, "Pillar 2: Azure AI Search Vectorizer", 310),
            ("Legal & Compliance", "gpt-4o", 3100, 890, 0.0345, "Pillar 2: Zero-Trust RAG Synthesizer", 85),
            ("Human Resources & IT", "gpt-4o-mini", 600, 110, 0.0009, "Pillar 4: M365 Declarative Agent", 410),
            ("Finance & Treasury", "gpt-4o", 1950, 490, 0.0175, "Pillar 4: FinOps PTU Optimizer", 140),
        ]

        base_trace = "4bf92f3577b34da6a3ce929d0e0e4736"
        for dept, model, p_tok, c_tok, cost, agent, count in sample_departments:
            for idx in range(min(count, 5)):
                event = LiveSpanStreamEvent(
                    span_id=f"span-{dept[:3].lower()}-{idx:03d}",
                    trace_id=base_trace,
                    name=agent,
                    department=dept,
                    model=model,
                    prompt_tokens=p_tok,
                    completion_tokens=c_tok,
                    cost_usd=cost,
                    status_code="OK",
                    timestamp=utc_now_iso(),
                )
                self._span_buffer.append(event)

    def record_otel_span(self, span: OTelGenAISpan, department: str = "Enterprise Engineering") -> None:
        """Ingests a live span from any executing pillar into the ring buffer."""
        p_tok = span.prompt_tokens or int(span.attributes.get("gen_ai.usage.input_tokens", 800))
        c_tok = span.completion_tokens or int(span.attributes.get("gen_ai.usage.output_tokens", 250))
        cost = span.estimated_cost_usd or float(span.attributes.get("cost_usd", 0.005))
        model = span.model or str(span.attributes.get("gen_ai.request.model", "gpt-4o"))
        name = span.operation_name

        event = LiveSpanStreamEvent(
            span_id=span.span_id,
            trace_id=span.trace_id,
            name=name,
            department=department,
            model=model,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            cost_usd=cost,
            status_code=span.status,
            timestamp=span.timestamp or utc_now_iso(),
        )
        self._span_buffer.appendleft(event)

    def get_recent_spans(self, limit: int = 50) -> list[LiveSpanStreamEvent]:
        """Returns the most recent OpenTelemetry GenAI spans for live streaming."""
        return list(self._span_buffer)[:limit]

    def execute_kql(self, request: KqlQueryRequest) -> KqlQueryResponse:
        """Executes a Kusto Query Language (KQL) query against the Azure Log Analytics schema (`REQ-OBS-01`)."""
        start_time = time.perf_counter()

        if request.query_type == KqlQueryType.TOKEN_COST_BY_DEPARTMENT:
            kql = (
                "AppTraces\n"
                "| where TimeGenerated > ago(24h)\n"
                "| extend Department = tostring(customDimensions[\"department\"]),\n"
                "         PromptTokens = toint(customDimensions[\"gen_ai.usage.input_tokens\"]),\n"
                "         CompletionTokens = toint(customDimensions[\"gen_ai.usage.output_tokens\"]),\n"
                "         CostUSD = todouble(customDimensions[\"cost_usd\"])\n"
                "| summarize TotalCalls = count(),\n"
                "            TotalPromptTokens = sum(PromptTokens),\n"
                "            TotalCompletionTokens = sum(CompletionTokens),\n"
                "            TotalSpendUSD = round(sum(CostUSD), 4)\n"
                "  by Department\n"
                "| order by TotalSpendUSD desc"
            )
            columns = ["Department", "TotalCalls", "TotalPromptTokens", "TotalCompletionTokens", "TotalSpendUSD", "TopAgent"]
            records = [
                {
                    "Department": "Legal & Compliance",
                    "TotalCalls": 395,
                    "TotalPromptTokens": 402500,
                    "TotalCompletionTokens": 75650,
                    "TotalSpendUSD": 3.4215,
                    "TopAgent": "Pillar 2: Zero-Trust RAG Synthesizer",
                },
                {
                    "Department": "Supply Chain & Logistics",
                    "TotalCalls": 275,
                    "TotalPromptTokens": 353000,
                    "TotalCompletionTokens": 76700,
                    "TotalSpendUSD": 2.2110,
                    "TopAgent": "Pillar 3: ERP Supervisor Agent",
                },
                {
                    "Department": "Procurement",
                    "TotalCalls": 360,
                    "TotalPromptTokens": 450000,
                    "TotalCompletionTokens": 93600,
                    "TotalSpendUSD": 2.2560,
                    "TopAgent": "Pillar 1: Copilot/Foundry Router",
                },
                {
                    "Department": "Finance & Treasury",
                    "TotalCalls": 140,
                    "TotalPromptTokens": 273000,
                    "TotalCompletionTokens": 68600,
                    "TotalSpendUSD": 2.4500,
                    "TopAgent": "Pillar 4: FinOps PTU Optimizer",
                },
                {
                    "Department": "Human Resources & IT",
                    "TotalCalls": 410,
                    "TotalPromptTokens": 246000,
                    "TotalCompletionTokens": 45100,
                    "TotalSpendUSD": 0.3690,
                    "TopAgent": "Pillar 4: M365 Declarative Agent",
                },
            ]
            vis = "bar_chart"

        elif request.query_type == KqlQueryType.P95_LATENCY_BY_NODE:
            kql = (
                "AppDependencies\n"
                "| where TimeGenerated > ago(24h) and Type == \"GenAI.AgentNode\"\n"
                "| summarize P50_ms = percentile(DurationMs, 50),\n"
                "            P95_ms = percentile(DurationMs, 95),\n"
                "            P99_ms = percentile(DurationMs, 99),\n"
                "            CallCount = count()\n"
                "  by Target\n"
                "| order by P95_ms desc"
            )
            columns = ["Target", "P50_ms", "P95_ms", "P99_ms", "CallCount", "SLA_Status"]
            records = [
                {"Target": "Foundry.SupervisorGraph", "P50_ms": 420.5, "P95_ms": 780.2, "P99_ms": 1150.0, "CallCount": 275, "SLA_Status": "MEETS_SLA"},
                {"Target": "AzureAISearch.HybridRRF", "P50_ms": 112.0, "P95_ms": 284.6, "P99_ms": 450.2, "CallCount": 395, "SLA_Status": "MEETS_SLA"},
                {"Target": "AzurePromptShield.InputGate", "P50_ms": 42.1, "P95_ms": 88.4, "P99_ms": 124.0, "CallCount": 735, "SLA_Status": "EXCELLENT"},
                {"Target": "Dataverse.AuditTransaction", "P50_ms": 65.0, "P95_ms": 145.0, "P99_ms": 210.5, "CallCount": 360, "SLA_Status": "MEETS_SLA"},
                {"Target": "CosmosDB.EpisodicMemoryRecall", "P50_ms": 18.5, "P95_ms": 38.2, "P99_ms": 62.0, "CallCount": 512, "SLA_Status": "EXCELLENT"},
            ]
            vis = "table"

        elif request.query_type == KqlQueryType.PROMPT_SHIELD_BLOCK_RATE:
            kql = (
                "AppEvents\n"
                "| where TimeGenerated > ago(24h) and Name == \"PromptShieldVerdict\"\n"
                "| extend Verdict = tostring(customDimensions[\"verdict\"]),\n"
                "         AttackCategory = tostring(customDimensions[\"attack_category\"])\n"
                "| summarize Blocked = countif(Verdict == \"BLOCK\"),\n"
                "            Flagged = countif(Verdict == \"FLAG\"),\n"
                "            Passed = countif(Verdict == \"PASS\"),\n"
                "            Total = count()\n"
                "  by AttackCategory\n"
                "| extend BlockRatePercent = round(100.0 * Blocked / Total, 2)"
            )
            columns = ["AttackCategory", "Blocked", "Flagged", "Passed", "Total", "BlockRatePercent"]
            records = [
                {"AttackCategory": "LLM01_PROMPT_INJECTION", "Blocked": 48, "Flagged": 4, "Passed": 0, "Total": 52, "BlockRatePercent": 92.31},
                {"AttackCategory": "LLM07_SYSTEM_PROMPT_LEAKAGE", "Blocked": 34, "Flagged": 2, "Passed": 0, "Total": 36, "BlockRatePercent": 94.44},
                {"AttackCategory": "XPIA_CROSS_PROMPT_INJECTION", "Blocked": 29, "Flagged": 3, "Passed": 0, "Total": 32, "BlockRatePercent": 90.63},
                {"AttackCategory": "LLM08_EXCESSIVE_AGENCY", "Blocked": 41, "Flagged": 1, "Passed": 0, "Total": 42, "BlockRatePercent": 97.62},
            ]
            vis = "pie_chart"

        elif request.query_type == KqlQueryType.TOP_TOOL_FAILURES:
            kql = (
                "AppDependencies\n"
                "| where TimeGenerated > ago(24h) and Success == false\n"
                "| summarize FailureCount = count(),\n"
                "            SampleErrorCode = any(ResultCode)\n"
                "  by Target\n"
                "| order by FailureCount desc"
            )
            columns = ["Target", "FailureCount", "SampleErrorCode", "AutoRemediationPattern"]
            records = [
                {"Target": "Dynamics365.InventoryReservation", "FailureCount": 12, "SampleErrorCode": "503 Service Unavailable", "AutoRemediationPattern": "Polly ExpBackoff Retry (Success on Attempt 2)"},
                {"Target": "LegacySAP.WarehouseNodeCheck", "FailureCount": 3, "SampleErrorCode": "408 Request Timeout", "AutoRemediationPattern": "Rerouted to Azure Service Bus DLQ"},
            ]
            vis = "table"

        else:
            kql = request.custom_kql or "// Custom KQL executed against Azure Log Analytics"
            columns = ["Timestamp", "Level", "Message", "OperationId"]
            records = [
                {"Timestamp": utc_now_iso(), "Level": "Information", "Message": "Custom KQL query executed successfully.", "OperationId": "op-kql-custom-99"},
            ]
            vis = "table"

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return KqlQueryResponse(
            query_type=request.query_type,
            kql_executed=kql,
            row_count=len(records),
            columns=columns,
            records=records,
            execution_duration_ms=duration_ms,
            visualization_type=vis,
        )


# Global singleton instance
kql_studio = AzureLogAnalyticsKqlStudio()
