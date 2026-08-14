"""Encode and decode Enneagram context using VCP/A."""
from __future__ import annotations

from vcp.adaptation.context import ContextEncoder, Dimension, VCPContext

# -- 1. Build a context using the ContextEncoder helper. --
encoder = ContextEncoder()
ctx = encoder.encode(
    time="morning",
    space="home",
    company=["children", "family"],
    emotional_tone=("happy", 4),
)

# -- 2. Encode to wire format (emoji-based, pipe-separated). --
wire = ctx.encode()
print(f"Wire format: {wire}")  # includes U+2016 before the personal-state band

# -- 3. Decode back from wire format. --
decoded = VCPContext.decode(wire)
assert decoded == ctx, "VCP context wire encoding must round-trip losslessly"
print(f"Roundtrip:   {decoded.encode()}")

# -- 4. Inspect individual dimensions. --
print(f"Has TIME?    {ctx.has(Dimension.TIME)}")
print(f"TIME values: {ctx.get(Dimension.TIME)}")

# -- 5. Export to JSON for interop. --
import json

print(f"JSON: {json.dumps(ctx.to_json(), ensure_ascii=False)}")
