# Specification-Driven Development (SDD) — Microsoft AI & Agentic Solution Architecture Suite

**Repository:** `microsoft-ai-agentic-suite`  
**Target Role Alignment:** Microsoft AI & Agentic Solution Architect (AB-100 / AI-102 / PL-600)  
**Architecture Paradigm:** 4-Layer SDD Lifecycle (`Constitution` -> `REQ-IDs` -> `Contract-First Schemas` -> `4-Gate Verification & Traceability Matrix`)

---

## 1. Architectural Constitution (Non-Negotiable Invariants)

1. **INV-01 (Deterministic Hybrid Routing — Copilot Studio vs. Microsoft Foundry)**:
   - Low-complexity, single-turn FAQ, Teams Adaptive Card UX, and standard Power Platform connector workflows **MUST** stay in **Copilot Studio** (`LOW_CODE_COPILOT`).
   - Complex multi-step reasoning, multi-document synthesis, custom Python/C# tool orchestration, or strict latency/cost token budgets **MUST** route via **Azure API Management (APIM)** with **Entra ID On-Behalf-Of (OBO)** tokens to **Microsoft Foundry Agent Service** (`PRO_CODE_FOUNDRY` or `HYBRID_HANDOFF`).
2. **INV-02 (Zero-Trust Pre-Retrieval Security Trimming & Purview Governance)**:
   - No RAG retrieval query against **Azure AI Search** or **Microsoft Fabric OneLake** may execute without pre-filtering candidate chunks by the caller's verified **Entra ID Group Object IDs** (`acl_groups`) and **Purview Sensitivity Clearance** (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `HIGHLY_CONFIDENTIAL_MA`). Post-retrieval LLM filtering is strictly forbidden.
3. **INV-03 (Cryptographic Human-in-the-Loop Gate & Immutable Dataverse Audit)**:
   - No `LIVE_SPEND` or consequential ERP mutation (`PO > $10,000`, `Dynamics 365 Credit Memo > $5,000`, `Vendor Bank Account Activation`) may execute without a verified **Entra ID Human Approval Token (`approval_jwt` / `signature_hash`)** captured via a **Power Automate / Teams Adaptive Card** interrupt and persisted to an immutable **Dataverse Audit Trail**.
4. **INV-04 (Azure AI Content Safety & Prompt Shield Defense)**:
   - All user inputs and untrusted external documents (e.g., uploaded vendor PDFs) **MUST** pass through **Azure AI Content Safety Prompt Shields** (User Prompt Attack + Indirect Document Attack detection) before any tool invocation.
5. **INV-05 (Resilient Enterprise Integration & Observability)**:
   - Every mutating tool invocation must use a deterministic **SHA-256 Idempotency Key** (`sha256(tenant_id:workflow_id:tool_name:canonical_args)`), retry transient `503 Service Unavailable` / `429 Too Many Requests` errors via exponential backoff, route unrecoverable payloads to an **Azure Service Bus Dead-Letter Queue (DLQ)**, and emit **OpenTelemetry GenAI (`gen_ai.*`)** spans to **Azure Monitor / Application Insights**.
6. **INV-06 (Power Platform Managed Environment DLP & Zero-Exfiltration Governance)**:
   - Any Copilot Studio agent or Power Automate flow combining a `Business` data connector (`Dataverse`, `SharePoint`, `Dynamics365`, `AzureAISearch`) with a `Non-Business` or `Blocked` connector (`CustomUnauthenticatedHttp`, `PersonalDropbox`, `Telegram`) **MUST** be blocked at design/deployment time by the Power Platform DLP Policy Evaluator before ALM solution export.
7. **INV-07 (Sovereign Data Residency & FinOps PTU Economics)**:
   - Production workloads operating under **UK GDPR (`uksouth`)** or **EU Data Boundary (`germanywestcentral`)** must disallow cross-geo `Global Standard` endpoints when `strict_data_residency=True` and deterministically calculate the exact token-throughput crossover threshold between **Azure OpenAI Pay-As-You-Go (PAYG)** and **Provisioned Throughput Units (PTU)**.
8. **INV-08 (Multi-Tier Agent Memory & Episodic Tenant Isolation)**:
   - Agent memory must maintain strict tier separation: (1) ephemeral Working Memory per session thread, (2) long-term Episodic Memory in **Azure Cosmos DB NoSQL** partitioned by `tenant_id`, and (3) Semantic Entity Grounding. Distillation of human review feedback must produce deterministic, immutable behavioral rules.
9. **INV-09 (Full-Stack Observability & KQL Cost Attribution)**:
   - Every graph execution, node transition, and tool call must emit structured **OpenTelemetry GenAI** (`gen_ai.*`) spans with department cost-center attribution, queryable via Azure Log Analytics Kusto Query Language (KQL) without data loss.
10. **INV-10 (STRIDE Threat Modeling & Microsoft AI Red Team Robustness)**:
    - Mutating agent pathways must be audited against the **OWASP Top 10 for LLMs** and **Microsoft AI Red Team** attack vectors. The system must generate formal, reproducible STRIDE threat assessments with 0% unauthenticated privilege escalation.
11. **INV-11 (Model Context Protocol [MCP] Wire Integrity)**:
    - Exposed agent capabilities must comply with the **Model Context Protocol (JSON-RPC 2.0)** spec, declaring tool sensitivity tiers (`READ_ONLY`, `DRAFT_MUTATION`, `LIVE_SPEND`), input/output JSON schemas, and structured error reporting.

---

## 2. Requirement Identifiers (`REQ-XX`)

| Requirement ID | Pillar / Module | Capability Specification | Architect Assessment Alignment |
| :--- | :--- | :--- | :--- |
| **`REQ-ARCH-01`** | Pillar 1: Hybrid Copilot + Foundry | Deterministic architectural router & scoring engine evaluating complexity, connectors, governance, licensing (`$200/25k messages` vs. Foundry PTU/PAYG), and OBO identity propagation. | **Q2:** Copilot Studio vs. Microsoft Foundry decision matrix |
| **`REQ-HARN-01`** | Pillar 1: Agent Harness & Safety | Tool sensitivity classification (`READ_ONLY`, `DRAFT_MUTATION`, `LIVE_SPEND`), Azure AI Content Safety Prompt Shields (direct + indirect XPIA), and SHA-256 idempotency. | **Q4:** Human approval, auditability & guardrails |
| **`REQ-HITL-01`** | Pillar 1: Power Automate + Dataverse | Stateful workflow checkpointing (`awaiting_human_approval`) when PO > `$10,000`, Adaptive Card payload generation, Entra ID cryptographic sign-off, and immutable Dataverse audit log. | **Q4:** Human approval, auditability & guardrails |
| **`REQ-RAG-01`** | Pillar 2: Zero-Trust Security RAG | Pre-retrieval Entra ID ACL security trimming (`search.in(acl_groups, ...)`) + Microsoft Purview sensitivity label enforcement (`HIGHLY_CONFIDENTIAL_MA`) prior to Hybrid RRF scoring. | **Q3:** Enterprise RAG with strict security boundaries |
| **`REQ-RAG-02`** | Pillar 2: Hybrid Search + Fabric SQL | Reciprocal Rank Fusion ($k=60$) combining BM25 lexical + dense vector similarity with structured **Microsoft Fabric OneLake / Warehouse** quantitative query routing. | **Q3:** Enterprise RAG + **Q5:** Architecture trade-offs |
| **`REQ-FIN-01`** | Pillar 2: APIM Semantic Cache & FinOps | Azure API Management (APIM) semantic vector cache (`similarity >= 0.92`) with tenant security-scope isolation (`tenant_id + acl_signature`) reducing token cost and p95 latency. | **Q5:** Cost, performance, security & delivery trade-offs |
| **`REQ-ERP-01`** | Pillar 3: Multi-Agent Supply Chain Hub | Microsoft Foundry Supervisor + specialized sub-agents (`TriageAgent`, `FabricInventoryAgent`, `PolicyComplianceAgent`, `Dynamics365ErpAgent`) resolving order exceptions end-to-end. | **Q1:** End-to-end Microsoft AI solution from discovery to prod |
| **`REQ-INT-01`** | Pillar 3: Service Bus & Self-Healing | Asynchronous **Azure Service Bus** envelope dispatch, automatic exponential backoff on `503` ERP/Logic App faults, Dead-Letter Queue (DLQ) fallback, and **OpenTelemetry GenAI** tracing. | **Q1 & Q4:** Production resilience, observability & escalation |
| **`REQ-GOV-01`** | Pillar 4: Power Platform DLP & ALM | Managed Environment DLP connector classification (`Business` vs. `Non-Business` vs. `Blocked`), cross-boundary data exfiltration blocker, and Dataverse Managed Solution (`solution.xml`) ALM generator. | **Preferred:** Advanced Power Platform governance & ALM |
| **`REQ-M365-01`** | Pillar 4: M365 Copilot Extensibility | Schema-valid **Microsoft 365 Copilot Declarative Agent (`v1.2`)**, API Plugin (`ai-plugin.json`), OpenAPI 3.1 spec, and `EntraOnBehalfOf` SSO manifest generator. | **Preferred:** Microsoft 365 Copilot & declarative agents |
| **`REQ-FIN-02`** | Pillar 4: FinOps PTU vs. PAYG & Residency | Interactive **Azure FinOps & Sovereignty Calculator** computing Copilot Studio vs. Foundry costs, **PTU vs. Pay-As-You-Go** crossover math, and UK/EU/US data residency compliance. | **Core:** Cost, latency, scale & data residency selection |
| **`REQ-MEM-01`** | Pillar 5: Multi-Tier Agent Memory | Working, Episodic (Cosmos DB NoSQL), and Semantic Entity memory tiers with semantic similarity recall and automated feedback distillation into permanent behavioral rules. | **Core:** Agent memory, state management & continuous improvement |
| **`REQ-OBS-01`** | Pillar 6: Observability & KQL Studio | Real-time OpenTelemetry GenAI span event stream (SSE), cost center attribution, and interactive Azure Log Analytics KQL Query Studio with production queries. | **Core:** Observability, diagnostics & FinOps tracking |
| **`REQ-SEC-01`** | Pillar 7: AI Red Team & STRIDE Engine | Automated Microsoft AI Red Team adversarial testing (OWASP LLM01-10, XPIA, jailbreaks, tool manipulation) and formal STRIDE threat modeling report generator. | **Core:** Responsible AI, security & threat defense |
| **`REQ-MCP-01`** | Pillar 8: Model Context Protocol Server | FastMCP / JSON-RPC 2.0 server surface with stdio & SSE transports, permission-tiered tool discovery, and schema validation. | **Preferred:** Open protocol interoperability & tool-calling |
| **`REQ-EVAL-01`** | Cross-Cutting Verification | 4-Gate Automated Evaluation Suite extended to verify Memory recall, KQL telemetry integrity, Red Team defense, and MCP protocol compliance. | **All:** Demonstrated production quality & assessment readiness |

---

## 3. Traceability Matrix (Spec $\rightarrow$ Code $\rightarrow$ Automated Verification)

| REQ ID | Primary Implementation Module | Automated Test / Eval Gate |
| :--- | :--- | :--- |
| `REQ-ARCH-01` | `src/pillars/p1_hybrid_procurement.py` | `tests/test_suite.py::test_req_arch_01_copilot_vs_foundry_router` |
| `REQ-HARN-01` | `src/core/harness.py` | `tests/test_suite.py::test_req_harn_01_prompt_shield_and_idempotency` |
| `REQ-HITL-01` | `src/pillars/p1_hybrid_procurement.py` | `tests/test_suite.py::test_req_hitl_01_adaptive_card_approval_and_audit` |
| `REQ-RAG-01` | `src/pillars/p2_zero_trust_rag.py` | `tests/test_suite.py::test_req_rag_01_entra_acl_and_purview_trimming` |
| `REQ-RAG-02` | `src/pillars/p2_zero_trust_rag.py` | `tests/test_suite.py::test_req_rag_02_hybrid_rrf_and_fabric_routing` |
| `REQ-FIN-01` | `src/pillars/p2_zero_trust_rag.py` | `tests/test_suite.py::test_req_fin_01_apim_semantic_cache_acl_isolated` |
| `REQ-ERP-01` | `src/pillars/p3_multi_agent_erp.py` | `tests/test_suite.py::test_req_erp_01_multi_agent_exception_resolution` |
| `REQ-INT-01` | `src/pillars/p3_multi_agent_erp.py` | `tests/test_suite.py::test_req_int_01_service_bus_retry_and_dlq` |
| `REQ-GOV-01` | `src/pillars/p4_governance_m365_finops.py` | `tests/test_suite.py::test_req_gov_01_power_platform_dlp_and_alm` |
| `REQ-M365-01` | `src/pillars/p4_governance_m365_finops.py` | `tests/test_suite.py::test_req_m365_01_declarative_agent_manifest` |
| `REQ-FIN-02` | `src/pillars/p4_governance_m365_finops.py` | `tests/test_suite.py::test_req_fin_02_ptu_vs_payg_and_sovereignty` |
| `REQ-MEM-01` | `src/pillars/p5_agent_memory.py` | `tests/test_suite.py::test_req_mem_01_multi_tier_memory_and_distillation` |
| `REQ-OBS-01` | `src/pillars/p6_observability_kql.py` | `tests/test_suite.py::test_req_obs_01_kql_studio_and_telemetry` |
| `REQ-SEC-01` | `src/pillars/p7_security_redteam.py` | `tests/test_suite.py::test_req_sec_01_red_team_and_stride_matrix` |
| `REQ-MCP-01` | `src/pillars/p8_mcp_server.py` | `tests/test_suite.py::test_req_mcp_01_mcp_server_protocol_and_dispatch` |
| `REQ-EVAL-01` | `src/evals/runner.py` | `tests/test_suite.py::test_req_eval_01_four_gate_evaluation_pass` |
