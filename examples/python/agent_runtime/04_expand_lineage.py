"""Expand an exact descriptor reference without passing raw digest plumbing."""

import asyncio

from vcp.agent import AgentRuntime


async def main() -> None:
    async with AgentRuntime.connect() as runtime:
        situation = (await runtime.bootstrap("Inspect available evidence tools")).require_value()
        options = (await situation.find_affordances(limit=1)).require_value()
        descriptor = await situation.expand(options[0].capability_ref)
        print(descriptor.require_value().model_dump(mode="json"))


if __name__ == "__main__":
    asyncio.run(main())
