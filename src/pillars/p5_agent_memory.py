"""Pillar 5: Multi-Tier Agent Memory & Cosmos DB Episodic Knowledge Store (`REQ-MEM-01`).

Architectural Invariant `INV-08`:
Agent memory must maintain strict tier separation:
1. Working Memory: Ephemeral in-memory context per active session thread.
2. Episodic Memory: Azure Cosmos DB NoSQL persistent records partitioned by tenant_id.
3. Semantic Distillation: Continuous feedback loop turning human approvals/rejections
   into permanent, deterministic behavioral governance rules.
"""

from __future__ import annotations

import math
import time
import uuid
from typing import Any

from src.core.schemas import (
    EpisodicMemoryRecord,
    HumanFeedbackDistillationRequest,
    HumanFeedbackDistillationResponse,
    MemoryCategory,
    MemoryRecallRequest,
    MemoryRecallResponse,
    utc_now_iso,
)


STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are",
    "was", "were", "what", "how", "why", "who", "all", "any", "this", "that", "with",
}


def _compute_pseudo_embedding(text: str, dim: int = 32) -> list[float]:
    """Generates a normalized semantic vector filtering stop words and using deterministic slotting."""
    tokens = [w.strip(".,;:?!'\"()[]{}") for w in text.lower().split()]
    meaningful = [w for w in tokens if w and w not in STOP_WORDS]
    if not meaningful:
        meaningful = tokens or ["default"]
    vector = [0.0] * dim
    for token in meaningful:
        slot = sum(ord(c) for c in token) % dim
        vector[slot] += 1.0
    # Normalize vector to unit length
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [round(v / norm, 4) for v in vector]


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculates cosine similarity between two unit vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    return max(0.0, min(1.0, dot_product))


class EnterpriseAgentMemoryHub:
    """Multi-tier memory orchestrator supporting Working Memory and Cosmos DB Episodic Knowledge."""

    def __init__(self) -> None:
        # In-memory working cache: session_id -> state dict
        self._working_memory: dict[str, dict[str, Any]] = {}
        # Simulated Cosmos DB NoSQL container: tenant_id -> list of EpisodicMemoryRecord
        self._cosmos_db_container: dict[str, list[EpisodicMemoryRecord]] = {}
        self._seed_default_memories()

    def _seed_default_memories(self) -> None:
        """Seeds standard enterprise episodic memories for Contoso Global."""
        tenant_id = "tenant-contoso-global"
        defaults = [
            EpisodicMemoryRecord(
                memory_id="mem-rule-001",
                tenant_id=tenant_id,
                session_id="session-arch-init",
                user_upn="cfo-governance@contoso.com",
                category=MemoryCategory.PROCUREMENT_RULE,
                summary="Hardware and Cloud subscriptions exceeding $100,000 USD require dual director sign-off and VP FinOps verification.",
                embedding_vector=_compute_pseudo_embedding("Hardware Cloud subscriptions 100000 dual director VP FinOps verification"),
                confidence_score=0.98,
                access_count=14,
                metadata={"source": "Contoso Global Financial Bylaws 2026", "enforced_by": "Pillar 1"},
            ),
            EpisodicMemoryRecord(
                memory_id="mem-rule-002",
                tenant_id=tenant_id,
                session_id="session-arch-init",
                user_upn="vpprocure@contoso.com",
                category=MemoryCategory.PROCUREMENT_RULE,
                summary="AI server racks and GPU compute clusters require a minimum SOC2 Type II and ISO 27001 vendor attestation before PO generation.",
                embedding_vector=_compute_pseudo_embedding("AI server racks GPU compute clusters SOC2 Type II ISO 27001 vendor attestation PO"),
                confidence_score=0.96,
                access_count=8,
                metadata={"source": "SecOps Procurement Standard", "enforced_by": "Pillar 1"},
            ),
            EpisodicMemoryRecord(
                memory_id="mem-override-003",
                tenant_id=tenant_id,
                session_id="session-arch-init",
                user_upn="operations-director@contoso.com",
                category=MemoryCategory.SUPPLY_CHAIN_OVERRIDE,
                summary="For SKU-TURBINE-VALVE-V9 disruptions, bypass Frankfurt hub and fulfill from Sheffield Advanced Logistics to avoid customs delays.",
                embedding_vector=_compute_pseudo_embedding("SKU-TURBINE-VALVE-V9 disruptions bypass Frankfurt fulfill Sheffield Advanced Logistics"),
                confidence_score=0.94,
                access_count=5,
                metadata={"source": "Executive Operations Resolution 2026-Q1", "enforced_by": "Pillar 3"},
            ),
            EpisodicMemoryRecord(
                memory_id="mem-sec-004",
                tenant_id=tenant_id,
                session_id="session-arch-init",
                user_upn="ciso@contoso.com",
                category=MemoryCategory.SECURITY_EXCEPTION,
                summary="M365 Copilot Declarative Agents must strictly enforce Purview Confidential labels and prevent third-party HTTP egress.",
                embedding_vector=_compute_pseudo_embedding("M365 Copilot Declarative Agents enforce Purview Confidential labels prevent third party HTTP egress"),
                confidence_score=0.99,
                access_count=22,
                metadata={"source": "CISO Policy Directive 404", "enforced_by": "Pillar 4"},
            ),
        ]
        self._cosmos_db_container[tenant_id] = defaults

    def get_working_memory(self, session_id: str) -> dict[str, Any]:
        """Retrieves active ephemeral working memory for an interactive session."""
        return self._working_memory.get(session_id, {
            "session_id": session_id,
            "turn_count": 0,
            "active_intent": "IDLE",
            "scratchpad": {},
            "last_updated": utc_now_iso(),
        })

    def update_working_memory(self, session_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Updates ephemeral session memory."""
        current = self.get_working_memory(session_id)
        current["turn_count"] = current.get("turn_count", 0) + 1
        current.setdefault("scratchpad", {}).update(updates.get("scratchpad", {}))
        for key, val in updates.items():
            if key != "scratchpad":
                current[key] = val
        current["last_updated"] = utc_now_iso()
        self._working_memory[session_id] = current
        return current

    def recall_episodic_memory(self, request: MemoryRecallRequest) -> MemoryRecallResponse:
        """Queries Azure Cosmos DB NoSQL partitioned container using semantic cosine similarity (`REQ-MEM-01`)."""
        start_time = time.perf_counter()
        tenant_memories = self._cosmos_db_container.get(request.tenant_id, [])

        query_vec = _compute_pseudo_embedding(request.query)
        query_words = set(w.strip(".,;:?!'\"()[]{}").lower() for w in request.query.split()) - STOP_WORDS
        scored: list[tuple[float, EpisodicMemoryRecord]] = []

        for record in tenant_memories:
            if request.category and record.category != request.category:
                continue

            # Compute semantic cosine similarity & lexical keyword overlap
            sim = _cosine_similarity(query_vec, record.embedding_vector)
            summary_words = set(w.strip(".,;:?!'\"()[]{}").lower() for w in record.summary.split()) - STOP_WORDS
            overlap = len(query_words & summary_words) / (len(query_words) or 1)
            combined_score = round(0.5 * sim + 0.3 * overlap + 0.2 * record.confidence_score, 4)

            if combined_score >= request.min_confidence or sim >= 0.3 or overlap >= 0.15:
                # Update access count & timestamp in-place
                record.access_count += 1
                record.last_accessed_at = utc_now_iso()
                scored.append((combined_score, record))

        # Sort descending by score
        scored.sort(key=lambda x: x[0], reverse=True)
        recalled = [item[1] for item in scored[: request.top_k]]

        working_state = self.get_working_memory(request.session_id)
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return MemoryRecallResponse(
            tenant_id=request.tenant_id,
            session_id=request.session_id,
            query=request.query,
            working_memory_state=working_state,
            recalled_episodic_memories=recalled,
            cosine_similarity_threshold=request.min_confidence,
            total_memories_found=len(recalled),
            latency_ms=latency_ms,
        )

    def distill_feedback(self, request: HumanFeedbackDistillationRequest) -> HumanFeedbackDistillationResponse:
        """Synthesizes human approval/rejection feedback into an immutable rule and stores in Cosmos DB (`INV-08`)."""
        rule_id = f"rule-{uuid.uuid4().hex[:8]}"

        # Deterministic rule synthesis
        if request.decision == "REJECTED":
            distilled_text = (
                f"STRICT PROHIBITION: When evaluating '{request.original_action}', "
                f"enforce human rejection rationale: '{request.human_feedback}'. Do not execute without explicit override."
            )
        elif request.decision == "MODIFIED":
            distilled_text = (
                f"MODIFIED BEHAVIORAL RULE: When processing '{request.original_action}', "
                f"apply adjustment directive: '{request.human_feedback}'."
            )
        else:
            distilled_text = (
                f"APPROVED POLICY PATTERN: Action '{request.original_action}' confirmed optimal "
                f"by reviewer {request.user_upn}. Feedback notes: '{request.human_feedback}'."
            )

        new_record = EpisodicMemoryRecord(
            memory_id=rule_id,
            tenant_id=request.tenant_id,
            session_id=request.session_id,
            user_upn=request.user_upn,
            category=request.target_category,
            summary=distilled_text,
            embedding_vector=_compute_pseudo_embedding(
                f"{request.original_action} {request.human_feedback} {request.decision}"
            ),
            confidence_score=0.99,
            access_count=1,
            metadata={
                "distilled_from": request.decision,
                "author_upn": request.user_upn,
                "session_id": request.session_id,
                "cosmos_partition_key": request.tenant_id,
            },
        )

        # Store in Cosmos DB partitioned list
        if request.tenant_id not in self._cosmos_db_container:
            self._cosmos_db_container[request.tenant_id] = []
        self._cosmos_db_container[request.tenant_id].append(new_record)

        return HumanFeedbackDistillationResponse(
            rule_id=rule_id,
            tenant_id=request.tenant_id,
            distilled_rule=distilled_text,
            target_category=request.target_category,
            saved_to_cosmos_db=True,
            impact_scope=f"Tenant-wide governance rule active across all agent sessions in '{request.tenant_id}'.",
        )


# Global singleton instance
memory_hub = EnterpriseAgentMemoryHub()
