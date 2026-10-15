/**
 * Contract chia sẻ backend ↔ frontend (spec M2 §2.3).
 * Khớp các Pydantic schema bên backend:
 *   app/schemas/api_schemas/{bid,question,pipeline,sample}.py
 * Tên field phải khớp CHÍNH XÁC với backend (Pydantic → JSON snake_case).
 */

export type HealthStatus = 'ok' | 'degraded';

export type LlmProvider = 'mock' | 'openai_compat';

export interface HealthResponse {
  /** 'ok' khi backend sẵn sàng; 'degraded' khi DB lỗi (endpoint vẫn trả HTTP 200). */
  status: HealthStatus;
  /** Tên ứng dụng cố định: presales-bidding-assistant. */
  app: string;
  /** Phiên bản ứng dụng, khớp `app.__version__` / pyproject.toml. */
  version: string;
  /** Giá trị env LLM_PROVIDER — backend không bao giờ trả key/base URL (BR-06). */
  llm_provider: LlmProvider;
  /** 'ok' nếu kết nối SQLite thành công. */
  database: string;
  /** Thời gian UTC theo ISO 8601. */
  time: string;
}

// ---------------------------------------------------------------------------
// M2 — Hồ sơ (Module A, spec §2.1)
// ---------------------------------------------------------------------------

export type CustomerLanguage = 'vi' | 'en' | 'ja';

export type BidStatus =
  | 'draft'
  | 'analyzing'
  | 'waiting_clarification'
  | 'waiting_tech_approval'
  | 'waiting_price_approval'
  | 'price_approved'
  | 'rejected'
  | 'error';

/** Backend enum values kept outside JSX so customer-facing components render labels only. */
export const BID_STATUS = {
  draft: 'draft',
  analyzing: 'analyzing',
  clarification: 'waiting_clarification',
  technicalApproval: 'waiting_tech_approval',
  priceApproval: 'waiting_price_approval',
  priceApproved: 'price_approved',
  rejected: 'rejected',
  error: 'error',
} as const satisfies Record<string, BidStatus>;

export type BudgetCurrency = 'VND' | 'JPY' | 'USD';

/** POST /api/bids — request body (BidCreate, §3.1). */
export interface BidCreate {
  project_name: string;
  customer_name: string;
  submission_deadline: string;
  customer_language: CustomerLanguage;
  /** Bắt buộc, tối thiểu 30 ký tự (yêu cầu milestone M2). */
  request_content: string;
  budget_amount?: number | null;
  budget_currency?: BudgetCurrency | null;
}

/** BidOut — response của POST /api/bids và GET /api/bids/{id}. */
export interface Bid {
  id: number;
  project_name: string;
  customer_name: string;
  submission_deadline: string;
  customer_language: CustomerLanguage;
  status: BidStatus;
  locked: boolean;
  budget_amount?: number | null;
  budget_currency?: BudgetCurrency | null;
  created_by: string;
  created_at: string;
  display_currency?: BudgetCurrency;
  customer_schedule_start?: string | null;
  customer_schedule_end?: string | null;
  customer_mvp_start?: string | null;
  customer_production_start?: string | null;
  deal_stage?: DealStage | null;
}

export type DealStage = 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';

/** BidListItem — một dòng trong GET /api/bids (§3.2). */
export interface BidListItem {
  id: number;
  project_name: string;
  customer_name: string;
  status: BidStatus;
  submission_deadline: string;
  customer_language: CustomerLanguage;
  locked: boolean;
  updated_at: string;
  deal_stage?: string | null;
  created_at?: string | null;
  total_price?: number | null;
  total_price_currency?: string | null;
}

/** Response của GET /api/bids — danh sách + tổng số (để phân trang). */
export interface BidsListResponse {
  items: BidListItem[];
  total: number;
  stats?: {
    total?: number;
    analyzing?: number;
    waiting_clarification?: number;
    price_approved?: number;
    sent?: number;
  };
}

// ---------------------------------------------------------------------------
// M2 — Pipeline (Module C, spec §2.1)
// ---------------------------------------------------------------------------

export type StepStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'waiting_clarification'
  | 'skipped';

export const STEP_STATUS = {
  pending: 'pending', running: 'running', completed: 'completed', failed: 'failed',
  clarification: 'waiting_clarification', skipped: 'skipped',
} as const satisfies Record<string, StepStatus>;

/** 7 bước pipeline (data_model §13). */
export type StepKey =
  | 'intake'
  | 'gap'
  | 'evaluate'
  | 'solution'
  | 'wbs'
  | 'proposal'
  | 'ja_check';

/**
 * Output bước B1 Intake (IntakeExtraction — llm_pipeline.md §2).
 * Chỉ là ghi chú văn bản, KHÔNG chứa số man-day/giá/ngày (BR-01).
 */
export interface IntakeOutput {
  objectives_vi: string;
  users_vi: string;
  data_vi: string;
  constraints_vi: string[];
  budget_mentioned: boolean;
  budget_note_vi?: string;
  deadline_mentioned: boolean;
  deadline_note_vi?: string;
  customer_language_detected: CustomerLanguage | 'unknown';
  summary_vi: string;
  keywords: string[];
  notes: string[];
}

/** Trạng thái một bước pipeline. */
export interface StepState {
  step_key: string;
  status: StepStatus;
  /**
   * Tùy chọn — backend có thể kèm output bước (vd. output B1 intake) để UI
   * hiển thị kết quả phân tích; nếu không gửi thì UI ẩn phần đó.
   */
  output_json?: IntakeOutput | null;
  /** Tùy chọn — thông báo lỗi bước (BR-02), hiển thị khi status=failed. */
  error_message?: string | null;
}

// ---------------------------------------------------------------------------
// M3 — Hướng giải pháp và effort (contract frozen §7.2, §8.0, §12)
// ---------------------------------------------------------------------------

export type SolutionDirection = 'none' | 'traditional_ml' | 'rag' | 'agent' | 'fine_tune';

export interface SolutionProposal {
  direction: SolutionDirection;
  reason_vi: string;
  /** Tùy chọn — contract §7.1: GET /evaluations không trả risks_vi/architecture_notes_vi. */
  architecture_notes_vi?: string;
  /** Các trường mở rộng được render khi backend cung cấp, không suy diễn ở frontend. */
  reliability_vi?: string | null;
  excluded_directions?: SolutionDirection[];
  assumptions_vi?: string[];
  feasibility?: Record<string, string> | null;
  risks_vi?: string[];
  risks?: SolutionRisk[];
  feasibility_score?: FeasibilityScore | null;
}

export interface SolutionRisk {
  type_vi: string;
  level: number;
  description_vi: string;
  mitigation_vi: string;
}

export interface FeasibilityScore {
  score: number;
  reason_vi: string;
}

export interface SolutionChoice extends SolutionProposal {
  selected_by?: string;
  selected_at?: string;
}

export interface ChooseSolutionRequest {
  direction: SolutionDirection;
  reason_vi: string;
  by: string;
}

export interface ChooseSolutionResponse {
  direction: SolutionDirection;
  effort_recalculated: boolean;
  warnings: string[];
}

export interface AppliedFactor {
  key: string;
  value: number;
  reason: string;
}

export interface EffortByPhase {
  min: number;
  max: number;
}

export interface EffortTrace {
  table_version: number;
  source: string;
  formula: string;
  factor_product_raw?: number;
  factor_product_capped?: number;
}

export interface EffortResponse {
  direction: SolutionDirection;
  factors: AppliedFactor[];
  factor_product: number;
  cap: number;
  by_phase: Record<'poc' | 'mvp' | 'production', EffortByPhase>;
  midpoint_total: number;
  trace: EffortTrace;
}

export interface EvaluationsResponse {
  solution_direction?: SolutionChoice | null;
  warnings: EvaluationWarning[];
  items: Requirement[];
  stats: Record<string, number>;
}

// ---------------------------------------------------------------------------
// M6 — Đính kèm, đọc file và ma trận đáp ứng
// ---------------------------------------------------------------------------
export type AttachmentFileType = 'rfp' | 'requirement' | 'sample_data';
export type ParseStatus = 'pending' | 'ok' | 'error';
export type DataReadiness = 'low' | 'medium' | 'high';

export interface SheetMapping {
  sheet_name: string;
  sheet_kind: 'requirement' | 'sample_data' | 'other';
  col_map: Record<string, string>;
}

export interface Attachment {
  id: number;
  filename: string;
  file_type: AttachmentFileType;
  detected_type?: AttachmentFileType;
  size_bytes: number;
  parse_status: ParseStatus;
  parse_error?: string | null;
  sheet_mappings: SheetMapping[];
}
export interface AttachmentUpdate {
  file_type?: AttachmentFileType;
  sheet_mappings?: SheetMapping[];
}
export interface AttachmentListResponse { items: Attachment[]; }

export interface ParseResult {
  requirements: { count: number; no_requirement_file: boolean };
  attachments: Array<{ id?: number; attachment_id?: number; filename: string; status: ParseStatus; error?: string | null }>;
  sample_profile: SampleProfile | null;
  column_mapping_confirmed: boolean;
}

export interface SampleProfile {
  row_count: number;
  columns: Array<{ name: string; type: string; empty_pct: number; pii_suspected: boolean }>;
  readiness_suggestion: DataReadiness;
}

export interface Requirement {
  req_code: string;
  content: string;
  priority?: string | null;
  category?: string | null;
  rating?: '◎' | '○' | '△' | '×' | 'cần làm rõ' | null;
  needs_clarification?: boolean;
  note_vi?: string;
  solution_direction?: string | null;
  batch_no?: number | null;
}

export interface EvaluationWarning {
  type: string;
  codes?: string[];
  message: string;
}

/** PipelineProgress — tóm tắt trạng thái các bước (spec §2.1). */
export interface PipelineProgress {
  steps: StepState[];
  waiting_clarification: boolean;
  rounds_used: number;
  max_rounds: number;
}

/** Response 202 của POST /api/bids/{id}/pipeline/start và POST /api/bids/{id}/rerun. */
export interface PipelineStartResponse {
  bid_id: number;
  status: string;
  steps: StepState[];
}

/** Request body POST /api/bids/{id}/rerun — M2 chỉ hỗ trợ from_step=null. */
export interface RerunRequest {
  from_step: string | null;
  reason: string;
  by: string;
}

/** BidDetailOut — GET /api/bids/{id}: BidOut + các trường mở rộng. */
export interface BidDetail extends Bid {
  no_requirement_file: boolean;
  data_readiness: 'low' | 'medium' | 'high' | null;
  display_currency: BudgetCurrency;
  pipeline_progress: PipelineProgress;
  /**
   * Tùy chọn — contract §3.3 không liệt kê nhưng kịch bản Preview §5(b) bước 3
   * yêu cầu hiển thị nội dung yêu cầu trên trang chi tiết; UI chỉ hiển thị
   * khi backend trả field này.
   */
  request_content?: string | null;
}

// ---------------------------------------------------------------------------
// M2 — Hỏi làm rõ (Module D, spec §2.1)
// ---------------------------------------------------------------------------

export type QuestionImpact = 'solution' | 'effort' | 'price';

/** QuestionOut — một câu hỏi làm rõ (§6.1). */
export interface Question {
  id: number;
  round_no: number;
  /** Nội dung câu hỏi bằng NGÔN NGỮ KHÁCH (vi/en/ja) — BR-07. */
  question: string;
  /** Lý do hỏi bằng tiếng Việt — BR-07. */
  reason_vi: string;
  impact: QuestionImpact;
  /** Luôn rỗng ở M2 (chưa có bảng requirements — M6). */
  related_req_codes: string[];
  answer: string | null;
  is_assumption: boolean;
  status: string;
}

/** QuestionsOut — GET /api/bids/{id}/questions (§6.1). */
export interface QuestionsResponse {
  items: Question[];
  rounds_used: number;
  max_rounds: number;
  blocking_reason?: string | null;
  /** Lý do phải hỏi vòng 2 (backend trả khi còn thông tin chặn) — hiển thị khi có câu vòng 2. */
  round_two_reason_vi?: string | null;
}

export interface AnswersResponse {
  status: string;
  pipeline_resumed_from: string;
  warnings?: string[];
}

/** AnswerItemIn — một câu trả lời trong POST answers (§6.2). */
export interface AnswerItem {
  question_id: number;
  answer: string;
  is_assumption: boolean;
}

export interface EmailDraft {
  bid_id: number;
  customer_name: string;
  sender: string;
  customer_language: CustomerLanguage;
  subject: string;
  body: string;
}

// ---------------------------------------------------------------------------
// M2 — Hồ sơ mẫu (Module A — sample, §3.7)
// ---------------------------------------------------------------------------

export type SampleKey = 'ja_email' | 'vi_email' | 'tokai_minato';

export interface SamplePreview {
  sample_key: SampleKey;
  project_name: string;
  customer_name: string;
  submission_deadline: string;
  customer_language: CustomerLanguage;
  display_currency: BudgetCurrency;
  request_content: string;
  files: Array<{ filename: string; file_type: AttachmentFileType; size_bytes: number }>;
}

// ---------------------------------------------------------------------------
// M4 — WBS 3 cấp (Module F, contract §8.1/8.2/8.3, spec M4 §2.1–2.3)
// ---------------------------------------------------------------------------

export type WbsPhase = 'poc' | 'mvp' | 'production';

export type WbsRole =
  | 'pm'
  | 'ba'
  | 'brse'
  | 'ai_engineer'
  | 'backend'
  | 'frontend'
  | 'qa'
  | 'infra';

/** WbsItemOut — một item trong WBS 3 cấp (§8.1). role/weight/man_day chỉ có trên task lá. */
export interface WbsItem {
  task_code: string;
  name_vi: string;
  phase: WbsPhase;
  parent_code: string | null;
  /** 1 = nhóm, 2 = task, 3 = sub-task (lá). Suy từ chuỗi parent_code — backend tính. */
  level: number;
  role: WbsRole | null;
  weight: number | null;
  /** Nhóm/task cha = Σ con (backend tính); lá ≤ 10. */
  man_day: number | null;
  depends_on: string[];
  /** Truy vết requirement (thiet_ke_danh_gia.md §4) — chỉ task lá, tối đa 8 mã. */
  requirement_codes: string[];
  sort_order: number;
  is_leaf: boolean;
}

export interface WbsTotals {
  man_day: number;
  by_phase: Partial<Record<WbsPhase, number>>;
}

/** WbsCheckOut — kiểm tra ngữ nghĩa do code tính (FR-032). */
export interface WbsCheck {
  midpoint: number;
  deviation_pct: number;
  within_20pct: boolean;
  pm_qa_ok: boolean;
  cycle_free: boolean;
  leaf_max_man_day: number;
  leaf_within_limit: boolean;
  warning: string | null;
}

export interface WbsTrace {
  direction: string;
  factors: { key: string; value: number; reason: string }[];
  factor_product: number;
  cap: number;
  range: { min: number; max: number };
  formula: string;
}

/** Response GET/PUT /api/bids/{id}/wbs (§8.1/8.2). */
export interface WbsResponse {
  items: WbsItem[];
  totals: WbsTotals;
  check: WbsCheck;
  trace: WbsTrace;
  /** PUT /wbs trả kèm lịch đã tính lại (không gọi AI). quotation bỏ trống ở M4. */
  recalculated?: {
    schedule?: ScheduleResponse | null;
    quotation?: unknown;
  } | null;
}

/** WbsChangeIn — một thay đổi trong mảng `changes` của PUT /wbs (§8.2). */
export type WbsChange =
  | {
      op: 'add';
      task: {
        task_code: string;
        name_vi: string;
        phase: WbsPhase;
        parent_code: string | null;
        role?: WbsRole | null;
        man_day?: number | null;
        weight?: number | null;
        depends_on?: string[];
        requirement_codes?: string[];
      };
    }
  | {
      op: 'update';
      task_code: string;
      fields: Partial<{
        name_vi: string;
        phase: WbsPhase;
        parent_code: string | null;
        role: WbsRole | null;
        man_day: number | null;
        depends_on: string[];
        requirement_codes: string[];
        sort_order: number;
      }>;
    }
  | {
      op: 'remove';
      task_code: string;
    };

export interface WbsUpdateRequest {
  changes: WbsChange[];
  by: string;
  note?: string | null;
}

/** Response POST /api/bids/{id}/wbs/snapshot (§8.3). */
export interface WbsSnapshotResponse {
  snapshot_id: number;
  diff_summary: WbsDiffSummary | null;
}

/** Diff mức item: thêm/sửa/xóa (gồm parent_code, depends_on, man_day — ADR-005). */
export interface WbsDiffSummary {
  added: Array<Record<string, unknown>>;
  removed: Array<Record<string, unknown>>;
  modified: Array<{ task_code: string; field: string; old: unknown; new: unknown }>;
}

// ---------------------------------------------------------------------------
// M4 — Master schedule (Module F, contract §8.4/8.4a, spec M4 §2.4–2.5)
// ---------------------------------------------------------------------------

export type WorkingCalendar = 'vn' | 'jp' | 'both';

export interface TeamAllocation {
  pm?: number;
  ba?: number;
  brse?: number;
  ai_engineer?: number;
  backend?: number;
  frontend?: number;
  qa?: number;
  infra?: number;
}

export interface PaymentMilestone {
  name: string;
  percent: number;
  due_offset_days: number;
  /** Ngày đến hạn = start_date + due_offset_days (ngày lịch) — backend tính, thêm vào response. */
  due_date?: string | null;
}

export interface RoleDuration {
  man_day: number;
  headcount: number;
  duration_days: number;
}

/** TaskDateOut — một task trong tasks[] của GET /schedule (dữ liệu Gantt). */
export interface TaskDate {
  task_code: string;
  phase: WbsPhase;
  role: WbsRole;
  man_day: number;
  start_date: string;
  end_date: string;
}

/** Response GET/PUT /api/bids/{id}/schedule (§8.4/8.4a). */
export interface ScheduleResponse {
  start_date: string;
  buffer_days: number;
  working_calendar: WorkingCalendar;
  team_allocation: TeamAllocation;
  payment_milestones: PaymentMilestone[];
  by_role: Record<string, RoleDuration>;
  tasks: TaskDate[];
  holidays_applied: string[];
  end_date: string;
  deadline_violation: boolean;
  warning: string | null;
  trace: { formula: string };
  work_breakdown?: Record<string, Record<string, number>>;
  go_no_go_gap_working_days?: number;
  go_no_go_start?: string | null;
  go_no_go_end?: string | null;
  earliest_mvp_start?: string | null;
  earliest_production_start?: string | null;
  customer_mvp_start?: string | null;
  customer_production_start?: string | null;
  gantt_break_interval?: 'day' | 'week' | 'month';
}

/** Request body PUT /api/bids/{id}/schedule (§8.4a). */
export interface ScheduleUpdateRequest {
  start_date: string;
  buffer_days: number;
  working_calendar: WorkingCalendar;
  team_allocation: TeamAllocation;
  payment_milestones?: PaymentMilestone[];
  go_no_go_gap_working_days?: number;
  gantt_break_interval?: 'day' | 'week' | 'month';
  by: string;
}

// ---------------------------------------------------------------------------
// M5 — Báo giá, proposal và cổng duyệt
// ---------------------------------------------------------------------------

export type ContractModel = 'fixed_price' | 'tm' | 'odc';
export type TaxMode = 'tax_excluded' | 'tax_included';
export type ApprovalDecision = 'approved' | 'rejected' | 'skip';

export interface QuotationRoleTotal {
  man_day: number;
  rate: number;
  amount: number;
}

export interface QuotationResponse {
  contract_model: ContractModel;
  contingency_percent: number;
  currency: string;
  fx_rate: { value: number; date: string; pair: string };
  valid_until: string;
  tax_mode: TaxMode;
  totals: {
    by_role: Record<string, QuotationRoleTotal>;
    overhead: { pm: number; brse: number };
    contingency_amount: number;
    operating_cost: number;
    subtotal: number;
    tax_excluded: number;
    tax_included: number;
    tax_amount?: number;
    tax_percent?: number;
    grand_total: number;
    by_phase?: Record<string, number>;
    onsite_percent?: number;
    payment_plan?: Array<{
      name: string;
      percent: number;
      month?: number;
      amount?: number;
      fte?: number;
      fte_months?: number;
    }>;
    odc_fte_months?: number | null;
  };
  budget?: {
    amount: number;
    currency: string;
    difference: number | null;
    difference_percent?: number | null;
    adjustment_suggestion_percent?: number | null;
    scope?: string;
    scope_label_vi?: string;
  } | null;
  payment_milestones: PaymentMilestone[];
  price_to_win_percent?: number;
  trace: { formula: string; rate_card_version: number; reference_snapshot_id: number; rounding: string };
}

export interface CheckReport {
  name?: string;
  code?: string;
  status: 'pass' | 'warning' | 'fail';
  message: string;
  deferred_to_m6?: boolean;
}

export interface ProposalSections {
  introduction: string;
  requirements_understanding: string;
  solution_overview: string;
  approach: string;
  schedule: string;
  team: string;
  assumptions_and_scope: string;
  risks: string;
}

export interface ProposalDraft {
  bid_id: number;
  sections: ProposalSections;
  assumptions_phrased: string[];
  scope_out_phrased: string[];
  price_gate: 'placeholder' | string;
  editable: boolean;
  updated_at: string;
  quotation_markdown?: string;
  customer_language?: CustomerLanguage;
  translations?: Partial<Record<CustomerLanguage, ProposalSections>>;
  document?: { page_size?: string; cover?: boolean; table_of_contents?: string[]; printable?: boolean };
}

export interface BidCriterion {
  id: string;
  label_vi: string;
  weight: number;
  score?: number | null;
  note_vi?: string | null;
}
export interface BidQualification {
  bid_id: number;
  criteria: BidCriterion[];
  decision?: 'bid' | 'no-bid' | null;
  confirmer?: string | null;
  suggestions: Array<Record<string, unknown>>;
  confirmed_at?: string | null;
}
export interface ProposalVersion {
  id: number;
  version: string;
  customer_language: string;
  sections: ProposalSections;
  sent: boolean;
  sent_at?: string | null;
  sent_note?: string | null;
  created_by: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// M7 — Xuất hồ sơ
// ---------------------------------------------------------------------------
export type ExportKind = 'docx' | 'xlsx' | 'pdf' | 'pptx' | 'bundle' | 'requirements';

export interface JaCheckIssue {
  severity: 'warning';
  section: string;
  message_vi: string;
  suggestion_ja: string;
  source: 'latin' | 'glossary' | 'name' | 'llm_context';
}

export interface JaCheckResult {
  result: 'pass' | 'warning';
  issues: JaCheckIssue[];
}

export interface ExportDownload {
  blob: Blob;
  filename: string;
  jaCheck: JaCheckResult | null;
}

export type SettingKey = 'company' | 'templates' | 'standard_content' | 'case_studies' | 'bid_no_bid' | 'effort' | 'rate_card' | 'factors' | 'confidence';
export interface SettingSummary {
  key: SettingKey;
  source: 'repo' | 'db';
  version: number;
  updated_by?: string | null;
  updated_at?: string | null;
  yaml_preview: string;
  payload: unknown;
}
export interface SettingsResponse { keys: SettingSummary[]; }
export interface SettingUpdated { key: SettingKey; version: number; source: 'db'; }
export interface HistoryItem {
  id: number;
  bid_id: number;
  project_name: string;
  customer_name: string;
  status: BidStatus;
  actor: string;
  action: string;
  field_changed?: string | null;
  note?: string | null;
  created_at: string;
}
export interface HistoryResponse { items: HistoryItem[]; total: number; }

export interface ApprovalResponse {
  status: BidStatus;
  locked: boolean;
  checks_report?: CheckReport[];
  decision?: ApprovalDecision;
  message?: string;
}

export interface ApprovalRequest {
  decision: ApprovalDecision;
  by: string;
  comment?: string | null;
  skip_with_reason?: string | null;
  contract_model?: ContractModel;
  contingency_percent?: number;
}

export interface UnlockResponse {
  locked: false;
  status: 'waiting_price_approval';
}

// ---------------------------------------------------------------------------
// Envelope lỗi chung (§2 — contract)
// ---------------------------------------------------------------------------

export interface ApiErrorDetails {
  [key: string]: unknown;
}

export interface ApiErrorEnvelope {
  error?: {
    code?: string;
    message?: string;
    details?: ApiErrorDetails;
  };
}

// ---------------------------------------------------------------------------
// Đợt 12/13 — Độ tin cậy ước lượng (thiet_ke_danh_gia.md §5.1)
// ---------------------------------------------------------------------------

export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type SignalStatus = 'pass' | 'warn' | 'fail' | 'na';

/** ConfidenceSignal — một tín hiệu độ tin cậy (§5.2). */
export interface ConfidenceSignal {
  key: string;
  label_vi: string;
  status: SignalStatus;
  detail_vi: string;
  data: Record<string, unknown>;
}

/** AnalogCase — một case tương tự trong analog (§5.4). */
export interface AnalogCase {
  id: string;
  title: string;
  similarity: number;
  direction?: string | null;
  market?: string | null;
  requirement_count?: number | null;
  actual_man_day?: Record<string, number> | null;
  actual_total: number;
  actual_duration_weeks?: Record<string, number | string> | null;
}

/** HistoryBiasOut — sai lệch lịch sử (§5.2). */
export interface HistoryBiasOut {
  direction: 'none' | 'above' | 'below' | null;
  median_actual_over_estimate: number | null;
  case_count: number;
}

/** AnalogOut — so với dự án tương tự (§5.1). */
export interface AnalogOut {
  cases: AnalogCase[];
  actual_total_range: number[];
  estimate_total: number | null;
  effort_midpoint: number | null;
  position: 'below' | 'inside' | 'above' | 'insufficient';
  history_bias: HistoryBiasOut;
}

/** ConfidenceOut — GET /api/bids/{id}/confidence (§5.1). */
export interface ConfidenceOut {
  level: ConfidenceLevel;
  level_label_vi: string;
  summary_vi: string;
  signals: ConfidenceSignal[];
  analog: AnalogOut;
  thresholds_version: number;
  case_studies_version: number;
}

// ---------------------------------------------------------------------------
// Đợt 13 — C: bản ghi duyệt kèm snapshot độ tin cậy (thiet_ke_danh_gia.md §5.5)
// ---------------------------------------------------------------------------

/** ApprovalRecord — một bản ghi duyệt từ GET /api/bids/{id}/approvals. */
export interface ApprovalRecord {
  id: number;
  kind: 'tech' | 'price';
  status: 'approved' | 'rejected';
  approver: string;
  reason: string | null;
  decided_at: string;
  /** Snapshot độ tin cậy lúc duyệt kỹ thuật (§5.5) — có thể null với bản ghi cũ. */
  snapshot: {
    confidence?: ConfidenceOut | null;
    case_studies_version?: number | null;
    confidence_thresholds_version?: number | null;
  } | null;
}

export interface ApprovalsResponse {
  items: ApprovalRecord[];
}

// ---------------------------------------------------------------------------
// Đợt 13 — D: nhập case study (thiet_ke_danh_gia.md §3.3)
// ---------------------------------------------------------------------------

export interface CaseStudyImportPreview {
  mode: 'preview';
  total: number;
  valid_count: number;
  error_count: number;
  valid: Array<Record<string, unknown>>;
  errors: string[];
}

export interface CaseStudyImportSave {
  mode: 'save';
  total: number;
  valid_count: number;
  error_count: number;
  saved: number;
  version: number;
  errors: string[];
}

// ---------------------------------------------------------------------------
// Đợt 13 — E: báo cáo đánh giá hệ thống (thiet_ke_danh_gia.md §6.4)
// ---------------------------------------------------------------------------

export interface EvalReport {
  provider: string;
  model: string;
  started_at: string;
  repeat: number;
  case_ids: string[];
  per_case: Record<string, Array<Record<string, unknown>>>;
  summary: Record<string, number>;
  seconds: number;
}
