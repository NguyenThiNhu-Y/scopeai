from sqlalchemy import select
from app.api.errors import pipeline_error
from app.llm.gateway import complete_with_retry, get_llm_client, LLMSchemaError
from app.llm.prompts.b3_evaluate import build_evaluation_prompt
from app.models import Requirement, Evaluation
from app.schemas.llm_schemas.evaluation import EvaluationBatch

def evaluate(session, bid_id: int, direction: str | None = None, client=None) -> dict:
    requirements=list(session.scalars(select(Requirement).where(Requirement.bid_id==bid_id).order_by(Requirement.id)))
    client=client or get_llm_client(); warnings=[]; all_codes={r.internal_code for r in requirements}
    for batch_no in range(0,len(requirements),40):
        batch=requirements[batch_no:batch_no+40]; expected={r.internal_code for r in batch}
        rows=[{"req_code":r.internal_code,"content":r.content,"priority":r.priority,"category":r.category} for r in batch]
        context={"requirements":rows,"batch_codes":sorted(expected),"solution_direction":direction,"architecture_components":[]}
        # Danh sách requirement phải nằm TRONG prompt — provider openai_compat
        # chỉ gửi prompt, không gửi context (BR-03). PII che tại gateway (BR-06).
        prompt=build_evaluation_prompt(rows, direction)
        try: output=complete_with_retry(client,EvaluationBatch,prompt,context=context,max_retries=2)
        except LLMSchemaError as exc: raise pipeline_error("Kết quả đánh giá từ AI không hợp lệ sau 2 lần thử",{"error":str(exc)}) from exc
        codes=[x["req_code"] for x in output["batch"]]; missing=expected-set(codes); extra=set(codes)-expected; duplicate={c for c in codes if codes.count(c)>1}
        if missing or extra or duplicate:
            warnings.append({"type":"code_mismatch","codes":sorted(missing|extra|duplicate),"message":"Thiếu/thừa/trùng mã trong kết quả đánh giá"}); continue
        by_code={x["req_code"]:x for x in output["batch"]}
        for r in batch:
            x=by_code[r.internal_code]; session.merge(Evaluation(bid_id=bid_id,requirement_id=r.id,rating=x["rating"],needs_clarification=x["needs_clarification"],note_vi=x["note_vi"],batch_no=batch_no//40+1,solution_direction=direction))
        session.commit()
    return {"warnings":warnings,"total":len(all_codes)}