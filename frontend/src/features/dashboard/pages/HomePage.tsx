import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../auth/hooks/useAuth';
import { Layout } from '../../../shared/components/Layout';
import { Card } from '../../../components/ui/card';
import { Button, buttonVariants } from '../../../components/ui/button';
import { cn } from '../../../lib/utils';
import { applicationsApi, jobsApi } from '../../../shared/lib/api';

type Thread = {
  id: string;
  name: string;
  unreadCount: number;
  source: 'company' | 'ai';
};

export const HomePage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<{ label: string; value: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'company' | 'ai'>('company');
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleStartTime, setScheduleStartTime] = useState('');
  const [scheduleEndTime, setScheduleEndTime] = useState('');

  const isSeeker = user?.role === 'seeker';
  const threads = useMemo<Thread[]>(
    () => [
      { id: 'company-1', name: 'テックギルド', unreadCount: 2, source: 'company' },
      { id: 'company-2', name: 'ワールドスタッフ', unreadCount: 0, source: 'company' },
      { id: 'company-3', name: 'アドバンスト・ソフト', unreadCount: 1, source: 'company' },
      { id: 'ai-1', name: 'AIキャリアアシスタント', unreadCount: 0, source: 'ai' },
      { id: 'ai-2', name: 'AI求人提案', unreadCount: 3, source: 'ai' },
    ],
    []
  );
  const currentThreads = useMemo(
    () => threads.filter((thread) => thread.source === activeTab),
    [activeTab, threads]
  );
  const selectedThread = useMemo(
    () => threads.find((thread) => thread.id === selectedThreadId) ?? null,
    [selectedThreadId, threads]
  );

  useEffect(() => {
    const fetchStats = async () => {
      if (!user) return;

      try {
        setLoading(true);

        if (isSeeker) {
          // 求職者の統計を取得
          const applicationsResponse = await applicationsApi.getApplications();
          const jobsResponse = await jobsApi.getJobs({ page: 1, perPage: 100 });

          setStats([
            { label: '提案求人', value: `${jobsResponse.total || 0} 件` },
            { label: '応募履歴', value: `${applicationsResponse.total || 0} 件` },
            { label: 'スカウト', value: '0 件' },
          ]);
        } else {
          // 企業の統計（現時点ではダミーデータ）
          setStats([
            { label: 'マッチング候補', value: '0 件' },
            { label: '選考中', value: '0 件' },
            { label: '内定者', value: '0 件' },
          ]);
        }
      } catch (err) {
        console.error('統計の取得に失敗:', err);
        // エラー時はデフォルト値を設定
        setStats(
          isSeeker
            ? [
                { label: '提案求人', value: '- 件' },
                { label: '応募履歴', value: '- 件' },
                { label: 'スカウト', value: '0 件' },
              ]
            : [
                { label: 'マッチング候補', value: '- 件' },
                { label: '選考中', value: '- 件' },
                { label: '内定者', value: '- 件' },
              ]
        );
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, isSeeker]);

  if (!user) return null;

  const profileCompletion = useMemo<{
    items: Array<{ label: string; complete: boolean }>;
    percent: number;
    statusLabel: string;
  }>(() => {
    const hasValue = (value: unknown) =>
      typeof value === 'string' ? value.trim().length > 0 : value != null;
    const accountComplete = hasValue(user.name) && hasValue(user.email);

    let preferencesComplete = false;
    try {
      const storedPreferences = localStorage.getItem('user-preferences');
      if (storedPreferences) {
        const parsed = JSON.parse(storedPreferences) as {
          salary?: number;
          jobType?: string | string[];
          answers?: Record<string, unknown>;
        };
        const jobTypeValue = Array.isArray(parsed.jobType)
          ? parsed.jobType.length > 0
          : hasValue(parsed.jobType);
        preferencesComplete = jobTypeValue && parsed.salary != null;
      }
    } catch (error) {
      console.error('希望条件の読み込みに失敗:', error);
    }

    let resumeComplete = false;
    try {
      const storedResume = localStorage.getItem(`resume-${user.id}`);
      if (storedResume) {
        const parsed = JSON.parse(storedResume) as Record<string, string>;
        resumeComplete = ['lastName', 'firstName', 'birthDate', 'phone', 'address', 'education', 'experience']
          .every((key) => hasValue(parsed[key]));
      }
    } catch (error) {
      console.error('履歴書の読み込みに失敗:', error);
    }

    const items = [
      { label: '基本情報', complete: accountComplete },
      { label: '希望条件', complete: preferencesComplete },
      { label: '履歴書', complete: resumeComplete },
    ];
    const completeCount = items.filter((item) => item.complete).length;
    const percent = Math.round((completeCount / items.length) * 100);
    const statusLabel = percent === 100 ? '完了' : percent >= 50 ? '途中' : '開始';

    return { items, percent, statusLabel };
  }, [user.email, user.id, user.name]);

  const formatSchedule = () => {
    if (!scheduleDate) return '';
    const dateLabel = scheduleDate.replace(/-/g, '/');
    if (scheduleStartTime && scheduleEndTime) {
      return `面談希望日: ${dateLabel} ${scheduleStartTime}〜${scheduleEndTime}`;
    }
    if (scheduleStartTime || scheduleEndTime) {
      return `面談希望日: ${dateLabel} ${scheduleStartTime || scheduleEndTime}`;
    }
    return `面談希望日: ${dateLabel}`;
  };

  if (isSeeker) {
    return (
      <Layout>
        <main className="min-h-screen bg-muted text-foreground">
          <div className="mx-auto w-full max-w-none px-4 py-6">
            <div className="bg-surface border border-subtle rounded-2xl shadow-sm">
              <div className="grid gap-4 p-4 lg:grid-cols-[220px_1fr_280px]">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-xs">
                    <button
                      type="button"
                      className={`pb-1 ${activeTab === 'company' ? 'text-main font-semibold border-b-2 border-brand-primary' : 'text-muted'}`}
                      onClick={() => {
                        setActiveTab('company');
                        setSelectedThreadId(null);
                      }}
                    >
                      企業から
                    </button>
                    <button
                      type="button"
                      className={`pb-1 ${activeTab === 'ai' ? 'text-main font-semibold border-b-2 border-brand-primary' : 'text-muted'}`}
                      onClick={() => {
                        setActiveTab('ai');
                        setSelectedThreadId(null);
                      }}
                    >
                      AIから
                    </button>
                  </div>
                  <button
                    type="button"
                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-subtle bg-subtle text-sm text-main"
                  >
                    フィルタ
                    <span className="text-muted">›</span>
                  </button>
                  <div className="px-3 py-2 rounded-lg border border-subtle bg-surface text-sm text-main">
                    スレッド {currentThreads.length} 件
                  </div>
                  <div className="space-y-2">
                    {currentThreads.map((thread) => (
                      <button
                        key={thread.id}
                        type="button"
                        className={`w-full text-left px-3 py-2 rounded-lg border text-sm transition flex items-center justify-between gap-2 ${
                          selectedThreadId === thread.id
                            ? 'border-brand-primary bg-subtle text-main'
                            : 'border-subtle bg-surface text-muted hover:bg-subtle'
                        }`}
                        onClick={() => setSelectedThreadId(thread.id)}
                      >
                        <span className="truncate">{thread.name}</span>
                        {thread.unreadCount > 0 && (
                          <span className="min-w-[20px] h-5 px-1 rounded-full bg-red-500 text-white text-xs font-semibold flex items-center justify-center">
                            {thread.unreadCount}
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-2xl border border-subtle bg-surface p-8 text-center space-y-4">
                    <div className="mx-auto w-24 h-24 rounded-full border border-dashed border-subtle flex items-center justify-center">
                      <div className="w-12 h-10 rounded-md border border-subtle bg-subtle" />
                    </div>
                    <div className="space-y-2">
                      <h1 className="text-lg font-semibold text-main">
                        プロフィールを充実させると、
                        <br />
                        自分に合ったスカウトが来るかも！？
                      </h1>
                      <p className="text-sm text-muted leading-relaxed">
                        AIがあなたの職歴・希望条件を整理し、企業からのスカウトや求人提案を後押しします。
                      </p>
                    </div>
                    <div className="flex flex-wrap items-center justify-center gap-3">
                      <Link
                        to="/preferencesUser"
                        className={cn(buttonVariants({ size: 'sm', variant: 'primary' }), 'no-underline rounded-full')}
                      >
                        プロフィール編集はこちら
                      </Link>
                      <Button variant="secondary" size="sm" className="rounded-full">
                        AIの求人提案を受ける
                      </Button>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-subtle bg-surface p-4 space-y-3">
                    <div className="flex items-center gap-2 text-sm font-semibold text-main">
                      <span className="text-primary">★</span>
                      AIサマリー
                    </div>
                    <div className="grid gap-3 sm:grid-cols-3">
                      {stats.map((item) => (
                        <div key={item.label} className="rounded-xl border border-subtle bg-subtle px-3 py-2">
                          <div className="text-xs text-muted">{item.label}</div>
                          <div className="text-lg font-semibold text-main">{item.value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-2xl border border-subtle bg-surface p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-semibold text-main">プロフィール充実度</div>
                      <span className="text-xs text-primary">{profileCompletion.statusLabel}</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-muted">
                        <span>入力状況</span>
                        <span className="font-semibold text-primary">{profileCompletion.percent}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted">
                        <div className="h-2 rounded-full bg-primary" style={{ width: `${profileCompletion.percent}%` }} />
                      </div>
                    </div>
                    <div className="space-y-2 text-sm">
                      {profileCompletion.items.map((item) => (
                        <div key={item.label} className="flex items-center justify-between">
                          <span className="text-muted">{item.label}</span>
                          <span className="text-main font-semibold">{item.complete ? '入力済み' : '未入力'}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-subtle bg-surface p-4 space-y-3">
                    <div className="text-sm font-semibold text-main">AIサマリー</div>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted">提案求人</span>
                        <span className="text-main font-semibold">3 件</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted">応募履歴</span>
                        <span className="text-main font-semibold">2 件</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted">スカウト受信</span>
                        <span className="text-main font-semibold">0 件</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
        {selectedThread && (
          <div
            className="fixed inset-0 bg-black/30 z-40"
            onClick={() => setSelectedThreadId(null)}
            aria-hidden="true"
          />
        )}
        <div
          className="fixed top-0 right-0 h-screen bg-surface border-l border-subtle shadow-lg flex flex-col z-50"
          style={{
            width: '520px',
            transform: selectedThread ? 'translateX(0)' : 'translateX(100%)',
            transition: 'transform 0.3s ease',
          }}
        >
          {selectedThread && (
            <>
              <div className="p-4 border-b border-subtle flex items-center justify-between">
                <div>
                  <div className="text-xs text-muted">チャット</div>
                  <div className="text-lg font-semibold text-main">{selectedThread.name}</div>
                </div>
                <button
                  className="p-2 rounded hover:bg-subtle"
                  onClick={() => setSelectedThreadId(null)}
                  aria-label="閉じる"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="flex-1 p-4 overflow-y-auto flex">
                <div className="flex-1 rounded-lg border border-subtle bg-muted/40 flex items-center justify-center text-sm text-muted">
                  チャットスペース（仮）
                </div>
              </div>
              <div className="border-t border-subtle p-4">
                <div className="flex flex-col gap-3">
                  <textarea
                    className="form-input min-h-[96px]"
                    placeholder="メッセージを入力..."
                    value={chatMessage}
                    onChange={(event) => setChatMessage(event.target.value)}
                  />
                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      className="h-9 w-9 rounded border border-subtle bg-surface text-sm"
                      aria-label="日程を選択"
                      onClick={() => setIsCalendarOpen(true)}
                    >
                      📅
                    </button>
                    <label
                      className="h-9 w-9 rounded border border-subtle bg-surface text-sm cursor-pointer flex items-center justify-center"
                      aria-label="ファイルを添付"
                    >
                      📎
                      <input type="file" className="hidden" />
                    </label>
                    <Button size="sm">送信</Button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
        {isCalendarOpen && (
          <div
            className="fixed inset-0 bg-black/40 z-[60] flex items-center justify-center px-4"
            onClick={() => setIsCalendarOpen(false)}
            aria-hidden="true"
          >
            <div
              className="bg-surface border border-subtle rounded-lg w-full max-w-sm p-5 space-y-4"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-main">日程を選択</h2>
                <button
                  className="p-1 rounded hover:bg-subtle"
                  onClick={() => setIsCalendarOpen(false)}
                  aria-label="閉じる"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="space-y-3">
                <input
                  type="date"
                  className="form-input"
                  value={scheduleDate}
                  onChange={(event) => setScheduleDate(event.target.value)}
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="time"
                    className="form-input"
                    value={scheduleStartTime}
                    onChange={(event) => setScheduleStartTime(event.target.value)}
                  />
                  <input
                    type="time"
                    className="form-input"
                    value={scheduleEndTime}
                    onChange={(event) => setScheduleEndTime(event.target.value)}
                  />
                </div>
              </div>
              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  className="px-4 py-2 rounded border border-subtle text-sm"
                  onClick={() => setIsCalendarOpen(false)}
                >
                  キャンセル
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded bg-brand-primary text-white text-sm font-semibold"
                  onClick={() => {
                    const text = formatSchedule();
                    if (!text) return;
                    setChatMessage((prev) => (prev ? `${prev}\n${text}` : text));
                    setIsCalendarOpen(false);
                  }}
                >
                  反映する
                </button>
              </div>
            </div>
          </div>
        )}
      </Layout>
    );
  }

  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-5xl px-4 py-6 space-y-6">
          <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <h1 className="text-2xl font-semibold leading-7 break-words">
                {isSeeker ? 'マイホーム' : '採用ダッシュボード'}
              </h1>
              <p className="text-sm leading-6 text-muted-foreground">
                {isSeeker ? '最新のスカウトや提案を確認しましょう' : '候補者と求人の進捗を確認しましょう'}
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm">エクスポート</Button>
              <Button size="sm">{isSeeker ? 'プロフィール編集' : '求人票を作成'}</Button>
            </div>
          </header>

          <section className="grid gap-4 sm:grid-cols-3">
            {loading ? (
              // ローディング中の表示
              Array.from({ length: 3 }).map((_, i) => (
                <Card key={i} className="p-4 space-y-2 min-w-0">
                  <div className="h-4 w-20 bg-muted animate-pulse rounded"></div>
                  <div className="h-6 w-16 bg-muted animate-pulse rounded"></div>
                  <div className="h-3 w-full bg-muted animate-pulse rounded"></div>
                </Card>
              ))
            ) : (
              stats.map((item) => (
                <Card key={item.label} className="p-4 space-y-2 min-w-0">
                  <p className="text-xs text-muted-foreground">{item.label}</p>
                  <p className="text-lg font-semibold">{item.value}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2 break-words">
                    {isSeeker ? 'AIがあなたに合う求人を提案します' : 'AIが候補者をスコアリングしています'}
                  </p>
                </Card>
              ))
            )}
          </section>

          <section className="grid gap-4 lg:grid-cols-[2fr,1fr]">
            <Card className="p-6 space-y-4">
              <div className="space-y-2 min-w-0">
                <p className="text-xs text-muted-foreground">AIサマリー</p>
                <h2 className="text-lg font-semibold break-words">
                  {isSeeker
                    ? 'プロフィールを充実させてスカウトを増やしましょう'
                    : 'AIで最適な候補者を見つけましょう'}
                </h2>
                <p className="text-sm leading-6 text-muted-foreground break-words">
                  {isSeeker
                    ? '職歴・スキル・希望条件を登録すると、マッチした求人が届きやすくなります。'
                    : '求人票を登録すると、スキル・経験からマッチ度をスコアリングします。'}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {isSeeker ? (
                  <Link
                    to="/preferencesUser"
                    className={cn(buttonVariants({ size: 'sm', variant: 'primary' }), 'no-underline')}
                  >
                    プロフィールを更新
                  </Link>
                ) : (
                  <Link
                    to="/jobsClient"
                    className={cn(buttonVariants({ size: 'sm', variant: 'primary' }), 'no-underline')}
                  >
                    求人票を作成
                  </Link>
                )}
                <Button variant="secondary" size="sm">
                  詳細を見る
                </Button>
              </div>
            </Card>

            <Card className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    {isSeeker ? 'プロフィール完成度' : '今月の進捗'}
                  </p>
                  <h3 className="text-lg font-semibold">
                    {isSeeker ? '履歴書' : '採用進捗'}
                  </h3>
                </div>
                <span className="text-xs font-semibold text-primary">進行中</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{isSeeker ? '入力状況' : '目標達成率'}</span>
                  <span className="font-semibold text-primary">
                    {isSeeker ? `${user.profileCompletion || '0'}%` : '80%'}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-muted">
                  <div
                    className="h-2 rounded-full bg-primary"
                    style={{ width: isSeeker ? `${user.profileCompletion || '0'}%` : '80%' }}
                  />
                </div>
              </div>
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground break-words min-w-0">
                      {isSeeker
                        ? ['基本情報', '学歴・職歴', 'スキル・資格'][i - 1]
                        : ['人気職種', '平均選考日数', '応募率'][i - 1]}
                    </span>
                    <span className="font-semibold text-foreground">
                      {isSeeker ? '未入力' : ['エンジニア', '14日', '23%'][i - 1]}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </section>
        </div>
      </main>
    </Layout>
  );
};
