"""Find current options by outcome, effect ceiling, and forecast cost."""

import asyncio

from vcp.agent import AgentRuntime, EffectClass


async def main() -> None:
    async with AgentRuntime.connect() as runtime:
        situation = (
            await runtime.bootstrap("Establish current bundle integrity evidence")
        ).require_value()
        result = await situation.find_affordances(
            evidence_for="bundle integrity",
            effect_ceiling=EffectClass.PURE_LOCAL,
            limit=3,
        )
        for option in result.require_value():
            print(option.summary, option.state.value, option.cost.model_dump(mode="json"))


if __name__ == "__main__":
    asyncio.run(main())
