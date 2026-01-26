import { useState, useRef, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { Layout } from '../../../shared/components/Layout';

interface Message {
  id: string;
  role: 'user' | 'candidate';
  content: string;
  timestamp: Date;
}

export const CandidateDetailPage = () => {
  const { id } = useParams();
  const location = useLocation();
  const isChatPreview = new URLSearchParams(location.search).get('from') === 'chatClient';
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
        'この度は弊社に気概をお持ちいただき、ありがとうございます。\n\n弊社の株式会社カイテクノロジーでのバックエンドエンジニアに経験を持してし、ぜひ一度カジュアル面談にてお話しさせていただければと思います！',
      timestamp: new Date('2024-02-10T12:07:00'),
    },
    {
      id: '3',
      role: 'candidate',
      content:
        'まずはカジュアル面談にて、フランクに情報交換をさせていただきますので、ありがたくご参加ください。\n\n土・日・19時以降の方がご都合がよい場合は、週2-3日 以降でもご調整致しますので、理由のところご都合がよろしければお知らせください！',
      timestamp: new Date('2024-02-10T14:00:00'),
    },
    {
      id: '4',
      role: 'user',
      content:
        '早速ですが、下記の日程でご都合いかがでしょうか？\n\n2月13日（火）14:00～16:00\n2月14日（水）14:00～16:00\n2月17日（木）13:00～17:00\n\n面談ツールは「Google Meet」を予定しております。',
      timestamp: new Date('2024-02-10T14:05:00'),
    },
    {
      id: '5',
      role: 'candidate',
      content:
        'もしお忙しい次の日程でご都合が合わない場合は、今週～来週以降でご都合の良い日程がご都合よろしければお知らせください。お忙しいところ恐縮です',
      timestamp: new Date('2024-02-10T14:06:00'),
    },
    {
      id: '6',
      role: 'user',
      content: 'もちろん事前にご質問などがありましたら、遠慮なくご質問ください！',
      timestamp: new Date('2024-02-10T14:07:00'),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // モック候補者データ
  const candidate = {
    id: id || '1',
    name: '山田 太郎',
    age: 28,
    gender: '男性',
    location: '埼玉県',
    email: 'taro.yamada@example.com',
    phone: '090-1234-5678',
    address: '東京都渋谷区神南1-2-3',
    currentSalary: '300万円',
    experience: 'バックエンドエンジニア 3年',
    education: '日本工学院専門学校・短大 ITカレッジ',
    graduationDate: '2020年03月 卒業',
    skills: [
      { category: '技術系（システム・ネットワーク）', items: ['プログラミング', 'SQL 3年～5年', 'Java 3年～5年', 'JavaScript 1年～3年'] },
      { category: '経験業務（プロジェクトマネジメント・システム開発）', items: ['要件定義 3年～5年', '基本設計 1年～3年'] },
    ],
    employmentHistory: [
      {
        company: '株式会社カイテクノロジー',
        period: '2020年04月 ～ 在職中',
        position: 'IT社員',
        duties: 'バックエンドエンジニア 3年\nフロントエンドエンジニア 1年\nプロジェクトマネージャー 1年',
      },
    ],
    preferences: '自由記入',
    matchScore: 85,
  };

  const maskPhone = (phone: string) => {
    const match = phone.match(/(\d{2,4})-?(\d{2,4})-?(\d{4})/);
    if (!match) return '非公開';
    return `${match[1]}-****-${match[3]}`;
  };

  const maskAddress = (address: string) => {
    const match = address.match(/^(.+?[都道府県])/);
    if (!match) return '非公開';
    return `${match[1]}以降非公開`;
  };

  const displayPhone = isChatPreview ? maskPhone(candidate.phone) : candidate.phone;
  const displayAddress = isChatPreview ? maskAddress(candidate.address) : candidate.address;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          {/* ブレッドクラム */}
          <div className="mb-4">
            <div className="flex items-center gap-2 text-sm text-muted">
              <Link to="/applicantsClient" className="hover:text-main">
                候補者管理
              </Link>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <span className="text-main">{candidate.name}</span>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-6">
            {/* 左側：候補者詳細 */}
            <div className="col-span-5">
              <div className="bg-surface rounded-lg border border-subtle">
                {/* ヘッダー */}
                <div className="p-4 border-b border-subtle">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <button className="p-2 hover:bg-subtle rounded">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                      </button>
                      <button className="p-2 hover:bg-subtle rounded">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                      <button className="p-2 hover:bg-subtle rounded">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </button>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="p-2 hover:bg-subtle rounded">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                      </button>
                      <button className="p-2 hover:bg-subtle rounded">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-blue-500 text-white text-xs rounded-full font-medium">
                      {candidate.age}歳
                    </span>
                    <h2 className="text-xl font-semibold text-main">{candidate.name}</h2>
                    <span className="text-sm text-muted">- 在住 {candidate.id}</span>
                  </div>
                </div>

                {/* 詳細情報 */}
                <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 250px)' }}>
                  {/* プロフィール情報 */}
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-main mb-3">プロフィール情報</h3>
                    <div className="bg-subtle border border-subtle rounded p-3 text-sm text-main grid gap-2">
                      <div>氏名: {candidate.name}</div>
                      <div>年齢: {candidate.age}歳 / 性別: {candidate.gender}</div>
                      <div>居住地: {candidate.location}</div>
                      <div>メール: {candidate.email}</div>
                      <div>電話番号: {displayPhone}</div>
                      <div>住所: {displayAddress}</div>
                    </div>
                  </div>

                  {/* 履歴書情報 */}
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-main mb-3">履歴書情報</h3>

                    {/* 職務経歴 */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-main mb-2">職務経歴</h4>
                      <div className="text-sm text-main mb-3">
                        2020年4月に株式会社カイテクノロジーへ入社し、現職です。
                        <br />
                        これまで3年間、バックエンドエンジニアを担当しました。
                        <br />
                        現在、茨城県、東京都、長崎県を顧客として希望しています。
                      </div>

                      {candidate.employmentHistory.map((job, index) => (
                        <div key={index} className="bg-subtle border border-subtle rounded p-3 mb-3">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm font-medium text-main">{job.company}</span>
                          </div>
                          <div className="text-xs text-muted mb-2">
                            【在籍期間】 {job.period}
                            <br />
                            【配属部署】 {job.position}
                          </div>
                          <div className="text-xs text-main whitespace-pre-line mb-2">
                            【職種】
                            <br />
                            {job.duties}
                          </div>
                          <button className="text-xs text-blue-500 hover:underline">もっと見る</button>
                        </div>
                      ))}
                    </div>

                    {/* 最終学歴 */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-main mb-2">最終学歴</h4>
                      <div className="bg-subtle border border-subtle rounded p-3">
                        <div className="text-sm text-main mb-1">{candidate.education}</div>
                        <div className="text-xs text-muted">{candidate.graduationDate}</div>
                      </div>
                    </div>

                    {/* スキル */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-main mb-2">スキル</h4>
                      {candidate.skills.map((skillGroup, index) => (
                        <div key={index} className="mb-3">
                          <div className="text-xs text-muted mb-2">{skillGroup.category}</div>
                          <div className="flex flex-wrap gap-2">
                            {skillGroup.items.map((skill, skillIndex) => (
                              <span
                                key={skillIndex}
                                className="px-2 py-1 bg-subtle border border-subtle text-main text-xs rounded"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                      <button className="text-xs text-blue-500 hover:underline">もっと見る</button>
                    </div>

                    {/* 経験職種 */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-main mb-2">経験職種</h4>
                      <div className="text-sm text-main">
                        インターネット/Webサービス・ASP
                        <br />
                        その他全業・保険業
                        <br />
                        不動産業具・住宅・中介・管理
                      </div>
                    </div>

                    {/* 現(前)年収 */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-main mb-2">現(前)年収</h4>
                      <div className="text-sm text-main">{candidate.currentSalary}</div>
                    </div>

                    {/* 趣味 */}
                    <div>
                      <h4 className="text-sm font-medium text-main mb-2">趣味</h4>
                      <div className="text-sm text-main">{candidate.preferences}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 右側：チャット */}
            <div className="col-span-7">
              <div className="bg-surface rounded-lg border border-subtle flex flex-col" style={{ height: 'calc(100vh - 150px)' }}>
                {/* チャットヘッダー */}
                <div className="p-4 border-b border-subtle flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                      {candidate.name.charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-main">{candidate.name}</div>
                      <div className="text-xs text-muted">2024年02月09日</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-semibold brand-primary">{candidate.matchScore}%</div>
                    <div className="text-xs text-muted">マッチ度</div>
                  </div>
                </div>

                {/* メッセージエリア */}
                <div className="flex-1 overflow-y-auto p-4">
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div key={message.id} className={message.role === 'user' ? 'flex justify-end' : ''}>
                        <div className={`max-w-[80%] ${message.role === 'user' ? 'bg-green-500 text-white' : 'bg-subtle border border-subtle text-main'} rounded-lg p-3`}>
                          <p className="text-sm whitespace-pre-line leading-relaxed">{message.content}</p>
                          <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-white/80' : 'text-muted'}`}>
                            {message.timestamp.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* INFO メッセージ */}
                  <div className="mt-8 p-4 bg-subtle border border-subtle rounded">
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-400 flex items-center justify-center text-white text-xs font-bold">
                        i
                      </div>
                      <div className="text-xs text-main">
                        求職者から反応があったら、メッセージのやり取りができるようになります。求職者からの返信をお待ち下さい。
                      </div>
                    </div>
                  </div>
                </div>

                {/* 入力エリア */}
                <div className="border-t border-subtle p-4">
                  <form onSubmit={handleSubmit}>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="メッセージを入力..."
                        className="form-input flex-1"
                      />
                      <button type="submit" disabled={!inputValue.trim()} className="btn btn-primary px-6">
                        送信
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
