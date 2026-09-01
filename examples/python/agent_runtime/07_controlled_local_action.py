"""Complete reversible local action with explicit preflight and proof."""

import asyncio

from vcp.agent import AgentRuntime


async def main() -> None:
    async with AgentRuntime.connect(profile="controlled@0.1.0") as runtime:
        situation = (
            await runtime.bootstrap("Set the release channel and prove it")
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
        arguments = {"key": "release", "value": "candidate"}
        intent = (
            await runtime.preflight(governed_run, write, arguments)
        ).require_value()
        receipt = (await runtime.perform(intent, arguments)).require_value()
        proof = (await runtime.prove(governed_run)).require_value()
        print(receipt.effect_status.value, proof.mandatory_complete)


if __name__ == "__main__":
    asyncio.run(main())
