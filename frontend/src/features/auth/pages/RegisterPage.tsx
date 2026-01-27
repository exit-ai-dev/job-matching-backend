import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { initializeLiff, loginWithLine as liffLogin, getLineProfile, isLineLoggedIn } from '../../../shared/lib/liff';
import type { RegisterData } from '../../../shared/types';
import styles from './RegisterPage.module.css';

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, loading, error } = useAuth();
  const [liffReady, setLiffReady] = useState(false);
  const [lineLoading, setLineLoading] = useState(false);

  useEffect(() => {
    const initLiff = async () => {
      const initialized = await initializeLiff();
      setLiffReady(initialized);

      // LINE OAuth コールバック処理
      // LINEログイン後にリダイレクトされて戻ってきた場合
      if (initialized && isLineLoggedIn()) {
        const lineProfile = await getLineProfile();
        if (lineProfile) {
          // LINEプロフィールを取得できたらLINE登録ページに遷移
          navigate('/auth/line-register', { state: { lineProfile } });
        }
      }
    };
    initLiff();
  }, [navigate]);

  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    name: '',
    role: 'seeker',
  });

  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [formError, setFormError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFormError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    // バリデーション
    if (!formData.email || !formData.password || !formData.name) {
      setFormError('全ての項目を入力してください');
      return;
    }

    if (formData.password !== passwordConfirm) {
      setFormError('パスワードが一致しません');
      return;
    }

    if (formData.password.length < 8) {
      setFormError('パスワードは8文字以上で入力してください');
      return;
    }

    try {
      await register(formData);
      // 登録成功後、LINE連携画面へ
      navigate('/auth/line-link');
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  const handleLineRegister = async () => {
    try {
      setFormError('');

      // LINEログインを開始（これはリダイレクトを引き起こす）
      // リダイレクト後、useEffectで自動的にLINE登録ページに遷移する
      await liffLogin();
    } catch (err: any) {
      console.error('LINE login error:', err);
      setFormError(err.message || 'LINE認証に失敗しました');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* ブランド */}
        <div className={styles.brand}>
          <div className={styles.brandTitle}>exitotrinity</div>
          <div className={styles.brandSub}>for Business</div>
        </div>

        <h1 className={styles.title}>新規登録</h1>

        {(error || formError) && (
          <div className={styles.error}>
            {error || formError}
          </div>
        )}

        {/* LINE登録ボタン */}
        <button
          type="button"
          onClick={handleLineRegister}
          disabled={loading || lineLoading || !liffReady}
          className={styles.submitButton}
          style={{
            backgroundColor: liffReady ? '#06C755' : '#ccc',
            marginBottom: '1rem'
          }}
        >
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24" style={{ marginRight: '8px' }}>
            <path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/>
          </svg>
          {lineLoading ? 'LINE認証中...' : (loading ? '処理中...' : (liffReady ? 'LINEで登録' : 'LIFF初期化中...'))}
        </button>

        <div className="flex items-center gap-2 mb-4">
          <div className="h-px flex-1 bg-border" style={{ borderTop: '1px solid #e0e0e0' }} />
          <div style={{ fontSize: '0.75rem', color: '#666' }}>または</div>
          <div className="h-px flex-1 bg-border" style={{ borderTop: '1px solid #e0e0e0' }} />
        </div>

        {/* フォーム */}
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="name" className={styles.label}>
              お名前
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className={styles.input}
              placeholder="山田 太郎"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="email" className={styles.label}>
              メールアドレス
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className={styles.input}
              placeholder="example@email.com"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="password" className={styles.label}>
              パスワード
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className={styles.input}
              placeholder="8文字以上"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="passwordConfirm" className={styles.label}>
              パスワード（確認）
            </label>
            <input
              type="password"
              id="passwordConfirm"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
              minLength={8}
              className={styles.input}
              placeholder="パスワードを再入力"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="role" className={styles.label}>
              利用目的
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              className={styles.select}
            >
              <option value="seeker">求職者として利用</option>
              <option value="employer">企業として利用</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={styles.submitButton}
          >
            {loading ? '登録中...' : '登録する'}
          </button>
        </form>

        {/* フッター */}
        <div className={styles.footer}>
          すでにアカウントをお持ちの方は{' '}
          <Link to="/login" className={styles.link}>
            ログイン
          </Link>
        </div>
      </div>
    </div>
  );
};
