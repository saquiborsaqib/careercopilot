import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import OnboardingPage from './pages/OnboardingPage'
import DashboardPage from './pages/DashboardPage'
import ProfilePage from './pages/ProfilePage'
import AcademicPage from './pages/AcademicPage'
import SkillsPage from './pages/SkillsPage'
import CareersPage from './pages/CareersPage'
import CareerDetailPage from './pages/CareerDetailPage'
import RoadmapPage from './pages/RoadmapPage'
import ResumePage from './pages/ResumePage'
import InterviewPage from './pages/InterviewPage'
import OpportunitiesPage from './pages/OpportunitiesPage'
import RecommendationsPage from './pages/RecommendationsPage'

function RootRedirect() {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return null
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<ProtectedRoute requireProfile={false} />}>
            <Route path="/onboarding" element={<OnboardingPage />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/academic" element={<AcademicPage />} />
              <Route path="/skills" element={<SkillsPage />} />
              <Route path="/careers" element={<CareersPage />} />
              <Route path="/careers/:careerId" element={<CareerDetailPage />} />
              <Route path="/roadmap" element={<RoadmapPage />} />
              <Route path="/resume" element={<ResumePage />} />
              <Route path="/interview" element={<InterviewPage />} />
              <Route path="/opportunities" element={<OpportunitiesPage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
