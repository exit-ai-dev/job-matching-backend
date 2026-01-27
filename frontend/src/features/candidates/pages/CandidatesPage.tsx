import { useState } from 'react';
import { Layout } from '../../../shared/components/Layout';
import { useAuth } from '../../auth/hooks/useAuth';

interface Candidate {
  id: number;
  name: string;
  age: number;
  gender: string;
  location: string;
  position: string;
  experience: string;
  salary: string;
  education: string;
  matchScore: number;
  skills: string[];
  status: string;
  lastContact: string;
  favorited: boolean;
}

interface Message {
  id: string;
  role: 'user' | 'candidate';
  content: string;
  timestamp: Date;
}

export const CandidatesPage = () => {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCandidateId, setActiveCandidateId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'candidate',
      content: 'クラウドエンジニアの求人に「気になる」が届きました！',
      timestamp: new Date('2024-02-10T12:33:00'),
    },
    {
      id: '2',
      role: 'user',
      content:
        'この度は弊社にご興味をお持ちいただき、ありがとうございます。ぜひ一度カジュアル面談でお話しさせてください。',
      timestamp: new Date('2024-02-10T12:07:00'),
    },
  ]);
  const [inputValue, setInputValue] = useState('');

  // モック候補者データ
  const candidates: Candidate[] = [
    {
      id: 1,
      name: '山田 太郎',
      age: 28,
      gender: '男性',
      location: '埼玉県',
      position: 'バックエンドエンジニア',
      experience: '3年',
      salary: '300万円',
      education: '日本工学院専門学校・短大卒業',
      matchScore: 85,
      skills: ['システム・ネットワーク', 'プログラミング', 'SQL'],
      status: 'カジュアル面談終了中 (申川)',
      lastContact: '24/02/10',
      favorited: true,
    },
    {
      id: 2,
      name: '佐藤 花子',
      age: 33,
      gender: '女性',
      location: '埼玉県',
      position: 'デジタルプロモーション',
      experience: '1年経験',
      salary: '400万円',
      education: '大東文化大学卒業',
      matchScore: 92,
      skills: ['プロジェクトマネジメント', 'システム開発'],
      status: 'カジュアル面談日程調整',
      lastContact: '23/12/14',
      favorited: false,
    },
    {
      id: 3,
      name: '鈴木 一郎',
      age: 28,
      gender: '男性',
      location: '埼玉県',
      position: 'システムエンジニア（未経験歓迎）',
      experience: '1年経験',
      salary: '270万円',
      education: '拓殖大学卒業',
      matchScore: 78,
      skills: ['インターネット/Webサービス', 'ASP', '不動産業'],
      status: '面談調整中 (私が)',
      lastContact: '23/08/31',
      favorited: false,
    },
    {
      id: 4,
      name: 'エン・ジャパン',
      age: 30,
      gender: '女性',
      location: '千葉県',
      position: 'エンジニア',
      experience: '3年経験',
      salary: '350万円',
      education: '豊富院保護出身専門学校卒業・短大卒業',
      matchScore: 88,
      skills: ['Java', 'Python', 'プロジェクト管理'],
      status: '面談調整中 (申川)',
      lastContact: '23/08/10',
      favorited: true,
    },
  ];

  const filteredCandidates = candidates.filter((candidate) => {
    const matchesSearch =
      searchQuery === '' ||
      candidate.name.includes(searchQuery) ||
      candidate.position.includes(searchQuery) ||
      candidate.skills.some((skill) => skill.includes(searchQuery));
    return matchesSearch;
  });

  if (!user) {
    return null;
  }

  const activeCandidate = candidates.find((candidate) => candidate.id === activeCandidateId) ?? candidates[0];
  const isPanelOpen = activeCandidateId !== null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages([...messages, newMessage]);
    setInputValue('');
  };

  return (
    <Layout>
      <div className="bg-page min-h-screen">
        <div className="max-w-7xl mx-auto">
          {/* ヘッダー */}
          <div className="mb-6">
            <h1 className="text-2xl font-semibold text-main mb-2">候補者管理</h1>
            <p className="text-sm text-muted">
              マッチングした候補者の管理・コミュニケーション
            </p>
          </div>

          <div className="grid grid-cols-12 gap-6">
            {/* メインコンテンツ */}
            <div className="col-span-12">
              {/* 検索バー */}
              <div className="bg-surface rounded-lg border border-subtle p-4 mb-4">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="候補者名、スキル等で検索"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
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
                  </div>
                  <button className="btn btn-secondary">
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              {/* 候補者リスト */}
              <div className="bg-surface rounded-lg border border-subtle overflow-hidden">
                <div className="px-4 py-3 border-b border-subtle bg-subtle">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted">
                      1 - {filteredCandidates.length} / {filteredCandidates.length}
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="p-1 hover:bg-surface rounded">
                        <svg
                          className="w-5 h-5 text-main"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 19l-7-7 7-7"
                          />
                        </svg>
                      </button>
                      <span className="text-sm text-main">1</span>
                      <button className="p-1 hover:bg-surface rounded">
                        <svg
                          className="w-5 h-5 text-main"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <div className="px-4 py-3 border-b border-subtle text-xs text-muted">
                  <div className="grid grid-cols-12 gap-4">
                    <div className="col-span-1"> </div>
                    <div className="col-span-2">ステータス | 最終更新日</div>
                    <div className="col-span-3">氏名 | 年齢 | 性別 | 現住所 | 求職者ID</div>
                    <div className="col-span-2">現(前)年収 | 経験社数 | 最終学歴</div>
                    <div className="col-span-3">メモ</div>
                    <div className="col-span-1 text-right">選考ステップ</div>
                  </div>
                </div>

                <div className="divide-y divide-subtle">
                  {filteredCandidates.map((candidate) => (
                    <div
                      key={candidate.id}
                      className="px-4 py-4 hover:bg-subtle transition cursor-pointer"
                      onClick={() => setActiveCandidateId(candidate.id)}
                    >
                      <div className="grid grid-cols-12 gap-4 items-start">
                        <div className="col-span-1">
                          <input type="checkbox" onClick={(event) => event.stopPropagation()} />
                        </div>
                        <div className="col-span-2">
                          <span className="inline-flex px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold">
                            既読
                          </span>
                          <div className="text-xs text-muted mt-2">{candidate.lastContact}</div>
                        </div>
                        <div className="col-span-3">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-main">{candidate.name}</span>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-rose-100 text-rose-600">
                              人気
                            </span>
                          </div>
                          <div className="text-sm text-muted mt-1">
                            {candidate.age}歳 | {candidate.gender} | {candidate.location}
                          </div>
                          <div className="text-sm text-main mt-1">A01{String(candidate.id).padStart(5, '0')}</div>
                        </div>
                        <div className="col-span-2">
                          <div className="text-sm text-main">現(前)年収: {candidate.salary}</div>
                          <div className="text-sm text-main mt-1">経験社数: {candidate.experience}</div>
                          <div className="text-sm text-main mt-1">{candidate.education}</div>
                        </div>
                        <div className="col-span-3">
                          <textarea
                            rows={2}
                            placeholder="メモを入力"
                            className="w-full text-sm border border-subtle rounded px-3 py-2 bg-surface resize-none"
                            onClick={(event) => event.stopPropagation()}
                          />
                        </div>
                        <div className="col-span-1 text-right">
                          <select
                            className="border border-subtle rounded px-2 py-1 text-sm bg-surface"
                            onClick={(event) => event.stopPropagation()}
                          >
                            <option>未対応</option>
                            <option>面談</option>
                            <option>書類選考</option>
                            <option>一次選考</option>
                            <option>二次選考</option>
                            <option>三次選考</option>
                            <option>最終面接</option>
                            <option>内定</option>
                            <option>内定承諾</option>
                            <option>お見送り</option>
                            <option>応募者辞退</option>
                          </select>
                        </div>
                      </div>

                      <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-main">
                        <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 border border-amber-300 text-amber-700 rounded-full">
                          ▷ スカウトからの応募
                        </span>
                        <span>入社予定日:2025/05/01</span>
                        <span>システムエンジニア（ポテンシャル・第二新卒歓迎）</span>
                        <span>（90万円）</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {isPanelOpen && (
        <div
          className="fixed inset-0 bg-black/30"
          onClick={() => setActiveCandidateId(null)}
          aria-hidden="true"
        />
      )}
      <div
        className="fixed top-0 right-0 h-screen bg-surface border-l border-subtle shadow-lg flex flex-col"
        style={{
          width: '720px',
          transform: isPanelOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease',
          zIndex: 40,
        }}
      >
        <div className="p-4 border-b border-subtle flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
              {activeCandidate.name.charAt(0)}
            </div>
            <div>
              <div className="text-sm font-semibold text-main">{activeCandidate.name}</div>
              <div className="text-xs text-muted">
                {activeCandidate.age}歳 / {activeCandidate.gender} / {activeCandidate.location}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-2xl font-semibold brand-primary">{activeCandidate.matchScore}%</div>
              <div className="text-xs text-muted">マッチ度</div>
            </div>
            <button
              className="p-2 rounded hover:bg-subtle"
              onClick={() => setActiveCandidateId(null)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-hidden grid grid-rows-[auto_1fr_auto]">
          <div className="p-4 border-b border-subtle bg-subtle">
            <div className="text-sm text-main font-medium">プロフィール</div>
            <div className="text-xs text-muted">候補者情報とチャットを同時に確認できます</div>
          </div>

          <div className="grid grid-cols-5 gap-4 p-4 overflow-hidden">
            <div className="col-span-2 overflow-y-auto pr-2">
              <div className="bg-surface border border-subtle rounded-lg p-4 mb-4">
                <div className="text-xs text-muted mb-2">基本情報</div>
                <div className="text-sm text-main mb-2">希望職種: {activeCandidate.position}</div>
                <div className="text-sm text-main mb-2">経験: {activeCandidate.experience}</div>
                <div className="text-sm text-main">現(前)年収: {activeCandidate.salary}</div>
              </div>
              <div className="bg-surface border border-subtle rounded-lg p-4 mb-4">
                <div className="text-xs text-muted mb-2">最終学歴</div>
                <div className="text-sm text-main">{activeCandidate.education}</div>
              </div>
              <div className="bg-surface border border-subtle rounded-lg p-4">
                <div className="text-xs text-muted mb-2">スキル</div>
                <div className="flex flex-wrap gap-2">
                  {activeCandidate.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-1 bg-subtle border border-subtle text-main text-xs rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="col-span-3 flex flex-col bg-surface border border-subtle rounded-lg overflow-hidden">
              <div className="p-3 border-b border-subtle flex items-center justify-between">
                <div className="text-sm font-medium text-main">チャット</div>
                <div className="text-xs text-muted">最終更新: {activeCandidate.lastContact}</div>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-page">
                {messages.map((message) => (
                  <div key={message.id} className={message.role === 'user' ? 'flex justify-end' : ''}>
                    <div
                      className={`max-w-[80%] ${
                        message.role === 'user'
                          ? 'bg-brand-primary text-white'
                          : 'bg-surface border border-subtle text-main'
                      } rounded-lg p-3`}
                    >
                      <p className="text-sm whitespace-pre-line leading-relaxed">{message.content}</p>
                      <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-white/80' : 'text-muted'}`}>
                        {message.timestamp.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="border-t border-subtle p-3">
                <form onSubmit={handleSubmit}>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="メッセージを入力..."
                      className="form-input flex-1"
                    />
                    <button type="submit" disabled={!inputValue.trim()} className="btn btn-primary px-4">
                      送信
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
