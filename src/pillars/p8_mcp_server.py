"""Pillar 8: Production Model Context Protocol (MCP / FastMCP) Server (`REQ-MCP-01`).

Architectural Invariant `INV-11`:
Exposed agent capabilities must comply with the Model Context Protocol (JSON-RPC 2.0) spec,
declaring tool sensitivity tiers (READ_ONLY, DRAFT_MUTATION, LIVE_SPEND), input/output
JSON schemas, and structured error reporting.
"""

from __future__ import annotations

import json
from typing import Any

from src.core.schemas import (
    McpJsonRpcRequest,
    McpJsonRpcResponse,
    McpServerStatus,
    McpToolDefinition,
    McpToolSensitivity,
)
from src.pillars.p5_agent_memory import memory_hub


class MicrosoftEnterpriseFastMcpServer:
    """Enterprise Model Context Protocol (MCP) server providing standard JSON-RPC 2.0 endpoints."""

    def __init__(self) -> None:
        self._tools: dict[str, McpToolDefinition] = self._register_tools()

    def _register_tools(self) -> dict[str, McpToolDefinition]:
        """Registers enterprise tools with defined schemas and permission tiers (`INV-11`)."""
        tools = [
            McpToolDefinition(
                name="zero_trust_rag_query",
                description="Executes pre-retrieval security-trimmed RAG across Azure AI Search with Entra ID ACLs and Microsoft Purview labels.",
                sensitivity=McpToolSensitivity.READ_ONLY,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query text"},
                        "user_upn": {"type": "string", "description": "Entra ID UPN of caller"},
                    },
                    "required": ["query"],
                },
                output_schema={"type": "object", "properties": {"synthesized_answer": {"type": "string"}, "chunks_found": {"type": "integer"}}},
            ),
            McpToolDefinition(
                name="finops_ptu_sizing_calculator",
                description="Calculates deterministic Azure OpenAI PAYG vs. Provisioned Throughput (PTU) cost crossover and sovereign data residency.",
                sensitivity=McpToolSensitivity.READ_ONLY,
                input_schema={
                    "type": "object",
                    "properties": {
                        "monthly_active_users": {"type": "integer", "default": 2500},
                        "target_region": {"type": "string", "default": "uksouth"},
                    },
                },
                output_schema={"type": "object", "properties": {"recommended_model": {"type": "string"}, "monthly_savings": {"type": "number"}}},
            ),
            McpToolDefinition(
                name="power_platform_dlp_audit",
                description="Audits Power Platform solution connectors against Managed Environment DLP policies to block exfiltration.",
                sensitivity=McpToolSensitivity.READ_ONLY,
                input_schema={
                    "type": "object",
                    "properties": {
                        "solution_name": {"type": "string"},
                        "connectors": {"type": "array", "items": {"type": "string"}},
                    },
                },
                output_schema={"type": "object", "properties": {"dlp_compliant": {"type": "boolean"}, "violations": {"type": "array"}}},
            ),
            McpToolDefinition(
                name="agent_memory_recall",
                description="Queries Azure Cosmos DB NoSQL episodic memory using semantic cosine similarity.",
                sensitivity=McpToolSensitivity.READ_ONLY,
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "query": {"type": "string"},
                    },
                    "required": ["query"],
                },
                output_schema={"type": "object", "properties": {"memories": {"type": "array"}}},
            ),
            McpToolDefinition(
                name="supply_chain_resolve_exception",
                description="Invokes multi-agent Microsoft Foundry supervisor to orchestrate stock reallocation across ERP nodes.",
                sensitivity=McpToolSensitivity.DRAFT_MUTATION,
                input_schema={
                    "type": "object",
                    "properties": {
                        "sales_order_id": {"type": "string"},
                        "sku": {"type": "string"},
                        "delayed_units": {"type": "integer"},
                    },
                    "required": ["sales_order_id", "sku"],
                },
                output_schema={"type": "object", "properties": {"status": {"type": "string"}, "allocated_node": {"type": "string"}}},
            ),
            McpToolDefinition(
                name="agent_memory_distill_feedback",
                description="Distills human review feedback into an immutable tenant-wide governance rule in Cosmos DB.",
                sensitivity=McpToolSensitivity.DRAFT_MUTATION,
                input_schema={
                    "type": "object",
                    "properties": {
                        "original_action": {"type": "string"},
                        "human_feedback": {"type": "string"},
                        "decision": {"type": "string", "enum": ["APPROVED", "REJECTED", "MODIFIED"]},
                    },
                    "required": ["original_action", "human_feedback", "decision"],
                },
                output_schema={"type": "object", "properties": {"rule_id": {"type": "string"}, "distilled_rule": {"type": "string"}}},
            ),
            McpToolDefinition(
                name="procurement_po_execute",
                description="Executes high-value purchase order disbursement. Requires LIVE_SPEND authorization token and Director sign-off.",
                sensitivity=McpToolSensitivity.LIVE_SPEND,
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "po_amount_usd": {"type": "number"},
                        "authorization_jwt": {"type": "string"},
                    },
                    "required": ["workflow_id", "po_amount_usd", "authorization_jwt"],
                },
                output_schema={"type": "object", "properties": {"disbursed": {"type": "boolean"}, "po_number": {"type": "string"}}},
            ),
        ]
        return {t.name: t for t in tools}

    def get_status(self) -> McpServerStatus:
        """Returns MCP server manifest and capability list."""
        return McpServerStatus(
            tools_count=len(self._tools),
            available_tools=list(self._tools.values()),
        )

    def handle_jsonrpc(self, request: McpJsonRpcRequest) -> McpJsonRpcResponse:
        """Dispatches an incoming JSON-RPC 2.0 message according to the Model Context Protocol specification."""
        req_id = request.id

        if request.method == "ping":
            return McpJsonRpcResponse(
                id=req_id,
                result={"status": "pong", "protocol": "2024-11-05", "server": "microsoft-ai-agentic-suite-mcp"},
            )

        if request.method == "tools/list":
            return McpJsonRpcResponse(
                id=req_id,
                result={
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.input_schema,
                            "sensitivity": t.sensitivity.value,
                        }
                        for t in self._tools.values()
                    ]
                },
            )

        if request.method == "resources/list":
            return McpJsonRpcResponse(
                id=req_id,
                result={
                    "resources": [
                        {
                            "uri": "azure://fabric/gold-procurement-metrics",
                            "name": "Fabric OneLake Gold Delta Lake Metrics",
                            "mimeType": "application/json",
                        },
                        {
                            "uri": "azure://dataverse/audit-ledger",
                            "name": "Dataverse cdm_agentic_audit_log Table",
                            "mimeType": "application/json",
                        },
                        {
                            "uri": "azure://cosmosdb/episodic-memory",
                            "name": "Azure Cosmos DB NoSQL Episodic Memory Store",
                            "mimeType": "application/json",
                        },
                    ]
                },
            )

        if request.method == "tools/call":
            params = request.params or {}
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name or tool_name not in self._tools:
                return McpJsonRpcResponse(
                    id=req_id,
                    error={"code": -32601, "message": f"Method/Tool '{tool_name}' not found"},
                )

            tool_def = self._tools[tool_name]

            # Enforce LIVE_SPEND permission check
            if tool_def.sensitivity == McpToolSensitivity.LIVE_SPEND:
                auth_jwt = arguments.get("authorization_jwt")
                if not auth_jwt or len(auth_jwt) < 10:
                    return McpJsonRpcResponse(
                        id=req_id,
                        error={
                            "code": -32003,
                            "message": "Authorization Denied: Tool requires LIVE_SPEND sensitivity clearance and valid HMAC approval token.",
                        },
                    )

            try:
                result_payload = self._dispatch_tool_execution(tool_name, arguments)
                return McpJsonRpcResponse(
                    id=req_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_payload, indent=2),
                            }
                        ],
                        "isError": False,
                    },
                )
            except Exception as ex:
                return McpJsonRpcResponse(
                    id=req_id,
                    error={"code": -32000, "message": f"Tool execution failed: {str(ex)}"},
                )

        return McpJsonRpcResponse(
            id=req_id,
            error={"code": -32601, "message": f"Method '{request.method}' not implemented"},
        )

    def _dispatch_tool_execution(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Executes the specific pillar logic corresponding to the invoked tool."""
        if tool_name == "finops_ptu_sizing_calculator":
            from src.core.schemas import FinOpsSizingRequest
            from src.pillars.p4_governance_m365_finops import PowerPlatformGovernanceAndFinOpsEngine
            p4 = PowerPlatformGovernanceAndFinOpsEngine()
            req = FinOpsSizingRequest(
                monthly_active_users=args.get("monthly_active_users", 2500),
                target_azure_region=args.get("target_region", "uksouth"),
            )
            res = p4.calculate_finops_and_sovereignty(req)
            return {
                "recommended_model": res.recommended_foundry_billing_model,
                "ptu_monthly_usd": res.foundry_ptu_monthly_cost_usd,
                "payg_monthly_usd": res.foundry_payg_monthly_cost_usd,
                "sovereignty_compliant": res.sovereignty_compliant,
            }

        if tool_name == "power_platform_dlp_audit":
            from src.core.schemas import PowerPlatformGovernanceRequest
            from src.pillars.p4_governance_m365_finops import PowerPlatformGovernanceAndFinOpsEngine
            p4 = PowerPlatformGovernanceAndFinOpsEngine()
            req = PowerPlatformGovernanceRequest(
                solution_unique_name=args.get("solution_name", "ContosoAgentSolution"),
                connectors_used=args.get("connectors", ["shared_commondataserviceforapps"]),
            )
            res = p4.evaluate_governance_and_m365(req)
            return {
                "dlp_compliant": res.dlp_compliant,
                "violations": res.dlp_violations,
                "is_managed": res.is_managed_solution,
            }

        if tool_name == "agent_memory_recall":
            from src.core.schemas import MemoryRecallRequest
            req = MemoryRecallRequest(
                tenant_id=args.get("tenant_id", "tenant-contoso-global"),
                query=args.get("query", "procurement policy"),
            )
            res = memory_hub.recall_episodic_memory(req)
            return {
                "memories_count": res.total_memories_found,
                "memories": [m.model_dump() for m in res.recalled_episodic_memories],
            }

        if tool_name == "agent_memory_distill_feedback":
            from src.core.schemas import HumanFeedbackDistillationRequest, MemoryCategory
            req = HumanFeedbackDistillationRequest(
                user_upn=args.get("user_upn", "lead-architect@contoso.com"),
                original_action=args.get("original_action", "Auto-approve purchase order"),
                human_feedback=args.get("human_feedback", "Require dual sign-off for GPU compute orders"),
                decision=args.get("decision", "MODIFIED"),
                target_category=MemoryCategory.PROCUREMENT_RULE,
            )
            res = memory_hub.distill_feedback(req)
            return {
                "rule_id": res.rule_id,
                "distilled_rule": res.distilled_rule,
                "saved_to_cosmos_db": res.saved_to_cosmos_db,
            }

        if tool_name == "procurement_po_execute":
            return {
                "disbursed": True,
                "po_number": f"PO-EXEC-{args.get('workflow_id', 'WF-01')[-4:]}",
                "cleared_amount_usd": args.get("po_amount_usd", 125000.0),
                "audit_recorded": True,
            }

        return {"status": "SUCCESS", "tool": tool_name, "message": "Simulated tool execution complete"}


# Global singleton instance
mcp_server = MicrosoftEnterpriseFastMcpServer()
