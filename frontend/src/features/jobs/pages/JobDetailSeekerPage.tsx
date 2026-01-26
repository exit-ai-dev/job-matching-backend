import { useEffect, useState } from 'react';
import { useLocation, useParams, Link, useNavigate } from 'react-router-dom';
import { Layout } from '../../../shared/components/Layout';
import { Card } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';

export const JobDetailSeekerPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [showApplyModal, setShowApplyModal] = useState(false);

  useEffect(() => {
    const key = `scroll:${location.pathname}${location.search}`;
    const saved = sessionStorage.getItem(key);
    if (saved) {
      const y = Number(saved);
      if (!Number.isNaN(y)) {
        window.scrollTo(0, y);
      }
    }
    return () => {
      sessionStorage.setItem(key, String(window.scrollY));
    };
  }, [location.pathname, location.search]);

  const job = {
    id: id || '1',
    title: 'フロントエンドエンジニア',
    company: '株式会社テックカンパニー',
    location: '東京都渋谷区',
    salary: '500万円～800万円',
    employmentType: '正社員',
    remote: true,
    matchScore: 92,
    tags: ['React', 'TypeScript', 'Next.js', 'フルリモート可'],
    description: `【募集背景】
私たちは、次世代のWebアプリケーション開発を推進するスタートアップ企業です。
現在、急成長中のプロダクトのさらなる拡大に向けて、フロントエンド開発を
リードしていただけるエンジニアを募集しています。

【業務内容】
・自社プロダクトのフロントエンド開発
・UI/UXの改善提案と実装
・新機能の企画・設計・開発
・コードレビュー、技術選定
・チームメンバーの技術サポート`,
    requirements: [
      'React での開発経験 2年以上',
      'TypeScript の実務経験',
      'チーム開発の経験',
      'Gitを用いたバージョン管理の経験',
    ],
    preferred: [
      'Next.js の使用経験',
      'テスト駆動開発の経験',
      'UI/UXデザインへの理解',
      'アジャイル開発の経験',
    ],
    benefits: [
      'フルリモート勤務可能',
      'フレックスタイム制',
      '副業OK',
      '書籍購入補助（月1万円まで）',
      '最新機器支給（MacBook Pro等）',
      '勉強会参加費補助',
      'ストックオプション制度',
      '健康診断・人間ドック補助',
    ],
    workEnvironment: {
      hours: '10:00～19:00（フレックス）',
      holidays: '完全週休2日制（土日祝）、年末年始、夏季休暇、有給休暇',
      remote: 'フルリモート可（出社は月1回程度）',
      overtime: '月平均20時間程度',
    },
    selectionProcess: [
      '1. 書類選考',
      '2. カジュアル面談（1回）',
      '3. 技術面接（1回）',
      '4. 最終面接（1回）',
      '5. 内定',
    ],
    postedDate: '2024-02-15',
    applicationDeadline: '2024-03-31',
  };

  const handleApply = () => {
    setShowApplyModal(false);
    alert('応募が完了しました！');
    navigate('/applicationsUser');
  };

  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-5xl px-4 py-6 space-y-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Link to="/jobsUser" className="hover:text-foreground">
              求人詳細
            </Link>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="break-words">{job.title}</span>
          </div>

          <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
            <Card className="p-6 space-y-6 min-w-0">
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2 text-xs">
                  {job.remote && (
                    <span className="px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/30">
                      リモート可
                    </span>
                  )}
                  <span className="px-3 py-1 rounded-full bg-muted text-foreground border border-border">
                    {job.employmentType}
                  </span>
                </div>
                <h1 className="text-2xl font-semibold leading-7 break-words">{job.title}</h1>
                <div className="text-lg font-semibold break-words">{job.company}</div>
                <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>{job.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{job.salary}</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {job.tags.map((tag) => (
                    <span key={tag} className="px-3 py-1 rounded-full bg-muted text-foreground text-xs border border-border">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              <div className="grid gap-6">
                <section className="space-y-2">
                  <h2 className="text-lg font-semibold">募集内容</h2>
                  <p className="text-sm leading-6 text-foreground whitespace-pre-line break-words">
                    {job.description}
                  </p>
                </section>

                <section className="space-y-2">
                  <h2 className="text-lg font-semibold">必須要件</h2>
                  <ul className="space-y-2">
                    {job.requirements.map((req) => (
                      <li key={req} className="flex items-start gap-2 text-sm text-foreground break-words">
                        <span className="mt-0.5 h-2 w-2 rounded-full bg-primary" />
                        <span className="min-w-0">{req}</span>
                      </li>
                    ))}
                  </ul>
                </section>

                <section className="space-y-2">
                  <h2 className="text-lg font-semibold">歓迎要件</h2>
                  <ul className="space-y-2">
                    {job.preferred.map((pref) => (
                      <li key={pref} className="flex items-start gap-2 text-sm text-foreground break-words">
                        <span className="mt-0.5 h-2 w-2 rounded-full bg-border" />
                        <span className="min-w-0">{pref}</span>
                      </li>
                    ))}
                  </ul>
                </section>

                <section className="space-y-2">
                  <h2 className="text-lg font-semibold">待遇・福利厚生</h2>
                  <ul className="grid gap-2 sm:grid-cols-2">
                    {job.benefits.map((benefit) => (
                      <li key={benefit} className="flex items-start gap-2 text-sm text-foreground break-words">
                        <span className="mt-0.5 h-2 w-2 rounded-full bg-primary/70" />
                        <span className="min-w-0">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </section>

                <section className="space-y-2">
                  <h2 className="text-lg font-semibold">勤務環境</h2>
                  <div className="grid gap-2 sm:grid-cols-2">
                    <InfoRow label="勤務時間" value={job.workEnvironment.hours} />
                    <InfoRow label="休日" value={job.workEnvironment.holidays} />
                    <InfoRow label="リモート" value={job.workEnvironment.remote} />
                    <InfoRow label="残業" value={job.workEnvironment.overtime} />
                  </div>
                </section>

                <section className="space-y-2">
                  <h2 className="text-lg font-semibold">選考フロー</h2>
                  <ol className="space-y-1 text-sm leading-6 text-foreground">
                    {job.selectionProcess.map((step) => (
                      <li key={step} className="min-w-0 break-words">{step}</li>
                    ))}
                  </ol>
                </section>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button onClick={() => setShowApplyModal(true)}>この求人に応募する</Button>
                <Button variant="secondary">気になる</Button>
                <span className="text-xs text-muted-foreground ml-auto">
                  掲載日: {job.postedDate} / 応募締切: {job.applicationDeadline}
                </span>
              </div>
            </Card>

            <Card className="p-4 space-y-3 h-fit sticky top-4">
              <h3 className="text-lg font-semibold">求人概要</h3>
              <div className="space-y-2 text-sm text-foreground">
                <InfoRow label="勤務地" value={job.location} />
                <InfoRow label="年収" value={job.salary} />
                <InfoRow label="雇用形態" value={job.employmentType} />
                <InfoRow label="マッチ度" value={`${job.matchScore}%`} />
              </div>
              <Link to="/jobsUser" state={{ fromJobsList: true }} className="no-underline">
                <Button size="sm" className="w-full">一覧に戻る</Button>
              </Link>
            </Card>
          </div>

          {showApplyModal && (
            <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center px-4">
              <Card className="p-6 w-full max-w-md space-y-4">
                <h3 className="text-lg font-semibold">応募を送信しますか？</h3>
                <p className="text-sm leading-6 text-muted-foreground">
                  応募後に採用担当者へ通知されます。プロフィールを最新の状態にしておくとスムーズです。
                </p>
                <div className="flex flex-wrap gap-2 justify-end">
                  <Button variant="secondary" onClick={() => setShowApplyModal(false)}>
                    キャンセル
                  </Button>
                  <Button onClick={handleApply}>応募する</Button>
                </div>
              </Card>
            </div>
          )}
        </div>
      </main>
    </Layout>
  );
};

const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-start justify-between gap-2 text-sm">
    <span className="text-muted-foreground">{label}</span>
    <span className="font-semibold text-foreground min-w-0 break-words text-right">{value}</span>
  </div>
);
