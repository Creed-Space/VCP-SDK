"""Deterministic generative checks for parser and security invariants."""

from __future__ import annotations

import ipaddress

from hypothesis import given, settings
from hypothesis import strategies as st

from vcp.identity import Token
from vcp.revocation import _is_private_ip
from vcp.semantics.csm1 import CSM1Code, Persona, Scope

PROPERTY_SETTINGS = settings(
    max_examples=300,
    derandomize=True,
    database=None,
    deadline=None,
)


@st.composite
def csm1_codes(draw: st.DrawFn) -> CSM1Code:
    persona = draw(st.sampled_from(list(Persona)))
    level = draw(st.integers(min_value=0, max_value=5))
    scopes = draw(st.lists(st.sampled_from(list(Scope)), unique=True, max_size=len(Scope)))
    incompatible = (
        (Scope.FAMILY, Scope.ADULT),
        (Scope.VULNERABLE, Scope.ADULT),
        (Scope.HEALTHCARE, Scope.ADULT),
    )
    if any(left in scopes and right in scopes for left, right in incompatible):
        scopes = [scope for scope in scopes if scope is not Scope.ADULT]
    namespace = draw(
        st.one_of(
            st.none(),
            st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=8),
        )
    )
    if persona is Persona.CUSTOM and namespace is None:
        namespace = "CUSTOM"
    version = draw(
        st.one_of(
            st.none(),
            st.sampled_from(["latest", "canary"]),
            st.tuples(*(st.integers(0, 999) for _ in range(3))).map(
                lambda parts: ".".join(str(part) for part in parts)
            ),
        )
    )
    return CSM1Code(
        persona=persona,
        adherence_level=level,
        scopes=scopes,
        namespace=namespace,
        version=version,
    )


@PROPERTY_SETTINGS
@given(csm1_codes())
def test_csm1_encode_parse_is_canonical(code: CSM1Code) -> None:
    encoded = code.encode()
    reparsed = CSM1Code.parse(encoded)
    assert reparsed.encode() == encoded
    assert reparsed.persona is code.persona
    assert reparsed.adherence_level == code.adherence_level
    assert set(reparsed.scopes) == set(code.scopes)
    assert reparsed.namespace == code.namespace
    assert reparsed.version == code.version


@PROPERTY_SETTINGS
@given(st.text(max_size=256))
def test_csm1_arbitrary_text_never_escapes_documented_error(raw: str) -> None:
    try:
        parsed = CSM1Code.parse(raw)
    except ValueError:
        return
    assert CSM1Code.parse(parsed.encode()).encode() == parsed.encode()


@PROPERTY_SETTINGS
@given(st.ip_addresses())
def test_private_ip_classifier_matches_global_address_contract(
    address: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> None:
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        expected_private = not address.ipv4_mapped.is_global
    else:
        expected_private = not address.is_global
    if isinstance(address, ipaddress.IPv6Address):
        packed = address.packed
        expected_private = expected_private or (
            packed[:12] == bytes.fromhex("0064ff9b0000000000000000")
            or packed[:6] == bytes.fromhex("0064ff9b0001")
            or packed[:12] == b"\x00" * 12
        )
    assert _is_private_ip(str(address)) is expected_private


@PROPERTY_SETTINGS
@given(
    st.lists(
        st.tuples(
            st.sampled_from(tuple("abcdefghijklmnopqrstuvwxyz")),
            st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", max_size=11),
        ).map(lambda parts: "".join(parts)),
        min_size=3,
        max_size=8,
    ),
    st.lists(st.booleans(), min_size=8, max_size=8),
)
def test_token_scope_globs_match_generated_authorized_paths(
    segments: list[str], wildcard_mask: list[bool]
) -> None:
    token = Token(segments=tuple(segments))
    pattern = ".".join(
        "*" if wildcard_mask[index] else segment for index, segment in enumerate(segments)
    )
    assert token.matches_pattern(pattern)
    assert token.matches_pattern("**")
    assert token.matches_pattern(f"{segments[0]}.**")
    assert not token.matches_pattern("definitely-different.**")
