import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { LineAuthData } from '../../../shared/types';
import styles from './RegisterPage.module.css';

export const LineRegisterPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { registerWithLine, loading, error } = useAuth();

  // RegisterPageから渡されたLINEプロフィール情報を取得
  const lineProfile = location.state?.lineProfile as LineAuthData | undefined;

  const [name, setName] = useState(lineProfile?.lineDisplayName || '');
  const [role, setRole] = useState<'seeker' | 'employer'>('seeker');
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [formError, setFormError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!lineProfile) {
      setFormError('LINEプロフィール情報が取得できていません');
      return;
    }

    if (!name) {
      setFormError('お名前を入力してください');
      return;
    }

    if (role === 'employer' && !companyName) {
      setFormError('企業名を入力してください');
      return;
    }

    try {
      await registerWithLine({
        ...lineProfile,
        name,
        role,
        companyName: role === 'employer' ? companyName : undefined,
        industry: role === 'employer' ? industry : undefined,
      });

      // 登録成功後、ロールに応じて遷移
      if (role === 'seeker') {
        navigate('/preferences');
      } else {
        navigate('/homeClient');
      }
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  // プロフィール情報がない場合はRegisterPageに戻す
  if (!lineProfile) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.brand}>
            <div className={styles.brandTitle}>exitotrinity</div>
            <div className={styles.brandSub}>for Business</div>
          </div>
          <div className="text-center py-8">
            <div className={styles.error} style={{ marginBottom: '1rem' }}>
              LINEプロフィール情報が取得できませんでした
            </div>
            <button
              onClick={() => navigate('/register')}
              className={styles.submitButton}
            >
              登録ページに戻る
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* ブランド */}
        <div className={styles.brand}>
          <div className={styles.brandTitle}>exitotrinity</div>
          <div className={styles.brandSub}>for Business</div>
        </div>

        <h1 className={styles.title}>LINE新規登録</h1>

        <div className="mb-4 flex items-center gap-3 p-3 bg-muted rounded-lg">
          {lineProfile.linePictureUrl && (
            <img
              src={lineProfile.linePictureUrl}
              alt="LINE Profile"
              className="w-12 h-12 rounded-full"
            />
          )}
          <div>
            <div className="text-sm font-semibold text-foreground">
              {lineProfile.lineDisplayName}
            </div>
            <div className="text-xs text-muted-foreground">
              LINEアカウントで登録します
            </div>
          </div>
        </div>

        {(error || formError) && (
          <div className={styles.error}>
            {error || formError}
          </div>
        )}

        {/* フォーム */}
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="name" className={styles.label}>
              お名前
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className={styles.input}
              placeholder="山田 太郎"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="role" className={styles.label}>
              利用目的
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as 'seeker' | 'employer')}
              required
              className={styles.select}
            >
              <option value="seeker">求職者として利用</option>
              <option value="employer">企業として利用</option>
            </select>
          </div>

          {role === 'employer' && (
            <>
              <div className={styles.field}>
                <label htmlFor="companyName" className={styles.label}>
                  企業名
                </label>
                <input
                  type="text"
                  id="companyName"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  required
                  className={styles.input}
                  placeholder="株式会社〇〇"
                />
              </div>

              <div className={styles.field}>
                <label htmlFor="industry" className={styles.label}>
                  業種（任意）
                </label>
                <input
                  type="text"
                  id="industry"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className={styles.input}
                  placeholder="IT・通信"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className={styles.submitButton}
          >
            {loading ? '登録中...' : '登録する'}
          </button>
        </form>
      </div>
    </div>
  );
};
