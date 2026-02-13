import { createBrowserRouter } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import CallbackPage from './pages/CallbackPage';
import DashboardPage from './pages/DashboardPage';
import RepoSelectionPage from './pages/RepoSelectionPage'; // 추가
import ProtectedRoute from './routes/ProtectedRoute';

export const router = createBrowserRouter([
    {
        path: '/login',
        element: <LoginPage />,
    },
    {
        path: '/auth/callback',
        element: <CallbackPage />,
    },
    {
        element: <ProtectedRoute />, 
        children: [
            {
                path: '/',
                element: <DashboardPage />,
            },
            {
                path: '/repo-select', // 추가
                element: <RepoSelectionPage />,
            },
        ],
    },
]);