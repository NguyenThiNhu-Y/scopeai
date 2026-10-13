from fastapi import APIRouter, Depends
from typing import cast, Literal
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.api_schemas.solution import SolutionCurrentOut
from app.schemas.llm_schemas.solution_proposal import SolutionDirection
from app.schemas.api_schemas.evaluation import EvaluationResponse, EvaluationItemOut
from app.models import Evaluation, Requirement
from sqlalchemy import select, func
from app.services.bid_service import get_bid_or_404
from app.services.solution_service import current_choice

router = APIRouter(prefix="/bids", tags=["evaluations"])


@router.get("/{bid_id}/evaluations", response_model=EvaluationResponse)
def evaluations(bid_id: int, session: Session = Depends(get_db)) -> EvaluationResponse:
    get_bid_or_404(session, bid_id)
    choice = current_choice(session, bid_id)
    current = SolutionCurrentOut(
        direction=SolutionDirection(choice.direction),
        reason_vi=choice.reason_vi,
        selected_by=choice.chosen_by,
        selected_at=choice.chosen_at,
        reliability_vi=choice.reliability_vi or "",
        assumptions_vi=choice.assumptions_vi or [],
        excluded_directions=choice.excluded_directions or [],
        feasibility=choice.feasibility or {},
        risks=choice.risks_vi or [],
        feasibility_score=choice.feasibility_score,
    ) if choice else None
    rows=session.execute(select(Evaluation, Requirement).join(Requirement, Evaluation.requirement_id==Requirement.id).where(Evaluation.bid_id==bid_id)).all()
    items=[EvaluationItemOut(req_code=r.internal_code,content=r.content,priority=r.priority,category=r.category,rating=cast(Literal["◎", "○", "△", "×", "cần làm rõ"], e.rating),needs_clarification=e.needs_clarification,note_vi=e.note_vi,solution_direction=e.solution_direction,batch_no=e.batch_no) for e,r in rows]
    counts={rating:sum(1 for x in items if x.rating==rating) for rating in ("◎","○","△","×","cần làm rõ")}
    return EvaluationResponse(
            solution_direction=current.model_dump() if current else None,
        warnings=[],
        items=items,
        stats={"total":session.scalar(select(func.count(Requirement.id)).where(Requirement.bid_id==bid_id)) or 0,"evaluated":len(items),**counts,"needs_clarification":sum(1 for x in items if x.needs_clarification)},
    )
