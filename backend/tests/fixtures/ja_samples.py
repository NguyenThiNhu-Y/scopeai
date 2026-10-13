"""Bộ mẫu tiếng Nhật 20 câu — fixture FR-025 (xây ở M2, kiểm tra ở M7).

- 10 câu CHUẨN (không lỗi).
- 10 câu có LỖI CỐ Ý (latin lẫn, sai thuật ngữ glossary, sai chính tả tên công ty)
  kèm ``issue_types`` để test_ja_check (M7) đối chiếu — ngưỡng ≥ 90%.

Tên công ty chuẩn (giả lập): 株式会社デモ商事.
"""

from __future__ import annotations

# Tên công ty đúng (giả lập) — dùng cho lỗi chính tả tên.
COMPANY_NAME = "株式会社デモ商事"

CORRECT_SAMPLES: list[str] = [
    "本提案では、要件定義から開発、運用保守までの一貫した支援を提供いたします。",
    "御社のご要望に合わせて、最適なソリューションをご提案いたします。",
    "納期は年末を予定しております。",
    "データ移行作業は、週末に実施する計画です。",
    "品質管理チームがテスト工程を担当いたします。",
    "ご不明な点がございましたら、いつでもご連絡ください。",
    "契約書類は電子署名にて対応させていただきます。",
    "プロジェクト体制は、管理者・開発者・テスターで構成されます。",
    "初回のご相談は無料で承っております。",
    "詳細な仕様書は、打ち合わせ後に共有いたします。",
]

ERROR_SAMPLES: list[dict] = [
    {
        "text": "本システムは RAG 技術を活用し、検索精度を向上させます。",
        "issue_types": ["latin"],
    },
    {
        "text": "画面遷移は UX を考慮して設計しました。",
        "issue_types": ["latin"],
    },
    {
        "text": "クラウド上の DB に接続してデータを取得します。",
        "issue_types": ["latin"],
    },
    {
        "text": "API 経由で外部システムと連携します。",
        "issue_types": ["latin"],
    },
    {
        "text": "本件のご要望を整理し、要求定義フェーズを開始します。",
        "issue_types": ["glossary"],
    },
    {
        "text": "プロジェクトマネジャーが全体の進捗を管理します。",
        "issue_types": ["glossary"],
    },
    {
        "text": "ご提案内容をまとめた見積もり書を提出いたします。",
        "issue_types": ["glossary"],
    },
    {
        "text": "株式会社デモ商社からのご依頼についてご連絡いたします。",
        "issue_types": ["name"],
    },
    {
        "text": "デモ商社株式会社の田中様と打ち合わせを実施しました。",
        "issue_types": ["name"],
    },
    {
        "text": "デモ商社株式会社のご要望に基づき、 RAG 方式を提案します。",
        "issue_types": ["name", "latin"],
    },
]

ALL_CORRECT = CORRECT_SAMPLES
ALL_ERRORS = ERROR_SAMPLES
ALL_SAMPLES = CORRECT_SAMPLES + [e["text"] for e in ERROR_SAMPLES]