import { useMemo, useState } from 'react';
import { Layout } from '../../../shared/components/Layout';
import { useAuth } from '../../auth/hooks/useAuth';

interface CandidateRow {
  id: string;
  surname: string;
  fullName: string;
  age: number;
  gender: string;
  location: string;
  approachStatus: string;
  experienceCategory: string;
  role: string;
  company: string;
  salary: string;
  salaryValue: number;
  desiredLocation: string;
  school: string;
  phone: string;
  address: string;
}

interface ScoutTemplate {
  id: string;
  name: string;
  body: string;
}

export const CandidateSearchPage = () => {
  const { user } = useAuth();
  const [keyword, setKeyword] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [profileCandidateId, setProfileCandidateId] = useState<string | null>(null);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [bulkMessage, setBulkMessage] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [newTemplateName, setNewTemplateName] = useState('');
  const [showTemplateNameModal, setShowTemplateNameModal] = useState(false);
  const [filters, setFilters] = useState({
    approachStatus: '',
    experienceCategory: '',
    desiredLocation: '',
    ageRange: '',
    salaryRange: '',
  });
  const [savedFilters, setSavedFilters] = useState<
    Array<{ id: string; name: string; keyword: string; filters: typeof filters }>
  >([]);
  const [showSaveFilterModal, setShowSaveFilterModal] = useState(false);
  const [saveFilterName, setSaveFilterName] = useState('');

  const companyKey = user?.name || 'デモ企業';
  const [templatesByCompany, setTemplatesByCompany] = useState<Record<string, ScoutTemplate[]>>({
    [companyKey]: [
      {
        id: 'casual',
        name: 'カジュアル面談のご案内',
        body: '○○様\nはじめまして。弊社の求人をご覧いただきありがとうございます。まずはカジュアルにお話しできれば幸いです。',
      },
      {
        id: 'detail',
        name: '選考案内（詳細確認）',
        body: '○○様\nご経歴を拝見し、ぜひ一度お話ししたくご連絡しました。',
      },
      {
        id: 'schedule',
        name: '日程調整のお願い',
        body: '○○様\n貴重なお時間をいただけますと幸いです。ご都合の良い日程をお知らせください。',
      },
    ],
  });

  const candidates: CandidateRow[] = [
    {
      id: 'A01162410',
      surname: '田中',
      fullName: '田中 太郎',
      age: 40,
      gender: '男性',
      location: '東京都',
      approachStatus: '未対応',
      experienceCategory: '営業',
      role: 'カスタマーサクセス1年',
      company: '日本立友ソフト株式会社',
      salary: '380万円',
      salaryValue: 380,
      desiredLocation: '東京都',
      school: '早稲田大学院',
      phone: '090-1234-5678',
      address: '東京都新宿区西新宿1-1-1',
    },
    {
      id: 'A01584467',
      surname: '佐藤',
      fullName: '佐藤 花子',
      age: 40,
      gender: '女性',
      location: '東京都',
      approachStatus: '連絡中',
      experienceCategory: 'デザイナー',
      role: 'Webデザイナー3年',
      company: '株式会社アドバンスト・ソフト',
      salary: '450万円',
      salaryValue: 450,
      desiredLocation: '東京都',
      school: '日本工学院専門学校',
      phone: '080-2345-6789',
      address: '東京都渋谷区渋谷2-2-2',
    },
    {
      id: 'A01600895',
      surname: '高橋',
      fullName: '高橋 恒一',
      age: 51,
      gender: '男性',
      location: '神奈川県',
      approachStatus: '面談調整',
      experienceCategory: 'バックオフィス',
      role: '総務1年',
      company: '株式会社ワールドスタッフ',
      salary: '320万円',
      salaryValue: 320,
      desiredLocation: '岩手県',
      school: '岩手県立大船渡高専',
      phone: '070-3456-7890',
      address: '神奈川県横浜市西区みなとみらい3-3-3',
    },
    {
      id: 'A01710982',
      surname: '鈴木',
      fullName: '鈴木 一郎',
      age: 60,
      gender: '男性',
      location: '神奈川県',
      approachStatus: '未対応',
      experienceCategory: '営業',
      role: '法人営業20年',
      company: '株式会社サンウェル',
      salary: '800万円',
      salaryValue: 800,
      desiredLocation: '神奈川県',
      school: '慶應義塾大学',
      phone: '090-4567-8901',
      address: '神奈川県川崎市幸区堀川町4-4-4',
    },
  ];

  const filteredCandidates = useMemo(() => {
    if (!keyword.trim()) {
      return candidates.filter((candidate) => {
        if (filters.approachStatus && candidate.approachStatus !== filters.approachStatus) return false;
        if (filters.experienceCategory && candidate.experienceCategory !== filters.experienceCategory) return false;
        if (filters.desiredLocation && candidate.desiredLocation !== filters.desiredLocation) return false;
        if (filters.ageRange) {
          if (filters.ageRange === '20s' && (candidate.age < 20 || candidate.age >= 30)) return false;
          if (filters.ageRange === '30s' && (candidate.age < 30 || candidate.age >= 40)) return false;
          if (filters.ageRange === '40s' && (candidate.age < 40 || candidate.age >= 50)) return false;
          if (filters.ageRange === '50s' && (candidate.age < 50 || candidate.age >= 60)) return false;
          if (filters.ageRange === '60s' && candidate.age < 60) return false;
        }
        if (filters.salaryRange) {
          if (filters.salaryRange === '300+' && candidate.salaryValue < 300) return false;
          if (filters.salaryRange === '500+' && candidate.salaryValue < 500) return false;
          if (filters.salaryRange === '700+' && candidate.salaryValue < 700) return false;
        }
        return true;
      });
    }
    const normalized = keyword.trim();
    return candidates.filter((candidate) => {
      if (filters.approachStatus && candidate.approachStatus !== filters.approachStatus) return false;
      if (filters.experienceCategory && candidate.experienceCategory !== filters.experienceCategory) return false;
      if (filters.desiredLocation && candidate.desiredLocation !== filters.desiredLocation) return false;
      if (filters.ageRange) {
        if (filters.ageRange === '20s' && (candidate.age < 20 || candidate.age >= 30)) return false;
        if (filters.ageRange === '30s' && (candidate.age < 30 || candidate.age >= 40)) return false;
        if (filters.ageRange === '40s' && (candidate.age < 40 || candidate.age >= 50)) return false;
        if (filters.ageRange === '50s' && (candidate.age < 50 || candidate.age >= 60)) return false;
        if (filters.ageRange === '60s' && candidate.age < 60) return false;
      }
      if (filters.salaryRange) {
        if (filters.salaryRange === '300+' && candidate.salaryValue < 300) return false;
        if (filters.salaryRange === '500+' && candidate.salaryValue < 500) return false;
        if (filters.salaryRange === '700+' && candidate.salaryValue < 700) return false;
      }
      return (
        candidate.role.includes(normalized) ||
        candidate.company.includes(normalized) ||
        candidate.school.includes(normalized) ||
        candidate.location.includes(normalized) ||
        candidate.desiredLocation.includes(normalized)
      );
    });
  }, [candidates, filters, keyword]);

  const allSelected = filteredCandidates.length > 0 && selectedIds.length === filteredCandidates.length;

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredCandidates.map((candidate) => candidate.id));
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const handleBulkScout = () => {
    if (selectedIds.length === 0) return;
    setShowBulkModal(true);
  };

  const currentTemplates = templatesByCompany[companyKey] || [];
  const selectedProfileCandidate = useMemo(
    () => candidates.find((candidate) => candidate.id === profileCandidateId) || null,
    [candidates, profileCandidateId]
  );
  const profileCandidate = selectedProfileCandidate ?? candidates[0];
  const isProfileOpen = selectedProfileCandidate !== null;

  const maskName = (name: string) => {
    return name.split(' ')[0] || name;
  };

  const maskPhone = (phone: string) => {
    return '*'.repeat(phone.length);
  };

  const maskAddress = (address: string) => {
    if (address.length <= 6) return '*'.repeat(address.length);
    return `${address.slice(0, 6)}${'*'.repeat(address.length - 6)}`;
  };

  return (
    <Layout>
      <div className="w-full">
        <div className="bg-surface border border-subtle rounded-lg p-4 mb-4">
          <div className="relative">
            <input
              type="text"
              placeholder="自由にキーワードを入力してください（職種、業界、社名、希望勤務地、スキルなど）"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="form-input pr-10"
            />
            <svg
              className="w-5 h-5 absolute right-3 top-1/2 -translate-y-1/2 text-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <div className="mt-3 flex flex-wrap gap-2 text-sm text-muted">
            <select
              className="border border-subtle rounded px-3 py-2 bg-surface text-sm"
              style={{ minWidth: 140 }}
              value={filters.approachStatus}
              onChange={(e) => setFilters((prev) => ({ ...prev, approachStatus: e.target.value }))}
            >
              <option value="">アプローチ状況</option>
              <option value="未対応">未対応</option>
              <option value="連絡中">連絡中</option>
              <option value="面談調整">面談調整</option>
              <option value="内定">内定</option>
              <option value="辞退">辞退</option>
            </select>
            <select
              className="border border-subtle rounded px-3 py-2 bg-surface text-sm"
              style={{ minWidth: 140 }}
              value={filters.experienceCategory}
              onChange={(e) => setFilters((prev) => ({ ...prev, experienceCategory: e.target.value }))}
            >
              <option value="">経験職種</option>
              <option value="営業">営業</option>
              <option value="カスタマーサクセス">カスタマーサクセス</option>
              <option value="デザイナー">デザイナー</option>
              <option value="エンジニア">エンジニア</option>
              <option value="バックオフィス">バックオフィス</option>
              <option value="マーケティング">マーケティング</option>
            </select>
            <select
              className="border border-subtle rounded px-3 py-2 bg-surface text-sm"
              style={{ minWidth: 140 }}
              value={filters.desiredLocation}
              onChange={(e) => setFilters((prev) => ({ ...prev, desiredLocation: e.target.value }))}
            >
              <option value="">希望勤務地</option>
              <option value="東京都">東京都</option>
              <option value="神奈川県">神奈川県</option>
              <option value="大阪府">大阪府</option>
              <option value="福岡県">福岡県</option>
              <option value="北海道">北海道</option>
              <option value="リモート">リモート</option>
            </select>
            <select
              className="border border-subtle rounded px-3 py-2 bg-surface text-sm"
              style={{ minWidth: 120 }}
              value={filters.ageRange}
              onChange={(e) => setFilters((prev) => ({ ...prev, ageRange: e.target.value }))}
            >
              <option value="">年齢</option>
              <option value="20s">20代</option>
              <option value="30s">30代</option>
              <option value="40s">40代</option>
              <option value="50s">50代</option>
              <option value="60s">60代</option>
            </select>
            <select
              className="border border-subtle rounded px-3 py-2 bg-surface text-sm"
              style={{ minWidth: 120 }}
              value={filters.salaryRange}
              onChange={(e) => setFilters((prev) => ({ ...prev, salaryRange: e.target.value }))}
            >
              <option value="">年収</option>
              <option value="300+">300万円以上</option>
              <option value="500+">500万円以上</option>
              <option value="700+">700万円以上</option>
              <option value="900+">900万円以上</option>
            </select>
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-muted">
            <button
              className="px-3 py-2 rounded bg-subtle border border-subtle"
              onClick={() => {
                if (
                  !keyword.trim() &&
                  !filters.approachStatus &&
                  !filters.experienceCategory &&
                  !filters.desiredLocation &&
                  !filters.ageRange &&
                  !filters.salaryRange
                ) {
                  return;
                }
                setShowSaveFilterModal(true);
              }}
            >
              条件を新規で保存
            </button>
            <button
              className="px-3 py-2 rounded border border-subtle bg-surface"
              onClick={() => {
                setFilters({
                  approachStatus: '',
                  experienceCategory: '',
                  desiredLocation: '',
                  ageRange: '',
                  salaryRange: '',
                });
                setKeyword('');
              }}
            >
              すべての条件をクリア
            </button>
          </div>
          {savedFilters.length > 0 && (
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted">
              <span className="text-xs text-muted">保存済み条件:</span>
              {savedFilters.map((entry) => (
                <div
                  key={entry.id}
                  className="flex items-center gap-1 rounded-full border border-subtle bg-surface px-3 py-1"
                >
                  <button
                    type="button"
                    className="text-xs text-main"
                    onClick={() => {
                      setFilters(entry.filters);
                      setKeyword(entry.keyword);
                    }}
                  >
                    {entry.name}
                  </button>
                  <button
                    type="button"
                    className="text-xs text-muted"
                    onClick={() => {
                      setSavedFilters((prev) => prev.filter((item) => item.id !== entry.id));
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
        {showSaveFilterModal && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
            <div className="bg-surface border border-subtle rounded-lg w-full max-w-sm p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-main">保存名を入力</h2>
                <button
                  className="p-1 rounded hover:bg-subtle"
                  onClick={() => setShowSaveFilterModal(false)}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <input
                className="form-input"
                placeholder="保存名"
                value={saveFilterName}
                onChange={(e) => setSaveFilterName(e.target.value)}
              />
              <div className="flex items-center justify-end gap-2">
                <button
                  className="px-4 py-2 rounded border border-subtle text-sm"
                  onClick={() => setShowSaveFilterModal(false)}
                >
                  キャンセル
                </button>
                <button
                  className="px-4 py-2 rounded bg-brand-primary text-white text-sm font-semibold"
                  type="button"
                  onClick={() => {
                    const name = saveFilterName.trim();
                    if (!name) return;
                    const existing = savedFilters.find((item) => item.name === name);
                    if (existing) {
                      const shouldOverwrite = window.confirm('同名の保存条件があります。上書きしますか？');
                      if (!shouldOverwrite) return;
                      setSavedFilters((prev) =>
                        prev.map((item) =>
                          item.id === existing.id
                            ? {
                                ...item,
                                keyword,
                                filters,
                              }
                            : item
                        )
                      );
                      setSaveFilterName('');
                      setShowSaveFilterModal(false);
                      return;
                    }
                    const entry = {
                      id: `saved-${Date.now()}`,
                      name,
                      keyword,
                      filters,
                    };
                    setSavedFilters((prev) => [entry, ...prev]);
                    setSaveFilterName('');
                    setShowSaveFilterModal(false);
                  }}
                >
                  保存する
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="mb-3 flex items-center justify-between">
          <div className="text-sm text-muted">1 - {filteredCandidates.length} / 1,035,133</div>
          <div className="flex items-center gap-3">
            <button
              className={`px-4 py-2 rounded text-sm font-semibold ${
                selectedIds.length > 0 ? 'bg-brand-primary text-white' : 'bg-subtle text-muted'
              }`}
              onClick={handleBulkScout}
              disabled={selectedIds.length === 0}
            >
              スカウト送付
            </button>
            <div className="flex items-center gap-2 text-sm text-muted">
              <span className="text-main">1</span>
              <span className="text-blue-600">2</span>
              <span className="text-blue-600">3</span>
              <span>...</span>
              <span className="text-blue-600">次へ</span>
            </div>
            <select className="border border-subtle rounded px-3 py-2 bg-surface text-sm text-muted">
              <option>返信率が高い順</option>
              <option>新着順</option>
              <option>更新日順</option>
            </select>
          </div>
        </div>

        <div className="bg-surface border border-subtle rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <div style={{ minWidth: 900 }}>
              <div className="px-4 py-3 border-b border-subtle text-xs text-muted bg-subtle">
                <div
                  className="grid gap-4"
                  style={{
                    gridTemplateColumns:
                      '60px minmax(160px, 2fr) minmax(200px, 3fr) minmax(120px, 1fr) minmax(140px, 1fr) minmax(160px, 1fr)',
                  }}
                >
                  <div>
                    <input
                      type="checkbox"
                      checked={allSelected}
                      onChange={toggleSelectAll}
                    />
                  </div>
                  <div>年齢 | 性別</div>
                  <div>経験職種 | 現(前)勤務先</div>
                  <div>年収</div>
                  <div>希望勤務地</div>
                  <div>出身校</div>
                </div>
              </div>
              <div className="divide-y divide-subtle">
                {filteredCandidates.map((candidate) => (
                  <div
                    key={candidate.id}
                    className={`px-4 py-4 hover:bg-subtle transition ${
                      profileCandidateId === candidate.id ? 'bg-subtle' : ''
                    }`}
                    onClick={(event) => {
                      const target = event.target as HTMLElement | null;
                      if (target?.closest('input[type="checkbox"]')) return;
                      setProfileCandidateId(candidate.id);
                    }}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        setProfileCandidateId(candidate.id);
                      }
                    }}
                  >
                    <div
                      className="grid gap-4 items-center text-sm text-main"
                      style={{
                        gridTemplateColumns:
                          '60px minmax(160px, 2fr) minmax(200px, 3fr) minmax(120px, 1fr) minmax(140px, 1fr) minmax(160px, 1fr)',
                      }}
                    >
                      <div>
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(candidate.id)}
                          onChange={() => toggleSelect(candidate.id)}
                          onClick={(event) => event.stopPropagation()}
                          onMouseDown={(event) => event.stopPropagation()}
                          onKeyDown={(event) => event.stopPropagation()}
                        />
                      </div>
                      <div>
                        <div className="text-sm">{candidate.age}歳</div>
                        <div className="text-xs text-muted">{candidate.gender} / {candidate.location}</div>
                        <div className="text-xs text-muted">{candidate.id}</div>
                      </div>
                      <div>
                        <div>{candidate.role}</div>
                        <div className="text-xs text-muted">{candidate.company}</div>
                      </div>
                      <div>{candidate.salary}</div>
                      <div>{candidate.desiredLocation}</div>
                      <div className="text-xs text-muted">{candidate.school}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      {showBulkModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
          <div className="bg-surface border border-subtle rounded-lg w-full max-w-lg p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-main">スカウト送付</h2>
              <button
                className="p-1 rounded hover:bg-subtle"
                onClick={() => setShowBulkModal(false)}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="text-sm text-muted">
              選択中の求職者にスカウトを送付します（{selectedIds.length}件）
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted">テンプレート</label>
              <select
                className="form-input"
                value={selectedTemplateId}
                onChange={(e) => {
                  const value = e.target.value;
                  setSelectedTemplateId(value);
                  const template = currentTemplates.find((item) => item.id === value);
                  if (template) {
                    setBulkMessage(template.body);
                  }
                }}
              >
                <option value="">テンプレートを選択</option>
                {currentTemplates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <button
                className="px-3 py-2 rounded bg-subtle border border-subtle text-sm"
                type="button"
                onClick={() => {
                  if (!bulkMessage.trim()) return;
                  setShowTemplateNameModal(true);
                }}
              >
                テンプレートに追加する
              </button>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted">メッセージ</label>
              <textarea
                className="form-input min-h-[120px]"
                value={bulkMessage}
                onChange={(e) => setBulkMessage(e.target.value)}
                placeholder="スカウトメッセージを入力してください"
              />
            </div>
            <div className="flex items-center justify-end gap-2">
              <button
                className="px-4 py-2 rounded border border-subtle text-sm"
                onClick={() => setShowBulkModal(false)}
              >
                キャンセル
              </button>
              <button
                className="px-4 py-2 rounded bg-brand-primary text-white text-sm font-semibold"
                onClick={() => {
                  const surnameMap = new Map(
                    candidates.filter((candidate) => selectedIds.includes(candidate.id)).map((candidate) => [candidate.id, candidate.surname])
                  );
                  const personalized = selectedIds.map((id) => {
                    const surname = surnameMap.get(id) || '○○';
                    return { id, message: bulkMessage.replace(/○○様/g, `${surname}様`) };
                  });
                  console.log('[DEBUG] Bulk scout payload:', personalized);
                  setShowBulkModal(false);
                  setBulkMessage('');
                  setSelectedTemplateId('');
                  setSelectedIds([]);
                  alert('スカウトを送付しました（モック）');
                }}
              >
                送付する
              </button>
            </div>
          </div>
        </div>
      )}
      {showTemplateNameModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
          <div className="bg-surface border border-subtle rounded-lg w-full max-w-sm p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-main">テンプレートを保存</h2>
              <button
                className="p-1 rounded hover:bg-subtle"
                onClick={() => setShowTemplateNameModal(false)}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <input
              className="form-input"
              placeholder="テンプレート名"
              value={newTemplateName}
              onChange={(e) => setNewTemplateName(e.target.value)}
            />
            <div className="text-xs text-muted">以下の内容でテンプレートを保存します。</div>
            <div className="rounded border border-subtle bg-subtle p-3 text-sm text-main whitespace-pre-line">
              {bulkMessage}
            </div>
            <div className="flex items-center justify-end gap-2">
              <button
                className="px-4 py-2 rounded border border-subtle text-sm"
                onClick={() => setShowTemplateNameModal(false)}
              >
                キャンセル
              </button>
              <button
                className="px-4 py-2 rounded bg-brand-primary text-white text-sm font-semibold"
                type="button"
                onClick={() => {
                  if (!newTemplateName.trim() || !bulkMessage.trim()) return;
                  const newTemplate: ScoutTemplate = {
                    id: `custom-${Date.now()}`,
                    name: newTemplateName.trim(),
                    body: bulkMessage.trim(),
                  };
                  setTemplatesByCompany((prev) => ({
                    ...prev,
                    [companyKey]: [...(prev[companyKey] || []), newTemplate],
                  }));
                  setSelectedTemplateId(newTemplate.id);
                  setNewTemplateName('');
                  setShowTemplateNameModal(false);
                }}
              >
                保存する
              </button>
            </div>
          </div>
        </div>
      )}
      {isProfileOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40"
          onClick={() => setProfileCandidateId(null)}
          aria-hidden="true"
        />
      )}
      <div
        className="fixed top-0 right-0 h-screen bg-surface border-l border-subtle shadow-lg flex flex-col z-50"
        style={{
          width: '520px',
          transform: isProfileOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease',
        }}
      >
        <div className="p-4 border-b border-subtle flex items-center justify-between">
          <div>
            <div className="text-sm text-muted">候補者プロフィール</div>
            <div className="text-lg font-semibold text-main">
              {profileCandidate.surname}さん（{profileCandidate.id}）
            </div>
          </div>
          <button
            className="p-2 rounded hover:bg-subtle"
            onClick={() => setProfileCandidateId(null)}
            aria-label="閉じる"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-4 overflow-y-auto">
          <div className="grid gap-4 text-sm text-main">
            <div className="space-y-2">
              <div className="text-xs text-muted">本名</div>
              <div>{maskName(profileCandidate.fullName)}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">電話番号</div>
              <div>{maskPhone(profileCandidate.phone)}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">住所</div>
              <div>{maskAddress(profileCandidate.address)}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">経験職種</div>
              <div>{profileCandidate.role}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">現(前)勤務先</div>
              <div>{profileCandidate.company}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">年齢 | 性別</div>
              <div>
                {profileCandidate.age}歳 / {profileCandidate.gender}
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">希望勤務地</div>
              <div>{profileCandidate.desiredLocation}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">年収</div>
              <div>{profileCandidate.salary}</div>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-muted">出身校</div>
              <div>{profileCandidate.school}</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};





