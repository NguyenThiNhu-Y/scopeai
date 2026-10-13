from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.api_schemas.quotation import QuotationOut, QuotationSettingsIn
from app.services.quotation_engine import calculate_quotation
from app.models import Bid, Quotation
from sqlalchemy import select
from app.api.errors import not_found
from app.services.lock_service import ensure_unlocked
router = APIRouter(prefix="/bids", tags=["quotation"])
@router.get("/{bid_id}/quotation", response_model=QuotationOut)
def get_quotation(bid_id: int, session: Session = Depends(get_db)):
    bid = session.get(Bid, bid_id)
    if not bid: raise not_found()
    row = session.execute(select(Quotation).where(Quotation.bid_id == bid_id).order_by(Quotation.id.desc())).scalars().first()
    return calculate_quotation(session, bid_id) if row is None else __import__("app.services.quotation_engine", fromlist=["quotation_to_out"]).quotation_to_out(row, bid)


@router.put("/{bid_id}/quotation", response_model=QuotationOut)
def update_quotation_settings(
    bid_id: int,
    body: QuotationSettingsIn,
    session: Session = Depends(get_db),
):
    bid = session.get(Bid, bid_id)
    if not bid:
        raise not_found()
    ensure_unlocked(bid)
    if body.currency is not None:
        bid.display_currency = body.currency
    row = session.execute(
        select(Quotation).where(Quotation.bid_id == bid_id).order_by(Quotation.id.desc())
    ).scalars().first()
    contract_model = body.contract_model or (row.contract_model if row else "fixed_price")
    contingency = body.contingency_percent
    onsite = body.onsite_percent
    price_to_win = body.price_to_win_percent
    tm_months = body.tm_months
    odc_fte = body.odc_fte
    odc_months = body.odc_months
    if row and contingency is None:
        contingency = row.contingency_percent
    if row and onsite is None:
        onsite = row.onsite_percent
    if row and price_to_win is None:
        price_to_win = row.price_to_win_percent
    if row and tm_months is None:
        tm_months = row.tm_months
    if row and odc_fte is None:
        odc_fte = row.odc_fte
    if row and odc_months is None:
        odc_months = row.odc_months
    session.commit()
    return calculate_quotation(
        session,
        bid_id,
        contract_model=contract_model,
        contingency_percent=contingency,
        onsite_percent=onsite,
        price_to_win_percent=price_to_win if price_to_win is not None else 0.0,
        tm_months=tm_months,
        odc_fte=odc_fte,
        odc_months=odc_months,
        by="presales",
    )
