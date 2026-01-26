import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../../../shared/components/Layout';
import { useAuth } from '../../auth/hooks/useAuth';
import { Card } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { applicationsApi } from '../../../shared/lib/api';
import type { Application } from '../../../shared/types';

type ApplicationStatus = 'all' | 'screening' | 'interview' | 'offered' | 'rejected';

export const ApplicationsPage = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<ApplicationStatus>('all');

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await applicationsApi.getApplications();
        setApplications(response.applications);
      } catch (err) {
        console.error('応募情報取得エラー:', err);
        setError('応募情報の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchApplications();
    }
  }, [user]);

  const statusOptions = [
    { value: 'all', label: 'すべて', count: applications.length },
    { value: 'screening', label: '書類選考中', count: applications.filter(a => a.status.includes('書類')).length },
    { value: 'interview', label: '面接予定', count: applications.filter(a => a.status.includes('面接')).length },
    { value: 'offered', label: '内定', count: applications.filter(a => a.status.includes('内定') || a.status.includes('通過')).length },
    { value: 'rejected', label: '不合格', count: applications.filter(a => a.status.includes('不合格') || a.status.includes('辞退')).length },
  ];

  const getStatusBadgeClass = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-primary/10 text-primary border-primary/30',
      yellow: 'bg-amber-100 text-amber-700 border-amber-200',
      green: 'bg-emerald-100 text-emerald-700 border-emerald-200',
      red: 'bg-red-100 text-red-700 border-red-200',
      gray: 'bg-gray-100 text-gray-700 border-gray-200',
    };
    return colors[color] || colors.gray;
  };

  if (!user) return null;
  const jobBasePath = user.role === 'seeker' ? '/jobsUser' : '/jobsClient';

  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-none px-4 py-6 space-y-6">
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold leading-7">応募管理</h1>
            <p className="text-sm leading-6 text-muted-foreground">応募した求人の選考状況を確認できます</p>
          </div>

          <div className="grid gap-4 lg:grid-cols-[260px,1fr]">
            {/* フィルター */}
            <aside className="space-y-4">
              <Card className="p-4 sticky top-4 space-y-4">
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">選考状況</h3>
                  <div className="space-y-2">
                    {statusOptions.map((option) => {
                      const active = selectedStatus === option.value;
                      return (
                        <button
                          key={option.value}
                          onClick={() => setSelectedStatus(option.value as ApplicationStatus)}
                          className={`w-full flex items-center justify-between rounded-lg px-3 py-2 text-sm transition ${
                            active ? 'bg-primary text-white' : 'bg-surface border border-border hover:bg-muted'
                          }`}
                        >
                          <span>{option.label}</span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              active ? 'bg-white/20' : 'bg-muted text-muted-foreground'
                            }`}
                          >
                            {option.count}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="pt-4 border-t border-border space-y-3">
                  <h4 className="text-sm font-semibold">統計</h4>
                  <StatRow label="総応募数" value={`${applications.length}`} />
                  <ProgressRow label="書類通過率" value="75%" percent={75} />
                  <ProgressRow label="面接通過率" value="60%" percent={60} />
                </div>
              </Card>
            </aside>

            {/* メイン */}
            <div className="space-y-4">
              {error && (
                <Card className="p-4 bg-destructive/10 text-destructive border-destructive">
                  <p className="text-sm">{error}</p>
                </Card>
              )}

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : applications.length === 0 ? (
                <Card className="p-10 text-center space-y-3">
                  <div className="text-4xl">📄</div>
                  <h3 className="text-lg font-semibold">応募履歴がありません</h3>
                  <p className="text-sm text-muted-foreground">まずは気になる求人に応募してみましょう</p>
                  <Link to={jobBasePath} className="no-underline">
                    <Button>求人を探す</Button>
                  </Link>
                </Card>
              ) : (
                <>
                  {applications.map((application) => (
                    <Card key={application.id} className="p-4 sm:p-5 space-y-3 hover:shadow-md transition">
                      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-start">
                        <div className="flex-1 min-w-0 space-y-2">
                          <div className="flex flex-wrap gap-2">
                            <span
                              className={`px-3 py-1 text-xs font-medium rounded-full border ${getStatusBadgeClass(
                                application.statusColor
                              )}`}
                            >
                              {application.status}
                            </span>
                            {application.nextStep && (
                              <span className="px-3 py-1 bg-muted text-foreground text-xs rounded-full border border-border">
                                次: {application.nextStep}
                              </span>
                            )}
                          </div>

                          <Link to={`/jobs/${application.jobId}`} className="block space-y-1">
                            <h3 className="text-lg font-semibold break-words">{application.jobTitle}</h3>
                            <p className="text-sm font-medium text-foreground break-words">{application.company}</p>
                          </Link>

                          <div className="grid gap-x-4 gap-y-2 text-sm text-muted-foreground sm:grid-cols-2">
                            <Info label="勤務地" value={application.location} />
                            <Info label="年収" value={application.salary} />
                            <Info label="応募日" value={application.appliedDate} />
                            <Info label="更新" value={application.lastUpdate} />
                          </div>

                          {application.interviewDate && (
                            <div className="bg-primary/10 border border-primary/30 rounded-lg p-3 text-sm">
                              <span className="font-semibold text-primary">面接予定: </span>
                              <span className="text-primary">{application.interviewDate}</span>
                            </div>
                          )}

                          <div className="flex items-center gap-3 text-xs">
                            <span className="text-muted-foreground">提出書類:</span>
                            <Doc status={application.documents.resume} label="履歴書" />
                            <Doc status={application.documents.portfolio} label="ポートフォリオ" />
                            <Doc status={application.documents.coverLetter} label="志望動機" />
                          </div>
                        </div>

                        <div className="text-right flex-shrink-0 space-y-2">
                          {application.matchScore && (
                            <>
                              <div className="text-2xl font-semibold text-primary">{application.matchScore}%</div>
                              <div className="text-xs text-muted-foreground">マッチ度</div>
                            </>
                          )}
                          <div className="space-y-2">
                            <Link to={`/jobs/${application.jobId}`} className="block no-underline">
                              <Button variant="secondary" size="sm" className="w-full">
                                求人を見る
                              </Button>
                            </Link>
                            <Button variant="ghost" size="sm" className="w-full">
                              企業に連絡
                            </Button>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </>
              )}
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
};

const StatRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-center justify-between text-xs text-muted-foreground">
    <span>{label}</span>
    <span className="text-foreground font-semibold">{value}</span>
  </div>
);

const ProgressRow = ({ label, value, percent }: { label: string; value: string; percent: number }) => (
  <div className="space-y-1">
    <div className="flex items-center justify-between text-xs text-muted-foreground">
      <span>{label}</span>
      <span className="text-foreground font-semibold">{value}</span>
    </div>
    <div className="h-1.5 rounded-full bg-muted">
      <div className="h-1.5 rounded-full bg-primary" style={{ width: `${percent}%` }} />
    </div>
  </div>
);

const Info = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-center gap-2 min-w-0">
    <span className="text-muted-foreground">{label}:</span>
    <span className="text-foreground break-words">{value}</span>
  </div>
);

const Doc = ({ status, label }: { status: boolean; label: string }) => (
  <span className={status ? 'text-primary font-semibold' : 'text-muted-foreground'}>
    {status ? '✓' : '×'} {label}
  </span>
);
