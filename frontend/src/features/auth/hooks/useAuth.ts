import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { authApi } from '../../../shared/lib/api';
import type { RegisterData, LoginData, User } from '../../../shared/types';

export const useAuth = () => {
  const navigate = useNavigate();
  const { setAuth, logout: logoutStore, user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const demoUser: User | null = import.meta.env.DEV && !user
    ? {
      id: 'demo-user',
      email: 'demo@example.com',
      name: 'デモユーザー',
      role: 'seeker',
      createdAt: new Date().toISOString(),
    }
    : null;

  const resolvedUser = user ?? demoUser;
  const resolvedIsAuthenticated = isAuthenticated || !!demoUser;

  const getPostLoginPath = (role?: User['role']) => (role === 'seeker' ? '/preferences' : '/homeClient');

  const mapBackendProfileToUser = (profile: any, role: User['role']): User => {
    // FastAPI: user.profile => {user_id,name,email,created_at,...,preferences?}
    // company.profile => {company_id, company_name, email,...}
    if (role === 'employer') {
      return {
        id: String(profile.company_id ?? profile.user_id ?? ''),
        email: profile.email,
        name: profile.company_name ?? profile.name ?? '企業',
        role,
        createdAt: profile.created_at ?? new Date().toISOString(),
        companyName: profile.company_name,
        industry: profile.industry,
        companySize: profile.company_size,
      };
    }

    const prefs = profile.preferences ?? null;
    return {
      id: String(profile.user_id ?? ''),
      email: profile.email,
      name: profile.name,
      role,
      createdAt: profile.created_at ?? new Date().toISOString(),
      desiredSalaryMin: prefs?.salary_min ? String(prefs.salary_min) : undefined,
      desiredLocation: prefs?.location_prefecture ?? undefined,
      desiredEmploymentType: prefs?.employment_type ?? undefined,
    };
  };

  // 新規登録
  const register = async (data: RegisterData) => {
    try {
      setLoading(true);
      setError(null);

      const tokenRes = await authApi.register(data);

      localStorage.setItem('auth-token', tokenRes.access_token);

      const profile = await authApi.me(data.role);
      const mappedUser = mapBackendProfileToUser(profile, data.role);

      setAuth(mappedUser, tokenRes.access_token);

      navigate(getPostLoginPath(mappedUser.role));
      return { user: mappedUser, token: tokenRes };
    } catch (err: any) {
      let message = '登録に失敗しました';
      if (err.response?.data?.detail) {
        message = Array.isArray(err.response.data.detail)
          ? err.response.data.detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ')
          : err.response.data.detail;
      }
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  // ログイン（roleは画面側で決める。未指定ならseeker）
  const login = async (data: LoginData & { role?: User['role'] }) => {
    const role = data.role ?? 'seeker';
    try {
      setLoading(true);
      setError(null);

      const tokenRes = await authApi.login({ ...data, role });

      localStorage.setItem('auth-token', tokenRes.access_token);

      const profile = await authApi.me(role);
      const mappedUser = mapBackendProfileToUser(profile, role);

      setAuth(mappedUser, tokenRes.access_token);

      navigate(getPostLoginPath(mappedUser.role));
      return { user: mappedUser, token: tokenRes };
    } catch (err: any) {
      let message = 'ログインに失敗しました';
      if (err.response?.data?.detail) message = err.response.data.detail;
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };


  // LINE連携はこの統合版では未実装（必要ならバックエンド側にLINE認証APIを追加してください）
  const linkLineAccount = async () => {
    throw new Error('LINE連携は未実装です');
  };
  const registerWithLine = async () => {
    throw new Error('LINE登録は未実装です');
  };
  const loginWithLine = async () => {
    throw new Error('LINEログインは未実装です');
  };

  // ログアウト
  const logout = async () => {
    if (demoUser && !user) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      await authApi.logout();
    } finally {
      localStorage.removeItem('auth-token');
      logoutStore();
      navigate('/login');
      setLoading(false);
    }
  };

  return {
    user: resolvedUser,
    isAuthenticated: resolvedIsAuthenticated,
    loading,
    error,
    register,
    login,
    linkLineAccount,
    registerWithLine,
    loginWithLine,
    logout,
  };
};
