import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/hooks/useAuth';
import { usersApi } from '../../../shared/lib/api';
import { JOB_TYPES } from '../../../shared/constants/jobTypes';
import { LOCATION_GROUPS } from '../../../shared/constants/locationGroups';
import layoutStyles from '../../../shared/components/Layout.module.css';
import styles from './PreferencesPage.module.css';

interface DynamicQuestion {
  id: string;
  question: string;
  type: 'text' | 'select' | 'multiselect';
  options?: string[];
}

export const PreferencesPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // 基本条件
  const [salary, setSalary] = useState(400); // 年収（万円）
  const [jobType, setJobType] = useState<string[]>([]);
  const [jobTypeDraft, setJobTypeDraft] = useState<string[]>([]);
  const [isJobTypeOpen, setIsJobTypeOpen] = useState(false);
  const jobTypePopoverRef = useRef<HTMLDivElement | null>(null);
  const [desiredLocations, setDesiredLocations] = useState<string[]>([]);
  const [locationDraft, setLocationDraft] = useState<string[]>([]);
  const [isLocationOpen, setIsLocationOpen] = useState(false);
  const locationPopoverRef = useRef<HTMLDivElement | null>(null);
  const [openGroup, setOpenGroup] = useState<string | null>(null);

  // 動的質問のサンプル
  const [dynamicQuestions] = useState<DynamicQuestion[]>([
    {
      id: 'work_style',
      question: '希望する働き方を教えてください',
      type: 'select',
      options: ['フルリモート', 'ハイブリッド（週2-3出社）', '完全出社', 'フレキシブル'],
    },
    {
      id: 'company_size',
      question: '希望する企業規模はありますか？',
      type: 'select',
      options: ['スタートアップ（10名未満）', '中小企業（10-100名）', '中堅企業（100-1000名）', '大企業（1000名以上）', 'こだわらない'],
    },
    {
      id: 'career_goal',
      question: '今後のキャリアで重視することは何ですか？',
      type: 'multiselect',
      options: ['技術力の向上', 'マネジメント経験', '年収アップ', 'ワークライフバランス', '裁量権の拡大', '新しい技術への挑戦'],
    },
    {
      id: 'past_experience',
      question: 'これまでの開発経験年数を教えてください',
      type: 'select',
      options: ['1年未満', '1-3年', '3-5年', '5-10年', '10年以上'],
    },
  ]);

  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isJobTypeOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (jobTypePopoverRef.current && !jobTypePopoverRef.current.contains(event.target as Node)) {
        setIsJobTypeOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isJobTypeOpen]);

  useEffect(() => {
    if (!isLocationOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (locationPopoverRef.current && !locationPopoverRef.current.contains(event.target as Node)) {
        setIsLocationOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isLocationOpen]);

  const handleAnswerChange = (questionId: string, value: string | string[], type: string) => {
    if (type === 'multiselect') {
      // 複数選択の場合
      const currentValues = (answers[questionId] as string[]) || [];
      const stringValue = value as string;

      if (currentValues.includes(stringValue)) {
        setAnswers({
          ...answers,
          [questionId]: currentValues.filter((v) => v !== stringValue),
        });
      } else {
        setAnswers({
          ...answers,
          [questionId]: [...currentValues, stringValue],
        });
      }
    } else {
      setAnswers({
        ...answers,
        [questionId]: value,
      });
    }
  };

  const handleSubmit = async () => {
    setLoading(true);

    // バリデーション
    if (jobType.length === 0) {
      alert('職種を選択してください');
      setLoading(false);
      return;
    }

    try {
      // バックエンドに希望条件を保存
      await usersApi.savePreferences({
        salary,
        jobType,
        desiredLocations,
        answers,
      });

      // ホーム画面へ遷移
      navigate('/chatUser');
    } catch (error) {
      console.error('希望条件の保存に失敗:', error);
      alert('保存に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  const jobTypeLabel = jobType.length ? jobType.join(' / ') : '選択してください';
  const locationLabel = desiredLocations.length ? desiredLocations.join(' / ') : '選択してください';

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        {/* ヘッダー */}
        <div className={styles.header}>
          <h1 className={styles.brand}>exitotrinity</h1>
          <p className={styles.sub}>for Business</p>
        </div>

        <div className={styles.card}>
          {/* タイトル */}
          <div className={styles.sectionHeading}>
            <h2 className={styles.title}>
              希望条件を教えてください
            </h2>
            <p className={styles.lead}>
              AIがあなたに最適な求人をマッチングするため、いくつか質問にお答えください
            </p>
          </div>

          {/* プログレスバー */}
          <div className={styles.progressBlock}>
            <div className={styles.progressLabelRow}>
              <span className={styles.progressLabel}>登録の進捗</span>
              <span className={styles.progressValue}>80%</span>
            </div>
            <div className={styles.progressTrack}>
              <div className={styles.progressBar} style={{ width: '80%' }}></div>
            </div>
          </div>

          <div className={styles.stack}>
            {/* 基本条件セクション */}
            <div className={styles.block}>
              <h3 className={styles.blockTitle}>基本条件</h3>

              {/* 年収スライダー */}
              <div className={styles.field}>
                <label className="form-label mb-2">
                  希望年収（万円）
                </label>
                <div className={styles.sliderWrap}>
                  <input
                    type="range"
                    min="300"
                    max="2000"
                    step="50"
                    value={salary}
                    onChange={(e) => setSalary(Number(e.target.value))}
                    className={styles.slider}
                    style={{
                      accentColor: 'var(--color-brand-primary)',
                    }}
                  />
                  <div className={styles.sliderMeta}>
                    <span>300万</span>
                    <span className={styles.sliderValue}>{salary}万円</span>
                    <span>2000万</span>
                  </div>
                </div>
              </div>

              {/* 職種プルダウン */}
              <div className={styles.field}>
                <label className="form-label mb-2">
                  希望職種 <span className="state-error">*</span>
                </label>
                <button
                  type="button"
                  className="form-input text-left"
                  onClick={() => {
                    setJobTypeDraft(jobType);
                    setIsJobTypeOpen(true);
                  }}
                >
                  {jobTypeLabel}
                </button>
              </div>

              <div className={styles.field}>
                <label className="form-label mb-2">希望勤務地</label>
                <button
                  type="button"
                  className="form-input text-left"
                  onClick={() => {
                    setLocationDraft(desiredLocations);
                    setIsLocationOpen(true);
                  }}
                >
                  {locationLabel}
                </button>
              </div>
            </div>

            {/* 動的質問セクション */}
            <div>
              <h3 className={styles.blockTitle}>
                さらに詳しく教えてください
              </h3>
              <p className={styles.blockLead}>
                過去のマッチング実績から、あなたに最適な質問を用意しました
              </p>

              <div className={styles.questionStack}>
                {dynamicQuestions.map((question) => (
                  <div key={question.id} className={styles.questionCard}>
                    <label className="form-label mb-2">
                      {question.question}
                    </label>

                    {question.type === 'select' && question.options && (
                      <select
                        value={(answers[question.id] as string) || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value, question.type)}
                        className="form-input"
                      >
                        <option value="">選択してください</option>
                        {question.options.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    )}

                    {question.type === 'multiselect' && question.options && (
                      <div className={styles.checkStack}>
                        {question.options.map((option) => {
                          const isChecked = ((answers[question.id] as string[]) || []).includes(option);
                          return (
                            <label
                              key={option}
                              className={styles.checkRow}
                            >
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => handleAnswerChange(question.id, option, question.type)}
                                className={styles.checkbox}
                                style={{
                                  accentColor: 'var(--color-brand-primary)',
                                }}
                              />
                              <span className={styles.checkLabel}>{option}</span>
                            </label>
                          );
                        })}
                      </div>
                    )}

                    {question.type === 'text' && (
                      <textarea
                        value={(answers[question.id] as string) || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value, question.type)}
                        className="form-input resize-none"
                        rows={3}
                        placeholder="自由に記入してください"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 送信ボタン */}
          <div className={styles.actions}>
            <button
              onClick={() => navigate('/homeUser')}
              className="btn btn-secondary flex-1 py-2.5 text-sm"
            >
              後で設定する
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="btn btn-primary flex-1 py-2.5 text-sm"
            >
              {loading ? '保存中...' : '完了する'}
            </button>
          </div>
        </div>

        {/* 注記 */}
        <p className={styles.note}>
          後から設定画面でいつでも変更できます
        </p>
      </div>
      {isJobTypeOpen && (
        <div
          className={layoutStyles.headerJobOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="職種を選択"
          onClick={() => setIsJobTypeOpen(false)}
        >
          <div
            className={layoutStyles.headerJobModal}
            onClick={(event) => event.stopPropagation()}
            ref={jobTypePopoverRef}
          >
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
              <button
                type="button"
                className={layoutStyles.headerJobConfirm}
                onClick={() => {
                  setJobType(jobTypeDraft);
                  setIsJobTypeOpen(false);
                }}
              >
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
          <div
            className={layoutStyles.headerLocationModal}
            onClick={(event) => event.stopPropagation()}
            ref={locationPopoverRef}
          >
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
                        {group.options.map((option) => (
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
              <button
                type="button"
                className={layoutStyles.headerLocationConfirm}
                onClick={() => {
                  setDesiredLocations(locationDraft);
                  setIsLocationOpen(false);
                }}
              >
                確定する
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
