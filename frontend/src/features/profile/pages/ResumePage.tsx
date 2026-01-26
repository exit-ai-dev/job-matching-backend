import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/hooks/useAuth';
import styles from '../../onboarding/pages/PreferencesPage.module.css';

type ResumeData = {
  lastName: string;
  firstName: string;
  lastNameKana: string;
  firstNameKana: string;
  birthDate: string;
  gender: string;
  phone: string;
  email: string;
  address: string;
  education: string;
  experience: string;
  skills: string;
  qualifications: string;
  summary: string;
  currentSalary: string;
  experienceRoles: string;
  careerChangeReason: string;
  futureVision: string;
  nativeLanguage: string;
  spokenLanguages: string;
  languageSkills: string;
};

const defaultResume: ResumeData = {
  lastName: '',
  firstName: '',
  lastNameKana: '',
  firstNameKana: '',
  birthDate: '',
  gender: '',
  phone: '',
  email: '',
  address: '',
  education: '',
  experience: '',
  skills: '',
  qualifications: '',
  summary: '',
  currentSalary: '',
  experienceRoles: '',
  careerChangeReason: '',
  futureVision: '',
  nativeLanguage: '',
  spokenLanguages: '',
  languageSkills: '',
};

export const ResumePage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const storageKey = useMemo(() => (user ? `resume-${user.id}` : 'resume-guest'), [user?.id]);
  const [resume, setResume] = useState<ResumeData>(defaultResume);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    let storedResume: ResumeData | null = null;
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      try {
        storedResume = { ...defaultResume, ...(JSON.parse(stored) as ResumeData) };
      } catch (error) {
        console.error('履歴書データの読み込みに失敗:', error);
      }
    }

    setResume((prev) => {
      const base = storedResume ?? prev;
      const baseName = base.lastName || base.firstName ? `${base.lastName} ${base.firstName}`.trim() : '';
      const userName = user.name || user.lineDisplayName || '';
      const mergedName = baseName || userName;
      const [lastName = '', ...firstParts] = mergedName.split(' ');
      const firstName = firstParts.join(' ').trim();
      return {
        ...defaultResume,
        ...base,
        lastName: base.lastName || lastName,
        firstName: base.firstName || firstName,
        email: base.email || user.email || '',
      };
    });
  }, [storageKey, user]);

  if (!user) {
    return null;
  }

  const handleChange = (field: keyof ResumeData, value: string) => {
    setResume((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (!resume.lastName || !resume.firstName) {
      alert('氏名を入力してください');
      return;
    }
    setLoading(true);
    try {
      localStorage.setItem(storageKey, JSON.stringify(resume));
    } catch (error) {
      console.error('履歴書データの保存に失敗:', error);
      alert('保存に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <h1 className={styles.brand}>exitotrinity</h1>
          <p className={styles.sub}>resume management</p>
        </div>

        <div className={styles.card}>
          <div className={styles.sectionHeading}>
            <h2 className={styles.title}>履歴書情報を入力してください</h2>
            <p className={styles.lead}>
              登録内容はユーザーに紐づいた履歴書として保存され、応募時に利用されます。
            </p>
          </div>

          <div className={styles.stack}>
            <div className={styles.block}>
              <h3 className={styles.blockTitle}>基本情報</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className={styles.field}>
                  <label className="form-label mb-2">氏名</label>
                  <div className="grid gap-2 sm:grid-cols-2">
                    <input
                      value={resume.lastName}
                      onChange={(event) => handleChange('lastName', event.target.value)}
                      className="form-input"
                      placeholder="山田"
                    />
                    <input
                      value={resume.firstName}
                      onChange={(event) => handleChange('firstName', event.target.value)}
                      className="form-input"
                      placeholder="太郎"
                    />
                  </div>
                </div>
                <div className={styles.field}>
                  <label className="form-label mb-2">氏名（カナ）</label>
                  <div className="grid gap-2 sm:grid-cols-2">
                    <input
                      value={resume.lastNameKana}
                      onChange={(event) => handleChange('lastNameKana', event.target.value)}
                      className="form-input"
                      placeholder="ヤマダ"
                    />
                    <input
                      value={resume.firstNameKana}
                      onChange={(event) => handleChange('firstNameKana', event.target.value)}
                      className="form-input"
                      placeholder="タロウ"
                    />
                  </div>
                </div>
                <div className={styles.field}>
                  <label className="form-label mb-2">生年月日</label>
                  <input
                    type="date"
                    value={resume.birthDate}
                    onChange={(event) => handleChange('birthDate', event.target.value)}
                    className="form-input"
                  />
                </div>
                <div className={styles.field}>
                  <label className="form-label mb-2">性別</label>
                  <select
                    value={resume.gender}
                    onChange={(event) => handleChange('gender', event.target.value)}
                    className="form-input"
                  >
                    <option value="">選択してください</option>
                    <option value="male">男性</option>
                    <option value="female">女性</option>
                    <option value="other">その他</option>
                    <option value="no-answer">回答しない</option>
                  </select>
                </div>
              </div>
            </div>

            <div className={styles.block}>
              <h3 className={styles.blockTitle}>連絡先</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className={styles.field}>
                  <label className="form-label mb-2">電話番号</label>
                  <input
                    value={resume.phone}
                    onChange={(event) => handleChange('phone', event.target.value)}
                    className="form-input"
                    placeholder="090-0000-0000"
                  />
                </div>
                <div className={styles.field}>
                  <label className="form-label mb-2">メールアドレス</label>
                  <input
                    value={resume.email}
                    onChange={(event) => handleChange('email', event.target.value)}
                    className="form-input"
                    placeholder="example@email.com"
                  />
                </div>
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">住所</label>
                <input
                  value={resume.address}
                  onChange={(event) => handleChange('address', event.target.value)}
                  className="form-input"
                  placeholder="東京都千代田区..."
                />
              </div>
            </div>

            <div className={styles.block}>
              <h3 className={styles.blockTitle}>学歴・職歴</h3>
              <div className={styles.field}>
                <label className="form-label mb-2">学歴</label>
                <textarea
                  value={resume.education}
                  onChange={(event) => handleChange('education', event.target.value)}
                  className="form-input resize-none"
                  rows={4}
                  placeholder="例: 2018年3月 ○○大学 卒業"
                />
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">職歴</label>
                <textarea
                  value={resume.experience}
                  onChange={(event) => handleChange('experience', event.target.value)}
                  className="form-input resize-none"
                  rows={5}
                  placeholder="例: 2018年4月 ○○株式会社 入社"
                />
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">経験職種</label>
                <input
                  value={resume.experienceRoles}
                  onChange={(event) => handleChange('experienceRoles', event.target.value)}
                  className="form-input"
                  placeholder="例: フロントエンドエンジニア / UIデザイナー"
                />
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">現(前)年収</label>
                <input
                  value={resume.currentSalary}
                  onChange={(event) => handleChange('currentSalary', event.target.value)}
                  className="form-input"
                  placeholder="500万円"
                />
              </div>
            </div>

            <div className={styles.block}>
              <h3 className={styles.blockTitle}>スキル・資格</h3>
              <div className={styles.field}>
                <label className="form-label mb-2">スキル</label>
                <textarea
                  value={resume.skills}
                  onChange={(event) => handleChange('skills', event.target.value)}
                  className="form-input resize-none"
                  rows={3}
                  placeholder="例: React, TypeScript, AWS"
                />
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">資格</label>
                <textarea
                  value={resume.qualifications}
                  onChange={(event) => handleChange('qualifications', event.target.value)}
                  className="form-input resize-none"
                  rows={3}
                  placeholder="例: 基本情報技術者"
                />
              </div>
            </div>

            <div className={styles.block}>
              <h3 className={styles.blockTitle}>語学スキル</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className={styles.field}>
                  <label className="form-label mb-2">母国語</label>
                  <input
                    value={resume.nativeLanguage}
                    onChange={(event) => handleChange('nativeLanguage', event.target.value)}
                    className="form-input"
                    placeholder="日本語"
                  />
                </div>
                <div className={styles.field}>
                  <label className="form-label mb-2">話せる言語</label>
                  <input
                    value={resume.spokenLanguages}
                    onChange={(event) => handleChange('spokenLanguages', event.target.value)}
                    className="form-input"
                    placeholder="英語 / 中国語"
                  />
                </div>
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">語学スキル</label>
                <textarea
                  value={resume.languageSkills}
                  onChange={(event) => handleChange('languageSkills', event.target.value)}
                  className="form-input resize-none"
                  rows={3}
                  placeholder="例: TOEIC 820点、英語ビジネス会話"
                />
              </div>
            </div>

            <div className={styles.block}>
              <h3 className={styles.blockTitle}>自己PR</h3>
              <div className={styles.field}>
                <label className="form-label mb-2">概要</label>
                <textarea
                  value={resume.summary}
                  onChange={(event) => handleChange('summary', event.target.value)}
                  className="form-input resize-none"
                  rows={4}
                  placeholder="強みや志向性、アピールポイントを記入してください"
                />
              </div>
            </div>

            <div>
              <h3 className={styles.blockTitle}>転職理由・将来の展望</h3>
              <div className={styles.field}>
                <label className="form-label mb-2">転職理由</label>
                <textarea
                  value={resume.careerChangeReason}
                  onChange={(event) => handleChange('careerChangeReason', event.target.value)}
                  className="form-input resize-none"
                  rows={4}
                  placeholder="転職を考えた背景や理由を入力してください"
                />
              </div>
              <div className={styles.field}>
                <label className="form-label mb-2">将来の展望</label>
                <textarea
                  value={resume.futureVision}
                  onChange={(event) => handleChange('futureVision', event.target.value)}
                  className="form-input resize-none"
                  rows={4}
                  placeholder="今後のキャリアで実現したいことを入力してください"
                />
              </div>
            </div>
          </div>

          <div className={styles.actions}>
            <button
              onClick={() => navigate('/homeUser')}
              className="btn btn-secondary flex-1 py-2.5 text-sm"
            >
              ホームへ戻る
            </button>
            <button
              onClick={handleSave}
              disabled={loading}
              className="btn btn-primary flex-1 py-2.5 text-sm"
            >
              {loading ? '保存中...' : '保存する'}
            </button>
          </div>
        </div>

        <p className={styles.note}>
          保存した履歴書は応募時のプロフィールとして利用されます
        </p>
      </div>
    </div>
  );
};
