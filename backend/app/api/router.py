from app.api.routes.knowledge_graph import router as knowledge_graph_router
from app.api.routes.extraction import router as extraction_router
from fastapi import APIRouter

from app.api.routes.papers import router as papers_router


api_router = APIRouter(prefix="/api")
api_router.include_router(papers_router)

api_router.include_router(extraction_router)
api_router.include_router(knowledge_graph_router)
