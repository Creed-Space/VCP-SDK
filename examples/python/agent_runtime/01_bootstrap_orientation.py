"""Answer the driver's-seat orientation questions in one bounded bootstrap."""

import asyncio

from vcp.agent import AgentRuntime


async def main() -> None:
    async with AgentRuntime.connect() as runtime:
        result = await runtime.bootstrap("Determine whether the local bundle is trustworthy")
        if not result.is_ready():
            print(result.explain())
            return
        situation = result.require_value()
        print(situation.explain())


if __name__ == "__main__":
    asyncio.run(main())
