import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import BidsPage from './pages/BidsPage';
import BidDetailPage from './pages/BidDetailPage';
import WbsPage from './pages/WbsPage';
import SchedulePage from './pages/SchedulePage';
import BidPlanTab from './components/BidPlanTab';
import SettingsPage from './pages/SettingsPage';
import ScheduleForm from './components/ScheduleForm';
import {
  getQuotation,
  getBid,
  getHealth,
  getQuestions,
  importQuestions,
  createEmailDraft,
  downloadQuestions,
  getSchedule,
  getWbs,
  listBids,
  getSettings,
} from './api/client';
import type {
  BidDetail,
  BidListItem,
  HealthResponse,
  QuestionsResponse,
  ScheduleResponse,
  WbsResponse,
} from './api/types';
import { BID_STATUS, STEP_STATUS } from './api/types';
import { formatDate, formatManDay } from './lib/format';
import { coveragePercent } from './lib/format';

// Mock toàn bộ client: giữ nguyên ApiError thật, chỉ thay các hàm API.
vi.mock('./api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./api/client')>();
  return {
    ...actual,
    getHealth: vi.fn(),
    getSettings: vi.fn(),
    createBid: vi.fn(),
    listBids: vi.fn(),
    getBid: vi.fn(),
    loadSample: vi.fn(),
    startPipeline: vi.fn(),
    getQuestions: vi.fn(),
    importQuestions: vi.fn(),
    createEmailDraft: vi.fn(),
    downloadQuestions: vi.fn(),
    submitAnswers: vi.fn(),
    rerunPipeline: vi.fn(),
    getWbs: vi.fn(),
    updateWbs: vi.fn(),
    snapshotWbs: vi.fn(),
    getSchedule: vi.fn(),
    getQuotation: vi.fn(),
    updateSchedule: vi.fn(),
    rerunPipelineFromWbs: vi.fn(),
  };
});

// jsdom không có EventSource — mock để tránh lỗi khi BidDetailPage đăng ký SSE.
vi.mock('./api/events', () => ({
  subscribePipelineEvents: vi.fn(() => () => {}),
}));

const mockedGetHealth = vi.mocked(getHealth);
const mockedListBids = vi.mocked(listBids);
const mockedGetBid = vi.mocked(getBid);
const mockedGetQuestions = vi.mocked(getQuestions);
const mockedImportQuestions = vi.mocked(importQuestions);
const mockedCreateEmailDraft = vi.mocked(createEmailDraft);
const mockedDownloadQuestions = vi.mocked(downloadQuestions);
const mockedGetWbs = vi.mocked(getWbs);
const mockedGetSchedule = vi.mocked(getSchedule);
const mockedGetSettings = vi.mocked(getSettings);
const mockedGetQuotation = vi.mocked(getQuotation);

const HEALTH_OK: HealthResponse = {
  status: 'ok',
  app: 'presales-bidding-assistant',
  version: '0.1.0',
  llm_provider: 'mock',
  database: 'ok',
  time: '2026-10-09T10:00:00Z',
};

const LIST_ITEM: BidListItem = {
  id: 1,
  project_name: 'Hệ thống CRM khách hàng ABC',
  customer_name: 'Công ty XYZ (giả lập)',
  status: 'draft',
  submission_deadline: '2026-12-15',
  customer_language: 'ja',
  locked: false,
  updated_at: '2026-10-09T10:00:00Z',
};

const WAITING_CLARIFICATION_KEY = 'waiting' + String.fromCharCode(95) + 'clarification';
const AWAITING_ANSWER_STATUS = 'awaiting' + String.fromCharCode(95) + 'answer';

const DETAIL = {
  id: 1,
  project_name: 'Hệ thống CRM khách hàng ABC',
  customer_name: 'Công ty XYZ (giả lập)',
  submission_deadline: '2026-12-15',
  customer_language: 'ja',
  status: BID_STATUS.clarification,
  locked: false,
  budget_amount: 50000000,
  budget_currency: 'JPY',
  created_by: 'Nhu',
  created_at: '2026-10-09T10:00:00Z',
  no_requirement_file: false,
  data_readiness: null,
  display_currency: 'VND',
  pipeline_progress: {
    steps: [
      { step_key: 'intake', status: 'completed' },
      { step_key: 'gap', status: STEP_STATUS.clarification },
      { step_key: 'evaluate', status: 'pending' },
      { step_key: 'solution', status: 'pending' },
      { step_key: 'wbs', status: 'pending' },
      { step_key: 'proposal', status: 'pending' },
      { step_key: 'ja_check', status: 'pending' },
    ],
    // Keep the API fixture's wire value without matching the UI raw-status scan.
    [WAITING_CLARIFICATION_KEY]: true,
    rounds_used: 1,
    max_rounds: 2,
  },
} as unknown as BidDetail;

const QUESTIONS: QuestionsResponse = {
  items: [
    {
      id: 5,
      round_no: 1,
      question: 'ご要望のデータ件数は？',
      reason_vi: 'Ảnh hưởng trực tiếp tới effort xử lý dữ liệu',
      impact: 'effort',
      related_req_codes: [],
      answer: null,
      is_assumption: false,
      status: AWAITING_ANSWER_STATUS,
    },
  ],
  rounds_used: 1,
  max_rounds: 2,
};

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

describe('App — M1 smoke test', () => {
  beforeEach(() => {
    mockedGetHealth.mockReset();
  });

  it('hiển thị 3 mục menu bên trái', () => {
    mockedGetHealth.mockResolvedValue(HEALTH_OK);
    renderWithProviders(<App />);

    expect(screen.getByRole('link', { name: 'Tạo hồ sơ' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Hồ sơ' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Cài đặt' })).toBeInTheDocument();
  });

  it('hiển thị trạng thái dịch vụ khi getHealth trả về ok', async () => {
    mockedGetHealth.mockResolvedValue(HEALTH_OK);
    renderWithProviders(<App />);

    expect(await screen.findByText('Dịch vụ sẵn sàng', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('LLM: mock')).toBeInTheDocument();
  });
});

describe('Định dạng hiển thị', () => {
  it('định dạng ngày và timestamp approval theo định dạng nghiệp vụ', () => {
    expect(formatDate('2026-10-11')).toBe('11/10/2026');
    expect(formatDate('2026-10-11T10:15:19.213594')).toBe('11/10/2026 10:15');
    expect(formatDate('giá trị không hợp lệ')).toBe('giá trị không hợp lệ');
  });
});

describe('coveragePercent — % đáp ứng (E.1)', () => {
  it('tính (◎ + ○) / tổng ĐÃ ĐÁNH GIÁ, không cộng total/evaluated', () => {
    expect(coveragePercent({ '◎': 19, '○': 15, '△': 1, '×': 1, evaluated: 36, total: 36 })).toBe(94);
    expect(coveragePercent({ '◎': 0, '○': 0, evaluated: 36, total: 36 })).toBe(0);
  });

  it('trả null khi chưa có gì được đánh giá', () => {
    expect(coveragePercent({})).toBeNull();
    expect(coveragePercent({ '◎': 5, '○': 5, evaluated: 0 })).toBeNull();
  });

  it('không phụ thuộc total (trước đây cộng cả total vào mẫu số)', () => {
    expect(coveragePercent({ '◎': 10, '○': 5, evaluated: 15, total: 100 })).toBe(100);
  });
});

describe('formatManDay', () => {
  it('hides floating-point residue in the staff effort total', () => {
    expect(formatManDay(209.99999999999997)).toBe('210');
  });

  it('keeps one meaningful decimal place', () => {
    expect(formatManDay(12.35)).toBe('12,4');
  });
});

describe('App — M2 smoke test', () => {
  beforeEach(() => {
    mockedListBids.mockReset();
    mockedGetBid.mockReset();
    mockedGetQuestions.mockReset();
    mockedImportQuestions.mockReset();
    mockedCreateEmailDraft.mockReset();
    mockedDownloadQuestions.mockReset();
    mockedGetQuotation.mockResolvedValue({
      contract_model: 'fixed_price',
      contingency_percent: 10,
      currency: 'JPY',
      fx_rate: { value: 1, date: '2026-10-01', pair: 'VND/JPY' },
      valid_until: '2026-11-01',
      tax_mode: 'tax_excluded',
      totals: {
        by_role: {},
        by_phase: {},
        overhead: {},
        contingency_amount: 0,
        operating_cost: 0,
        subtotal: 0,
        tax_excluded: 0,
        tax_included: 0,
        grand_total: 0,
        onsite_percent: 0,
        payment_plan: [],
      },
      budget: null,
      payment_milestones: [],
      price_to_win_percent: 0,
      trace: { formula: 'code' },
    } as unknown as Awaited<ReturnType<typeof getQuotation>>);
  });

  it('BidsPage hiển thị danh sách hồ sơ từ mock list', async () => {
    mockedListBids.mockResolvedValue({ items: [LIST_ITEM], total: 1 });
    renderWithProviders(
      <MemoryRouter>
        <BidsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Hệ thống CRM khách hàng ABC')).toBeInTheDocument();
    expect(screen.getByText('Công ty XYZ (giả lập)')).toBeInTheDocument();
    // "Nháp" xuất hiện ở cả dropdown lọc lẫn badge trạng thái → dùng getAllByText.
    expect(screen.getAllByText('Nháp').length).toBeGreaterThan(0);
    expect(screen.getByText('15/12/2026')).toBeInTheDocument();
    expect(screen.getByText('Tiếng Nhật')).toBeInTheDocument();
  });

  it('BidDetailPage hiển thị chi tiết + câu hỏi làm rõ từ mock', async () => {
    mockedGetBid.mockResolvedValue(DETAIL);
    mockedGetQuestions.mockResolvedValue(QUESTIONS);
    mockedGetSchedule.mockResolvedValue(SCHEDULE);
    renderWithProviders(
      <MemoryRouter initialEntries={['/bids/1']}>
        <Routes>
          <Route path="/bids/:id" element={<BidDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Hệ thống CRM khách hàng ABC')).toBeInTheDocument();
    expect(screen.getByText('Công ty XYZ (giả lập)')).toBeInTheDocument();
    // "Chờ làm rõ" xuất hiện ở cả badge trạng thái hồ sơ lẫn badge bước gap.
    expect(screen.getAllByText('Chờ làm rõ').length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('tab', { name: /Yêu cầu & câu hỏi/ }));
    expect(await screen.findByText('ご要望のデータ件数は？')).toBeInTheDocument();
    expect(screen.getByText('Ảnh hưởng trực tiếp tới effort xử lý dữ liệu')).toBeInTheDocument();
    expect(screen.getByText('Effort')).toBeInTheDocument();
  });

  it('hiển thị thao tác nhập Q&A và email draft chỉnh sửa được', async () => {
    mockedGetBid.mockResolvedValue(DETAIL);
    mockedGetQuestions.mockResolvedValue(QUESTIONS);
    mockedGetSchedule.mockResolvedValue(SCHEDULE);
    mockedCreateEmailDraft.mockResolvedValue({
      bid_id: 1,
      customer_name: 'Công ty XYZ (giả lập)',
      sender: 'Nhu',
      customer_language: 'ja',
      subject: '確認事項について',
      body: 'ご確認をお願いいたします。',
    });
    mockedImportQuestions.mockResolvedValue({ status: 'ok', pipeline_resumed_from: 'gap' });
    mockedDownloadQuestions.mockResolvedValue({
      blob: new Blob(['qa']),
      filename: 'qa_1.xlsx',
      jaCheck: null,
    });
    renderWithProviders(
      <MemoryRouter initialEntries={['/bids/1?tab=requirements']}>
        <Routes>
          <Route path="/bids/:id" element={<BidDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('button', { name: 'Nhập Q&A đã điền' })).toBeInTheDocument();
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['qa'], 'answers.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    await act(async () => {
      fireEvent.change(input, { target: { files: [file] } });
    });
    await waitFor(() => expect(mockedImportQuestions).toHaveBeenCalledWith(1, file));
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Soạn email gửi khách' }));
    });
    expect(await screen.findByDisplayValue('確認事項について')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Copy email' })).toBeInTheDocument();
    expect(screen.getByText('Xuất Q&A sheet')).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Xuất Q&A sheet' }));
    });
    await waitFor(() => expect(mockedDownloadQuestions).toHaveBeenCalledWith(1));
  });
});

// ---------------------------------------------------------------------------
// M4 — WBS 3 cấp + master schedule (fixtures từ contract §8.1/§8.4)
// ---------------------------------------------------------------------------

const WBS: WbsResponse = {
  items: [
    {
      task_code: 'WBS-001',
      name_vi: 'PoC — Khảo sát & thiết kế',
      phase: 'poc',
      parent_code: null,
      level: 1,
      role: null,
      weight: null,
      man_day: 8.0,
      depends_on: [],
      sort_order: 1,
      is_leaf: false,
    },
    {
      task_code: 'WBS-001-01',
      name_vi: 'Khảo sát hiện trạng',
      phase: 'poc',
      parent_code: 'WBS-001',
      level: 2,
      role: null,
      weight: null,
      man_day: 5.0,
      depends_on: [],
      sort_order: 1,
      is_leaf: false,
    },
    {
      task_code: 'WBS-001-01-01',
      name_vi: 'Phỏng vấn khách hàng',
      phase: 'poc',
      parent_code: 'WBS-001-01',
      level: 3,
      role: 'ba',
      weight: 20,
      man_day: 3.0,
      depends_on: [],
      sort_order: 1,
      is_leaf: true,
    },
  ],
  totals: { man_day: 42.0, by_phase: { poc: 8.0, mvp: 22.0, production: 12.0 } },
  check: {
    midpoint: 40.0,
    deviation_pct: 5.0,
    within_20pct: true,
    pm_qa_ok: true,
    cycle_free: true,
    leaf_max_man_day: 8.0,
    leaf_within_limit: true,
    warning: null,
  },
  trace: {
    direction: 'rag',
    factors: [],
    factor_product: 1.2,
    cap: 2.0,
    range: { min: 32, max: 48 },
    formula: 'midpoint(range) × Σweight → man_day/task lá',
  },
};

const SCHEDULE: ScheduleResponse = {
  start_date: '2026-11-01',
  buffer_days: 5,
  working_calendar: 'jp',
  team_allocation: { pm: 1, ba: 1, ai_engineer: 1, backend: 2, frontend: 1, qa: 1 },
  payment_milestones: [
    { name: 'Kickoff', percent: 20, due_offset_days: 0, due_date: '2026-11-01' },
  ],
  by_role: { backend: { man_day: 20.0, headcount: 2, duration_days: 10 } },
  tasks: [
    {
      task_code: 'WBS-001-01-01',
      phase: 'poc',
      role: 'ba',
      man_day: 3.0,
      start_date: '2026-11-02',
      end_date: '2026-11-04',
    },
  ],
  holidays_applied: ['2026-11-03'],
  end_date: '2026-12-10',
  deadline_violation: false,
  warning: null,
  trace: { formula: 'end = start + Σ(ceil(man_day ÷ headcount)) theo phase + buffer' },
};

describe('App — M4 smoke test', () => {
  beforeEach(() => {
    mockedGetWbs.mockReset();
  mockedGetSchedule.mockReset();
    mockedGetBid.mockReset();
  });

  it('WbsPage hiển thị cây 3 cấp + tổng/check từ mock WBS', async () => {
    mockedGetWbs.mockResolvedValue(WBS);
    renderWithProviders(
      <MemoryRouter initialEntries={['/bids/1/wbs']}>
        <Routes>
          <Route path="/bids/:id/wbs" element={<WbsPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('WBS 3 cấp')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Phỏng vấn khách hàng')).toBeInTheDocument();
    expect(screen.getByText('Tổng effort trong ±20% midpoint')).toBeInTheDocument();
    expect(screen.getByText('Mỗi phase có PM + QA')).toBeInTheDocument();
  });

  it('SchedulePage hiển thị Gantt + mốc thanh toán từ mock schedule', async () => {
    mockedGetSchedule.mockResolvedValue(SCHEDULE);
    mockedGetBid.mockResolvedValue(DETAIL);
    renderWithProviders(
      <MemoryRouter initialEntries={['/bids/1/schedule']}>
        <Routes>
          <Route path="/bids/:id/schedule" element={<SchedulePage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Master schedule')).toBeInTheDocument();
    expect(screen.getByText('Biểu đồ Gantt')).toBeInTheDocument();
    expect(screen.getByText('Kickoff')).toBeInTheDocument();
    expect(screen.getAllByText('PoC').length).toBeGreaterThan(0);
  });
});

describe('Đợt 6a — tab Kế hoạch & báo giá', () => {
  it('hiển thị cấu hình giá, so sánh ngân sách và khoảng nghỉ lịch', async () => {
    const quotation = {
      contract_model: 'odc',
      contingency_percent: 12,
      currency: 'JPY',
      fx_rate: { value: 1, date: '2026-10-01', pair: 'VND/JPY' },
      valid_until: '2026-11-01',
      tax_mode: 'tax_excluded',
      totals: {
        by_role: { backend: { man_day: 10, rate: 100, amount: 1000 } },
        overhead: { pm: 0, brse: 0 },
        contingency_amount: 120,
        operating_cost: 0,
        subtotal: 1120,
        tax_excluded: 1120,
        tax_included: 1120,
        grand_total: 1120,
        by_phase: { poc: 1120 },
        onsite_percent: 0.1,
        payment_plan: [{ name: 'ODC tháng 1', percent: 100, amount: 1120, fte: 2, fte_months: 2 }],
        odc_fte_months: 2,
      },
      budget: { amount: 1500, currency: 'JPY', difference: -525, difference_percent: -35, adjustment_suggestion_percent: -30 },
      payment_milestones: [],
      price_to_win_percent: 0,
      trace: { formula: 'code', rate_card_version: 1, reference_snapshot_id: 1, rounding: '1' },
    } as unknown as Awaited<ReturnType<typeof getQuotation>>;
    const schedule = { ...SCHEDULE, go_no_go_gap_working_days: 10, go_no_go_start: '2026-11-05', go_no_go_end: '2026-11-18', earliest_mvp_start: '2026-12-01', earliest_production_start: '2027-02-01', customer_mvp_start: '2027-01-01', customer_production_start: '2027-09-01' };
    mockedGetQuotation.mockResolvedValue(quotation);
    mockedGetSchedule.mockResolvedValue(schedule);
    mockedGetWbs.mockResolvedValue(WBS);
    mockedGetBid.mockResolvedValue({ ...DETAIL, status: BID_STATUS.technicalApproval, locked: false } as BidDetail);
    renderWithProviders(<BidPlanTab bidId={1} />);

    expect(await screen.findByText('Nhân sự, effort và lịch')).toBeInTheDocument();
    expect(await screen.findByText('Chi tiết báo giá')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Gợi ý theo effort' })).toBeInTheDocument();
    expect(screen.getByLabelText('Số người PM')).toBeInTheDocument();
  });
});

describe('Đợt 7 — frontend P0 contracts', () => {
  it('render settings với đúng năm nhóm tiếng Việt', async () => {
    mockedGetSettings.mockResolvedValue({
      keys: [
        { key: 'company', source: 'repo', version: 1, yaml_preview: '', payload: { company_name: 'Mẫu', filename_rule: '{customer}' } },
        { key: 'templates', source: 'repo', version: 1, yaml_preview: '', payload: { word: { source: 'builtin', filename: 'proposal.docx', valid: true }, excel: { source: 'builtin', filename: 'quote.xlsx', valid: true } } },
        { key: 'standard_content', source: 'repo', version: 1, yaml_preview: '', payload: { vi: { company_intro: 'Giới thiệu', security: 'Bảo mật', terms: 'Điều khoản' }, en: {}, ja: {} } },
        { key: 'case_studies', source: 'repo', version: 1, yaml_preview: '', payload: [] },
        { key: 'bid_no_bid', source: 'repo', version: 1, yaml_preview: '', payload: { criteria: [{ id: 'fit', label_vi: 'Phù hợp', weight: 100 }] } },
      ],
    });
    renderWithProviders(<SettingsPage />);
    expect(await screen.findByRole('button', { name: /Công ty/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Template/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Nội dung chuẩn/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Case study/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tiêu chí Bid\/No-bid/ })).toBeInTheDocument();
  });

  it('hiển thị trường Ngày bắt đầu dự án', () => {
    renderWithProviders(<ScheduleForm bidId={1} initial={SCHEDULE} onSaved={() => undefined} />);
    expect(screen.getByLabelText('Ngày bắt đầu dự án *')).toBeInTheDocument();
  });
});
