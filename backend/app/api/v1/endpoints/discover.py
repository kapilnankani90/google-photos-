"""
Discovery Engine API Endpoint.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 18.1, 18.2)
- part1_discovery_engine_architecture_final.md (Stages 2–6)

Wraps DiscoveryEnginePipeline.run() into a clean, schema-validated REST endpoint
POST /api/v1/discover returning the locked Section 18.2 DiscoveryResponse schema.
"""

import logging
from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from app.retrieval.pipeline import DiscoveryEnginePipeline
from app.retrieval.models import RetrievalFilter, DiscoveryResponse
from app.representation.models import V2MemoryRepresentation

logger = logging.getLogger("DiscoveryEndpoint")

router = APIRouter()


class DiscoveryRequest(BaseModel):
    """
    Request payload for Discovery Engine endpoint.
    Conforms to Section 18.1 with support for raw natural-language query or pre-parsed V2 frame.
    """
    model_config = ConfigDict(extra="ignore")

    raw_input: Optional[str] = Field(
        None,
        description="Natural language memory query (e.g. 'rohtang ki ice wali photo', '5 sisters')",
    )
    query: Optional[Union[str, V2MemoryRepresentation]] = Field(
        None,
        description="Alternative query input: either raw string or full V2MemoryRepresentation",
    )
    v2_representation: Optional[V2MemoryRepresentation] = Field(
        None,
        description="Optional pre-parsed V2 memory representation",
    )
    filters: Optional[RetrievalFilter] = Field(
        None,
        description="Optional structured and temporal retrieval filters",
    )
    top_k: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of candidate results to return",
    )
    enable_recovery: bool = Field(
        True,
        description="Whether controlled recovery broadening is allowed",
    )


def get_pipeline() -> DiscoveryEnginePipeline:
    """Dependency provider returning a DiscoveryEnginePipeline instance."""
    return DiscoveryEnginePipeline()


@router.post(
    "",
    response_model=DiscoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Discovery Engine Retrieval",
    description="Executes Stages 2–6 of the Discovery Engine pipeline on a raw query or V2 frame.",
)
@router.post(
    "/",
    response_model=DiscoveryResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def discover(
    request: DiscoveryRequest,
    pipeline: DiscoveryEnginePipeline = Depends(get_pipeline),
) -> DiscoveryResponse:
    """
    HTTP POST handler for /api/v1/discover.
    Wraps existing DiscoveryEnginePipeline.run() and returns DiscoveryResponse.
    """
    # Resolve target query from request parameters
    target_query: Union[str, V2MemoryRepresentation]
    if request.v2_representation is not None:
        target_query = request.v2_representation
    elif isinstance(request.query, V2MemoryRepresentation):
        target_query = request.query
    elif request.raw_input is not None:
        target_query = request.raw_input
    elif isinstance(request.query, str):
        target_query = request.query
    else:
        raise HTTPException(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            detail="A query is required. Provide 'raw_input', 'query', or 'v2_representation'.",
        )

    try:
        response = await pipeline.run(
            query=target_query,
            filters=request.filters,
            top_k=request.top_k,
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error executing DiscoveryEnginePipeline: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Discovery engine retrieval failed: {str(exc)}",
        )
