import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../../../shared/components/Layout';
import { useAuth } from '../../auth/hooks/useAuth';
import { Card } from '../../../components/ui/card';
import { Button, buttonVariants } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { cn } from '../../../lib/utils';
import { jobsApi } from '../../../shared/lib/api';
import type { Job } from '../../../shared/types';

export const JobsPage = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // 初期データ取得
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await jobsApi.getJobs({ page: 1, perPage: 20 });
        setJobs(response.jobs);
      } catch (err) {
        console.error('求人取得エラー:', err);
        setError('求人情報の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchJobs();
    }
  }, [user]);

  // 検索実行
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await jobsApi.searchJobs({ query: searchQuery });
      setJobs(response.jobs);
    } catch (err) {
      console.error('検索エラー:', err);
      setError('検索に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // クライアント側フィルタリング（検索前の一時的なフィルタ）
  const filteredJobs = searchQuery
    ? jobs.filter((job) => {
        const matchesSearch =
          job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
          job.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesSearch;
      })
    : jobs;

  if (!user) {
    return null;
  }

  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-5xl px-4 py-6 space-y-6">
          <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <h1 className="text-2xl font-semibold leading-7 break-words">求人管理</h1>
              <p className="text-sm leading-6 text-muted-foreground">
                企業が公開している求人を管理・編集します
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm">インポート</Button>
              <Button size="sm">新規求人を作成</Button>
            </div>
          </header>

          <div className="space-y-4">
            <Card className="p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0 flex-1">
                  <Input
                    placeholder="求人名・職種で検索"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button
                    onClick={handleSearch}
                    size="sm"
                    className="w-full"
                    disabled={loading}
                  >
                    検索
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="secondary" size="sm">公開中</Button>
                  <Button variant="secondary" size="sm">下書き</Button>
                  <Button variant="secondary" size="sm">募集停止</Button>
                  <Button variant="ghost" size="sm">並び替え</Button>
                </div>
              </div>
            </Card>

            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">求人 {filteredJobs.length} 件</p>
              <Button variant="ghost" size="sm">一括操作</Button>
            </div>

            {/* 検索結果 */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  {loading ? '読み込み中...' : `検索結果 ${filteredJobs.length} 件`}
                </p>
                <Button variant="ghost" size="sm">並び替え</Button>
              </div>

              {error && (
                <Card className="p-4 bg-destructive/10 text-destructive border-destructive">
                  <p className="text-sm">{error}</p>
                </Card>
              )}

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : filteredJobs.length === 0 ? (
                <Card className="p-8 text-center">
                  <p className="text-muted-foreground">求人が見つかりませんでした</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {filteredJobs.map((job) => (
                    <Card key={job.id} className="p-4 sm:p-5 space-y-3 min-w-0">
                      <div className="flex flex-col gap-2">
                        <div className="flex flex-wrap gap-2 text-xs">
                          {job.remote && (
                            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/30">
                              リモート可
                            </span>
                          )}
                          <span className="px-3 py-1 rounded-full bg-muted text-foreground border border-border">
                            {job.employmentType}
                          </span>
                          {job.featured && (
                            <span className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300">
                              注目
                            </span>
                          )}
                        </div>
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 space-y-1">
                            <h2 className="text-lg font-semibold break-words">{job.title}</h2>
                            <p className="text-sm text-muted-foreground break-words">{job.company}</p>
                            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
                              <span>{job.location}</span>
                              <span>{job.salary}</span>
                            </div>
                          </div>
                          {job.matchScore && (
                            <div className="text-right text-sm font-semibold text-primary flex-shrink-0">
                              {job.matchScore}%
                            </div>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {job.tags.map((tag) => (
                            <span key={tag} className="px-3 py-1 rounded-full bg-muted text-foreground text-xs border border-border">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <Link
                          to={`/jobs/${job.id}`}
                          className={cn(buttonVariants({ size: 'sm', variant: 'primary' }), 'no-underline')}
                        >
                          詳細を見る
                        </Link>
                        <Button variant="secondary" size="sm">気になる</Button>
                        {job.postedDate && (
                          <span className="text-xs text-muted-foreground ml-auto">掲載日: {job.postedDate}</span>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
};
