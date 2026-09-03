"""Candidate-first learning with promotion and attributable retrieval."""

import asyncio

from vcp.agent import AgentRuntime


async def main() -> None:
    async with AgentRuntime.connect(profile="accretive@0.1.0") as runtime:
        situation = (
            await runtime.bootstrap("Set one local preference safely")
        ).require_value()
        affordances = (
            await situation.find_affordances(effect_ceiling="reversible_write")
        ).require_value()
        write = next(
            item
            for item in affordances
            if item.capability_ref.endswith(":local.setting.write")
        )
        governed_run = (await situation.start_run()).require_value()
        arguments = {"key": "mode", "value": "safe"}
        intent = (
            await runtime.preflight(governed_run, write, arguments)
        ).require_value()
        receipt = (await runtime.perform(intent, arguments)).require_value()
        (await runtime.prove(governed_run)).require_value()
        candidate = (
            await runtime.propose_accretion(
                governed_run,
                candidate_kind="procedure",
                content={"steps": ["preflight", "perform", "prove"]},
                scope=("tenant:local-reference", "project:vcp"),
                provenance_refs=receipt.evidence_refs,
            )
        ).require_value()
        promotion = (await runtime.promote(candidate)).require_value()
        influences = (
            await runtime.retrieve_promoted(
                scope=("tenant:local-reference", "project:vcp"),
                decision_or_output_ref="vcp:artifact:run:next-run",
            )
        ).require_value()
        print(promotion.promoted_asset_ref, influences[0].influence_id)


if __name__ == "__main__":
    asyncio.run(main())
