import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import ProtectedRoute from './routes/ProtectedRoute'
import MemberLayout from './components/layout/MemberLayout'
import AdminLayout from './components/layout/AdminLayout'

// Every routed page is code-split so a member never downloads the admin
// bundle (recharts, papaparse, etc.) and vice versa - the entry bundle
// used to ship the entire app (~1.4MB) on first load regardless of which
// single page was actually needed, which is the main reason page loads
// felt slow over a real network even though the code itself was fast.
const WelcomeAuthPage = lazy(() => import('./features/auth/WelcomeAuthPage'))
const SignInPage = lazy(() => import('./features/auth/SignInPage'))
const SignUpPage = lazy(() => import('./features/auth/SignUpPage'))
const ForgotPasswordPage = lazy(() => import('./features/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('./features/auth/ResetPasswordPage'))
const VerifyEmailPage = lazy(() => import('./features/auth/VerifyEmailPage'))
const StaffLoginPage = lazy(() => import('./features/auth/StaffLoginPage'))
const AuthCallbackPage = lazy(() => import('./features/auth/AuthCallbackPage'))
const OnboardingPage = lazy(() => import('./features/auth/OnboardingPage'))
const HomePage = lazy(() => import('./features/home/HomePage'))
const BiblePage = lazy(() => import('./features/bible/BiblePage'))
const BibleBookPage = lazy(() => import('./features/bible/BibleBookPage'))
const SearchPage = lazy(() => import('./features/bible/SearchPage'))
const BookmarksPage = lazy(() => import('./features/bible/BookmarksPage'))
const ProgressPage = lazy(() => import('./features/progress/ProgressPage'))
const CommunityPage = lazy(() => import('./features/community/CommunityPage'))
const CommunityRequestsPage = lazy(() => import('./features/community/CommunityRequestsPage'))
const ChallengeDetailPage = lazy(() => import('./features/community/ChallengeDetailPage'))
const GroupDetailPage = lazy(() => import('./features/community/GroupDetailPage'))
const ChurchDetailPage = lazy(() => import('./features/community/ChurchDetailPage'))
const FellowshipDetailPage = lazy(() => import('./features/community/FellowshipDetailPage'))
const NotificationsPage = lazy(() => import('./features/notifications/NotificationsPage'))
const ProfilePage = lazy(() => import('./features/profile/ProfilePage'))
const NotesPage = lazy(() => import('./features/profile/NotesPage'))
const HighlightsPage = lazy(() => import('./features/profile/HighlightsPage'))
const AchievementsPage = lazy(() => import('./features/profile/AchievementsPage'))
const ReadingHistoryPage = lazy(() => import('./features/profile/ReadingHistoryPage'))
const SettingsPage = lazy(() => import('./features/profile/SettingsPage'))
const HelpSupportPage = lazy(() => import('./features/profile/HelpSupportPage'))
const PlanOverviewPage = lazy(() => import('./features/plans/PlanOverviewPage'))

const AdminDashboardPage = lazy(() => import('./admin/pages/AdminDashboardPage'))
const AdminMembersPage = lazy(() => import('./admin/pages/AdminMembersPage'))
const AdminReadingPlanPage = lazy(() => import('./admin/pages/AdminReadingPlanPage'))
const AdminPlanGeneratorPage = lazy(() => import('./admin/pages/AdminPlanGeneratorPage'))
const AdminAnnouncementsPage = lazy(() => import('./admin/pages/AdminAnnouncementsPage'))
const AdminReportsPage = lazy(() => import('./admin/pages/AdminReportsPage'))
const AdminCsvImportPage = lazy(() => import('./admin/pages/AdminCsvImportPage'))
const AdminSettingsPage = lazy(() => import('./admin/pages/AdminSettingsPage'))
const AdminChallengesPage = lazy(() => import('./admin/pages/AdminChallengesPage'))
const AdminChallengeDetailPage = lazy(() => import('./admin/pages/AdminChallengeDetailPage'))
const AdminAuditLogsPage = lazy(() => import('./admin/pages/AdminAuditLogsPage'))
const AdminFamiliesPage = lazy(() => import('./admin/pages/AdminFamiliesPage'))
const AdminBuddyGroupsPage = lazy(() => import('./admin/pages/AdminBuddyGroupsPage'))
const AdminChurchesPage = lazy(() => import('./admin/pages/AdminChurchesPage'))
const AdminFellowshipsPage = lazy(() => import('./admin/pages/AdminFellowshipsPage'))
const AdminQuizPage = lazy(() => import('./admin/pages/AdminQuizPage'))

const ReadingScreen = lazy(() => import('./features/reading/ReadingScreen'))
const QuizScreen = lazy(() => import('./features/reading/QuizScreen'))

function RouteFallback() {
  return (
    <div className="flex items-center justify-center h-screen">
      <Loader2 className="animate-spin text-primary" size={28} />
    </div>
  )
}

export default function App() {
  return (
    <Suspense fallback={<RouteFallback />}>
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
            <Route path="/community/church/:id" element={<ChurchDetailPage />} />
            <Route path="/community/fellowship/:id" element={<FellowshipDetailPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
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
            <Route path="families" element={<AdminFamiliesPage />} />
            <Route path="buddy-groups" element={<AdminBuddyGroupsPage />} />
            <Route path="churches" element={<AdminChurchesPage />} />
            <Route path="fellowships" element={<AdminFellowshipsPage />} />
            <Route path="quiz" element={<AdminQuizPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
