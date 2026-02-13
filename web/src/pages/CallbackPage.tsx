import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { useQueryClient } from '@tanstack/react-query';

export default function CallbackPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const setAccessToken = useAuthStore((state) => state.setAccessToken);
    const queryClient = useQueryClient();
    const processedRef = useRef(false); // 중복 실행 방지

    useEffect(() => {
        if (processedRef.current) return;
        processedRef.current = true;

        const token = searchParams.get('token');

        if (token) {
            // 1. 토큰 저장 (메모리)
            setAccessToken(token);

            // 2. React Query 캐시 무효화 (이전 유저 데이터 제거)
            queryClient.removeQueries(); 

            console.log("✅ Login successful, token stored.");

            // 3. 홈으로 이동
            navigate('/', { replace: true });
        } else {
            console.error("❌ No token found in URL");
            navigate('/login', { replace: true });
        }
    }, [searchParams, navigate, setAccessToken, queryClient]);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-github-bg">
            <Loader2 className="w-10 h-10 text-github-btn animate-spin mb-4" />
            <h2 className="text-lg font-semibold text-gray-700 dark:text-github-text">
                Authenticating...
            </h2>
            <p className="text-gray-500 text-sm">Logging you in...</p>
        </div>
    );
}