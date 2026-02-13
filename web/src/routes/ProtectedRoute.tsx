import { Navigate, Outlet, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../hooks/useAuth';
import { useRepos } from '../hooks/queries/useRepos';
import { useUIStore } from '../store/useUIStore';
import { useAuthStore } from '../store/useAuthStore'; // ✅ [추가]
import { Layout } from '../components/Layout';
import { Loader2 } from 'lucide-react';
import { useCallback, useMemo } from 'react';
import toast from 'react-hot-toast';
import { logout } from '../api/auth';

export default function ProtectedRoute() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const setAccessToken = useAuthStore((state) => state.setAccessToken); // ✅ [추가] 토큰 초기화 함수 가져오기
    
    const { data: user, isLoading: isAuthLoading, isError } = useAuth();
    const { data: repos, isLoading: isReposLoading } = useRepos();
    const { isDarkMode, toggleTheme } = useUIStore();

    const currentRepo = useMemo(() => {
        return repos?.find(r => r.is_selected) || null;
    }, [repos]);

    // ✅ 로그아웃 핸들러 (수정됨)
    const handleLogout = useCallback(async () => {
        try {
            // 1. 서버 쿠키 삭제 (Refresh Token 폐기)
            await logout(); 

            // 2. 클라이언트 메모리 초기화 (Access Token 삭제)
            setAccessToken(null); // ✅ [중요] 이게 없으면 로그인 상태로 인식됨

            // 3. React Query 캐시 삭제 (유저 정보 등)
            queryClient.removeQueries(); 

            toast.success('Successfully logged out');
            navigate('/login');
        } catch (error) {
            console.error('Logout failed', error);
            // 실패하더라도 클라이언트 상태는 지워주는게 안전함 (강제 로그아웃)
            setAccessToken(null);
            queryClient.removeQueries();
            navigate('/login');
            toast.error('Logout failed, but session cleared locally.');
        }
    }, [navigate, queryClient, setAccessToken]);

    const handleChangeRepo = useCallback(() => {
        navigate('/repo-select');
    }, [navigate]);

    if (isAuthLoading || isReposLoading) {
        return (
            <div className="h-screen flex items-center justify-center bg-white dark:bg-github-bg">
                <Loader2 className="animate-spin text-github-accent" size={32} />
            </div>
        );
    }

    // 토큰이 없거나(user null) 에러가 나면 로그인 페이지로 이동
    if (isError || !user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <Layout
            user={user}
            currentRepo={currentRepo}
            onLogout={handleLogout}
            onChangeRepo={handleChangeRepo}
            isDarkMode={isDarkMode}
            toggleTheme={toggleTheme}
        >
            <Outlet />
        </Layout>
    );
}