import type {
  AnswerItem,
  AnswersResponse,
  EmailDraft,
  ApiErrorEnvelope,
  Bid,
  BidCreate,
  BidDetail,
  BidsListResponse,
  HealthResponse,
  PipelineStartResponse,
  QuestionsResponse,
  SampleKey,
  ChooseSolutionRequest,
  ChooseSolutionResponse,
  EffortResponse,
  EvaluationsResponse,
  ScheduleResponse,
  ScheduleUpdateRequest,
  WbsChange,
  WbsResponse,
  WbsSnapshotResponse,
  QuotationResponse,
  ProposalDraft,
  ApprovalRequest,
  ApprovalResponse,
  UnlockResponse,
  Attachment,
  AttachmentFileType,
  AttachmentUpdate,
  AttachmentListResponse,
  ParseResult,
  DataReadiness,
  ExportDownload,
  ExportKind,
  JaCheckResult,
  SettingsResponse,
  SettingKey,
  SettingUpdated,
  HistoryResponse,
  SamplePreview,
  BidQualification,
  DealStage,
  ProposalVersion,
  ProposalSections,
} from './types';

/**
 * Base root-relative (BR-10): mọi request đi qua "/api/...".
 * KHÔNG hardcode địa chỉ tuyệt đối (host:port) trong src/ — proxy /api → backend
 * chỉ được khai báo ở vite.config.ts (dev config) / cấu hình Preview (prod).
 */
const API_BASE = '/api';

export class ApiError extends Error {
  readonly status?: number;
  readonly code?: string;
  readonly details?: Record<string, unknown>;

  constructor(
    message: string,
    status?: number,
    code?: string,
    details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/**
 * Request chung: parse envelope lỗi {error:{code,message,details}} (contract §2)
 * và hiển thị `message` tiếng Việt từ backend (BR-07).
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new ApiError('Không kết nối được backend');
  }

  if (!res.ok) {
    let message = `Lỗi máy chủ (HTTP ${res.status})`;
    let code: string | undefined;
    let details: Record<string, unknown> | undefined;
    try {
      const body = (await res.json()) as ApiErrorEnvelope;
      if (body.error?.message) {
        message = body.error.message;
      }
      code = body.error?.code;
      details = body.error?.details;
    } catch {
      // body không phải JSON — giữ message mặc định
    }
    throw new ApiError(message, res.status, code, details);
  }

  return (await res.json()) as T;
}

function filenameFromDisposition(value: string | null, fallback: string): string {
  if (!value) return fallback;
  const match = value.match(/filename="?([^";]+)"?/i);
  return match?.[1] ? decodeURIComponent(match[1]) : fallback;
}

function jaCheckFromHeader(value: string | null): JaCheckResult | null {
  if (!value) return null;
  try {
    return JSON.parse(decodeURIComponent(value)) as JaCheckResult;
  } catch {
    return null;
  }
}

/** Tải binary do backend tạo; FE không tự sinh hoặc diễn giải nội dung file. */
export async function downloadExport(id: number, kind: ExportKind): Promise<ExportDownload> {
  const paths: Record<ExportKind, string> = {
    docx: `/bids/${id}/exports/proposal.docx`,
    xlsx: `/bids/${id}/exports/estimate.xlsx`,
    pdf: `/bids/${id}/exports/proposal.pdf`,
    bundle: `/bids/${id}/exports/bundle.zip`,
    requirements: `/bids/${id}/exports/requirements.xlsx`,
  };
  const fallback = `ho-so-${id}-${kind}`;
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${paths[kind]}`);
  } catch {
    throw new ApiError('Không kết nối được backend');
  }
  if (!response.ok) {
    let message = `Lỗi máy chủ (HTTP ${response.status})`;
    let code: string | undefined;
    let details: Record<string, unknown> | undefined;
    try {
      const body = (await response.json()) as ApiErrorEnvelope;
      message = body.error?.message ?? message;
      code = body.error?.code;
      details = body.error?.details;
    } catch { /* response lỗi không phải JSON */ }
    throw new ApiError(message, response.status, code, details);
  }
  return {
    blob: await response.blob(),
    filename: filenameFromDisposition(response.headers.get('Content-Disposition'), fallback),
    jaCheck: jaCheckFromHeader(response.headers.get('X-Ja-Check-Result')),
  };
}

function jsonPost(body: unknown): RequestInit {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
}

/** GET /api/health — trạng thái backend cho trang chủ. */
export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

export function getSettings(): Promise<SettingsResponse> {
  return request<SettingsResponse>('/settings');
}

export function updateSetting(key: SettingKey, yaml_content: string, by: string): Promise<SettingUpdated> {
  return request<SettingUpdated>(`/settings/${key}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ yaml_content, by }),
  });
}

export function getHistory(params?: { customer?: string; status?: string; bid_id?: number }): Promise<HistoryResponse> {
  const search = new URLSearchParams();
  if (params?.customer) search.set('customer', params.customer);
  if (params?.status) search.set('status', params.status);
  if (params?.bid_id != null) search.set('bid_id', String(params.bid_id));
  const qs = search.toString();
  return request<HistoryResponse>(`/history${qs ? `?${qs}` : ''}`);
}

// ---------------------------------------------------------------------------
// M2 — Hồ sơ (Module A)
// ---------------------------------------------------------------------------

/** POST /api/bids — tạo hồ sơ (FR-001). */
export function createBid(data: BidCreate): Promise<Bid> {
  return request<Bid>('/bids', jsonPost(data));
}

/** GET /api/bids — danh sách hồ sơ, lọc theo status/q, phân trang (FR-007). */
export function listBids(params?: {
  status?: string;
  q?: string;
  page?: number;
  page_size?: number;
  deal_stage?: string;
}): Promise<BidsListResponse> {
  const search = new URLSearchParams();
  if (params?.status) search.set('status', params.status);
  if (params?.q) search.set('q', params.q);
  if (params?.deal_stage) search.set('deal_stage', params.deal_stage);
  if (params?.page != null) search.set('page', String(params.page));
  if (params?.page_size != null) search.set('page_size', String(params.page_size));
  const qs = search.toString();
  return request<BidsListResponse>(`/bids${qs ? `?${qs}` : ''}`);
}

/** GET /api/bids/{id} — chi tiết hồ sơ + pipeline_progress (FR-007). */
export function getBid(id: number): Promise<BidDetail> {
  return request<BidDetail>(`/bids/${id}`);
}

export function getBidQualification(id: number): Promise<BidQualification> {
  return request<BidQualification>(`/bids/${id}/bid-qualification`);
}

export function updateBidQualification(id: number, data: Pick<BidQualification, 'criteria' | 'decision' | 'confirmer'>): Promise<BidQualification> {
  return request<BidQualification>(`/bids/${id}/bid-qualification`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
}

export function updateDealStage(id: number, deal_stage: DealStage, note?: string): Promise<{ bid_id: number; deal_stage: DealStage }> {
  return request<{ bid_id: number; deal_stage: DealStage }>(`/bids/${id}/deal-stage`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ deal_stage, note }) });
}

/** POST /api/bids/sample — nạp hồ sơ mẫu giả lập (FR-006, path đã sửa §2.2). */
export function loadSample(key?: SampleKey): Promise<Bid> {
  return request<Bid>('/bids/sample', jsonPost(key ? { sample_key: key } : {}));
}

export function getSamplePreview(key: SampleKey): Promise<SamplePreview> {
  return request<SamplePreview>(`/bids/sample/preview?sample_key=${encodeURIComponent(key)}`);
}

// ---------------------------------------------------------------------------
// M2 — Pipeline (Module C)
// ---------------------------------------------------------------------------

/** POST /api/bids/{id}/pipeline/start — chạy pipeline (FR-023). */
export function startPipeline(id: number): Promise<PipelineStartResponse> {
  return request<PipelineStartResponse>(`/bids/${id}/pipeline/start`, jsonPost({}));
}

/** POST /api/bids/{id}/rerun — chạy lại từ bước lỗi (M2: from_step=null). */
export function rerunPipeline(id: number): Promise<PipelineStartResponse> {
  return request<PipelineStartResponse>(
    `/bids/${id}/rerun`,
    jsonPost({ from_step: null, reason: 'Resume sau lỗi', by: 'presales' }),
  );
}

// ---------------------------------------------------------------------------
// M2 — Hỏi làm rõ (Module D)
// ---------------------------------------------------------------------------

/** GET /api/bids/{id}/questions — danh sách câu hỏi làm rõ (FR-010). */
export function getQuestions(id: number): Promise<QuestionsResponse> {
  return request<QuestionsResponse>(`/bids/${id}/questions`);
}

export async function downloadQuestions(id: number): Promise<ExportDownload> {
  const response = await fetch(`${API_BASE}/bids/${id}/questions/export`);
  if (!response.ok) throw new ApiError('Không tải được bảng câu hỏi', response.status);
  return {
    blob: await response.blob(),
    filename: filenameFromDisposition(response.headers.get('Content-Disposition'), `qa-${id}.xlsx`),
    jaCheck: null,
  };
}

export function importQuestions(id: number, file: File): Promise<AnswersResponse> {
  const form = new FormData();
  form.append('file', file);
  return request<AnswersResponse>(`/bids/${id}/questions/import`, { method: 'POST', body: form });
}

export function createEmailDraft(id: number): Promise<EmailDraft> {
  return request<EmailDraft>(`/bids/${id}/questions/email-draft`, jsonPost({}));
}

/** POST /api/bids/{id}/questions/{round}/answers — gửi trả lời (FR-011). */
export function submitAnswers(
  id: number,
  round: number,
  answers: AnswerItem[],
): Promise<AnswersResponse> {
  return request<AnswersResponse>(`/bids/${id}/questions/${round}/answers`, jsonPost({ answers }));
}

// ---------------------------------------------------------------------------
// M3 — Hướng giải pháp và effort
// ---------------------------------------------------------------------------

/** POST /api/bids/{id}/solution — chọn hoặc đổi hướng giải pháp. */
export function chooseSolution(
  id: number,
  data: ChooseSolutionRequest,
): Promise<ChooseSolutionResponse> {
  return request<ChooseSolutionResponse>(`/bids/${id}/solution`, jsonPost(data));
}

/** GET /api/bids/{id}/effort — effort do backend tính từ YAML. */
export function getEffort(id: number): Promise<EffortResponse> {
  return request<EffortResponse>(`/bids/${id}/effort`);
}

/** GET /api/bids/{id}/evaluations — cảnh báo đánh giá theo hướng cũ. */
export function getEvaluations(id: number): Promise<EvaluationsResponse> {
  return request<EvaluationsResponse>(`/bids/${id}/evaluations`);
}

export function listAttachments(id: number): Promise<AttachmentListResponse> {
  return request<AttachmentListResponse>(`/bids/${id}/attachments`);
}

export function uploadAttachment(id: number, file: File, fileType?: AttachmentFileType): Promise<Attachment> {
  const form = new FormData();
  form.append('file', file);
  const query = fileType ? `?file_type=${encodeURIComponent(fileType)}` : '';
  return request<Attachment>(`/bids/${id}/attachments${query}`, { method: 'POST', body: form });
}

export function updateAttachment(id: number, attachmentId: number, data: AttachmentUpdate): Promise<Attachment> {
  return request<Attachment>(`/bids/${id}/attachments/${attachmentId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
  });
}

export function parseAttachments(id: number): Promise<ParseResult> {
  return request<ParseResult>(`/bids/${id}/parse`, jsonPost({}));
}

export function confirmParse(id: number, dataReadiness: DataReadiness): Promise<Bid> {
  return request<Bid>(`/bids/${id}/parse/confirm`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data_readiness: dataReadiness, confirmed: true }),
  });
}

// ---------------------------------------------------------------------------
// M4 — WBS 3 cấp (Module F, §8.1/8.2/8.3)
// ---------------------------------------------------------------------------

/** GET /api/bids/{id}/wbs — xem WBS 3 cấp (FR-032, §8.1). */
export function getWbs(id: number): Promise<WbsResponse> {
  return request<WbsResponse>(`/bids/${id}/wbs`);
}

/**
 * PUT /api/bids/{id}/wbs — sửa WBS (FR-041, §8.2).
 * Backend tính lại tổng + check + lịch, KHÔNG gọi AI; response kèm recalculated.schedule.
 */
export function updateWbs(
  id: number,
  changes: WbsChange[],
  note?: string | null,
): Promise<WbsResponse> {
  return request<WbsResponse>(`/bids/${id}/wbs`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ changes, by: 'ai_developer', note: note ?? null }),
  });
}

/** POST /api/bids/{id}/wbs/snapshot — chụp snapshot WBS (FR-041.2, §8.3). */
export function snapshotWbs(id: number, reason: string): Promise<WbsSnapshotResponse> {
  return request<WbsSnapshotResponse>(
    `/bids/${id}/wbs/snapshot`,
    jsonPost({ reason, by: 'ai_developer' }),
  );
}

// ---------------------------------------------------------------------------
// M4 — Master schedule (Module F, §8.4/8.4a)
// ---------------------------------------------------------------------------

/** GET /api/bids/{id}/schedule — master schedule (FR-034, §8.4). */
export function getSchedule(id: number): Promise<ScheduleResponse> {
  return request<ScheduleResponse>(`/bids/${id}/schedule`);
}

/** PUT /api/bids/{id}/schedule — cập nhật tham số lịch, code tính lại (FR-034, §8.4a). */
export function updateSchedule(
  id: number,
  params: ScheduleUpdateRequest,
): Promise<ScheduleResponse> {
  return request<ScheduleResponse>(`/bids/${id}/schedule`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
}

/**
 * POST /api/bids/{id}/rerun — chạy lại từ bước WBS (M4, §5.3):
 * backend tự snapshot WBS cũ, giữ evaluate + solution, chạy lại wbs (+ downstream).
 */
export function rerunPipelineFromWbs(id: number, reason: string): Promise<PipelineStartResponse> {
  return request<PipelineStartResponse>(
    `/bids/${id}/rerun`,
    jsonPost({ from_step: 'wbs', reason, by: 'ai_developer' }),
  );
}

// ---------------------------------------------------------------------------
// M5 — quotation, proposal và approvals
// ---------------------------------------------------------------------------

export function getQuotation(id: number): Promise<QuotationResponse> {
  return request<QuotationResponse>(`/bids/${id}/quotation`);
}

export function updateQuotation(id: number, data: Record<string, unknown>): Promise<QuotationResponse> {
  return request<QuotationResponse>(`/bids/${id}/quotation`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
  });
}

export function getProposal(id: number): Promise<ProposalDraft> {
  return request<ProposalDraft>(`/bids/${id}/proposal`);
}

export function listProposalVersions(id: number): Promise<ProposalVersion[]> {
  return request<ProposalVersion[]>(`/bids/${id}/proposal/versions`);
}

export function createProposalVersion(id: number, by = 'presales', language?: 'vi' | 'en' | 'ja'): Promise<ProposalVersion> {
  return request<ProposalVersion>(`/bids/${id}/proposal/versions`, jsonPost({ by, language }));
}

export function markProposalVersionSent(id: number, versionId: number, note?: string): Promise<ProposalVersion> {
  return request<ProposalVersion>(`/bids/${id}/proposal/versions/${versionId}/sent`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ note: note || null }) });
}

export function translateProposal(id: number, language: 'vi' | 'en' | 'ja', sections?: ProposalSections): Promise<ProposalDraft> {
  return request<ProposalDraft>(`/bids/${id}/proposal/translate`, { ...jsonPost({ language, sections, by: 'presales' }) });
}

export function updateProposal(id: number, sections: ProposalDraft['sections']): Promise<ProposalDraft> {
  return request<ProposalDraft>(`/bids/${id}/proposal`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sections, by: 'presales' }),
  });
}

export function approveTech(id: number, data: ApprovalRequest): Promise<ApprovalResponse> {
  return request<ApprovalResponse>(`/bids/${id}/approvals/tech`, {
    ...jsonPost(data),
    headers: { 'Content-Type': 'application/json', 'X-User': 'ai_developer' },
  });
}

export function approvePrice(id: number, data: ApprovalRequest): Promise<ApprovalResponse> {
  return request<ApprovalResponse>(`/bids/${id}/approvals/price`, {
    ...jsonPost(data),
    headers: { 'Content-Type': 'application/json', 'X-User': 'manager' },
  });
}

export function unlockBid(id: number, reason: string): Promise<UnlockResponse> {
  return request<UnlockResponse>(`/bids/${id}/unlock`, {
    ...jsonPost({ reason, by: 'manager' }),
    headers: { 'Content-Type': 'application/json', 'X-User': 'manager' },
  });
}
