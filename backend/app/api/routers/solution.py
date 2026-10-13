from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.api_schemas.solution import SolutionChoiceIn, SolutionChoiceOut, SolutionCurrentOut
from app.services.solution_service import choose_solution, current_choice
from app.services.bid_service import get_bid_or_404
from app.schemas.llm_schemas.solution_proposal import SolutionDirection

router = APIRouter(prefix="/bids", tags=["solution"])


@router.post("/{bid_id}/solution", response_model=SolutionChoiceOut)
def post_solution(bid_id: int, body: SolutionChoiceIn, session: Session = Depends(get_db)) -> SolutionChoiceOut:
    return SolutionChoiceOut(**choose_solution(session, bid_id, body.direction.value, body.reason_vi, body.by, assumptions=body.assumptions_vi, excluded_directions=body.excluded_directions, feasibility=body.feasibility))


@router.get("/{bid_id}/solution", response_model=SolutionCurrentOut)
def get_solution(bid_id: int, session: Session = Depends(get_db)) -> SolutionCurrentOut:
    get_bid_or_404(session, bid_id)
    choice = current_choice(session, bid_id)
    if choice is None:
        from app.api.errors import not_found
        raise not_found("Chưa có hướng giải pháp")
    return SolutionCurrentOut(
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
    )
