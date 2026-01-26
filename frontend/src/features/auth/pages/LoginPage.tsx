import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { initializeLiff } from '../../../shared/lib/liff';
import type { LoginData } from '../../../shared/types';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';

export const LoginPage = () => {
  const { login, loginWithLine, loading, error } = useAuth();
  const [formData, setFormData] = useState<LoginData>({
    email: '',
    password: '',
  });
  const [liffReady, setLiffReady] = useState(false);

  useEffect(() => {
    const initLiff = async () => {
      const initialized = await initializeLiff();
      setLiffReady(initialized);
    };
    initLiff();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(formData);
    } catch (err) {
      // エラーはuseAuthで処理
    }
  };

  const handleLineLogin = async () => {
    try {
      await loginWithLine();
    } catch (err) {
      // エラーはuseAuthで処理
    }
  };

  return (
    <div className="min-h-screen bg-muted flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md rounded-xl border border-border bg-surface p-6 shadow-sm">
        <div className="text-center space-y-1 mb-6">
          <div className="text-sm font-semibold text-primary tracking-[0.08em]">exitotrinity</div>
          <div className="text-xs text-muted-foreground">for Business</div>
        </div>

        <h1 className="text-2xl font-semibold mb-4 text-foreground">ログイン</h1>

        {error && (
          <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        <Button
          onClick={handleLineLogin}
          disabled={loading || !liffReady}
          variant="secondary"
          className="w-full mb-4"
        >
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/>
          </svg>
          {loading ? 'ログイン中...' : 'LINEでログイン'}
        </Button>

        <div className="flex items-center gap-2 my-4">
          <div className="h-px flex-1 bg-border" />
          <div className="text-xs text-muted-foreground">または</div>
          <div className="h-px flex-1 bg-border" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="space-y-1.5">
            <label htmlFor="email" className="text-xs font-semibold text-foreground">
              メールアドレス
            </label>
            <Input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="example@email.com"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="text-xs font-semibold text-foreground">
              パスワード
            </label>
            <Input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="パスワードを入力"
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'ログイン中...' : 'ログイン'}
          </Button>
        </form>

        <div className="mt-4 text-center text-xs text-muted-foreground">
          アカウントをお持ちでない方は{' '}
          <Link to="/register" className="text-primary font-semibold">
            新規登録
          </Link>
        </div>
      </div>
    </div>
  );
};
