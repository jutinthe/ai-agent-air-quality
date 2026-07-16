from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.schemas.knowledge_graph import CytoscapeGraph, PaperKnowledgeGraph
from app.services.knowledge_graph_service import (
    generate_knowledge_graph,
    load_knowledge_graph,
    save_knowledge_graph,
    to_cytoscape,
)
from app.services.llm_extraction_service import load_extraction


router = APIRouter(prefix="/papers", tags=["Knowledge Graph"])


def _build_or_load_graph(
    paper_id: UUID,
    settings: Settings,
    force: bool,
) -> PaperKnowledgeGraph:
    if not force:
        existing = load_knowledge_graph(
            paper_id=paper_id,
            processed_directory=settings.processed_directory,
        )
        if existing is not None:
            return existing

    stored_extraction = load_extraction(
        paper_id=paper_id,
        processed_directory=settings.processed_directory,
    )

    if stored_extraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Structured extraction not found. Run the extraction "
                "endpoint before generating the graph."
            ),
        )

    graph = generate_knowledge_graph(
        paper_id=paper_id,
        extraction=stored_extraction.extraction,
    )
    save_knowledge_graph(
        graph=graph,
        processed_directory=settings.processed_directory,
    )

    return graph


@router.post(
    "/{paper_id}/knowledge-graph",
    response_model=PaperKnowledgeGraph,
    summary="Generate a knowledge graph for one paper",
)
async def create_paper_knowledge_graph(
    paper_id: UUID,
    force: bool = Query(default=False),
    settings: Settings = Depends(get_settings),
) -> PaperKnowledgeGraph:
    return _build_or_load_graph(paper_id, settings, force)


@router.get(
    "/{paper_id}/knowledge-graph",
    response_model=PaperKnowledgeGraph,
    summary="Retrieve a saved paper knowledge graph",
)
async def get_paper_knowledge_graph(
    paper_id: UUID,
    settings: Settings = Depends(get_settings),
) -> PaperKnowledgeGraph:
    graph = load_knowledge_graph(
        paper_id=paper_id,
        processed_directory=settings.processed_directory,
    )

    if graph is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge graph not found.",
        )

    return graph


@router.get(
    "/{paper_id}/knowledge-graph/cytoscape",
    response_model=CytoscapeGraph,
    summary="Retrieve the graph in Cytoscape.js format",
)
async def get_cytoscape_knowledge_graph(
    paper_id: UUID,
    settings: Settings = Depends(get_settings),
) -> CytoscapeGraph:
    graph = load_knowledge_graph(
        paper_id=paper_id,
        processed_directory=settings.processed_directory,
    )

    if graph is None:
        graph = _build_or_load_graph(paper_id, settings, force=False)

    return to_cytoscape(graph)
