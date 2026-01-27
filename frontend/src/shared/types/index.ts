// トークンレスポンス型
export interface TokenResponse {
  accessToken: string;
  tokenType?: string;
  expiresIn: number;
}

// ユーザー型
export type UserRole = 'seeker' | 'employer';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'seeker' | 'employer';
  lineLinked?: boolean;
  profileCompletion?: string;
  createdAt: string;

  // 求職者用フィールド
  skills?: string[];
  experienceYears?: string;
  desiredSalaryMin?: string;
  desiredSalaryMax?: string;
  desiredLocation?: string;
  desiredEmploymentType?: string;

  // 企業用フィールド
  companyName?: string;
  industry?: string;
  companySize?: string;
  companyDescription?: string;

  // LINE連携情報
  lineUserId?: string;
  lineDisplayName?: string;
  linePictureUrl?: string;
  lineEmail?: string;
}

// 認証レスポンス型
export interface AuthResponse {
  user: User;
  token: TokenResponse;
}

// 登録データ型
export interface RegisterData {
  email: string;
  password: string;
  name: string;
  role: 'seeker' | 'employer';
  // 企業の場合
  companyName?: string;
  industry?: string;
}

// ログインデータ型
export interface LoginData {
  email: string;
  password: string;
}

// LINE認証データ型
export interface LineAuthData {
  lineUserId: string;
  lineDisplayName: string;
  linePictureUrl?: string;
  lineEmail?: string;
}

// LINE新規登録データ型
export interface LineRegisterData extends LineAuthData {
  name: string;
  role: 'seeker' | 'employer';
  companyName?: string;
  industry?: string;
}

// APIエラー型
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}

// ========================================
// 求人関連の型
// ========================================

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  employmentType: string;
  remote: boolean;
  matchScore?: number;
  tags: string[];
  description: string;
  requirements?: string[];
  benefits?: string[];
  postedDate?: string;
  featured: boolean;
}

export interface JobSearchRequest {
  query?: string;
  location?: string;
  employmentType?: string;
  remote?: boolean;
  salaryMin?: number;
  tags?: string[];
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
  page: number;
  perPage: number;
}

// ========================================
// 応募関連の型
// ========================================

export interface ApplicationCreate {
  jobId: string;
  message?: string;
  resumeSubmitted: boolean;
  portfolioSubmitted: boolean;
  coverLetter?: string;
}

export interface ApplicationUpdate {
  status?: string;
  notes?: string;
}

export interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  company: string;
  location: string;
  salary: string;
  matchScore?: number;
  status: string;
  statusColor: string;
  statusDetail?: string;
  appliedDate: string;
  lastUpdate: string;
  nextStep?: string;
  interviewDate?: string;
  message?: string;
  notes?: string;
  documents: {
    resume: boolean;
    portfolio: boolean;
    coverLetter: boolean;
  };
}

export interface ApplicationListResponse {
  applications: Application[];
  total: number;
}

// ========================================
// ユーザー設定関連の型
// ========================================

export interface PreferencesRequest {
  salary?: number;
  jobType?: string[];
  answers?: Record<string, any>;
  desiredLocation?: string;
  desiredLocations?: string[];
  desiredEmploymentType?: string;
}

export interface ProfileUpdateRequest {
  name?: string;
  // 求職者用フィールド
  skills?: string[];
  experienceYears?: string;
  desiredSalaryMin?: string;
  desiredSalaryMax?: string;
  desiredLocation?: string;
  desiredEmploymentType?: string;
  resumeUrl?: string;
  portfolioUrl?: string;
  // 企業用フィールド
  companyName?: string;
  industry?: string;
  companySize?: string;
  companyDescription?: string;
  companyWebsite?: string;
  companyLocation?: string;
  companyLogoUrl?: string;
}

// ========================================
// マッチング関連の型
// ========================================

export interface SeekerProfileRequest {
  name?: string;
  skills: string[];
  experience?: string;
  education?: string;
  location?: string;
  desired_salary_min?: number;
  preferred_employment_types: string[];
}

export interface CareerChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CareerChatRequest {
  message: string;
  conversation_history: CareerChatMessage[];
  seeker_profile: SeekerProfileRequest;
}

export interface CareerChatResponse {
  reply: string;
}
