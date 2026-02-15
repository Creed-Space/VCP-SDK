"""Parse a VCP identity token and inspect its components."""
from __future__ import annotations

from vcp.identity import Token

# Parse a fully-qualified VCP/I token string.
token = Token.parse("family.safe.guide@1.2.0")

print(f"Full:      {token.full}")       # family.safe.guide@1.2.0
print(f"Domain:    {token.domain}")      # family
print(f"Approach:  {token.approach}")    # safe
print(f"Role:      {token.role}")        # guide
print(f"Version:   {token.version}")     # 1.2.0
print(f"Canonical: {token.canonical}")   # family.safe.guide
print(f"Depth:     {token.depth}")       # 3
print(f"URI:       {token.to_uri()}")    # creed://creed.space/family.safe.guide@1.2.0

# Tokens are immutable -- derive variants with with_version / with_namespace.
v2 = token.with_version("2.0.0")
print(f"v2:        {v2.full}")           # family.safe.guide@2.0.0

# Glob-style pattern matching.
print(f"Matches family.*.guide? {token.matches_pattern('family.*.guide')}")  # True
