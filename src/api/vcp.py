"""
VCP API Router

Endpoints for VCP token validation, CSM1 parsing, and context encoding.
Provides programmatic access to VCP protocol operations.

Feature flags:
- vcp_identity_enabled: VCP/I endpoints
- vcp_semantics_enabled: VCP/S endpoints
- vcp_adaptation_enabled: VCP/A endpoints
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api_routers.auth_dependencies import get_current_user
from core.config.logging_config import get_logger
from services.feature_flags import is_feature_enabled
from services.persona_manager import SessionToken
from services.vcp import ContextEncoder, CSM1Code, Dimension, Persona, Token

logger = get_logger(__name__)

router = APIRouter(prefix="/api/vcp", tags=["vcp"])


# === Request/Response Models ===


class TokenValidateRequest(BaseModel):
    """Request to validate a VCP/I token."""

    token: str = Field(..., description="VCP token string (e.g., family.safe.guide@1.2.0)")


class TokenValidateResponse(BaseModel):
    """Response from token validation."""

    valid: bool
    canonical: str | None = None
    domain: str | None = None
    approach: str | None = None
    role: str | None = None
    version: str | None = None
    namespace: str | None = None
    uri: str | None = None
    error: str | None = None


class CSM1ParseRequest(BaseModel):
    """Request to parse a CSM1 code."""

    code: str = Field(..., description="CSM1 code string (e.g., N5+F+E)")


class CSM1ParseResponse(BaseModel):
    """Response from CSM1 parsing."""

    valid: bool
    persona: str | None = None
    persona_description: str | None = None
    adherence_level: int | None = None
    scopes: list[str] | None = None
    namespace: str | None = None
    version: str | None = None
    encoded: str | None = None
    error: str | None = None


class ContextEncodeRequest(BaseModel):
    """Request to encode context dimensions."""

    time: str | None = Field(None, description="Time context (morning, midday, evening, night)")
    space: str | None = Field(None, description="Space context (home, office, school, hospital, transit)")
    company: list[str] | None = Field(None, description="Company context (alone, children, colleagues, family)")
    culture: str | None = Field(None, description="Cultural context")
    occasion: str | None = Field(None, description="Occasion (normal, celebration, mourning, emergency)")
    state: str | None = Field(None, description="Mental state (happy, anxious, tired, contemplative)")
    environment: str | None = Field(None, description="Physical environment")
    agency: str | None = Field(None, description="Agency level (leader, peer, subordinate, limited)")
    constraints: list[str] | None = Field(None, description="Active constraints")


class ContextEncodeResponse(BaseModel):
    """Response from context encoding."""

    wire_format: str
    json_format: dict[str, Any]
    dimensions_set: list[str]


class PersonaInfo(BaseModel):
    """Information about a CSM1 persona."""

    code: str
    name: str
    description: str


class PersonasResponse(BaseModel):
    """Response listing all personas."""

    personas: list[PersonaInfo]


class VCPStatusResponse(BaseModel):
    """VCP feature status response."""

    vcp_identity_enabled: bool
    vcp_semantics_enabled: bool
    vcp_adaptation_enabled: bool
    vcp_full_stack_enabled: bool
    vcp_strict_mode: bool
    version: str


# === Endpoints ===


@router.post("/token/validate", response_model=TokenValidateResponse)
async def validate_token(
    request: TokenValidateRequest,
    _user: Annotated[SessionToken, Depends(get_current_user)],
) -> TokenValidateResponse:
    """Validate a VCP/I token string.

    Parses the token according to VCP/I grammar and returns its components.
    """
    if not is_feature_enabled("vcp_identity_enabled"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VCP Identity layer not enabled",
        )

    try:
        token = Token.parse(request.token)
        return TokenValidateResponse(
            valid=True,
            canonical=token.canonical,
            domain=token.domain,
            approach=token.approach,
            role=token.role,
            version=token.version,
            namespace=token.namespace,
            uri=token.to_uri(),
        )
    except ValueError as e:
        return TokenValidateResponse(
            valid=False,
            error=str(e),
        )


@router.post("/csm1/parse", response_model=CSM1ParseResponse)
async def parse_csm1(
    request: CSM1ParseRequest,
    _user: Annotated[SessionToken, Depends(get_current_user)],
) -> CSM1ParseResponse:
    """Parse a CSM1 constitutional code.

    Parses the code according to CSM1 grammar and returns its components.
    """
    if not is_feature_enabled("vcp_semantics_enabled"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VCP Semantics layer not enabled",
        )

    try:
        code = CSM1Code.parse(request.code)
        return CSM1ParseResponse(
            valid=True,
            persona=code.persona.name,
            persona_description=code.persona.description,
            adherence_level=code.adherence_level,
            scopes=[s.name for s in code.scopes],
            namespace=code.namespace,
            version=code.version,
            encoded=code.encode(),
        )
    except ValueError as e:
        return CSM1ParseResponse(
            valid=False,
            error=str(e),
        )


@router.post("/context/encode", response_model=ContextEncodeResponse)
async def encode_context(
    request: ContextEncodeRequest,
    _user: Annotated[SessionToken, Depends(get_current_user)],
) -> ContextEncodeResponse:
    """Encode context dimensions to VCP/A format.

    Encodes provided context dimensions into wire format and JSON.
    """
    if not is_feature_enabled("vcp_adaptation_enabled"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VCP Adaptation layer not enabled",
        )

    encoder = ContextEncoder()
    context = encoder.encode(
        time=request.time,
        space=request.space,
        company=request.company,
        culture=request.culture,
        occasion=request.occasion,
        state=request.state,
        environment=request.environment,
        agency=request.agency,
        constraints=request.constraints,
    )

    return ContextEncodeResponse(
        wire_format=context.encode(),
        json_format=context.to_json(),
        dimensions_set=[dim._name for dim in context.dimensions.keys()],
    )


@router.get("/personas", response_model=PersonasResponse)
async def list_personas(
    _user: Annotated[SessionToken, Depends(get_current_user)],
) -> PersonasResponse:
    """List all available CSM1 personas.

    Returns the 8 archetypal personas with their codes and descriptions.
    """
    return PersonasResponse(
        personas=[
            PersonaInfo(
                code=p.value,
                name=p.name,
                description=p.description,
            )
            for p in Persona
        ]
    )


@router.get("/dimensions")
async def list_dimensions(
    _user: Annotated[SessionToken, Depends(get_current_user)],
) -> dict[str, Any]:
    """List all available context dimensions.

    Returns the 9 context dimensions with their possible values.
    """
    return {
        "dimensions": [
            {
                "name": dim._name,
                "symbol": dim.symbol,
                "position": dim.position,
                "values": {emoji: name for emoji, name in dim.values.items()},
            }
            for dim in Dimension
        ]
    }


@router.get("/status", response_model=VCPStatusResponse)
async def vcp_status() -> VCPStatusResponse:
    """Get VCP feature status.

    Returns the current state of all VCP feature flags.
    No authentication required for status check.
    """
    return VCPStatusResponse(
        vcp_identity_enabled=is_feature_enabled("vcp_identity_enabled"),
        vcp_semantics_enabled=is_feature_enabled("vcp_semantics_enabled"),
        vcp_adaptation_enabled=is_feature_enabled("vcp_adaptation_enabled"),
        vcp_full_stack_enabled=is_feature_enabled("vcp_full_stack_enabled"),
        vcp_strict_mode=is_feature_enabled("vcp_strict_mode"),
        version="2.0.0",
    )
