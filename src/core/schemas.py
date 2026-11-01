"""
Contract-First Schemas (Layer 3 of SDD) for Microsoft AI & Agentic Solution Architecture Suite.
Covers:
- REQ-ARCH-01: Copilot Studio vs. Microsoft Foundry architectural routing contracts
- REQ-HARN-01: Tool Sensitivity Tiers, Azure AI Content Safety Prompt Shields, Idempotency
- REQ-HITL-01: Power Automate Adaptive Card HITL Approval & Immutable Dataverse Audit Record
- REQ-RAG-01 / REQ-RAG-02: Entra ID ACL-Trimmed Hybrid RAG, Purview Sensitivity Labels, Fabric SQL
- REQ-FIN-01: APIM Semantic Cache with ACL Scope Isolation & FinOps Token Telemetry
- REQ-ERP-01 / REQ-INT-01: Multi-Agent Supply Chain Exception Hub, Dynamics 365, Service Bus DLQ
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


# ============================================================================
# 1. Cross-Cutting Security, Identity & Governance Enums
# ============================================================================

class ToolSensitivityTier(str, Enum):
    """Governs Agent Harness execution gating (REQ-HARN-01)."""
    READ_ONLY = "READ_ONLY"
    DRAFT_MUTATION = "DRAFT_MUTATION"
    LIVE_SPEND = "LIVE_SPEND"


class PurviewSensitivityLabel(str, Enum):
    """Microsoft Purview Information Protection labels (REQ-RAG-01)."""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    HIGHLY_CONFIDENTIAL_MA = "HIGHLY_CONFIDENTIAL_MA"


class OrchestrationPattern(str, Enum):
    """Microsoft AI target architecture pattern (REQ-ARCH-01)."""
    LOW_CODE_COPILOT = "LOW_CODE_COPILOT"
    PRO_CODE_FOUNDRY = "PRO_CODE_FOUNDRY"
    HYBRID_COPILOT_FOUNDRY_OBO = "HYBRID_COPILOT_FOUNDRY_OBO"


class WorkflowStatus(str, Enum):
    """Lifecycle states for stateful agent workflows."""
    COMPLETED = "completed"
    AWAITING_HUMAN_APPROVAL = "awaiting_human_approval"
    BLOCKED_BY_GUARDRAIL = "blocked_by_guardrail"
    REJECTED_BY_REVIEWER = "rejected_by_reviewer"
    ESCALATED_TO_DLQ = "escalated_to_dlq"


class EntraIdentityContext(BaseModel):
    """Simulated Microsoft Entra ID (formerly Azure AD) JWT claims for On-Behalf-Of (OBO) flows."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tenant_id: str = Field(..., description="Entra ID Directory / Tenant GUID")
    user_oid: str = Field(..., description="Entra ID User Object ID")
    user_principal_name: str = Field(..., description="UPN e.g. sarah.chen@contoso.com")
    display_name: str = Field(..., description="Human readable name")
    roles: list[str] = Field(default_factory=list, description="App roles e.g. Procurement.Approver")
    acl_groups: list[str] = Field(
        default_factory=list,
        description="Entra ID Security Group Object IDs for Azure AI Search pre-retrieval trimming",
    )
    max_purview_clearance: PurviewSensitivityLabel = Field(
        default=PurviewSensitivityLabel.INTERNAL,
        description="Highest Purview sensitivity label this user is authorized to decrypt/view",
    )


# ============================================================================
# 2. Observability & Agent Harness Contracts (REQ-HARN-01, REQ-INT-01)
# ============================================================================

class OTelGenAISpan(BaseModel):
    """OpenTelemetry GenAI Semantic Conventions span exported to Azure Monitor / App Insights."""
    span_id: str
    trace_id: str
    parent_span_id: str | None = None
    operation_name: str = Field(..., description="e.g. gen_ai.agent.invoke, gen_ai.tool.call")
    system: str = Field(default="azure.ai.foundry", description="gen_ai.system")
    model: str = Field(default="gpt-4o-2024-11-20", description="gen_ai.request.model")
    sensitivity_tier: ToolSensitivityTier | None = None
    idempotency_key: str | None = None
    idempotency_cache_hit: bool = False
    retry_attempts: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    duration_ms: float = 0.0
    status: Literal["OK", "ERROR", "BLOCKED", "PAUSED_HITL"] = "OK"
    attributes: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=utc_now_iso)


class PromptShieldVerdict(BaseModel):
    """Azure AI Content Safety Prompt Shields result (Direct UPIA + Indirect Document XPIA)."""
    safe: bool
    user_prompt_attack_detected: bool = False
    document_attack_detected: bool = False
    flagged_triggers: list[str] = Field(default_factory=list)
    shield_latency_ms: float = 2.4


class DataverseAuditRecord(BaseModel):
    """Immutable audit log persisted to Microsoft Dataverse (`msft_agentauditlogs`)."""
    audit_id: str
    workflow_id: str
    tenant_id: str
    actor_upn: str
    actor_oid: str
    action_type: str
    tool_name: str
    sensitivity_tier: ToolSensitivityTier
    idempotency_key: str
    approval_signature: str | None = None
    outcome: str
    payload_summary: str
    created_on: str = Field(default_factory=utc_now_iso)


# ============================================================================
# 3. Pillar 1: Hybrid Copilot Studio + Microsoft Foundry Operations Agent
# ============================================================================

class ArchitectureRoutingEvaluation(BaseModel):
    """Answers Vurke Screening Question #2: Copilot Studio vs. Microsoft Foundry decision matrix."""
    selected_pattern: OrchestrationPattern
    copilot_studio_fit_score: int = Field(..., ge=0, le=100)
    foundry_pro_code_fit_score: int = Field(..., ge=0, le=100)
    primary_rationale: str
    identity_flow: str = Field(
        default="Teams -> Copilot Studio -> Azure APIM (Validate JWT) -> Entra ID OBO Token Exchange -> Microsoft Foundry Agent Service"
    )
    licensing_comparison: dict[str, Any]
    tradeoffs: list[str]


class ProcurementRequest(BaseModel):
    """Input request for Pillar 1 Hybrid Vendor Onboarding & Purchase Order Agent."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    workflow_id: str = Field(default="po-req-2026-001")
    identity: EntraIdentityContext
    user_query: str = Field(..., min_length=5)
    vendor_name: str = Field(..., min_length=2)
    vendor_tax_id: str = Field(default="US-EIN-94-3829100")
    requested_amount_usd: float = Field(..., gt=0)
    cost_center: str = Field(default="CC-4020-CLOUD-INFRA")
    uploaded_contract_excerpt: str = Field(
        default="Standard MSA v4.2: Net-30 payment terms, SOC2 Type II attested, liability cap 2x annual fees."
    )
    require_multi_doc_synthesis: bool = True


class AdaptiveCardApprovalRequest(BaseModel):
    """Human-in-the-Loop approval payload submitted via Teams / Power Automate Adaptive Card."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    reviewer_upn: str = Field(..., min_length=5)
    reviewer_oid: str = Field(default="oid-approver-director-01")
    reviewer_notes: str = Field(default="Verified budget allocation in SAP/Dataverse and SOC2 attestation.")


class ProcurementWorkflowResponse(BaseModel):
    """Full state response for Pillar 1 workflow execution."""
    workflow_id: str
    status: WorkflowStatus
    routing_decision: ArchitectureRoutingEvaluation
    prompt_shield: PromptShieldVerdict
    vendor_risk_score: int = Field(..., ge=0, le=100)
    contract_clauses_extracted: list[str]
    po_number: str | None = None
    total_amount_usd: float
    requires_hitl_approval: bool
    adaptive_card_payload: dict[str, Any] | None = None
    approval_jwt_signature: str | None = None
    dataverse_audit_trail: list[DataverseAuditRecord] = Field(default_factory=list)
    otel_spans: list[OTelGenAISpan] = Field(default_factory=list)


# ============================================================================
# 4. Pillar 2: Zero-Trust Security-Trimmed RAG & Fabric Analytics Engine
# ============================================================================

class IndexedDocumentChunk(BaseModel):
    """Document chunk stored in Azure AI Search with Entra ID ACLs & Purview sensitivity metadata."""
    chunk_id: str
    document_title: str
    source_system: Literal["SharePoint_Online", "Fabric_OneLake", "Dataverse_Knowledge"]
    content: str
    acl_groups: list[str] = Field(..., description="Entra ID security group OIDs permitted to read this chunk")
    sensitivity_label: PurviewSensitivityLabel
    embedding_vector: list[float] = Field(default_factory=list)
    bm25_keywords: list[str] = Field(default_factory=list)


class ScoredSearchChunk(BaseModel):
    """Retrieved chunk after pre-retrieval ACL trimming and Reciprocal Rank Fusion (RRF)."""
    chunk_id: str
    document_title: str
    source_system: str
    sensitivity_label: PurviewSensitivityLabel
    acl_groups_matched: list[str]
    bm25_rank: int
    vector_rank: int
    rrf_score: float
    content_snippet: str


class EnterpriseRagQueryRequest(BaseModel):
    """Input query for Pillar 2 Zero-Trust RAG & Microsoft Fabric OneLake Engine."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(..., min_length=3)
    identity: EntraIdentityContext
    include_fabric_warehouse_metrics: bool = True
    use_apim_semantic_cache: bool = True


class EnterpriseRagQueryResponse(BaseModel):
    """Output response demonstrating pre-retrieval ACL trimming, Purview filtering, RRF, and FinOps cache."""
    query: str
    caller_upn: str
    caller_acl_groups: list[str]
    caller_purview_clearance: PurviewSensitivityLabel
    odata_security_filter: str = Field(
        ...,
        description="Exact Azure AI Search OData filter string applied pre-retrieval",
    )
    total_index_chunks: int
    chunks_permitted_after_acl_trim: int
    chunks_blocked_by_acl_or_purview: int
    blocked_document_titles: list[str]
    retrieved_chunks: list[ScoredSearchChunk]
    fabric_sql_metrics: dict[str, Any] | None = None
    synthesized_answer: str
    apim_cache_hit: bool
    apim_cache_scope_key: str
    latency_ms: float
    estimated_cost_usd: float
    baseline_uncached_cost_usd: float
    otel_spans: list[OTelGenAISpan] = Field(default_factory=list)


# ============================================================================
# 5. Pillar 3: Multi-Agent Supply Chain & Dynamics 365 / Service Bus Hub
# ============================================================================

class SupplyChainExceptionRequest(BaseModel):
    """Input event for Pillar 3 Multi-Agent ERP & Supply Chain Resolution Hub."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    exception_id: str = Field(default="exc-d365-9941")
    identity: EntraIdentityContext
    sales_order_id: str = Field(default="SO-2026-88412")
    customer_name: str = Field(default="Contoso Aerospace Ltd (UK)")
    disrupted_sku: str = Field(default="SKU-TURBINE-VALVE-V9")
    delayed_units: int = Field(default=40, gt=0)
    contract_sla_tier: Literal["PLATINUM", "GOLD", "STANDARD"] = "PLATINUM"
    simulate_erp_transient_503: bool = Field(
        default=True,
        description="Injects a synthetic 503 error on attempt #1 to prove Polly/Harness self-healing retry",
    )
    simulate_unrecoverable_outage: bool = Field(
        default=False,
        description="Forces all retries to fail so payload routes to Azure Service Bus Dead-Letter Queue (DLQ)",
    )


class AgentHandoffStep(BaseModel):
    """Step in the Microsoft Foundry Supervisor -> Worker multi-agent orchestration graph."""
    step_order: int
    agent_name: str
    role: str
    input_summary: str
    output_summary: str
    tool_invoked: str
    latency_ms: float


class ServiceBusEnvelope(BaseModel):
    """Asynchronous integration message published to Azure Service Bus Topic / Queue."""
    message_id: str
    correlation_id: str
    topic_name: str = "sbt-d365-erp-fulfillment"
    subscription_name: str = "sbs-logicapp-sap-d365-sync"
    delivery_count: int
    status: Literal["DELIVERED", "DEAD_LETTERED"]
    dead_letter_reason: str | None = None
    payload: dict[str, Any]
    published_at: str = Field(default_factory=utc_now_iso)


class SupplyChainResolutionResponse(BaseModel):
    """End-to-end resolution output from Pillar 3 Multi-Agent Hub."""
    exception_id: str
    sales_order_id: str
    status: WorkflowStatus
    sla_penalty_exposure_usd: float
    recommended_remediation_cost_usd: float
    net_sla_savings_usd: float
    allocated_warehouse_node: str
    d365_credit_memo_id: str | None = None
    agent_trajectory: list[AgentHandoffStep]
    service_bus_envelope: ServiceBusEnvelope
    customer_communication_draft: str
    otel_spans: list[OTelGenAISpan] = Field(default_factory=list)
