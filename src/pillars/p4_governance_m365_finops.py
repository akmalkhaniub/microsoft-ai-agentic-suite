"""
Pillar 4: Advanced Power Platform Governance (DLP & ALM), Microsoft 365 Copilot Extensibility
(Declarative Agent v1.2 + API Plugin), and Azure FinOps PTU vs. Pay-As-You-Go Sovereignty Engine.
Directly satisfies:
- REQ-GOV-01: Managed Environment DLP Policy Evaluator blocking Business + Non-Business/Blocked
  connector combinations and generating Dataverse Managed Solution (`solution.xml`) ALM artifacts.
- REQ-M365-01: Microsoft 365 Copilot Declarative Agent (`declarativeAgent.json` v1.2) and API Plugin
  (`ai-plugin.json`) with `EntraOnBehalfOf` SSO and Adaptive Card response templates.
- REQ-FIN-02: Deterministic Azure FinOps & Sovereignty Calculator computing Copilot Studio message pack
  economics, Azure OpenAI PTU vs. Pay-As-You-Go crossover thresholds, APIM cache savings, and
  UK GDPR / EU Data Boundary residency compliance.
"""

from __future__ import annotations

import math
from typing import Any

from src.core.schemas import (
    ConnectorClassificationDetail,
    ConnectorDataGroup,
    FinOpsSizingRequest,
    FinOpsSizingResponse,
    PowerPlatformGovernanceRequest,
    PowerPlatformGovernanceResponse,
)

# Canonical Power Platform Managed Environment DLP Connector Catalog
_CONNECTOR_CATALOG: dict[str, tuple[str, ConnectorDataGroup]] = {
    "shared_commondataserviceforapps": ("Microsoft Dataverse", ConnectorDataGroup.BUSINESS),
    "shared_sharepointonline": ("SharePoint Online", ConnectorDataGroup.BUSINESS),
    "shared_teams": ("Microsoft Teams", ConnectorDataGroup.BUSINESS),
    "shared_azuread": ("Microsoft Entra ID", ConnectorDataGroup.BUSINESS),
    "shared_dynamicscrmonline": ("Dynamics 365 Supply Chain & Finance", ConnectorDataGroup.BUSINESS),
    "shared_apim_foundry_custom": ("Azure APIM -> Microsoft Foundry Custom Connector", ConnectorDataGroup.BUSINESS),
    "shared_approvals": ("Power Automate Approvals", ConnectorDataGroup.BUSINESS),
    "shared_gmail": ("Personal Gmail (Consumer)", ConnectorDataGroup.NON_BUSINESS),
    "shared_dropbox": ("Personal Dropbox", ConnectorDataGroup.NON_BUSINESS),
    "shared_twitter": ("X / Social Media Public Connector", ConnectorDataGroup.NON_BUSINESS),
    "shared_http_unauthenticated": ("Unauthenticated Raw HTTP Webhook", ConnectorDataGroup.BLOCKED),
    "shared_telegram": ("Telegram External Bot API", ConnectorDataGroup.BLOCKED),
}


class PowerPlatformGovernanceAndFinOpsEngine:
    """
    Evaluates Power Platform Managed Environment DLP rules, generates Dataverse ALM solution manifests,
    synthesizes Microsoft 365 Copilot Declarative Agent packages, and computes Azure FinOps PTU economics.
    """

    @staticmethod
    def evaluate_governance_and_m365(
        req: PowerPlatformGovernanceRequest,
    ) -> PowerPlatformGovernanceResponse:
        """
        Evaluate Power Platform DLP compliance (`INV-06` / `REQ-GOV-01`) and generate
        ALM Managed Solution XML + Microsoft 365 Copilot Declarative Agent (`REQ-M365-01`).
        """
        classifications: list[ConnectorClassificationDetail] = []
        business_conns: list[str] = []
        non_business_conns: list[str] = []
        blocked_conns: list[str] = []

        for conn_id in req.connectors_used:
            display_name, group = _CONNECTOR_CATALOG.get(
                conn_id,
                (f"Unregistered Custom Connector ({conn_id})", ConnectorDataGroup.NON_BUSINESS),
            )
            classifications.append(
                ConnectorClassificationDetail(
                    connector_id=conn_id,
                    display_name=display_name,
                    dlp_group=group,
                )
            )
            if group == ConnectorDataGroup.BUSINESS:
                business_conns.append(display_name)
            elif group == ConnectorDataGroup.NON_BUSINESS:
                non_business_conns.append(display_name)
            else:
                blocked_conns.append(display_name)

        violations: list[str] = []
        if blocked_conns:
            violations.append(
                f"DLP_BLOCKED_CONNECTOR: Solution includes prohibited connectors: {', '.join(blocked_conns)}."
            )
        if business_conns and non_business_conns:
            violations.append(
                "DLP_CROSS_BOUNDARY_EXFILTRATION_RISK: Cannot combine Business connectors "
                f"({', '.join(business_conns)}) with Non-Business connectors ({', '.join(non_business_conns)}) "
                "in the same Copilot Studio agent or Power Automate flow."
            )

        is_managed = req.target_environment_tier in ("TEST_UAT", "PROD_MANAGED")
        managed_flag = "1" if is_managed else "0"

        solution_xml = (
            f'<ImportExportXml version="9.2.24104.192">\n'
            f'  <SolutionManifest>\n'
            f'    <UniqueName>{req.solution_unique_name}</UniqueName>\n'
            f'    <Version>{req.solution_version}</Version>\n'
            f'    <Managed>{managed_flag}</Managed>\n'
            f'    <Publisher>\n'
            f'      <UniqueName>ContosoEnterpriseAI</UniqueName>\n'
            f'      <CustomizationPrefix>msftai</CustomizationPrefix>\n'
            f'    </Publisher>\n'
            f'  </SolutionManifest>\n'
            f'</ImportExportXml>'
        )

        env_vars = {
            "msftai_FoundryApimGatewayUrl": "https://apim-msft-agentic-prod.azure-api.net/foundry/v1",
            "msftai_AzureAISearchIndexName": "idx-enterprise-zero-trust-rag-v2",
            "msftai_HitlApprovalThresholdUsd": "10000.00",
            "msftai_ServiceBusErpTopic": "sbt-d365-erp-fulfillment",
            "msftai_TargetEnvironmentTier": req.target_environment_tier,
        }

        declarative_manifest: dict[str, Any] | None = None
        plugin_manifest: dict[str, Any] | None = None

        if req.enable_m365_copilot_declarative_agent:
            declarative_manifest = {
                "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.2/schema.json",
                "version": "v1.2",
                "name": "Enterprise Operations & Supply Chain Copilot",
                "description": (
                    "Declarative Agent extending Microsoft 365 Copilot with Zero-Trust Purview RAG, "
                    "Foundry Contract Risk Synthesis, and Dynamics 365 Supply Chain Resolution."
                ),
                "instructions": (
                    "Always enforce pre-retrieval Entra ID ACL trimming before citing SharePoint or Fabric "
                    "documents. Require a Teams Adaptive Card human approval signature for any PO > $10,000."
                ),
                "capabilities": [
                    {"name": "OneDriveAndSharePoint", "items_by_url": [{"url": "https://contoso.sharepoint.com/sites/EnterpriseGovernance"}]},
                    {"name": "GraphConnectors", "connections": [{"connection_id": "fabriconelakegold"}]},
                ],
                "actions": [
                    {"id": "foundryEnterprisePlugin", "file": "ai-plugin.json"},
                ],
            }
            plugin_manifest = {
                "$schema": "https://developer.microsoft.com/json-schemas/copilot/plugin/v2.1/schema.json",
                "schema_version": "v2.1",
                "name_for_human": "Microsoft Foundry & Dynamics 365 ERP Bridge",
                "namespace": "contoso_foundry_erp",
                "description_for_model": (
                    "Invoke Microsoft Foundry multi-agent workflows for PO onboarding, ACL-trimmed RAG, "
                    "and Dynamics 365 supply chain exception resolution."
                ),
                "auth": {
                    "type": "OAuthPluginVault",
                    "reference_id": "entra-obo-apim-token-exchange-v1",
                },
                "runtimes": [
                    {
                        "type": "OpenApi",
                        "auth": {"type": "EntraOnBehalfOf"},
                        "spec": {"url": "openapi-foundry-gateway.json"},
                        "run_for_functions": [
                            "runProcurementWorkflow",
                            "queryZeroTrustRag",
                            "resolveSupplyChainException",
                        ],
                    }
                ],
            }

        return PowerPlatformGovernanceResponse(
            solution_unique_name=req.solution_unique_name,
            is_managed_solution=is_managed,
            dlp_compliant=len(violations) == 0,
            connector_classifications=classifications,
            dlp_violations=violations,
            alm_solution_xml_preview=solution_xml,
            alm_environment_variables=env_vars,
            m365_declarative_agent_manifest=declarative_manifest,
            m365_api_plugin_manifest=plugin_manifest,
        )

    @staticmethod
    def calculate_finops_and_sovereignty(req: FinOpsSizingRequest) -> FinOpsSizingResponse:
        """
        Calculate Copilot Studio licensing, Azure OpenAI PTU vs. Pay-As-You-Go crossover economics,
        APIM semantic cache savings, and EU/UK GDPR data residency compliance (`REQ-FIN-02`).
        """
        total_turns = (
            req.monthly_active_users
            * req.avg_conversations_per_user_per_month
            * req.avg_turns_per_conversation
        )
        gross_input_tokens = total_turns * req.avg_input_tokens_per_turn
        gross_output_tokens = total_turns * req.avg_output_tokens_per_turn

        cache_multiplier = 1.0 - req.apim_semantic_cache_hit_ratio
        net_input_tokens = int(gross_input_tokens * cache_multiplier)
        net_output_tokens = int(gross_output_tokens * cache_multiplier)
        net_total_tokens = net_input_tokens + net_output_tokens

        # Estimate Peak Tokens-Per-Minute (TPM) assuming 22 business days, 8 active hours/day, 3.2x peak-to-mean ratio
        active_minutes_per_month = 22 * 8 * 60  # 10,560 active business minutes
        avg_tpm = ( net_input_tokens + (net_output_tokens * 3) ) / active_minutes_per_month
        peak_tpm = int(math.ceil(avg_tpm * 3.2))

        # 1. Copilot Studio Licensing ($200 per 25,000 messages/month tenant pack)
        # Generative answers in Copilot Studio consume 2 messages per turn
        total_copilot_messages = total_turns * 2
        packs_required = max(1, math.ceil(total_copilot_messages / 25_000))
        copilot_monthly_cost = round(packs_required * 200.0, 2)

        # 2. Azure OpenAI GPT-4o Pay-As-You-Go Pricing ($2.50 / 1M input, $10.00 / 1M output)
        uncached_payg_cost = (
            (gross_input_tokens / 1_000_000.0) * 2.50
            + (gross_output_tokens / 1_000_000.0) * 10.00
        )
        cached_payg_cost = round(
            (net_input_tokens / 1_000_000.0) * 2.50
            + (net_output_tokens / 1_000_000.0) * 10.00,
            2,
        )
        apim_savings_usd = round(uncached_payg_cost - cached_payg_cost, 2)

        # 3. Azure OpenAI Provisioned Throughput Units (PTU) Sizing
        # Minimum 15 PTU base block (~37,500 TPM capacity for GPT-4o, ~$2,970/month with 1-year reservation)
        ptu_blocks = max(1, math.ceil(peak_tpm / 37_500.0))
        recommended_ptus = ptu_blocks * 15
        ptu_monthly_cost = round(ptu_blocks * 2970.0, 2)

        if cached_payg_cost >= ptu_monthly_cost or peak_tpm >= 30_000:
            recommended_model = "PROVISIONED_THROUGHPUT_PTU"
            rationale = (
                f"Peak workload ({peak_tpm:,} TPM) and net PAYG spend (${cached_payg_cost:,.2f}/mo) justify "
                f"{recommended_ptus} PTUs (${ptu_monthly_cost:,.2f}/mo) for deterministic p99 latency SLAs "
                "and zero HTTP 429 token throttling during business hours."
            )
        else:
            recommended_model = "PAY_AS_YOU_GO"
            rationale = (
                f"Net PAYG spend (${cached_payg_cost:,.2f}/mo after {int(req.apim_semantic_cache_hit_ratio*100)}% APIM cache) "
                f"is below the 15-PTU reservation floor (${ptu_monthly_cost:,.2f}/mo). Use DataZone/Regional PAYG "
                "with APIM token-bucket burst protection."
            )

        # 4. Data Residency & Sovereignty Check (`INV-07`)
        sovereignty_ok = True
        warning: str | None = None
        if req.strict_gdpr_data_residency and req.deployment_sku_preference == "GLOBAL_STANDARD":
            sovereignty_ok = False
            warning = (
                f"SOVEREIGNTY_VIOLATION: 'GLOBAL_STANDARD' routes inference traffic across global geographies, "
                f"violating strict in-region data residency for '{req.target_azure_region}'. "
                "Switch to 'REGIONAL_PTU' or 'DATA_ZONE_STANDARD' (EU/US boundary)."
            )

        region_labels = {
            "uksouth": "UK South (London) — UK GDPR & FCA Sovereign Boundary",
            "germanywestcentral": "Germany West Central (Frankfurt) — EU Data Boundary & BaFin Compliant",
            "swedencentral": "Sweden Central (Gävle) — EU Data Boundary & 100% Carbon-Free AI Hub",
            "eastus2": "US East 2 (Virginia) — North America Commercial & SOC2 Boundary",
        }

        return FinOpsSizingResponse(
            total_monthly_turns=total_turns,
            gross_monthly_input_tokens=gross_input_tokens,
            gross_monthly_output_tokens=gross_output_tokens,
            net_billable_tokens_after_apim_cache=net_total_tokens,
            peak_tokens_per_minute_tpm=peak_tpm,
            copilot_studio_message_packs_required=packs_required,
            copilot_studio_monthly_cost_usd=copilot_monthly_cost,
            foundry_payg_monthly_cost_usd=cached_payg_cost,
            foundry_ptu_recommended_units=recommended_ptus,
            foundry_ptu_monthly_cost_usd=ptu_monthly_cost,
            apim_cache_monthly_savings_usd=apim_savings_usd,
            recommended_foundry_billing_model=recommended_model,
            ptu_vs_payg_crossover_rationale=rationale,
            sovereignty_compliant=sovereignty_ok,
            sovereignty_violation_warning=warning,
            regional_architecture_summary=region_labels[req.target_azure_region],
        )
