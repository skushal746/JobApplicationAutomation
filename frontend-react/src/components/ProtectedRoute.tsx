import { Navigate, Outlet } from 'react-router-dom'
import { getToken, hasValidToken, LOGIN_EXPIRED_PATH } from '../auth'

// Rendering must stay free of side effects (React may render twice), so the stale
// token is not removed here; the login page clears it when it opens with reason=expired.
export default function ProtectedRoute() {
  if (!getToken()) return <Navigate to="/login" replace />
  if (!hasValidToken()) return <Navigate to={LOGIN_EXPIRED_PATH} replace />
  return <Outlet />
}
