import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Login } from '../components/Login'; // ✅ UI 컴포넌트 재사용
import { useAuth } from '../hooks/useAuth'; // ✅ React Query 훅 사용

export default function LoginPage() {
    const navigate = useNavigate();
    // ✅ 로그인 상태 확인 (useAuth 훅 활용)
    const { data: user, isLoading } = useAuth();

    // ✅ 이미 로그인된 유저라면 대시보드로 리다이렉트
    useEffect(() => {
        if (!isLoading && user) {
            navigate('/', { replace: true });
        }
    }, [user, isLoading, navigate]);

    const handleLogin = () => {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        window.location.href = `${API_URL}/api/v1/auth/github/login`;
    };

    // ✅ 인증 체크 중이거나 이미 로그인된 상태면 화면 그리지 않음 (UX: 깜빡임 방지)
    if (isLoading || user) return null;

    // ✅ 공통 UI 컴포넌트 렌더링
    return <Login onLogin={handleLogin} />;
}