import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Layout } from '../../../shared/components/Layout';
import { Card } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';

export const JobDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // モック求人データ
  const job = {
    id: id || '1',
    title: 'フロントエンドエンジニア',
    location: '東京都渋谷区',
    salary: '500万円～800万円',
    employmentType: '正社員',
    status: '公開中',
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
    updatedAt: '2024-02-15',
  };

  const [formData, setFormData] = useState({
    title: job.title,
    location: job.location,
    salary: job.salary,
    employmentType: job.employmentType,
    status: job.status,
    tags: job.tags.join(', '),
    description: job.description,
    requirements: job.requirements.join('\n'),
    preferred: job.preferred.join('\n'),
    benefits: job.benefits.join('\n'),
    hours: job.workEnvironment.hours,
    holidays: job.workEnvironment.holidays,
    remote: job.workEnvironment.remote,
    overtime: job.workEnvironment.overtime,
    selectionProcess: job.selectionProcess.join('\n'),
    postedDate: job.postedDate,
    applicationDeadline: job.applicationDeadline,
  });

  const handleSave = (event: React.FormEvent) => {
    event.preventDefault();
    alert('保存しました（モック）');
  };

  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-5xl px-4 py-6 space-y-4">
          {/* ブレッドクラム */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Link to="/jobsClient" className="hover:text-foreground">
              求人管理
            </Link>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="break-words">求人編集</span>
          </div>

          <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
            {/* メイン */}
            <Card className="p-6 space-y-6 min-w-0">
              <form className="space-y-6" onSubmit={handleSave}>
                <section className="space-y-4">
                  <h1 className="text-2xl font-semibold">求人編集</h1>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">求人タイトル</span>
                      <input
                        className="form-input"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      />
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">雇用形態</span>
                      <select
                        className="form-input"
                        value={formData.employmentType}
                        onChange={(e) => setFormData({ ...formData, employmentType: e.target.value })}
                      >
                        <option>正社員</option>
                        <option>契約社員</option>
                        <option>業務委託</option>
                        <option>アルバイト</option>
                      </select>
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">勤務地</span>
                      <input
                        className="form-input"
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      />
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">年収</span>
                      <input
                        className="form-input"
                        value={formData.salary}
                        onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                      />
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">公開ステータス</span>
                      <select
                        className="form-input"
                        value={formData.status}
                        onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      >
                        <option>公開中</option>
                        <option>下書き</option>
                        <option>募集停止</option>
                      </select>
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">タグ（カンマ区切り）</span>
                      <input
                        className="form-input"
                        value={formData.tags}
                        onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                      />
                    </label>
                  </div>
                </section>

                <section className="space-y-3">
                  <h2 className="text-lg font-semibold">募集内容</h2>
                  <textarea
                    className="form-input min-h-[140px]"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </section>

                <section className="grid gap-4 sm:grid-cols-2">
                  <label className="space-y-2 text-sm">
                    <span className="text-muted-foreground">必須要件（改行区切り）</span>
                    <textarea
                      className="form-input min-h-[140px]"
                      value={formData.requirements}
                      onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                    />
                  </label>
                  <label className="space-y-2 text-sm">
                    <span className="text-muted-foreground">歓迎要件（改行区切り）</span>
                    <textarea
                      className="form-input min-h-[140px]"
                      value={formData.preferred}
                      onChange={(e) => setFormData({ ...formData, preferred: e.target.value })}
                    />
                  </label>
                </section>

                <section className="space-y-3">
                  <h2 className="text-lg font-semibold">待遇・福利厚生（改行区切り）</h2>
                  <textarea
                    className="form-input min-h-[120px]"
                    value={formData.benefits}
                    onChange={(e) => setFormData({ ...formData, benefits: e.target.value })}
                  />
                </section>

                <section className="space-y-4">
                  <h2 className="text-lg font-semibold">勤務環境</h2>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">勤務時間</span>
                      <input
                        className="form-input"
                        value={formData.hours}
                        onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
                      />
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">休日</span>
                      <input
                        className="form-input"
                        value={formData.holidays}
                        onChange={(e) => setFormData({ ...formData, holidays: e.target.value })}
                      />
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">リモート</span>
                      <input
                        className="form-input"
                        value={formData.remote}
                        onChange={(e) => setFormData({ ...formData, remote: e.target.value })}
                      />
                    </label>
                    <label className="space-y-2 text-sm">
                      <span className="text-muted-foreground">残業</span>
                      <input
                        className="form-input"
                        value={formData.overtime}
                        onChange={(e) => setFormData({ ...formData, overtime: e.target.value })}
                      />
                    </label>
                  </div>
                </section>

                <section className="space-y-3">
                  <h2 className="text-lg font-semibold">選考フロー（改行区切り）</h2>
                  <textarea
                    className="form-input min-h-[120px]"
                    value={formData.selectionProcess}
                    onChange={(e) => setFormData({ ...formData, selectionProcess: e.target.value })}
                  />
                </section>

                <section className="grid gap-4 sm:grid-cols-2">
                  <label className="space-y-2 text-sm">
                    <span className="text-muted-foreground">掲載日</span>
                    <input
                      className="form-input"
                      type="date"
                      value={formData.postedDate}
                      onChange={(e) => setFormData({ ...formData, postedDate: e.target.value })}
                    />
                  </label>
                  <label className="space-y-2 text-sm">
                    <span className="text-muted-foreground">応募締切</span>
                    <input
                      className="form-input"
                      type="date"
                      value={formData.applicationDeadline}
                      onChange={(e) => setFormData({ ...formData, applicationDeadline: e.target.value })}
                    />
                  </label>
                </section>

                <div className="flex flex-wrap items-center gap-2">
                  <Button type="submit">保存</Button>
                  <Button variant="secondary" type="button">プレビュー</Button>
                  <Button variant="ghost" type="button" onClick={() => navigate('/jobsClient')}>
                    一覧に戻る
                  </Button>
                </div>
              </form>
            </Card>

            {/* サイド */}
            <Card className="p-4 space-y-3 h-fit sticky top-4">
              <h3 className="text-lg font-semibold">求人概要</h3>
              <div className="space-y-2 text-sm text-foreground">
                <InfoRow label="勤務地" value={formData.location} />
                <InfoRow label="年収" value={formData.salary} />
                <InfoRow label="雇用形態" value={formData.employmentType} />
                <InfoRow label="ステータス" value={formData.status} />
              </div>
              <div className="text-xs text-muted-foreground">
                最終更新: {job.updatedAt}
              </div>
            </Card>
          </div>
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
