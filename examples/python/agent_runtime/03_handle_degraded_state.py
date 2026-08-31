"""Treat a missing option as an expected structured state."""

import asyncio

from vcp.agent import AgentRuntime


async def main() -> None:
    async with AgentRuntime.connect() as runtime:
        situation = (await runtime.bootstrap("Find legal filing authority")).require_value()
        result = await situation.find_affordances(
            outcome="submit a legal filing",
            effect_ceiling="pure_local",
        )
        if result.status.value != "ready":
            print(result.explain())
            return
        print(result.require_value())


if __name__ == "__main__":
    asyncio.run(main())
