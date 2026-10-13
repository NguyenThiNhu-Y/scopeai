"""Aggregation router — gom mọi router con, main.py mount prefix /api."""

from fastapi import APIRouter

from app.api.routers.bids import router as bids_router
from app.api.routers.health import router as health_router
from app.api.routers.pipeline import router as pipeline_router
from app.api.routers.questions import router as questions_router
from app.api.routers.solution import router as solution_router
from app.api.routers.effort import router as effort_router
from app.api.routers.evaluations import router as evaluations_router
from app.api.routers.schedule import router as schedule_router
from app.api.routers.wbs import router as wbs_router
from app.api.routers.quotation import router as quotation_router
from app.api.routers.proposal import router as proposal_router
from app.api.routers.approvals import router as approvals_router
from app.api.routers.attachments import router as attachments_router
from app.api.routers.parse import router as parse_router
from app.api.routers.exports import router as exports_router
from app.api.routers.settings import router as settings_router
from app.api.routers.proposal_versions import router as proposal_versions_router
from app.api.routers.bid_qualification import router as bid_qualification_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(bids_router)
api_router.include_router(pipeline_router)
api_router.include_router(questions_router)
api_router.include_router(solution_router)
api_router.include_router(effort_router)
api_router.include_router(evaluations_router)
api_router.include_router(wbs_router)
api_router.include_router(schedule_router)
api_router.include_router(quotation_router)
api_router.include_router(proposal_router)
api_router.include_router(approvals_router)
api_router.include_router(attachments_router)
api_router.include_router(parse_router)
api_router.include_router(exports_router)
api_router.include_router(settings_router)
api_router.include_router(proposal_versions_router)
api_router.include_router(bid_qualification_router)

__all__ = ["api_router"]
