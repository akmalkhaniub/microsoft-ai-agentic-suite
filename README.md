# Microsoft AI & Agentic Solution Architecture Suite (`AB-100` / `AI-102` / `PL-600`)

[![SDD Architecture](https://img.shields.io/badge/Methodology-Spec--Driven%20Development%20(SDD)-0284c7)](./SPECIFICATION.md)
[![Microsoft Stack](https://img.shields.io/badge/Stack-Copilot%20Studio%20%7C%20Microsoft%20Foundry%20%7C%20Fabric%20%7C%20Dataverse-10b981)](./docs/architecture/SOLUTION_ARCHITECTURE_AND_ADRS.md)
[![4-Gate Evals](https://img.shields.io/badge/4--Gate%20Verification-100%25%20Passing-22c55e)](./src/evals/runner.py)

A production-grade reference architecture and interactive workbench built with **Specification-Driven Development (SDD)** demonstrating end-to-end enterprise **Microsoft AI, Copilot Studio, Microsoft Foundry (Azure AI Foundry), Azure AI Search, Microsoft Fabric OneLake, Microsoft Purview, Power Platform (Dataverse & Power Automate), and Dynamics 365 / Azure Service Bus** integration.

---

## 🎯 Executive Mapping to Enterprise Solution Architect Requirements

| Flagship Pillar | Core Microsoft Technologies | Architectural Capabilities Demonstrated | Screening Question Answered |
| :--- | :--- | :--- | :--- |
| **Pillar 1: Hybrid Low-Code + Pro-Code Operations Agent** ([`p1_hybrid_procurement.py`](./src/pillars/p1_hybrid_procurement.py)) | **Microsoft Copilot Studio**, **Microsoft Foundry**, **Power Automate Adaptive Cards**, **Dataverse**, **Azure APIM**, **Entra ID OBO**, **Azure AI Content Safety** | • Deterministic router scoring **Copilot Studio vs. Microsoft Foundry vs. Hybrid OBO**<br/>• **Prompt Shields** blocking direct (UPIA) & indirect PDF (XPIA) prompt injections<br/>• Stateful HITL interrupt (`PO > $10,000`) with Teams Adaptive Card v1.5 sign-off, HMAC-SHA256 Entra ID approval signature, and immutable Dataverse audit trail | **Q2:** Copilot Studio vs. Foundry decision matrix<br/>**Q4:** Human approval, auditability & guardrails |
| **Pillar 2: Zero-Trust Security-Trimmed RAG & Fabric Engine** ([`p2_zero_trust_rag.py`](./src/pillars/p2_zero_trust_rag.py)) | **Azure AI Search**, **Microsoft Fabric OneLake**, **Microsoft Purview**, **Entra ID Groups**, **Azure APIM Semantic Cache** | • **Pre-retrieval OData ACL security trimming** (`search.in(acl_groups, ...)`)<br/>• **Microsoft Purview Sensitivity Label** enforcement (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `HIGHLY_CONFIDENTIAL_MA`)<br/>• Hybrid BM25 + Vector **Reciprocal Rank Fusion ($k=60$)** + Fabric Gold SQL metrics<br/>• **ACL-Scoped APIM Semantic Cache** preventing cross-role cache poisoning (`313ms -> 6.4ms`, `-43.8%` token cost) | **Q3:** Enterprise RAG with strict security boundaries<br/>**Q5:** Cost, performance & security trade-offs |
| **Pillar 3: Multi-Agent Supply Chain & ERP Hub** ([`p3_multi_agent_erp.py`](./src/pillars/p3_multi_agent_erp.py)) | **Microsoft Foundry Multi-Agent Service**, **Dynamics 365 Supply Chain**, **Azure Service Bus (Topics + DLQ)**, **OpenTelemetry GenAI** | • 4-Agent Supervisor (`TriageAgent` $\rightarrow$ `FabricInventoryAgent` $\rightarrow$ `PolicyComplianceAgent` $\rightarrow$ `Dynamics365ErpAgent`)<br/>• Self-healing exponential backoff on transient `HTTP 503` ERP throttling<br/>• Automatic **Dead-Letter Queue (`$DeadLetterQueue`)** isolation on persistent outage + `gen_ai.*` OTel spans | **Q1:** End-to-end solution from discovery to production<br/>**Q4 & Q5:** Resiliency & escalation |
| **Pillar 4: Power Platform DLP/ALM, M365 Copilot & FinOps PTU** ([`p4_governance_m365_finops.py`](./src/pillars/p4_governance_m365_finops.py)) | **Power Platform Managed Environments (DLP)**, **Dataverse Solutions (`solution.xml`)**, **Microsoft 365 Copilot Declarative Agent (`v1.2`)**, **Azure OpenAI PTU vs. PAYG** | • Managed Environment DLP evaluator blocking cross-boundary `Business` + `Non-Business`/`Blocked` data exfiltration<br/>• Schema-valid **M365 Copilot Declarative Agent (`v1.2`)** & `EntraOnBehalfOf` API Plugin generator<br/>• Interactive **Azure FinOps PTU vs. PAYG Crossover & UK/EU GDPR Sovereignty Calculator** | **Preferred:** Advanced Power Platform governance, M365 Copilot, FinOps & data residency |
| **Pillar 5: Multi-Tier Agent Memory & Cosmos DB Store** ([`p5_agent_memory.py`](./src/pillars/p5_agent_memory.py)) | **Azure Cosmos DB NoSQL**, **Semantic Cosine Embeddings**, **Human Feedback Distillation Loop** | • Multi-tier state: ephemeral session Working Memory + persistent Episodic Memory partitioned by `tenant_id`<br/>• Cosine similarity recall with semantic thresholding<br/>• Automated distillation of human approvals/rejections into immutable governance rules | **Core:** Agent memory, state management & continuous improvement |
| **Pillar 6: Live OpenTelemetry Telemetry & KQL Studio** ([`p6_observability_kql.py`](./src/pillars/p6_observability_kql.py)) | **Azure Log Analytics KQL**, **OpenTelemetry GenAI (`gen_ai.*`)**, **Server-Sent Events (SSE)** | • Interactive KQL studio running production queries (`Token Spend by Department`, `P95 Latency by Node`, `Prompt Shield Block Rate`, `Top 503 Tool Failures`)<br/>• Real-time SSE streaming span buffer with department cost center attribution | **Core:** Observability, diagnostics & FinOps tracking |
| **Pillar 7: AI Red Team & STRIDE Threat Engine** ([`p7_security_redteam.py`](./src/pillars/p7_security_redteam.py)) | **Microsoft AI Red Team**, **OWASP Top 10 for LLMs**, **STRIDE Threat Modeling** | • Automated 6-scenario red team battery (XPIA, Crescendo, System Prompt Leakage, SQLi, Unauthorized PO Release) with 100% defense rate<br/>• Formal STRIDE matrix mapping threats to Microsoft zero-trust controls | **Core:** Responsible AI, security & threat defense |
| **Pillar 8: FastMCP Protocol Server & Tool Registry** ([`p8_mcp_server.py`](./src/pillars/p8_mcp_server.py)) | **Model Context Protocol (2024-11-05)**, **FastMCP / JSON-RPC 2.0**, **Tiered Authorization** | • Standard JSON-RPC 2.0 interface supporting `ping`, `tools/list`, `resources/list`, and `tools/call`<br/>• 3 sensitivity tiers: `READ_ONLY`, `DRAFT_MUTATION`, and `LIVE_SPEND` with mandatory cryptographic JWT approval checks | **Preferred:** Open protocol interoperability & tool-calling |

---

## 🏛️ Repository Structure & Key Artifacts

```text
microsoft-ai-agentic-suite/
├── SPECIFICATION.md                                     # Layer 1 & 2 SDD: Architectural Constitution (INV-01..05) & REQ-IDs
├── docs/architecture/
│   └── SOLUTION_ARCHITECTURE_AND_ADRS.md                # Full SAD, C4 Mermaid Diagrams, FinOps Sheet & 5 Screening Question ADRs
├── deploy/azure/
│   └── main.bicep                                       # Azure IaC: AI Foundry, AI Search, Service Bus Topic/DLQ, App Insights
├── src/
│   ├── core/
│   │   ├── schemas.py                                   # Layer 3 SDD: Strict Pydantic v2 contracts & Entra ID OBO models
│   │   └── harness.py                                   # Agent Harness: LIVE_SPEND lock, Prompt Shields, SHA-256 Idempotency, OTel
│   ├── pillars/
│   │   ├── p1_hybrid_procurement.py                     # Pillar 1: Copilot Studio + Foundry Hybrid & Teams Adaptive Card HITL
│   │   ├── p2_zero_trust_rag.py                         # Pillar 2: Pre-Retrieval Entra ACL + Purview RRF RAG + Fabric + APIM Cache
│   │   ├── p3_multi_agent_erp.py                        # Pillar 3: 4-Agent Foundry Supervisor + Dynamics 365 & Service Bus DLQ
│   │   ├── p4_governance_m365_finops.py                 # Pillar 4: Power Platform DLP & ALM + M365 Copilot & FinOps PTU
│   │   ├── p5_agent_memory.py                           # Pillar 5: Multi-Tier Agent Memory (Working, Cosmos DB & Distillation)
│   │   ├── p6_observability_kql.py                      # Pillar 6: Live OpenTelemetry Telemetry & Azure Log Analytics KQL Studio
│   │   ├── p7_security_redteam.py                       # Pillar 7: Microsoft AI Red Team & STRIDE Threat Modeling Engine
│   │   └── p8_mcp_server.py                             # Pillar 8: FastMCP / Model Context Protocol (JSON-RPC 2.0) Server
│   ├── evals/
│   │   └── runner.py                                    # Layer 4 SDD: 4-Gate Automated Verification & Regression Runner
│   └── api/
│       ├── main.py                                      # FastAPI Lifespan Server + REST Endpoints
│       └── static/index.html                            # Light/Dark Human-Centered Solution Architect Workbench UI
└── tests/
    └── test_suite.py                                    # 100% Traceable Pytest Verification Suite
```

---

## 🚀 Quickstart (1-Command Verification & Interactive Workbench)

### 1. Run Automated Pytest Suite & 4-Gate Evaluation Harness
```bash
uv run pytest -v
uv run python -m src.evals.runner
```

### 2. Launch the Interactive Architect Workbench
```bash
uv run uvicorn src.api.main:app --reload --port 8010
```
Open `http://localhost:8010` to interactively test:
- **Pillar 1:** Trigger a `$48,500` PO to inspect the paused **Microsoft Teams Adaptive Card**, sign off with an **Entra ID cryptographic token**, or inject a malicious PDF prompt to see **Azure AI Content Safety Prompt Shields** block the workflow.
- **Pillar 2:** Switch caller identities between *Procurement Analyst (`INTERNAL`)*, *EMEA FinOps Lead (`CONFIDENTIAL`)*, and *M&A Board Executive (`HIGHLY_CONFIDENTIAL_MA`)* to observe real-time **Azure AI Search OData ACL security trimming** and **ACL-scoped APIM semantic caching**.
- **Pillar 3:** Inject synthetic `HTTP 503` Dynamics 365 faults to observe automatic retry recovery vs. **Azure Service Bus Dead-Letter Queue (`$DeadLetterQueue`)** escalation.
