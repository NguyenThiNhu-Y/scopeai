"""ORM models — import mọi model để ``Base.metadata.create_all`` thấy đủ bảng."""

from app.models.bid import Bid
from app.models.changelog import Changelog
from app.models.pipeline_step import PipelineStep
from app.models.question import Question
from app.models.schedule import Schedule
from app.models.solution_choice import SolutionChoice
from app.models.wbs_item import WbsItem
from app.models.wbs_snapshot import WbsSnapshot
from app.models.quotation import Quotation
from app.models.approval import Approval
from app.models.proposal_draft import ProposalDraft
from app.models.reference_snapshot import ReferenceSnapshot
from app.models.attachment import Attachment
from app.models.requirement import Requirement
from app.models.evaluation import Evaluation
from app.models.export_log import ExportLog
from app.models.reference_setting import ReferenceSetting
from app.models.proposal_version import ProposalVersion
from app.models.bid_qualification import BidQualification

__all__ = [
    "Bid",
    "Changelog",
    "PipelineStep",
    "Question",
    "Schedule",
    "SolutionChoice",
    "WbsItem",
    "WbsSnapshot",
    "Quotation", "Approval", "ProposalDraft", "ProposalVersion", "BidQualification", "ReferenceSnapshot", "Attachment", "Requirement", "Evaluation", "ExportLog", "ReferenceSetting",
]
