import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './routes/ProtectedRoute'
import MemberLayout from './components/layout/MemberLayout'
import AdminLayout from './components/layout/AdminLayout'

import WelcomeAuthPage from './features/auth/WelcomeAuthPage'
import SignInPage from './features/auth/SignInPage'
import SignUpPage from './features/auth/SignUpPage'
import ForgotPasswordPage from './features/auth/ForgotPasswordPage'
import ResetPasswordPage from './features/auth/ResetPasswordPage'
import VerifyEmailPage from './features/auth/VerifyEmailPage'
import StaffLoginPage from './features/auth/StaffLoginPage'
import AuthCallbackPage from './features/auth/AuthCallbackPage'
import OnboardingPage from './features/auth/OnboardingPage'
import HomePage from './features/home/HomePage'
import BiblePage from './features/bible/BiblePage'
import BibleBookPage from './features/bible/BibleBookPage'
import SearchPage from './features/bible/SearchPage'
import BookmarksPage from './features/bible/BookmarksPage'
import ProgressPage from './features/progress/ProgressPage'
import CommunityPage from './features/community/CommunityPage'
import CommunityRequestsPage from './features/community/CommunityRequestsPage'
import ChallengeDetailPage from './features/community/ChallengeDetailPage'
import GroupDetailPage from './features/community/GroupDetailPage'
import ProfilePage from './features/profile/ProfilePage'
import NotesPage from './features/profile/NotesPage'
import HighlightsPage from './features/profile/HighlightsPage'
import AchievementsPage from './features/profile/AchievementsPage'
import ReadingHistoryPage from './features/profile/ReadingHistoryPage'
import SettingsPage from './features/profile/SettingsPage'
import HelpSupportPage from './features/profile/HelpSupportPage'
import PlanOverviewPage from './features/plans/PlanOverviewPage'

import AdminDashboardPage from './admin/pages/AdminDashboardPage'
import AdminMembersPage from './admin/pages/AdminMembersPage'
import AdminReadingPlanPage from './admin/pages/AdminReadingPlanPage'
import AdminPlanGeneratorPage from './admin/pages/AdminPlanGeneratorPage'
import AdminAnnouncementsPage from './admin/pages/AdminAnnouncementsPage'
import AdminReportsPage from './admin/pages/AdminReportsPage'
import AdminCsvImportPage from './admin/pages/AdminCsvImportPage'
import AdminSettingsPage from './admin/pages/AdminSettingsPage'
import AdminChallengesPage from './admin/pages/AdminChallengesPage'
import AdminChallengeDetailPage from './admin/pages/AdminChallengeDetailPage'
import AdminAuditLogsPage from './admin/pages/AdminAuditLogsPage'

import ReadingScreen from './features/reading/ReadingScreen'
import QuizScreen from './features/reading/QuizScreen'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<WelcomeAuthPage />} />
      <Route path="/signin" element={<SignInPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/staff-login" element={<StaffLoginPage />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />

      {/* Member routes */}
      <Route element={<ProtectedRoute allowedRoles={['member', 'leader', 'admin', 'super_admin']} />}>
        <Route element={<MemberLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/bible" element={<BiblePage />} />
          <Route path="/bible/:book" element={<BibleBookPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/community" element={<CommunityPage />} />
          <Route path="/community/requests" element={<CommunityRequestsPage />} />
          <Route path="/community/challenges/:id" element={<ChallengeDetailPage />} />
          <Route path="/community/family/:id" element={<GroupDetailPage kind="family" />} />
          <Route path="/community/buddy-group/:id" element={<GroupDetailPage kind="buddy" />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/plans" element={<PlanOverviewPage />} />
          <Route path="/notes" element={<NotesPage />} />
          <Route path="/highlights" element={<HighlightsPage />} />
          <Route path="/achievements" element={<AchievementsPage />} />
          <Route path="/history" element={<ReadingHistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/help" element={<HelpSupportPage />} />
          <Route path="/bookmarks" element={<BookmarksPage />} />
        </Route>

        {/* Full-screen, distraction-free - deliberately NOT inside MemberLayout so the bottom nav/menus don't show. */}
        <Route path="/bible/search" element={<SearchPage />} />
        <Route path="/read/:book/:chapter" element={<ReadingScreen />} />
        <Route path="/quiz/:chapterId" element={<QuizScreen />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
      </Route>

      {/* Admin routes */}
      <Route element={<ProtectedRoute allowedRoles={['admin', 'super_admin']} />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="members" element={<AdminMembersPage />} />
          <Route path="reading-plan" element={<AdminReadingPlanPage />} />
          <Route path="plan-generator" element={<AdminPlanGeneratorPage />} />
          <Route path="announcements" element={<AdminAnnouncementsPage />} />
          <Route path="reports" element={<AdminReportsPage />} />
          <Route path="csv-import" element={<AdminCsvImportPage />} />
          <Route path="settings" element={<AdminSettingsPage />} />
          <Route path="challenges" element={<AdminChallengesPage />} />
          <Route path="challenges/:id" element={<AdminChallengeDetailPage />} />
          <Route path="audit-logs" element={<AdminAuditLogsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
