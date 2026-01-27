import { useState } from 'react';
import { JOB_TYPES } from '../../../shared/constants/jobTypes';
import { LOCATION_GROUPS } from '../../../shared/constants/locationGroups';
import styles from './LandingPage.module.css';

const NAV_ITEMS = [
  { label: '機能', href: '#features' },
  { label: '特徴', href: '#benefits' },
  { label: 'ログイン', href: '/login' },
  { label: '登録', href: '/register' },
];

const HERO_COPY = [
  '転職市場におけるマッチングは、長い間、企業から求職者へと一方向的に求人情報が提供される形が一般的でした。この伝統的なアプローチの多くは、求職者の真のキャリアニーズを置き去りにしていたのかもしれません。',
  '私たちはAI技術の領域でデザインの力を活用することが、キャリアマッチングの課題を解決する糸口だと信じています。デザインは単に物事を美しく見せる以上の役割を果たします。それは、人間の生活に深く根ざし、あらゆる転職体験を滑らかにします。',
  '私たちの使命は、求職者が最適なキャリアを見つけ、企業が最適な人材と出会える、自由で便利な転職体験の実現を支援することです。',
];

const VALUE_CARDS = [
  { label: 'AI Matching', desc: 'スキルと経験から最適なマッチング。' },
  { label: 'Chat Support', desc: '24時間365日、AIが転職をサポート。' },
  { label: 'Career Fit', desc: 'カルチャーと価値観の相性を可視化。' },
];

export const LandingPage = () => {
  const [isJobTypeOpen, setIsJobTypeOpen] = useState(false);
  const [jobTypeValues, setJobTypeValues] = useState<string[]>([]);
  const [jobTypeDraft, setJobTypeDraft] = useState<string[]>([]);
  const [isLocationOpen, setIsLocationOpen] = useState(false);
  const [locationValues, setLocationValues] = useState<string[]>([]);
  const [locationDraft, setLocationDraft] = useState<string[]>([]);
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const [salaryValue, setSalaryValue] = useState('');

  const openJobTypeModal = () => {
    setJobTypeDraft(jobTypeValues);
    setIsJobTypeOpen(true);
  };

  const openLocationModal = () => {
    setLocationDraft(locationValues);
    setIsLocationOpen(true);
  };

  const closeJobTypeModal = () => {
    setIsJobTypeOpen(false);
  };

  const closeLocationModal = () => {
    setIsLocationOpen(false);
  };

  const confirmJobType = () => {
    setJobTypeValues(jobTypeDraft);
    setIsJobTypeOpen(false);
  };

  const confirmLocation = () => {
    setLocationValues(locationDraft);
    setIsLocationOpen(false);
  };

  return (
    <div className={styles.pageShell}>
      <div className={styles.page}>
        <div className={styles.overlay} />
        <div className={styles.wrap}>
        <header className={styles.header}>
          <div className={styles.headerInner}>
            <div className={styles.brand}>
              <div className={styles.brandMark}>ET</div>
              <div className={styles.brandText}>
                <p>EXITOTRINITY</p>
                <h1>AI Job Matching</h1>
              </div>
            </div>
            <form
              className={styles.searchBar}
              action="/jobsUser"
              method="get"
              onSubmit={(event) => {
                const form = event.currentTarget;
                const inputs = Array.from(form.querySelectorAll<HTMLInputElement>('input[type="search"]'));
                const hasValue = inputs.some((input) => input.value.trim().length > 0);
                const salarySelect = form.querySelector<HTMLSelectElement>('select[name="salary"]');
                if (salarySelect && salarySelect.value === '') {
                  salarySelect.disabled = true;
                  setTimeout(() => {
                    salarySelect.disabled = false;
                  }, 0);
                }
                if (!hasValue) {
                  event.preventDefault();
                }
              }}
            >
              <input
                className={styles.searchInput}
                type="search"
                placeholder="職種"
                aria-label="職種"
                value={jobTypeValues.join(' / ')}
                readOnly
                onClick={openJobTypeModal}
              />
              <input type="hidden" name="jobType" value={jobTypeValues.join(',')} />
              <div className={styles.searchDivider} />
              <input
                className={styles.searchInput}
                type="search"
                placeholder="勤務地"
                aria-label="勤務地"
                value={locationValues.join(' / ')}
                readOnly
                onClick={openLocationModal}
              />
              <input type="hidden" name="location" value={locationValues.join(',')} />
              <div className={styles.searchDivider} />
              <div className={styles.searchSelectWrap} data-empty={salaryValue === '' ? 'true' : 'false'}>
                <select
                  className={styles.searchSelect}
                  name="salary"
                  aria-label="年収"
                  value={salaryValue}
                  onChange={(event) => {
                    const value = event.target.value;
                    setSalaryValue(value === 'none' ? '' : value);
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
                {salaryValue === '' && <span className={styles.searchSelectPlaceholder}>年収</span>}
              </div>
              <div className={styles.searchDivider} />
              <input className={styles.searchInput} type="search" name="keyword" placeholder="キーワード" aria-label="キーワード" />
              <button className={styles.searchButton} type="submit" aria-label="検索">
                <span className={styles.searchIcon} />
              </button>
            </form>
            <div className={styles.rightGroup}>
              <nav className={styles.nav}>
                {NAV_ITEMS.map((item) => (
                  <a key={item.label} href={item.href} className={styles.navLink}>
                    {item.label}
                  </a>
                ))}
              </nav>
              <a href="/register" className={`${styles.primaryBtn} ${styles.darkCta}`}>無料で始める</a>
            </div>
          </div>
        </header>

        <section className={styles.hero} id="about">
          <div className={styles.copy}>
            <h1 className={styles.heroTitle}>
              AIの力で、理想のキャリアを描く。
              <br />
              <span>スキルマッチ</span>×<span>チャットUI</span>で体験を導く。
            </h1>
            {HERO_COPY.map((text) => (
              <p key={text} className={styles.heroLead}>
                {text}
              </p>
            ))}
            <div className={styles.heroActions}>
              <a href="/register" className={styles.primaryBtn}>今すぐ始める</a>
              <a href="#features" className={styles.ghostBtn}>機能を見る</a>
            </div>
          </div>

          <div className={styles.visual}>
            <div className={styles.visualNoise} />
            <div className={styles.visualGrid} />
            <div className={styles.visualGlow} />
            <div className={styles.visualContent}>
              <div className={styles.visualScene}>
                <div className={styles.visualWindow}>
                  <div className={styles.windowHeader}>
                    <div className={styles.windowDots}>
                      <span />
                      <span />
                      <span />
                    </div>
                    <div className={styles.windowTitle}>EXITOTRINITY</div>
                    <div className={styles.windowTag}>AI Match</div>
                  </div>
                  <div className={styles.windowBody}>
                    <div className={styles.chatRow}>
                      <div className={styles.chatBubble} />
                    </div>
                    <div className={styles.chatRowCenter}>
                      <div className={`${styles.chatBubble} ${styles.chatBubblePrimary}`} />
                    </div>
                    <div className={styles.chatRow}>
                      <div className={styles.chatBubble} />
                    </div>
                  </div>
                </div>
              </div>

              <div className={styles.glassCard}>
                <p className={styles.glassTitle}>CAREER MATCHING SNAPSHOT</p>
                <div className={styles.glassRow}>
                  {[
                    { label: 'AIマッチング', value: '92%', desc: '精度' },
                    { label: '求人数', value: '5000+', desc: '件' },
                    { label: 'チャット', value: '24/7', desc: 'サポート' },
                    { label: '登録者', value: '10K+', desc: 'ユーザー' },
                  ].map((item) => (
                    <div key={item.label} className={styles.miniCard}>
                      <p className={styles.miniLabel}>{item.label}</p>
                      <p className={styles.miniValue}>{item.value}</p>
                      <p className={styles.miniDesc}>{item.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.section} id="features">
          <div className={styles.sectionHeading}>
            <div className={styles.sectionLabel}>FEATURES</div>
            <div>
              <div className={styles.sectionTitle}>求職者とキャリアに、静かに寄り添う。</div>
              <p className={styles.sectionBody}>
                余白を活かした情報設計と、トーンを絞り込んだアクセントで、信頼と安心を感じる転職体験を作ります。
              </p>
            </div>
          </div>
          <div className={styles.highlightGrid}>
            {VALUE_CARDS.map((card) => (
              <div key={card.label} className={styles.highlightCard}>
                <div className={styles.highlightLabel}>{card.label}</div>
                <div className={styles.highlightValue}>{card.desc}</div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.section} id="benefits">
          <div className={styles.sectionHeading}>
            <div className={styles.sectionLabel}>BENEFITS</div>
            <div>
              <div className={styles.sectionTitle}>多層に広がる機能で、転職活動を支える。</div>
              <p className={styles.sectionBody}>
                AI検索、チャット、スキル診断、応募管理。複数の機能を一つの体験に束ね、転職活動の裏側を支えています。
              </p>
            </div>
          </div>
          <div className={styles.cardGrid}>
            {['AI求人検索', 'チャットサポート', 'スキル診断'].map((item, index) => (
              <div key={item} className={styles.card}>
                <div className={styles.cardAccent} />
                <div className={styles.flowBadge}>0{index + 1}</div>
                <div className={styles.cardTitle}>{item}</div>
                <p className={styles.cardText}>求職者と企業の接点を最短距離で結ぶ、柔らかなUIコンポーネント群。</p>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.section} id="users">
          <div className={styles.sectionHeading}>
            <div className={styles.sectionLabel}>FOR EVERYONE</div>
            <div>
              <div className={styles.sectionTitle}>異なるニーズが交差するプラットフォーム。</div>
              <p className={styles.sectionBody}>
                求職者、企業、AI。多様な要素が重なり合い、最適なマッチングに凝縮されています。
              </p>
            </div>
          </div>
          <div className={styles.flowGrid}>
            {['求職者向け', '企業向け', 'AIマッチング'].map((item, index) => (
              <div key={item} className={styles.flowCard}>
                <div className={styles.flowBadge}>0{index + 1}</div>
                <div className={styles.cardTitle}>{item}</div>
                <p className={styles.cardText}>登録から内定まで一気通貫で並走し、確かなキャリア体験に落とし込みます。</p>
              </div>
            ))}
          </div>
        </section>

        </div>
      </div>
      <footer className={styles.footer} id="contact">
        <div className={styles.footerInner}>
          <div>
            <div className={styles.brandMark}>ET</div>
            <div className={styles.sectionBody} style={{ marginTop: 10 }}>
              AIを活用した転職支援プラットフォームで、理想のキャリアを見つけませんか。無料で今すぐ始められます。
            </div>
          </div>
          <div className={styles.footerLinks}>
            <a href="#features">機能</a>
            <a href="#benefits">特徴</a>
            <a href="/login">ログイン</a>
            <a href="/register">登録</a>
          </div>
        </div>
      </footer>
      {isLocationOpen && (
        <div
          className={styles.locationOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="勤務地を選択"
          onClick={closeLocationModal}
        >
          <div className={styles.locationModal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.locationHeader}>
              <div className={styles.locationTitle}>勤務地を選択</div>
              <button
                type="button"
                className={styles.locationClear}
                onClick={() => setLocationDraft([])}
              >
                選択をクリア
              </button>
            </div>
            <div className={styles.locationList}>
              {LOCATION_GROUPS.map((group) => {
                const isOpen = openGroup === group.label;
                return (
                  <div key={group.label} className={styles.locationGroup}>
                    <button
                      type="button"
                      className={styles.locationGroupButton}
                      aria-expanded={isOpen}
                      onClick={() => setOpenGroup(isOpen ? null : group.label)}
                    >
                      {group.label}
                    </button>
                    {isOpen && (
                      <div className={styles.locationOptions}>
                        {group.options.map((option) => (
                          <button
                            key={option}
                            type="button"
                            className={`${styles.locationOption} ${
                              locationDraft.includes(option) ? styles.locationOptionActive : ''
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
            <div className={styles.locationActions}>
              <button type="button" className={styles.locationCancel} onClick={closeLocationModal}>
                キャンセル
              </button>
              <button type="button" className={styles.locationConfirm} onClick={confirmLocation}>
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
      {isJobTypeOpen && (
        <div
          className={styles.jobOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="職種を選択"
          onClick={closeJobTypeModal}
        >
          <div className={styles.jobModal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.jobHeader}>
              <div className={styles.jobTitle}>職種を選択</div>
              <button
                type="button"
                className={styles.jobClear}
                onClick={() => setJobTypeDraft([])}
              >
                選択をクリア
              </button>
            </div>
            <div className={styles.jobList}>
              <div className={styles.jobOptions}>
                {JOB_TYPES.map((type) => {
                  const isSelected = jobTypeDraft.includes(type);
                  return (
                    <button
                      key={type}
                      type="button"
                      className={`${styles.jobOption} ${isSelected ? styles.jobOptionActive : ''}`}
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
            <div className={styles.jobActions}>
              <button type="button" className={styles.jobCancel} onClick={closeJobTypeModal}>
                キャンセル
              </button>
              <button type="button" className={styles.jobConfirm} onClick={confirmJobType}>
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
