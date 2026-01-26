import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Link, useLocation, useSearchParams } from 'react-router-dom';
import { Layout } from '../../../shared/components/Layout';
import { JOB_TYPES } from '../../../shared/constants/jobTypes';
import { LOCATION_GROUPS } from '../../../shared/constants/locationGroups';
import { useAuth } from '../../auth/hooks/useAuth';
import { Card } from '../../../components/ui/card';
import { Button, buttonVariants } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { cn } from '../../../lib/utils';
import layoutStyles from '../../../shared/components/Layout.module.css';

interface SeekerJob {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  employmentType: string;
  tags: string[];
  updatedAt: string;
  createdAt: string;
  views: number;
}

export const JobsSeekerPage = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const keywordParam = searchParams.get('keyword') ?? '';
  const jobTypeParam = searchParams.get('jobType') ?? '';
  const locationParam = searchParams.get('location') ?? '';
  const salaryParam = searchParams.get('salary') ?? '';
  const workStyleParam = searchParams.get('workStyle') ?? '';
  const favoritesParam = searchParams.get('favorites') ?? '';
  const sortParam = searchParams.get('sort') ?? '';
  const [searchQuery, setSearchQuery] = useState(keywordParam);
  const [jobTypeValues, setJobTypeValues] = useState<string[]>(jobTypeParam ? jobTypeParam.split(',') : []);
  const [jobTypeDraft, setJobTypeDraft] = useState<string[]>([]);
  const [isJobTypeOpen, setIsJobTypeOpen] = useState(false);
  const [locationValues, setLocationValues] = useState<string[]>(locationParam ? locationParam.split(',') : []);
  const [locationDraft, setLocationDraft] = useState<string[]>([]);
  const [isLocationOpen, setIsLocationOpen] = useState(false);
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const [salaryValue, setSalaryValue] = useState(salaryParam ? parseInt(salaryParam, 10) : 0);
  const [isSalaryOpen, setIsSalaryOpen] = useState(false);
  const salaryPopoverRef = useRef<HTMLDivElement | null>(null);
  const [isSortOpen, setIsSortOpen] = useState(false);
  const sortPopoverRef = useRef<HTMLDivElement | null>(null);
  const [sortOrder, setSortOrder] = useState<'default' | 'updated' | 'new' | 'salary'>(
    sortParam === 'updated' || sortParam === 'new' || sortParam === 'salary' ? sortParam : 'default'
  );
  const [isWorkStyleOpen, setIsWorkStyleOpen] = useState(false);
  const workStylePopoverRef = useRef<HTMLDivElement | null>(null);
  const [workStyleDraft, setWorkStyleDraft] = useState<string[]>([]);
  const [workStyleValues, setWorkStyleValues] = useState<string[]>(
    workStyleParam ? workStyleParam.split(',').map((item) => item.trim()).filter(Boolean) : []
  );
  const [favoriteJobIds, setFavoriteJobIds] = useState<Set<number>>(new Set());
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(favoritesParam === '1');

  useEffect(() => {
    setSearchQuery(keywordParam);
  }, [keywordParam]);

  useEffect(() => {
    setJobTypeValues(jobTypeParam ? jobTypeParam.split(',') : []);
  }, [jobTypeParam]);

  useEffect(() => {
    setLocationValues(locationParam ? locationParam.split(',') : []);
  }, [locationParam]);

  useEffect(() => {
    setSalaryValue(salaryParam ? parseInt(salaryParam, 10) : 0);
  }, [salaryParam]);

  useEffect(() => {
    setWorkStyleValues(workStyleParam ? workStyleParam.split(',').map((item) => item.trim()).filter(Boolean) : []);
  }, [workStyleParam]);

  useEffect(() => {
    setShowFavoritesOnly(favoritesParam === '1');
  }, [favoritesParam]);

  useEffect(() => {
    setSortOrder(sortParam === 'updated' || sortParam === 'new' || sortParam === 'salary' ? sortParam : 'default');
  }, [sortParam]);

  useLayoutEffect(() => {
    const key = `scroll:${location.pathname}${location.search}`;
    const restore = (value: string | null) => {
      if (!value) return;
      const y = Number(value);
      if (!Number.isNaN(y)) {
        window.scrollTo(0, y);
      }
    };
    const saved = sessionStorage.getItem(key);
    restore(saved);
    requestAnimationFrame(() => restore(saved));
    const timeoutId = window.setTimeout(() => restore(saved), 50);
    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [location.pathname, location.search]);

  const saveScrollPosition = () => {
    const key = `scroll:${location.pathname}${location.search}`;
    sessionStorage.setItem(key, String(window.scrollY));
  };

  useEffect(() => {
    const key = `scroll:${location.pathname}${location.search}`;
    let rafId = 0;
    const handleScroll = () => {
      if (rafId) return;
      rafId = window.requestAnimationFrame(() => {
        sessionStorage.setItem(key, String(window.scrollY));
        rafId = 0;
      });
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (rafId) window.cancelAnimationFrame(rafId);
    };
  }, [location.pathname, location.search]);

  useEffect(() => {
    const previous = window.history.scrollRestoration;
    window.history.scrollRestoration = 'manual';
    return () => {
      window.history.scrollRestoration = previous;
    };
  }, []);

  useEffect(() => {
    if (!isSalaryOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (salaryPopoverRef.current && !salaryPopoverRef.current.contains(event.target as Node)) {
        setIsSalaryOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isSalaryOpen]);

  useEffect(() => {
    if (!isSortOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (sortPopoverRef.current && !sortPopoverRef.current.contains(event.target as Node)) {
        setIsSortOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isSortOpen]);

  useEffect(() => {
    if (!isWorkStyleOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (workStylePopoverRef.current && !workStylePopoverRef.current.contains(event.target as Node)) {
        setIsWorkStyleOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isWorkStyleOpen]);

  const updateSearchParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    setSearchParams(params, { replace: true });
  };

  const openJobTypeModal = () => {
    setJobTypeDraft(jobTypeValues);
    setIsJobTypeOpen(true);
  };

  const openLocationModal = () => {
    setLocationDraft(locationValues);
    setIsLocationOpen(true);
  };

  const confirmJobType = () => {
    setJobTypeValues(jobTypeDraft);
    updateSearchParam('jobType', jobTypeDraft.join(','));
    setIsJobTypeOpen(false);
  };

  const confirmLocation = () => {
    setLocationValues(locationDraft);
    updateSearchParam('location', locationDraft.join(','));
    setIsLocationOpen(false);
  };

  const jobs: SeekerJob[] = [
    {
      id: 1,
      title: 'フロントエンドエンジニア',
      company: '株式会社ネクストキャリア',
      location: '東京都渋谷区',
      salary: '500万円～800万円',
      employmentType: '正社員',
      tags: ['React', 'TypeScript', 'フルリモート可'],
      updatedAt: '2024-02-15',
      createdAt: '2024-02-10',
      views: 1240,
    },
    {
      id: 2,
      title: 'バックエンドエンジニア',
      company: 'テックグロース株式会社',
      location: '東京都港区',
      salary: '600万円～900万円',
      employmentType: '正社員',
      tags: ['Python', 'Django', 'AWS'],
      updatedAt: '2024-02-14',
      createdAt: '2024-02-08',
      views: 980,
    },
    {
      id: 3,
      title: 'フルスタックエンジニア',
      company: 'スタートアップ合同会社',
      location: '大阪府大阪市',
      salary: '450万円～700万円',
      employmentType: '正社員',
      tags: ['Vue.js', 'Node.js', 'スタートアップ'],
      updatedAt: '2024-02-13',
      createdAt: '2024-02-13',
      views: 760,
    },
    {
      id: 4,
      title: 'モバイルアプリエンジニア',
      company: 'エッジモバイル株式会社',
      location: '東京都新宿区',
      salary: '550万円～850万円',
      employmentType: '正社員',
      tags: ['React Native', 'iOS', 'Android'],
      updatedAt: '2024-02-12',
      createdAt: '2024-02-12',
      views: 640,
    },
  ];

  const filteredJobs = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    const jobTypeQueries = jobTypeParam
      ? jobTypeParam.split(',').map((type) => type.trim().toLowerCase()).filter(Boolean)
      : [];
    const salaryMin = salaryParam ? parseInt(salaryParam, 10) : 0;
    const locations = locationParam ? locationParam.split(',').map((item) => item.trim()) : [];
    const workStyles = workStyleParam ? workStyleParam.split(',').map((item) => item.trim()) : [];

    const matchesLocation = (job: SeekerJob) => {
      if (locations.length === 0) return true;
      return locations.some((loc) => {
        if (loc === 'フルリモート') {
          return job.tags.some((tag) => tag.includes('フルリモート'));
        }
        return job.location.includes(loc);
      });
    };

    const matchesSalary = (job: SeekerJob) => {
      if (!salaryMin) return true;
      const match = job.salary.match(/(\d+)\s*万/);
      const min = match ? parseInt(match[1], 10) : 0;
      return min >= salaryMin;
    };

    const filtered = jobs.filter((job) => {
      if (showFavoritesOnly && !favoriteJobIds.has(job.id)) return false;
      if (jobTypeQueries.length) {
        const matched = jobTypeQueries.some((type) =>
          job.title.toLowerCase().includes(type) ||
          job.tags.some((tag) => tag.toLowerCase().includes(type))
        );
        if (!matched) return false;
      }
      if (query) {
        const matched =
          job.title.toLowerCase().includes(query) ||
          job.company.toLowerCase().includes(query) ||
          job.tags.some((tag) => tag.toLowerCase().includes(query));
        if (!matched) return false;
      }
      if (!matchesLocation(job)) return false;
      if (!matchesSalary(job)) return false;
      if (workStyles.length) {
        const matched = workStyles.some((style) => job.tags.some((tag) => tag.includes(style)));
        if (!matched) return false;
      }
      return true;
    });

    const parseDate = (value: string) => new Date(value).getTime();
    const parseSalaryMin = (value: string) => {
      const match = value.match(/(\d+)\s*万/);
      return match ? parseInt(match[1], 10) : 0;
    };

    return [...filtered].sort((a, b) => {
      if (sortOrder === 'updated') {
        return parseDate(b.updatedAt) - parseDate(a.updatedAt);
      }
      if (sortOrder === 'new') {
        return parseDate(b.createdAt) - parseDate(a.createdAt);
      }
      if (sortOrder === 'salary') {
        return parseSalaryMin(b.salary) - parseSalaryMin(a.salary);
      }
      return b.views - a.views;
    });
  }, [favoriteJobIds, jobTypeParam, jobs, keywordParam, locationParam, salaryParam, searchQuery, showFavoritesOnly, sortOrder, workStyleParam]);

  if (!user) {
    return null;
  }

  const jobTypeLabel = jobTypeValues.length ? jobTypeValues.join(' / ') : '職種';
  const locationLabel = locationValues.length ? locationValues.join(' / ') : '勤務地';
  const salaryLabel = salaryValue === 0 ? '指定無し' : salaryValue === 1000 ? '1000万以上' : `${salaryValue}万以上`;
  const workStyleLabel = workStyleValues.length ? workStyleValues.join(' / ') : '働き方';
  const sortLabel = (() => {
    switch (sortOrder) {
      case 'updated':
        return '更新順';
      case 'new':
        return '新着順';
      case 'salary':
        return '年収が高い順';
      default:
        return '指定なし';
    }
  })();

  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-none px-4 py-6 space-y-6">
          <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <h1 className="text-2xl font-semibold leading-7 break-words">求人一覧</h1>
              <p className="text-sm leading-6 text-muted-foreground">
                希望に合った求人を検索して詳細を確認できます
              </p>
            </div>
            <Button variant="secondary" size="sm">条件を保存</Button>
          </header>

          <Card className="p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0 flex-1 flex flex-col gap-2 sm:flex-row sm:items-center">
                <div className="flex-1 min-w-0">
                  <Input
                    placeholder="企業名・スキルで検索"
                    value={searchQuery}
                    onChange={(e) => {
                      const value = e.target.value;
                      setSearchQuery(value);
                      updateSearchParam('keyword', value.trim());
                    }}
                  />
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <Button variant="secondary" size="sm" onClick={openJobTypeModal}>
                  {jobTypeLabel}
                </Button>
                <Button variant="secondary" size="sm" onClick={openLocationModal}>
                  {locationLabel}
                </Button>
                <div className="relative" ref={salaryPopoverRef}>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setIsSalaryOpen((prev) => !prev)}
                    aria-haspopup="dialog"
                    aria-expanded={isSalaryOpen}
                  >
                    年収: {salaryLabel}
                  </Button>
                  {isSalaryOpen && (
                    <div className="absolute right-0 mt-2 w-64 rounded-lg border border-subtle bg-surface shadow-lg p-3 z-10">
                      <div className="text-xs text-muted-foreground mb-2">年収</div>
                      <div className="space-y-2">
                        <input
                          type="range"
                          min="0"
                          max="1000"
                          step="100"
                          value={salaryValue}
                          onChange={(e) => {
                            const value = Number(e.target.value);
                            setSalaryValue(value);
                            updateSearchParam('salary', value === 0 ? '' : String(value));
                          }}
                          className="w-full"
                          style={{ accentColor: 'var(--color-brand-primary)' }}
                        />
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>指定無し</span>
                          <span className="font-semibold text-primary">{salaryLabel}</span>
                          <span>1000万以上</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="relative" ref={workStylePopoverRef}>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setWorkStyleDraft(workStyleValues);
                      setIsWorkStyleOpen((prev) => !prev);
                    }}
                    aria-haspopup="dialog"
                    aria-expanded={isWorkStyleOpen}
                  >
                    {workStyleLabel}
                  </Button>
                  {isWorkStyleOpen && (
                    <div className="absolute right-0 mt-2 w-64 rounded-lg border border-subtle bg-surface shadow-lg p-3 z-10">
                      <div className="text-sm text-main font-semibold mb-2">働き方</div>
                      <div className="space-y-2">
                        {['フルリモート', 'ハイブリッド（週2-3出社）', '完全出社', 'フレキシブル'].map((option) => {
                          const isChecked = workStyleDraft.includes(option);
                          return (
                            <label key={option} className="flex items-center gap-2 text-sm text-main">
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => {
                                  setWorkStyleDraft((prev) =>
                                    prev.includes(option)
                                      ? prev.filter((item) => item !== option)
                                      : [...prev, option]
                                  );
                                }}
                                style={{ accentColor: 'var(--color-brand-primary)' }}
                              />
                              {option}
                            </label>
                          );
                        })}
                      </div>
                      <div className="flex items-center justify-between gap-2 mt-3">
                        <button
                          type="button"
                          className="text-xs text-muted"
                          onClick={() => {
                            setWorkStyleDraft([]);
                            setWorkStyleValues([]);
                            updateSearchParam('workStyle', '');
                          }}
                        >
                          クリア
                        </button>
                        <button
                          type="button"
                          className="text-xs font-semibold text-primary"
                          onClick={() => {
                            setWorkStyleValues(workStyleDraft);
                            updateSearchParam('workStyle', workStyleDraft.join(','));
                            setIsWorkStyleOpen(false);
                          }}
                        >
                          確定する
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                <div className="relative" ref={sortPopoverRef}>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsSortOpen((prev) => !prev)}
                    aria-haspopup="menu"
                    aria-expanded={isSortOpen}
                  >
                    並び替え: {sortLabel}
                  </Button>
                  {isSortOpen && (
                    <div className="absolute right-0 mt-2 w-48 rounded-lg border border-subtle bg-surface shadow-lg p-2 z-10">
                      {[
                        { value: 'default', label: '指定なし' },
                        { value: 'updated', label: '更新順' },
                        { value: 'new', label: '新着順' },
                        { value: 'salary', label: '年収が高い順' },
                      ].map((option) => (
                        <button
                          key={option.value}
                          type="button"
                          className={`w-full text-left px-3 py-2 text-sm rounded ${
                            sortOrder === option.value ? 'bg-subtle text-main' : 'text-muted'
                          }`}
                          onClick={() => {
                            const value = option.value as 'default' | 'updated' | 'new' | 'salary';
                            setSortOrder(value);
                            updateSearchParam('sort', value === 'default' ? '' : value);
                            setIsSortOpen(false);
                          }}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>

          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">求人 {filteredJobs.length} 件</p>
            <Button
              variant={showFavoritesOnly ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => {
                setShowFavoritesOnly((prev) => {
                  const next = !prev;
                  updateSearchParam('favorites', next ? '1' : '');
                  return next;
                });
              }}
            >
              お気に入り
            </Button>
          </div>

          <div className="space-y-3">
            {filteredJobs.map((job) => (
              <Card key={job.id} className="p-4 sm:p-5 space-y-3 min-w-0">
                <div className="flex flex-col gap-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 space-y-2">
                    <h2 className="text-lg font-semibold break-words">{job.title}</h2>
                    <div className="text-sm text-muted-foreground">{job.company}</div>
                      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
                        <span>{job.location}</span>
                        <span>{job.salary}</span>
                        <span>{job.employmentType}</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {job.tags.map((tag) => (
                          <span key={tag} className="px-3 py-1 rounded-full bg-muted text-foreground text-xs border border-border">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  <div className="text-right text-sm text-muted-foreground flex-shrink-0 space-y-1">
                    <button
                      type="button"
                      className="inline-flex items-center justify-center text-lg text-amber-500"
                      aria-label={favoriteJobIds.has(job.id) ? 'お気に入り解除' : 'お気に入りに追加'}
                      onClick={() => {
                        setFavoriteJobIds((prev) => {
                          const next = new Set(prev);
                          if (next.has(job.id)) {
                            next.delete(job.id);
                          } else {
                            next.add(job.id);
                          }
                          return next;
                        });
                      }}
                    >
                      {favoriteJobIds.has(job.id) ? '★' : '☆'}
                    </button>
                    <div className="text-xs">更新日: {job.updatedAt}</div>
                  </div>
                </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <Link
                    to={`/jobsUser/${job.id}`}
                    state={{ fromJobsList: true }}
                    className={cn(buttonVariants({ size: 'sm', variant: 'primary' }), 'no-underline')}
                    onClick={saveScrollPosition}
                  >
                    詳細を見る
                  </Link>
                  <Link
                    to={`/jobsUser/${job.id}/apply`}
                    state={{ fromJobsList: true }}
                    className={cn(buttonVariants({ size: 'sm', variant: 'secondary' }), 'no-underline')}
                    onClick={saveScrollPosition}
                  >
                    応募する
                  </Link>
                  <Button variant="ghost" size="sm">保存</Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </main>
      {isJobTypeOpen && (
        <div
          className={layoutStyles.headerJobOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="職種を選択"
          onClick={() => setIsJobTypeOpen(false)}
        >
          <div className={layoutStyles.headerJobModal} onClick={(event) => event.stopPropagation()}>
            <div className={layoutStyles.headerJobHeader}>
              <div className={layoutStyles.headerJobTitle}>職種を選択</div>
              <button
                type="button"
                className={layoutStyles.headerJobClear}
                onClick={() => setJobTypeDraft([])}
              >
                選択をクリア
              </button>
            </div>
            <div className={layoutStyles.headerJobList}>
              <div className={layoutStyles.headerJobOptions}>
                {JOB_TYPES.map((type) => {
                  const isSelected = jobTypeDraft.includes(type);
                  return (
                    <button
                      key={type}
                      type="button"
                      className={`${layoutStyles.headerJobOption} ${isSelected ? layoutStyles.headerJobOptionActive : ''}`}
                      onClick={() => {
                        setJobTypeDraft((prev) =>
                          prev.includes(type) ? prev.filter((item) => item !== type) : [...prev, type]
                        );
                      }}
                    >
                      <input type="checkbox" checked={isSelected} readOnly />
                      {type}
                    </button>
                  );
                })}
              </div>
            </div>
            <div className={layoutStyles.headerJobActions}>
              <button type="button" className={layoutStyles.headerJobCancel} onClick={() => setIsJobTypeOpen(false)}>
                キャンセル
              </button>
              <button type="button" className={layoutStyles.headerJobConfirm} onClick={confirmJobType}>
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
      {isLocationOpen && (
        <div
          className={layoutStyles.headerLocationOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="勤務地を選択"
          onClick={() => setIsLocationOpen(false)}
        >
          <div className={layoutStyles.headerLocationModal} onClick={(event) => event.stopPropagation()}>
            <div className={layoutStyles.headerLocationHeader}>
              <div className={layoutStyles.headerLocationTitle}>勤務地を選択</div>
              <button
                type="button"
                className={layoutStyles.headerLocationClear}
                onClick={() => setLocationDraft([])}
              >
                選択をクリア
              </button>
            </div>
            <div className={layoutStyles.headerLocationList}>
              {LOCATION_GROUPS.map((group) => {
                const displayLabel = group.label === 'フルリモート・海外' ? '海外' : group.label;
                const isOpen = openGroup === group.label;
                return (
                  <div key={group.label} className={layoutStyles.headerLocationGroup}>
                    <button
                      type="button"
                      className={layoutStyles.headerLocationGroupButton}
                      aria-expanded={isOpen}
                      onClick={() => setOpenGroup(isOpen ? null : group.label)}
                    >
                      {displayLabel}
                    </button>
                    {isOpen && (
                      <div className={layoutStyles.headerLocationOptions}>
                        {group.options.filter((option) => option !== 'フルリモート').map((option) => (
                          <button
                            key={option}
                            type="button"
                            className={`${layoutStyles.headerLocationOption} ${
                              locationDraft.includes(option) ? layoutStyles.headerLocationOptionActive : ''
                            }`}
                            onClick={() => {
                              setLocationDraft((prev) =>
                                prev.includes(option) ? prev.filter((item) => item !== option) : [...prev, option]
                              );
                            }}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <div className={layoutStyles.headerLocationActions}>
              <button type="button" className={layoutStyles.headerLocationCancel} onClick={() => setIsLocationOpen(false)}>
                キャンセル
              </button>
              <button type="button" className={layoutStyles.headerLocationConfirm} onClick={confirmLocation}>
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};
