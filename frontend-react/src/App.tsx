import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import Dashboard from './pages/Dashboard'
import UpworkJobsPage from './pages/UpworkJobsPage'
import AddUpworkJob from './pages/UpworkJobsPage/add'
import JobEntriesPage from './pages/JobEntriesPage'
import AddJobEntry from './pages/JobEntriesPage/add'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />}>
            <Route path="upwork" element={<UpworkJobsPage />} />
            <Route path="upwork/add" element={<AddUpworkJob />} />
            <Route path="job-entries" element={<JobEntriesPage />} />
            <Route path="job-entries/add" element={<AddJobEntry />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
