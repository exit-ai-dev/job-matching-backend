import axios, { AxiosError } from 'axios';
import type { RegisterData, LoginData, ApiError } from '../types';
import { API_BASE_URL } from '../config/env';

// Axiosインスタンス作成
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（トークンを自動で付与）
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// レスポンスインターセプター（エラーハンドリング）
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-token');
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==============================
// Backend (FastAPI) Adapter APIs
// ==============================

// 認証API（このフロントエンドのUIは role を持つが、バックエンドは user/company で分かれる）
export const authApi = {
  // 新規登録
  register: async (data: RegisterData): Promise<{ access_token: string; user_id: string }> => {
    if (data.role === 'employer') {
      const response = await apiClient.post('/company/register', {
        company_name: data.companyName ?? data.name,
        email: data.email,
        password: data.password,
        industry: data.industry ?? null,
        company_size: null,
        website: null,
      });
      return response.data;
    }
    const response = await apiClient.post('/user/register', {
      name: data.name,
      email: data.email,
      password: data.password,
      age: null,
      gender: null,
      location: null,
    });
    return response.data;
  },

  // ログイン
  login: async (
    data: LoginData & { role?: 'seeker' | 'employer' }
  ): Promise<{ access_token: string; user_id: string }> => {
    const role = data.role ?? 'seeker';
    if (role === 'employer') {
      const response = await apiClient.post('/company/login', {
        email: data.email,
        password: data.password,
      });
      return response.data;
    }
    const response = await apiClient.post('/user/login', {
      email: data.email,
      password: data.password,
    });
    return response.data;
  },

  // 現在のユーザー情報取得（role に応じて呼び分け）
  me: async (role: 'seeker' | 'employer'): Promise<any> => {
    const url = role === 'employer' ? '/company/profile' : '/user/profile';
    const response = await apiClient.get(url);
    return response.data;
  },

  // ログアウト（バックエンド側に専用エンドポイントがないためクライアント側だけで完結）
  logout: async (): Promise<void> => {
    return;
  },
};

// ユーザー設定API
export const usersApi = {
  // 希望条件保存（Step2）
  savePreferences: async (data: {
    salary: number; // 万円
    jobType: string[];
    desiredLocations: string[];
    answers?: Record<string, any>;
  }): Promise<void> => {
    const jobTitle = data.jobType?.[0] ?? '未設定';
    const locationPref = data.desiredLocations?.[0] ?? '未設定';
    const salaryYen = Math.round((data.salary ?? 0) * 10000);

    await apiClient.post('/user/preferences', {
      job_title: jobTitle,
      location_prefecture: locationPref,
      salary_min: salaryYen || null,
      salary_max: salaryYen || null,
      remote_work_preference: (data.answers?.work_style as string) ?? null,
    });
  },
};

// マッチング/チャットAPI（求職者）
export const matchingApi = {
  // チャット（初回は message='初回接続' を送る）
  chat: async (payload: { message: string; context?: { session_id?: string } }): Promise<{
    ai_message: string;
    recommendations: any[] | null;
    conversation_id: string;
    turn_number: number;
    current_score?: number;
  }> => {
    const response = await apiClient.post('/user/chat', payload);
    return response.data;
  },
};

export const jobsApi = {
  // ダッシュボードなどが参照する想定（ひとまず空で返す）
  getJobs: async (_params?: any): Promise<{ jobs: any[]; total: number }> => {
    return { jobs: [], total: 0 };
  },
  searchJobs: async (_params?: any): Promise<{ jobs: any[]; total: number }> => {
    return { jobs: [], total: 0 };
  },
};

export const applicationsApi = {
  // 応募一覧ページなどが参照する想定（ひとまず空で返す）
  getApplications: async (_params?: any): Promise<{ applications: any[]; total: number }> => {
    return { applications: [], total: 0 };
  },
};

export default apiClient;
