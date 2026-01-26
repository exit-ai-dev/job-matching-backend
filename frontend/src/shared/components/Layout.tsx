import { useEffect, useRef, useState, type ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { JOB_TYPES } from '../constants/jobTypes';
import { LOCATION_GROUPS } from '../constants/locationGroups';
import styles from './Layout.module.css';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [jobSearch, setJobSearch] = useState({
    jobType: '',
    location: '',
    salary: '',
    keyword: '',
  });
  const [isJobTypeOpen, setIsJobTypeOpen] = useState(false);
  const [jobTypeValues, setJobTypeValues] = useState<string[]>([]);
  const [jobTypeDraft, setJobTypeDraft] = useState<string[]>([]);
  const [isLocationOpen, setIsLocationOpen] = useState(false);
  const [locationValues, setLocationValues] = useState<string[]>([]);
  const [locationDraft, setLocationDraft] = useState<string[]>([]);
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const seekerPaths = ['/homeUser', '/jobsUser', '/applicationsUser', '/chatUser', '/preferencesUser', '/resumeUser', '/settingsUser'];
  const employerPaths = ['/homeClient', '/jobsClient', '/applicantsClient', '/scouts', '/chatClient', '/search', '/membersClient', '/contractsClient'];
  const isSeekerView = seekerPaths.some((path) => location.pathname.startsWith(path));
  const isEmployerView = employerPaths.some((path) => location.pathname.startsWith(path));
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [helpMessages, setHelpMessages] = useState<{ id: string; role: 'user' | 'assistant'; text: string }[]>([]);
  const [helpInput, setHelpInput] = useState('');
  const userMenuRef = useRef<HTMLDivElement | null>(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (!user) return;
    const stored = localStorage.getItem(`help-chat-${user.id}`);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as { id: string; role: 'user' | 'assistant'; text: string }[];
        setHelpMessages(parsed);
      } catch (error) {
        console.error('ヘルプチャットの読み込みに失敗:', error);
      }
    }
  }, [user]);

  useEffect(() => {
    if (!user) return;
    localStorage.setItem(`help-chat-${user.id}`, JSON.stringify(helpMessages));
  }, [helpMessages, user]);

  const sendHelpMessage = () => {
    const text = helpInput.trim();
    if (!text) return;
    const userMessage = {
      id: `u-${Date.now()}`,
      role: 'user' as const,
      text,
    };
    setHelpMessages((prev) => [...prev, userMessage]);
    setHelpInput('');
    setTimeout(() => {
      setHelpMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: 'assistant',
          text: 'お問い合わせ内容を確認しました。順次ご案内しますので少々お待ちください。',
        },
      ]);
    }, 600);
  };

  const openLocationModal = () => {
    setLocationDraft(locationValues);
    setIsLocationOpen(true);
  };

  const openJobTypeModal = () => {
    setJobTypeDraft(jobTypeValues);
    setIsJobTypeOpen(true);
  };

  const closeLocationModal = () => {
    setIsLocationOpen(false);
  };

  const closeJobTypeModal = () => {
    setIsJobTypeOpen(false);
  };

  const confirmLocation = () => {
    setLocationValues(locationDraft);
    setJobSearch((prev) => ({ ...prev, location: locationDraft.join(',') }));
    setIsLocationOpen(false);
  };

  const confirmJobType = () => {
    setJobTypeValues(jobTypeDraft);
    setJobSearch((prev) => ({ ...prev, jobType: jobTypeDraft.join(',') }));
    setIsJobTypeOpen(false);
  };

  // 求職者向けメニュー
  const seekerMenuItems = [
    { label: 'ホーム', path: '/homeUser', icon: '🏠' },
    { label: '求人検索', path: '/jobsUser', icon: '🔍' },
    { label: '応募管理', path: '/applicationsUser', icon: '📝' },
    { label: 'AI相談', path: '/chatUser', icon: '💬' },
  ];

  // 企業向けメニュー
  const employerMenuItems = [
    { label: 'HOME', path: '/homeClient', icon: '🏠' },
    { label: '応募者一覧', path: '/applicantsClient', icon: '👥' },
    { label: '求人管理', path: '/jobsClient', icon: '📋' },
    { label: 'スカウト', path: '/scouts', icon: '✉️' },
    { label: 'AI相談', path: '/chatClient', icon: '💬' },
  ];

  // ユーザーの役割に応じてメニューを選択
  const menuItems = isSeekerView
    ? seekerMenuItems
    : isEmployerView
      ? employerMenuItems
      : user?.role === 'employer'
        ? employerMenuItems
        : seekerMenuItems;

  return (
    <div className={styles.layout}>
      {/* ヘッダー */}
      <header className={styles.header}>
        <div className={styles.headerInner}>
          {/* ブランド */}
          <Link
            to={isSeekerView ? '/homeUser' : isEmployerView ? '/homeClient' : user?.role === 'seeker' ? '/homeUser' : '/homeClient'}
            className={styles.brand}
          >
            <div className={styles.brandMark}>ET</div>
            <div className={styles.brandText}>
              <div className={styles.brandTitle}>exitotrinity</div>
            </div>
          </Link>

          {/* 求職者検索 */}
          <div className={styles.searchBar}>
            {isSeekerView ? (
              <form
                className={styles.headerSearchBar}
                onSubmit={(event) => {
                  event.preventDefault();
                  const params = new URLSearchParams();
                  if (jobSearch.jobType) params.set('jobType', jobSearch.jobType);
                  if (jobSearch.location) params.set('location', jobSearch.location);
                  if (jobSearch.salary) params.set('salary', jobSearch.salary);
                  if (jobSearch.keyword) params.set('keyword', jobSearch.keyword);
                  navigate(`/jobsUser${params.toString() ? `?${params.toString()}` : ''}`);
                }}
              >
                <input
                  className={styles.headerSearchInput}
                  type="search"
                  placeholder="職種"
                  aria-label="職種"
                  value={jobTypeValues.join(' / ')}
                  readOnly
                  onClick={openJobTypeModal}
                />
                <div className={styles.headerSearchDivider} />
                <input
                  className={styles.headerSearchInput}
                  type="search"
                  placeholder="勤務地"
                  aria-label="勤務地"
                  value={locationValues.join(' / ')}
                  readOnly
                  onClick={openLocationModal}
                />
                <div className={styles.headerSearchDivider} />
                <div
                  className={styles.headerSearchSelectWrap}
                  data-empty={jobSearch.salary === '' ? 'true' : 'false'}
                >
                  <select
                    className={styles.headerSearchSelect}
                    aria-label="年収"
                    value={jobSearch.salary}
                    onChange={(event) => {
                      const value = event.target.value;
                      setJobSearch((prev) => ({ ...prev, salary: value === 'none' ? '' : value }));
                    }}
                  >
                    <option value=""></option>
                    <option value="none">指定無し</option>
                    {Array.from({ length: 9 }, (_, index) => (index + 1) * 100).map((amount) => (
                      <option key={amount} value={`${amount}万以上`}>
                        {amount}万円以上
                      </option>
                    ))}
                    <option value="1000万以上">1000万円以上</option>
                  </select>
                  {jobSearch.salary === '' && (
                    <span className={styles.headerSearchSelectPlaceholder}>年収</span>
                  )}
                </div>
                <div className={styles.headerSearchDivider} />
                <input
                  className={styles.headerSearchInput}
                  type="search"
                  placeholder="キーワード"
                  aria-label="キーワード"
                  value={jobSearch.keyword}
                  onChange={(event) => setJobSearch((prev) => ({ ...prev, keyword: event.target.value }))}
                />
                <button className={styles.headerSearchButton} type="submit" aria-label="検索">
                  <span className={styles.headerSearchIcon} />
                </button>
              </form>
            ) : isEmployerView ? (
              <Link to="/search" className={styles.manageButton}>
                求職者を検索
              </Link>
            ) : (
              <Link to={user?.role === 'employer' ? '/search' : '/jobsUser'} className={styles.manageButton}>
                {user?.role === 'employer' ? '求職者を検索' : '求人検索'}
              </Link>
            )}
          </div>

          <div className={styles.headerRight}>
            {/* ヘッダーナビ（求職者） */}
            {isSeekerView && (
              <nav className={styles.headerNav}>
                {seekerMenuItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`${styles.headerNavLink} ${location.pathname === item.path ? styles.headerNavLinkActive : ''}`}
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            )}

            {/* ユーザー情報 */}
            {user && (
              <div className={styles.userMenu} ref={userMenuRef}>
                <button
                  type="button"
                  className={styles.userMenuButton}
                  onClick={() => setIsUserMenuOpen((prev) => !prev)}
                  aria-haspopup="menu"
                  aria-expanded={isUserMenuOpen}
                >
                  <span className={styles.userAvatar}>
                    {user.name?.charAt(0) || 'U'}
                  </span>
                </button>
                {isUserMenuOpen && (
                  <div className={styles.userMenuDropdown} role="menu">
                    {isSeekerView && (
                      <>
                        <Link
                          to="/preferencesUser"
                          className={styles.userMenuItem}
                          role="menuitem"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          プロフィール編集
                        </Link>
                        <Link
                          to="/resumeUser"
                          className={styles.userMenuItem}
                          role="menuitem"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          履歴書管理
                        </Link>
                        <Link
                          to="/settingsUser"
                          className={styles.userMenuItem}
                          role="menuitem"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          設定
                        </Link>
                        <div className={styles.userMenuDivider} />
                      </>
                    )}
                    {isEmployerView && (
                      <>
                        <Link
                          to="/membersClient"
                          className={styles.userMenuItem}
                          role="menuitem"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          社員管理
                        </Link>
                        <Link
                          to="/contractsClient"
                          className={styles.userMenuItem}
                          role="menuitem"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          契約情報
                        </Link>
                        <div className={styles.userMenuDivider} />
                      </>
                    )}
                    <button
                      type="button"
                      className={styles.userMenuItem}
                      onClick={handleLogout}
                      role="menuitem"
                    >
                      ログアウト
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      <div className={`${styles.container} ${isSeekerView ? styles.containerWide : ''}`}>
        {/* サイドバー */}
        {!isSeekerView && (
          <aside className={styles.sidebar}>
          <nav className={styles.sidebarNav}>
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`${styles.sidebarLink} ${location.pathname === item.path ? styles.active : ''}`}
              >
                <span className={styles.sidebarIcon}>{item.icon}</span>
                <span className={styles.sidebarLabel}>{item.label}</span>
              </Link>
            ))}
          </nav>
          </aside>
        )}

        {/* メインコンテンツ */}
        <main className={`${styles.main} ${isSeekerView ? styles.mainWide : ''}`}>
          {children}
        </main>
      </div>
      {user && (
        <>
          {!isHelpOpen && (
            <button
              type="button"
              className={styles.helpButton}
              aria-label="AIヘルプを開く"
              onClick={() => setIsHelpOpen(true)}
            >
              ?
            </button>
          )}
          <div className={`${styles.helpPanel} ${isHelpOpen ? styles.helpPanelOpen : ''}`} role="dialog" aria-label="AIヘルプチャット">
            <div className={styles.helpHeader}>
              <div className={styles.helpTitle}>AIヘルプチャット</div>
              <button
                type="button"
                className={styles.helpClose}
                aria-label="閉じる"
                onClick={() => setIsHelpOpen(false)}
              >
                ×
              </button>
            </div>
            <div className={styles.helpBody}>
              {helpMessages.length === 0 ? (
                <div>AIヘルプがここに表示されます。質問内容を入力してください。</div>
              ) : (
                helpMessages.map((message) => (
                  <div key={message.id} style={{ marginBottom: '10px' }}>
                    <strong>{message.role === 'user' ? 'あなた' : 'AI'}</strong>
                    <div>{message.text}</div>
                  </div>
                ))
              )}
            </div>
            <div className={styles.helpFooter}>
              <input
                className={styles.helpInput}
                placeholder="質問を入力..."
                value={helpInput}
                onChange={(event) => setHelpInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    sendHelpMessage();
                  }
                }}
              />
              <button
                type="button"
                className={styles.helpSend}
                onClick={sendHelpMessage}
              >
                送信
              </button>
            </div>
          </div>
        </>
      )}
      {isLocationOpen && (
        <div
          className={styles.headerLocationOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="勤務地を選択"
          onClick={closeLocationModal}
        >
          <div className={styles.headerLocationModal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.headerLocationHeader}>
              <div className={styles.headerLocationTitle}>勤務地を選択</div>
              <button
                type="button"
                className={styles.headerLocationClear}
                onClick={() => setLocationDraft([])}
              >
                選択をクリア
              </button>
            </div>
            <div className={styles.headerLocationList}>
              {LOCATION_GROUPS.map((group) => {
                const isOpen = openGroup === group.label;
                return (
                  <div key={group.label} className={styles.headerLocationGroup}>
                    <button
                      type="button"
                      className={styles.headerLocationGroupButton}
                      aria-expanded={isOpen}
                      onClick={() => setOpenGroup(isOpen ? null : group.label)}
                    >
                      {group.label}
                    </button>
                    {isOpen && (
                      <div className={styles.headerLocationOptions}>
                        {group.options.map((option) => (
                          <button
                            key={option}
                            type="button"
                            className={`${styles.headerLocationOption} ${
                              locationDraft.includes(option) ? styles.headerLocationOptionActive : ''
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
            <div className={styles.headerLocationActions}>
              <button type="button" className={styles.headerLocationCancel} onClick={closeLocationModal}>
                キャンセル
              </button>
              <button type="button" className={styles.headerLocationConfirm} onClick={confirmLocation}>
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
      {isJobTypeOpen && (
        <div
          className={styles.headerJobOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="職種を選択"
          onClick={closeJobTypeModal}
        >
          <div className={styles.headerJobModal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.headerJobHeader}>
              <div className={styles.headerJobTitle}>職種を選択</div>
              <button
                type="button"
                className={styles.headerJobClear}
                onClick={() => setJobTypeDraft([])}
              >
                選択をクリア
              </button>
            </div>
            <div className={styles.headerJobList}>
              <div className={styles.headerJobOptions}>
                {JOB_TYPES.map((type) => {
                  const isSelected = jobTypeDraft.includes(type);
                  return (
                    <button
                      key={type}
                      type="button"
                      className={`${styles.headerJobOption} ${isSelected ? styles.headerJobOptionActive : ''}`}
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
            <div className={styles.headerJobActions}>
              <button type="button" className={styles.headerJobCancel} onClick={closeJobTypeModal}>
                キャンセル
              </button>
              <button type="button" className={styles.headerJobConfirm} onClick={confirmJobType}>
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

