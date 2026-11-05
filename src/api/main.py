"""
FastAPI Backend for Microsoft AI & Agentic Solution Architecture Suite.
Follows `fullstack-fastapi-architecture` standards:
- Async `@asynccontextmanager` lifespan initializing shared harness & 3 pillar engines
- Strict Pydantic v2 contracts and clean HTTP status codes (`200`, `202 Accepted` for HITL interrupt, `403` for blocked guardrail)
- Serves interactive Operator & Architecture Console at `/`
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.core.harness import EnterpriseAgentHarness
from src.core.schemas import (
    AdaptiveCardApprovalRequest,
    EnterpriseRagQueryRequest,
    EnterpriseRagQueryResponse,
    FinOpsSizingRequest,
    FinOpsSizingResponse,
    HumanFeedbackDistillationRequest,
    HumanFeedbackDistillationResponse,
    KqlQueryRequest,
    KqlQueryResponse,
    LiveSpanStreamEvent,
    McpJsonRpcRequest,
    McpJsonRpcResponse,
    McpServerStatus,
    MemoryRecallRequest,
    MemoryRecallResponse,
    PowerPlatformGovernanceRequest,
    PowerPlatformGovernanceResponse,
    ProcurementRequest,
    ProcurementWorkflowResponse,
    RedTeamEvaluationResult,
    StrideAssessmentReport,
    StrideThreatRecord,
    SupplyChainExceptionRequest,
    SupplyChainResolutionResponse,
    WorkflowStatus,
)
from src.evals.runner import run_four_gate_evaluation
from src.pillars.p1_hybrid_procurement import HybridProcurementOrchestrator
from src.pillars.p2_zero_trust_rag import ZeroTrustEnterpriseRagEngine
from src.pillars.p3_multi_agent_erp import MultiAgentSupplyChainHub
from src.pillars.p4_governance_m365_finops import PowerPlatformGovernanceAndFinOpsEngine
from src.pillars.p5_agent_memory import memory_hub
from src.pillars.p6_observability_kql import kql_studio
from src.pillars.p7_security_redteam import red_team_engine
from src.pillars.p8_mcp_server import mcp_server

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize shared Enterprise Agent Harness and 4 Pillar Engines."""
    harness = EnterpriseAgentHarness()
    app.state.harness = harness
    app.state.pillar1 = HybridProcurementOrchestrator(harness=harness)
    app.state.pillar2 = ZeroTrustEnterpriseRagEngine()
    app.state.pillar3 = MultiAgentSupplyChainHub(harness=harness)
    app.state.pillar4 = PowerPlatformGovernanceAndFinOpsEngine()
    yield


app = FastAPI(
    title="Microsoft AI & Agentic Solution Architecture Suite",
    description=(
        "Production reference architecture for Copilot Studio + Microsoft Foundry Hybrid Orchestration, "
        "Zero-Trust ACL-Trimmed Azure AI Search & Fabric RAG, and Dynamics 365 / Service Bus Multi-Agent Hub."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root_console() -> FileResponse:
    """Serve the interactive Microsoft AI Solution Architect Workbench."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/v1/health")
async def health_check() -> dict[str, Any]:
    """Health & readiness probe for Azure Container Apps (ACA) / AKS."""
    harness: EnterpriseAgentHarness = app.state.harness
    return {
        "status": "healthy",
        "service": "microsoft-ai-agentic-suite",
        "pillars_online": [
            "Pillar 1: Copilot Studio + Microsoft Foundry Hybrid Operations Agent",
            "Pillar 2: Zero-Trust Entra ID ACL + Purview + Fabric RAG Engine",
            "Pillar 3: Multi-Agent Dynamics 365 & Azure Service Bus Hub",
            "Pillar 4: Power Platform DLP & ALM + M365 Copilot & FinOps Sizing",
            "Pillar 5: Multi-Tier Agent Memory & Cosmos DB Episodic Knowledge Store",
            "Pillar 6: Live OpenTelemetry GenAI Telemetry & Azure Log Analytics KQL Studio",
            "Pillar 7: Automated Microsoft AI Red Team & STRIDE Threat Modeling Engine",
            "Pillar 8: Production Model Context Protocol (FastMCP / JSON-RPC 2.0) Server",
        ],
        "dataverse_audit_records_count": len(harness.dataverse_audit_table),
        "otel_spans_exported_count": len(harness.exported_otel_spans),
    }


# ============================================================================
# Pillar 1 Endpoints: Hybrid Copilot Studio + Foundry Procurement Agent
# ============================================================================

@app.post("/api/v1/pillar1/procurement/run", response_model=ProcurementWorkflowResponse)
async def run_procurement_workflow(
    req: ProcurementRequest,
    response: Response,
) -> ProcurementWorkflowResponse:
    """
    Run Pillar 1 Hybrid workflow.
    Returns 202 Accepted if paused at Teams Adaptive Card HITL checkpoint (`PO > $10,000`),
    403 Forbidden if blocked by Azure AI Content Safety Prompt Shields, or 200 OK on completion.
    """
    p1: HybridProcurementOrchestrator = app.state.pillar1
    result = p1.run_workflow(req)
    if result.status == WorkflowStatus.AWAITING_HUMAN_APPROVAL:
        response.status_code = status.HTTP_202_ACCEPTED
    elif result.status == WorkflowStatus.BLOCKED_BY_GUARDRAIL:
        response.status_code = status.HTTP_403_FORBIDDEN
    return result


@app.post(
    "/api/v1/pillar1/procurement/{workflow_id}/approve",
    response_model=ProcurementWorkflowResponse,
)
async def approve_procurement_workflow(
    workflow_id: str,
    approval: AdaptiveCardApprovalRequest,
) -> ProcurementWorkflowResponse:
    """Resume a paused Pillar 1 workflow after Microsoft Teams Adaptive Card sign-off."""
    p1: HybridProcurementOrchestrator = app.state.pillar1
    try:
        return p1.resume_after_adaptive_card_approval(workflow_id=workflow_id, approval=approval)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ============================================================================
# Pillar 2 Endpoints: Zero-Trust Security-Trimmed RAG & Fabric Analytics
# ============================================================================

@app.post("/api/v1/pillar2/rag/query", response_model=EnterpriseRagQueryResponse)
async def query_zero_trust_rag(req: EnterpriseRagQueryRequest) -> EnterpriseRagQueryResponse:
    """Execute pre-retrieval Entra ID ACL + Purview trimmed Hybrid RRF search + Fabric SQL metrics."""
    p2: ZeroTrustEnterpriseRagEngine = app.state.pillar2
    return p2.query(req)


# ============================================================================
# Pillar 3 Endpoints: Multi-Agent Supply Chain & Dynamics 365 / Service Bus Hub
# ============================================================================

@app.post("/api/v1/pillar3/supply-chain/resolve", response_model=SupplyChainResolutionResponse)
async def resolve_supply_chain_exception(
    req: SupplyChainExceptionRequest,
) -> SupplyChainResolutionResponse:
    """Execute 4-agent Microsoft Foundry supervisor workflow with Service Bus retry & DLQ handling."""
    p3: MultiAgentSupplyChainHub = app.state.pillar3
    return p3.resolve_exception(req)


# ============================================================================
# Pillar 4 Endpoints: Power Platform DLP/ALM, M365 Copilot & FinOps PTU Sizing
# ============================================================================

@app.post("/api/v1/pillar4/governance/evaluate", response_model=PowerPlatformGovernanceResponse)
async def evaluate_power_platform_governance(
    req: PowerPlatformGovernanceRequest,
    response: Response,
) -> PowerPlatformGovernanceResponse:
    """Evaluate Managed Environment DLP policies, generate ALM solution.xml & M365 Copilot v1.2 manifest."""
    p4: PowerPlatformGovernanceAndFinOpsEngine = app.state.pillar4
    res = p4.evaluate_governance_and_m365(req)
    if not res.dlp_compliant:
        response.status_code = status.HTTP_403_FORBIDDEN
    return res


@app.post("/api/v1/pillar4/finops/estimate", response_model=FinOpsSizingResponse)
async def calculate_finops_and_sovereignty(
    req: FinOpsSizingRequest,
) -> FinOpsSizingResponse:
    """Calculate Copilot Studio packs, Azure OpenAI PTU vs. PAYG crossover, and GDPR sovereignty."""
    p4: PowerPlatformGovernanceAndFinOpsEngine = app.state.pillar4
    return p4.calculate_finops_and_sovereignty(req)


# ============================================================================
# Pillar 5 Endpoints: Multi-Tier Agent Memory & Cosmos DB Episodic Knowledge
# ============================================================================

@app.post("/api/v1/memory/recall", response_model=MemoryRecallResponse)
async def recall_agent_memory(req: MemoryRecallRequest) -> MemoryRecallResponse:
    """Recall working and episodic memory across Azure Cosmos DB NoSQL (`REQ-MEM-01`)."""
    return memory_hub.recall_episodic_memory(req)


@app.post("/api/v1/memory/distill", response_model=HumanFeedbackDistillationResponse)
async def distill_human_feedback(req: HumanFeedbackDistillationRequest) -> HumanFeedbackDistillationResponse:
    """Distill human approval/rejection feedback into permanent Cosmos DB governance rules (`INV-08`)."""
    return memory_hub.distill_feedback(req)


# ============================================================================
# Pillar 6 Endpoints: Observability, OpenTelemetry & Azure Log Analytics KQL
# ============================================================================

@app.post("/api/v1/telemetry/kql/execute", response_model=KqlQueryResponse)
async def execute_kql_query(req: KqlQueryRequest) -> KqlQueryResponse:
    """Execute KQL queries against simulated Azure Log Analytics workspace (`REQ-OBS-01`)."""
    return kql_studio.execute_kql(req)


@app.get("/api/v1/telemetry/spans/recent", response_model=list[LiveSpanStreamEvent])
async def get_recent_spans() -> list[LiveSpanStreamEvent]:
    """Retrieve recent OpenTelemetry GenAI spans for streaming visualization (`INV-09`)."""
    return kql_studio.get_recent_spans(limit=30)


# ============================================================================
# Pillar 7 Endpoints: Microsoft AI Red Team & STRIDE Threat Modeling
# ============================================================================

@app.post("/api/v1/security/redteam/run", response_model=StrideAssessmentReport)
async def run_red_team_suite() -> StrideAssessmentReport:
    """Execute full automated Microsoft AI Red Team adversarial testing battery (`REQ-SEC-01`)."""
    return red_team_engine.run_red_team_suite()


@app.get("/api/v1/security/stride/matrix", response_model=list[StrideThreatRecord])
async def get_stride_threat_matrix() -> list[StrideThreatRecord]:
    """Retrieve formal STRIDE Threat Modeling matrix mapped to Microsoft security controls (`INV-10`)."""
    return red_team_engine.get_stride_threat_matrix()


# ============================================================================
# Pillar 8 Endpoints: Model Context Protocol (FastMCP / JSON-RPC 2.0)
# ============================================================================

@app.post("/api/v1/mcp/jsonrpc", response_model=McpJsonRpcResponse)
async def handle_mcp_jsonrpc(req: McpJsonRpcRequest) -> McpJsonRpcResponse:
    """Standard Model Context Protocol JSON-RPC 2.0 wire dispatch endpoint (`REQ-MCP-01`)."""
    return mcp_server.handle_jsonrpc(req)


@app.get("/api/v1/mcp/status", response_model=McpServerStatus)
async def get_mcp_server_status() -> McpServerStatus:
    """Retrieve MCP server capabilities, protocol version, and exposed tool definitions (`INV-11`)."""
    return mcp_server.get_status()


# ============================================================================
# Cross-Cutting Endpoints: 4-Gate Evaluation Suite & Dataverse / OTel Telemetry
# ============================================================================

@app.post("/api/v1/evals/run")
async def trigger_four_gate_evals() -> dict[str, Any]:
    """Execute the 4-Gate Automated SDD Verification Suite."""
    return run_four_gate_evaluation()


@app.get("/api/v1/telemetry/audit-and-spans")
async def get_telemetry_and_audit() -> dict[str, Any]:
    """Inspect immutable Dataverse audit logs and exported OpenTelemetry GenAI spans."""
    harness: EnterpriseAgentHarness = app.state.harness
    p3: MultiAgentSupplyChainHub = app.state.pillar3
    return {
        "dataverse_audit_records": [r.model_dump() for r in harness.dataverse_audit_table[-25:]],
        "otel_genai_spans": [s.model_dump() for s in harness.exported_otel_spans[-25:]],
        "service_bus_dlq_messages": [m.model_dump() for m in p3.dead_letter_queue],
    }
