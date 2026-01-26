import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RegisterPage } from '../features/auth/pages/RegisterPage';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { LineLinkPage } from '../features/auth/pages/LineLinkPage';
import { LineRegisterPage } from '../features/auth/pages/LineRegisterPage';
import { HomePage } from '../features/dashboard/pages/HomePage';
import { LandingPage } from '../features/landing/pages/LandingPage';
import { PreferencesPage } from '../features/onboarding/pages/PreferencesPage';
import { ResumePage } from '../features/profile/pages/ResumePage';
import { SettingsPage } from '../features/profile/pages/SettingsPage';
import { ChatPage } from '../features/chat/pages/ChatPage';
import { CandidatesPage, CandidateDetailPage } from '../features/candidates/pages';
import { JobsPage, JobDetailPage } from '../features/jobs/pages';
import { JobDetailSeekerPage } from '../features/jobs/pages/JobDetailSeekerPage';
import { JobsSeekerPage } from '../features/jobs/pages/JobsSeekerPage';
import { ApplicationsPage } from '../features/applications/pages';
import { ScoutsPage } from '../features/scouts/pages/ScoutsPage';
import { CandidateSearchPage } from '../features/search/pages/CandidateSearchPage';
import { MembersPage } from '../features/company/pages/MembersPage';
import { ContractsPage } from '../features/company/pages/ContractsPage';
import { ProtectedRoute } from './ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/auth/line-link',
    element: <LineLinkPage />,
  },
  {
    path: '/auth/line-register',
    element: <LineRegisterPage />,
  },
  {
    path: '/preferences',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <PreferencesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/preferencesUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <PreferencesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/resumeUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <ResumePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settingsUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <SettingsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/homeClient',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <HomePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/homeUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <HomePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/chatClient',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <ChatPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/chatUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <ChatPage />
      </ProtectedRoute>
    ),
  },
  // 求人関連
  {
    path: '/jobsClient',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <JobsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/jobsUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <JobsSeekerPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/jobsClient/:id',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <JobDetailPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/jobsUser/:id',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <JobDetailSeekerPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/jobsUser/:id/apply',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <JobDetailSeekerPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/jobsClient/new',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <JobDetailPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/jobsClient/:id/edit',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <JobDetailPage />
      </ProtectedRoute>
    ),
  },
  // 応募管理
  {
    path: '/applications',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <ApplicationsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/applicationsUser',
    element: (
      <ProtectedRoute allowedRoles={['seeker']}>
        <ApplicationsPage />
      </ProtectedRoute>
    ),
  },
  // スカウト
  {
    path: '/scouts',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <ScoutsPage />
      </ProtectedRoute>
    ),
  },
  // 候補者管理（企業向け）
  {
    path: '/applicantsClient',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <CandidatesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/applicantsClient/:id',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <CandidateDetailPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/membersClient',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <MembersPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/contractsClient',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <ContractsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/search',
    element: (
      <ProtectedRoute allowedRoles={['employer']}>
        <CandidateSearchPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
