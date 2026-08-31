"""Read resource forecasts and assurance axes before choosing an option."""

import asyncio

from vcp.agent import AgentRuntime


async def main() -> None:
    async with AgentRuntime.connect() as runtime:
        result = await runtime.bootstrap("Choose a resource-efficient local verifier")
        print(result.resources.model_dump(mode="json"))
        print(result.explain()["assurance"])
        situation = result.require_value()
        options = await situation.find_affordances(effect_ceiling="pure_local")
        print(options.resources.model_dump(mode="json"))


if __name__ == "__main__":
    asyncio.run(main())
